#!/usr/bin/env python3
"""
SECURITY CHECKER IMPROVED - AUDIT DOCUSENSE AI
==============================================

Scanner de sécurité amélioré avec patterns précis pour réduire les faux positifs.
Analyse le code pour détecter les vraies vulnérabilités de sécurité.
"""

import os
import re
import ast
import sys
import json
import argparse
import logging
from html import escape as html_escape
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Any, Tuple, Iterable

class SecurityChecker:
    """Scanner de sécurité amélioré avec patterns précis."""
    
    def __init__(
        self,
        project_dir: Path | None = None,
        audit_dir: Path | None = None,
        include_pyi: bool = True,
        include_configs: bool = True,
        include_shell: bool = True,
        max_workers: int = 8,
        verbose: bool = False,
        log_file: str | None = None,
    ):
        self.project_dir = project_dir or Path(__file__).resolve().parent.parent.parent
        self.project_dir = audit_dir or Path(__file__).resolve().parent.parent
        self.include_pyi = include_pyi
        self.include_configs = include_configs
        self.include_shell = include_shell
        self.max_workers = max(1, int(max_workers))
        
        # Configuration du logging
        self.logger = logging.getLogger(f"SecurityChecker_{id(self)}")
        self.logger.setLevel(logging.DEBUG if verbose else logging.INFO)
        
        # Handler console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # Handler fichier si spécifié
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        
        # Patterns de vulnérabilités avec contexte
        self.vulnerability_patterns = {
            'sql_injection': {
                'patterns': [
                    # Requêtes SQL avec f-strings (vraiment dangereux)
                    r'f["\']\s*[^"\']*(?:SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\s+[^"\']*{',
                    # Exécution directe de requêtes utilisateur
                    r'execute\s*\(\s*[^)]*\+\s*[^)]*\)',
                    r'cursor\.execute\s*\(\s*[^)]*\+\s*[^)]*\)',
                ],
                'exclusions': [
                    # Exclure les mises à jour de dictionnaires
                    r'\.update\s*\(\s*{',
                    # Exclure les headers HTTP
                    r'headers\.update',
                    # Exclure les paramètres SQLAlchemy
                    r'primary_key\s*=',
                    r'foreign_key\s*=',
                ],
                'severity': 'HIGH'
            },
            'command_injection': {
                'patterns': [
                    # Exécution de commandes avec entrées utilisateur (chaînes concaténées)
                    r'os\.system\s*\(\s*[^)]*\+\s*[^)]*\)',
                    # Seulement eval/exec avec concaténation (vraiment dangereux)
                    r'eval\s*\(\s*[^)]*\+\s*[^)]*\)',
                    r'exec\s*\(\s*[^)]*\+\s*[^)]*\)',
                ],
                'exclusions': [
                    # Exclure les commandes statiques
                    r'os\.system\s*\(\s*["\'][^"\']*["\']\s*\)',
                    # Exclure les listes d'arguments (bonne pratique)
                    r'subprocess\.run\s*\(\s*\[[^\]]+\]',
                    r'subprocess\.Popen\s*\(\s*\[[^\]]+\]',
                    # Exclure les commandes avec arguments séparés
                    r'subprocess\.run\s*\(\s*\[[^\]]+\],\s*cwd=',
                    r'subprocess\.Popen\s*\(\s*\[[^\]]+\],\s*cwd=',
                    # Exclure les commandes npm, pip, etc. avec listes
                    r'subprocess\.run\s*\(\s*\[["\'](?:npm|pip|python|wmic|explorer|open|xdg-open)["\']',
                    r'subprocess\.Popen\s*\(\s*\[["\'](?:npm|pip|python|wmic|explorer|open|xdg-open)["\']',
                ],
                'severity': 'CRITICAL'
            },
            'sensitive_data_exposure': {
                'patterns': [
                    # Clés API, mots de passe, tokens en dur (vraiment dangereux) - exclure les chaînes vides
                    r'(?:api_key|secret_key|private_key)\s*=\s*["\'][^"\']{1,}["\']',
                    r'password\s*=\s*["\'][^"\']{1,}["\']',
                    r'secret\s*=\s*["\'][^"\']{1,}["\']',
                    # Assignations directes de secrets
                    r'(?:api_key|secret_key|password|token|private_key)\s*=\s*[^=]+["\'][^"\']{1,}["\']',
                ],
                'exclusions': [
                    # Exclure les types et alias
                    r'CacheKey\s*=',
                    r'primary_key\s*=',
                    r'foreign_key\s*=',
                    # Exclure les paramètres de fonction
                    r'def\s+[^(]*\([^)]*password[^)]*\)',
                    r'def\s+[^(]*\([^)]*token[^)]*\)',
                    # Exclure les variables de réception
                    r'password\s*=\s*[^=]+\.get\(',
                    r'token\s*=\s*[^=]+\.credentials',
                    r'password\s*=\s*credentials\.get\(',
                    r'token\s*=\s*credentials\.credentials',
                    # Exclure les récupérations de paramètres
                    r'password\s*=\s*[^=]+\.get\(',
                    r'token\s*=\s*[^=]+\.credentials',
                    # Exclure les assignations depuis des objets
                    r'password\s*=\s*[^=]+\.password',
                    r'token\s*=\s*[^=]+\.token',
                    # Exclure les clés API depuis la configuration
                    r'api_key\s*=\s*config\[',
                    r'api_key\s*=\s*config\.get\(',
                    # Exclure les commentaires
                    r'#.*password',
                    r'#.*secret',
                    # Exclure les chaînes de caractères dans des contextes sûrs
                    r'["\'][^"\']*password[^"\']*["\']',
                    r'["\'][^"\']*token[^"\']*["\']',
                ],
                'severity': 'HIGH'
            },
            'weak_cryptography': {
                'patterns': [
                    # Hash faibles
                    r'hashlib\.md5\s*\(',
                    r'hashlib\.sha1\s*\(',
                    # Chiffrement faible
                    r'base64\.b64encode\s*\(\s*[^)]*password[^)]*\)',
                    r'base64\.b64encode\s*\(\s*[^)]*secret[^)]*\)',
                ],
                'exclusions': [
                    # Exclure l'encodage de données non sensibles
                    r'base64\.b64encode\s*\(\s*buffer\.getvalue\(\)\s*\)',
                    r'base64\.b64encode\s*\(\s*[^)]*image[^)]*\)',
                    r'base64\.b64encode\s*\(\s*[^)]*thumbnail[^)]*\)',
                ],
                'severity': 'MEDIUM'
            },
            'path_traversal': {
                'patterns': [
                    # Accès aux fichiers avec entrées utilisateur
                    r'open\s*\(\s*[^)]*\+\s*[^)]*\)',
                    r'Path\s*\(\s*[^)]*\+\s*[^)]*\)',
                ],
                'exclusions': [
                    # Exclure les chemins statiques
                    r'open\s*\(\s*["\'][^"\']*["\']\s*\)',
                    r'Path\s*\(\s*["\'][^"\']*["\']\s*\)',
                ],
                'severity': 'HIGH'
            }
        }
        
        # Fichiers et dossiers à exclure
        self.excluded_patterns = [
            r'__pycache__',
            r'\.git',
            r'\.venv',
            r'venv',
            r'node_modules',
            r'\.pytest_cache',
            r'codemort',
            r'audit',
            r'\.backup',
            r'\.log',
        ]
    
    def is_excluded_file(self, file_path: Path) -> bool:
        """Vérifie si un fichier doit être exclu de l'analyse."""
        file_str = str(file_path)
        
        for pattern in self.excluded_patterns:
            if re.search(pattern, file_str, re.IGNORECASE):
                return True
        
        return False
    
    def _is_excluded_by_context(self, match_text: str, exclusions: List[str]) -> bool:
        """Vérifie si une correspondance doit être exclue basée sur le contexte."""
        for exclusion in exclusions:
            if re.search(exclusion, match_text, re.IGNORECASE | re.MULTILINE):
                return True
        return False
    
    def scan_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Scanne un fichier pour les vulnérabilités."""
        vulnerabilities = []
        
        # Python source files (.py / .pyi)
        if file_path.suffix in {'.py', '.pyi'}:
            vulnerabilities.extend(self._scan_file_text_regex(file_path))
            vulnerabilities.extend(self._scan_file_ast_python(file_path))
            return vulnerabilities

        # Config files
        if self.include_configs and file_path.suffix.lower() in {'.env', '.json', '.yml', '.yaml'}:
            vulnerabilities.extend(self._scan_config_file(file_path))
            return vulnerabilities

        # Shell scripts
        if self.include_shell and file_path.suffix.lower() in {'.sh'}:
            vulnerabilities.extend(self._scan_shell_file(file_path))
            return vulnerabilities
        
        return vulnerabilities

    def _scan_file_text_regex(self, file_path: Path) -> List[Dict[str, Any]]:
        vulnerabilities: List[Dict[str, Any]] = []
        try:
            # Fallback d'encodage pour gérer latin-1/ISO-8859-1
            try:
                content = file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                self.logger.debug(f"Fallback latin-1 pour {file_path}")
                content = file_path.read_text(encoding='latin-1')
            
            lines = content.split('\n')
            
            # Analyser chaque pattern de vulnérabilité
            for vuln_type, config in self.vulnerability_patterns.items():
                for pattern in config['patterns']:
                    matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                    
                    for match in matches:
                        # Vérifier les exclusions sur le contexte plus large
                        context_start = max(0, match.start() - 100)
                        context_end = min(len(content), match.end() + 100)
                        context = content[context_start:context_end]
                        
                        if self._is_excluded_by_context(context, config.get('exclusions', [])):
                            continue
                        
                        # Obtenir le contexte (ligne)
                        line_num = content[:match.start()].count('\n') + 1
                        line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                        
                        # Vérifier que ce n'est pas un commentaire
                        if line_content.strip().startswith('#'):
                            continue
                        
                        vulnerabilities.append({
                            'file': str(file_path),
                            'type': vuln_type,
                            'pattern': pattern,
                            'line': line_num,
                            'line_content': line_content.strip(),
                            'match': match.group(),
                            'severity': config['severity'],
                            'description': self._get_vulnerability_description(vuln_type)
                        })
        
        except Exception as e:
            self.logger.error(f"Erreur lors du scan de {file_path}: {e}")
        
        return vulnerabilities

    def _scan_file_ast_python(self, file_path: Path) -> List[Dict[str, Any]]:
        """Analyse AST pour réduire les faux positifs et détecter des cas réels."""
        findings: List[Dict[str, Any]] = []
        try:
            # Fallback d'encodage pour AST
            try:
                source = file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                self.logger.debug(f"Fallback latin-1 pour AST {file_path}")
                source = file_path.read_text(encoding='latin-1')
            
            tree = ast.parse(source)
        except Exception:
            return findings

        # Helpers
        def add(vuln_type: str, node: ast.AST, severity: str, desc: str):
            line = getattr(node, 'lineno', 1)
            line_text = source.splitlines()[line - 1] if 0 < line <= len(source.splitlines()) else ''
            findings.append({
                'file': str(file_path),
                'type': vuln_type,
                'pattern': 'ast',
                'line': line,
                'line_content': line_text.strip(),
                'match': '',
                'severity': severity,
                'description': desc,
            })

        sql_keywords = {'select', 'insert', 'update', 'delete', 'drop', 'create', 'alter'}

        class Visitor(ast.NodeVisitor):
            def visit_Assign(self, node: ast.Assign) -> Any:
                # Detect hardcoded secrets
                targets = []
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        targets.append(t.id.lower())
                    elif isinstance(t, ast.Attribute):
                        targets.append(t.attr.lower())
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    for name in targets:
                        if any(k in name for k in ['password', 'secret', 'token', 'api_key', 'private_key']):
                            if node.value.value.strip() != '':
                                add('sensitive_data_exposure', node, 'HIGH', 'Assignation en dur d\'une donnée sensible')
                self.generic_visit(node)

            def visit_Call(self, node: ast.Call) -> Any:
                # Detect hashlib weak hashes
                try:
                    if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == 'hashlib':
                        if node.func.attr in {'md5', 'sha1'}:
                            add('weak_cryptography', node, 'MEDIUM', f"Usage de {node.func.attr} (obsolète)")
                except Exception:
                    pass

                # Detect os.system / subprocess with dynamic input
                def is_dynamic_expr(expr: ast.AST) -> bool:
                    return isinstance(expr, (ast.BinOp, ast.JoinedStr, ast.Call, ast.Name, ast.Attribute))

                func_qual = ''
                if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                    func_qual = f"{node.func.value.id}.{node.func.attr}"
                elif isinstance(node.func, ast.Name):
                    func_qual = node.func.id

                if func_qual in {'os.system'} and node.args:
                    if is_dynamic_expr(node.args[0]):
                        add('command_injection', node, 'CRITICAL', 'os.system avec entrée dynamique')

                if func_qual in {'subprocess.run', 'subprocess.Popen'} and node.args:
                    arg0 = node.args[0]
                    # If first arg is string and dynamic or list with dynamic pieces
                    dynamic = False
                    if is_dynamic_expr(arg0):
                        dynamic = True
                    elif isinstance(arg0, (ast.List, ast.Tuple)):
                        for elt in arg0.elts:
                            if is_dynamic_expr(elt):
                                dynamic = True
                                break
                    if dynamic:
                        add('command_injection', node, 'CRITICAL', f'{func_qual} avec entrée dynamique')

                # Detect SQL constructed dynamically in execute()
                if isinstance(node.func, ast.Attribute) and node.func.attr == 'execute' and node.args:
                    q = node.args[0]
                    dynamic = is_dynamic_expr(q)
                    sql_like = False
                    try:
                        if isinstance(q, ast.Constant) and isinstance(q.value, str):
                            sql_like = any(k in q.value.lower() for k in sql_keywords)
                        elif isinstance(q, ast.JoinedStr):
                            sql_like = True
                        elif isinstance(q, ast.BinOp):
                            sql_like = True
                    except Exception:
                        pass
                    if dynamic and sql_like:
                        add('sql_injection', node, 'HIGH', 'Requête SQL construite dynamiquement')

                self.generic_visit(node)

        Visitor().visit(tree)
        return findings

    def _scan_config_file(self, file_path: Path) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        key_patterns = re.compile(r'(api_key|secret|password|token|private_key)\s*[:=]\s*(.+)', re.IGNORECASE)
        try:
            # Fallback d'encodage pour configs
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
            except UnicodeDecodeError:
                self.logger.debug(f"Fallback latin-1 pour config {file_path}")
                content = file_path.read_text(encoding='latin-1', errors='ignore')
            for idx, line in enumerate(content.splitlines(), start=1):
                m = key_patterns.search(line)
                if m:
                    value = m.group(2).strip().strip('"\'')
                    if value:
                        findings.append({
                            'file': str(file_path),
                            'type': 'sensitive_data_exposure',
                            'pattern': 'config',
                            'line': idx,
                            'line_content': line.strip(),
                            'match': m.group(0),
                            'severity': 'HIGH',
                            'description': 'Secret potentiellement exposé dans un fichier de configuration'
                        })
        except Exception:
            pass
        return findings

    def _scan_shell_file(self, file_path: Path) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        try:
            # Fallback d'encodage pour shell
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
            except UnicodeDecodeError:
                self.logger.debug(f"Fallback latin-1 pour shell {file_path}")
                content = file_path.read_text(encoding='latin-1', errors='ignore')
            for idx, line in enumerate(content.splitlines(), start=1):
                if re.search(r'`.*`|\$\(.*\)', line):
                    findings.append({
                        'file': str(file_path),
                        'type': 'command_injection',
                        'pattern': 'shell',
                        'line': idx,
                        'line_content': line.strip(),
                        'match': 'subshell',
                        'severity': 'HIGH',
                        'description': 'Utilisation de sous-shell potentiellement dangereuse'
                    })
                if re.search(r'\beval\b', line):
                    findings.append({
                        'file': str(file_path),
                        'type': 'command_injection',
                        'pattern': 'shell',
                        'line': idx,
                        'line_content': line.strip(),
                        'match': 'eval',
                        'severity': 'CRITICAL',
                        'description': 'Usage de eval dans un script shell'
                    })
        except Exception:
            pass
        return findings
    
    def _is_excluded_by_context(self, match: str, exclusions: List[str]) -> bool:
        """Vérifie si un match est exclu par le contexte."""
        for exclusion in exclusions:
            if re.search(exclusion, match, re.IGNORECASE):
                return True
        return False
    
    def _get_vulnerability_description(self, vuln_type: str) -> str:
        """Retourne la description d'une vulnérabilité."""
        descriptions = {
            'sql_injection': 'Injection SQL potentielle - requête construite avec des entrées utilisateur',
            'command_injection': 'Injection de commande - exécution de commandes avec entrées utilisateur',
            'sensitive_data_exposure': 'Exposition de données sensibles - clés, mots de passe en dur',
            'weak_cryptography': 'Cryptographie faible - utilisation d\'algorithmes obsolètes',
            'path_traversal': 'Traversée de chemin - accès non sécurisé aux fichiers'
        }
        return descriptions.get(vuln_type, 'Vulnérabilité de sécurité détectée')
    
    def scan_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Scanne le projet pour les vulnérabilités (parallélisé)."""
        self.logger.info("🔒 Scan de sécurité amélioré en cours...")

        files_to_scan: List[Path] = []
        for root, dirs, files in os.walk(self.project_dir):
            dirs[:] = [d for d in dirs if not self.is_excluded_file(Path(root) / d)]
            for file in files:
                file_path = Path(root) / file
                if self.is_excluded_file(file_path):
                    continue
                ext = file_path.suffix.lower()
                if ext in {'.py', '.pyi'} or (self.include_configs and ext in {'.env', '.json', '.yml', '.yaml'}) or (self.include_shell and ext in {'.sh'}):
                    files_to_scan.append(file_path)

        all_vulnerabilities: List[Dict[str, Any]] = []

        def worker(path: Path) -> List[Dict[str, Any]]:
            return self.scan_file(path)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(worker, p): p for p in files_to_scan}
            for fut in as_completed(futures):
                try:
                    all_vulnerabilities.extend(fut.result())
                except Exception as e:
                    self.logger.error(f"Erreur worker: {e}")

        self.logger.info(f"  ✅ {len(files_to_scan)} fichiers scannés")
        self.logger.info(f"  ⚠️ {len(all_vulnerabilities)} vulnérabilités détectées")
        return all_vulnerabilities
    
    def check_best_practices(self) -> List[str]:
        """Vérifie les bonnes pratiques de sécurité."""
        recommendations = [
            "Utiliser des variables d'environnement pour les secrets",
            "Implémenter une validation stricte des entrées utilisateur",
            "Utiliser des requêtes préparées pour les bases de données",
            "Mettre en place une gestion des erreurs sécurisée",
            "Implémenter des logs de sécurité",
            "Effectuer des tests de sécurité réguliers",
            "Utiliser HTTPS en production",
            "Implémenter une authentification forte",
            "Mettre en place des limites de taux (rate limiting)",
            "Utiliser des algorithmes de chiffrement modernes"
        ]
        
        return recommendations
    
    def generate_security_report(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Génère un rapport de sécurité détaillé."""
        # Grouper par sévérité
        by_severity = {}
        for vuln in vulnerabilities:
            severity = vuln['severity']
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(vuln)
        
        # Grouper par type
        by_type = {}
        for vuln in vulnerabilities:
            vuln_type = vuln['type']
            if vuln_type not in by_type:
                by_type[vuln_type] = []
            by_type[vuln_type].append(vuln)
        
        return {
            'summary': {
                'total_vulnerabilities': len(vulnerabilities),
                'critical': len(by_severity.get('CRITICAL', [])),
                'high': len(by_severity.get('HIGH', [])),
                'medium': len(by_severity.get('MEDIUM', [])),
                'low': len(by_severity.get('LOW', []))
            },
            'by_severity': by_severity,
            'by_type': by_type,
            'vulnerabilities': vulnerabilities,
            'recommendations': self.check_best_practices()
        }

def _write_json(report: Dict[str, Any], output_path: Path) -> None:
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')

def _write_html(report: Dict[str, Any], output_path: Path) -> None:
    html = [
        '<!DOCTYPE html>',
        '<html><head><meta charset="utf-8"><title>Security Report</title>',
        '<style>body{font-family:Arial;background:#0b0f17;color:#eaeef5;padding:20px} table{width:100%;border-collapse:collapse;margin-top:12px} th,td{border:1px solid #22303d;padding:8px} th{background:#142030} .sev-CRITICAL{color:#ff6b6b} .sev-HIGH{color:#ffa94d} .sev-MEDIUM{color:#ffd43b} .sev-LOW{color:#69db7c}</style>',
        '</head><body>',
        '<h1>Security Report</h1>',
        f"<p>Total: {report['summary']['total_vulnerabilities']} | Critical: {report['summary']['critical']} | High: {report['summary']['high']} | Medium: {report['summary']['medium']} | Low: {report['summary']['low']}</p>",
        '<table><thead><tr><th>Severity</th><th>Type</th><th>File</th><th>Line</th><th>Description</th><th>Context</th></tr></thead><tbody>'
    ]
    for v in report.get('vulnerabilities', []):
        html.append(
            f"<tr><td class='sev-{html_escape(v['severity'])}'>{html_escape(v['severity'])}</td><td>{html_escape(v['type'])}</td><td>{html_escape(v['file'])}</td><td>{v.get('line','')}</td><td>{html_escape(v.get('description',''))}</td><td><code>{html_escape(v.get('line_content',''))}</code></td></tr>"
        )
    html.extend(['</tbody></table>', '</body></html>'])
    output_path.write_text('\n'.join(html), encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description='SecurityChecker - scanner de sécurité')
    parser.add_argument('--project', type=str, default=None, help='Répertoire projet à scanner')
    parser.add_argument('--include-configs', action='store_true', help='Scanner aussi les fichiers de config (.env/.json/.yml)')
    parser.add_argument('--include-shell', action='store_true', help='Scanner aussi les scripts shell (.sh)')
    parser.add_argument('--no-pyi', action='store_true', help='Ne pas scanner les fichiers .pyi')
    parser.add_argument('--workers', type=int, default=8, help='Nombre de workers (parallélisme)')
    parser.add_argument('--format', choices=['console','json','html'], default='console', help='Format du rapport')
    parser.add_argument('--output', type=str, default=None, help='Chemin du fichier de sortie pour json/html')
    parser.add_argument('--fail-on', choices=['none','low','medium','high','critical','any'], default='none', help='Code de retour non nul si sévérité minimale trouvée')
    parser.add_argument('--verbose', '-v', action='store_true', help='Mode verbeux avec logs détaillés')
    parser.add_argument('--log-file', type=str, default=None, help='Fichier de log pour tracer les erreurs')

    args = parser.parse_args()

    project_dir = Path(args.project).resolve() if args.project else None
    checker = SecurityChecker(
        project_dir=project_dir,
        include_pyi=not args.no_pyi,
        include_configs=args.include_configs,
        include_shell=args.include_shell,
        max_workers=args.workers,
        verbose=args.verbose,
        log_file=args.log_file,
    )

    vulnerabilities = checker.scan_vulnerabilities()
    report = checker.generate_security_report(vulnerabilities)

    if args.format == 'console':
        print(f"\n📊 RAPPORT DE SÉCURITÉ AMÉLIORÉ:")
        print(f"   Total vulnérabilités: {report['summary']['total_vulnerabilities']}")
        print(f"   Critiques: {report['summary']['critical']}")
        print(f"   Élevées: {report['summary']['high']}")
        print(f"   Moyennes: {report['summary']['medium']}")
        print(f"   Faibles: {report['summary']['low']}")
        if vulnerabilities:
            print(f"\n🔍 VULNÉRABILITÉS DÉTECTÉES:")
            for vuln in vulnerabilities:
                print(f"   {vuln['severity']}: {vuln['type']} dans {vuln['file']}:{vuln['line']}")
                print(f"      {vuln['description']}")
        else:
            print(f"\n✅ Aucune vulnérabilité détectée !")
    else:
        out = Path(args.output) if args.output else (Path.cwd() / f"security_report.{args.format}")
        if args.format == 'json':
            _write_json(report, out)
        else:
            _write_html(report, out)
        print(f"✅ Rapport écrit: {out}")

    # Exit code policy
    severity_map = {
        'none': -1,
        'low': 1,
        'medium': 2,
        'high': 3,
        'critical': 4,
        'any': 0,
    }
    threshold = severity_map.get(args.fail_on, -1)
    summary = report['summary']
    should_fail = False
    if args.fail_on == 'any':
        should_fail = summary['total_vulnerabilities'] > 0
    elif threshold >= 4:
        should_fail = summary['critical'] > 0
    elif threshold == 3:
        should_fail = (summary['critical'] + summary['high']) > 0
    elif threshold == 2:
        should_fail = (summary['critical'] + summary['high'] + summary['medium']) > 0
    elif threshold == 1:
        should_fail = summary['total_vulnerabilities'] > 0

    if should_fail:
        sys.exit(1)

if __name__ == "__main__":
    main()
