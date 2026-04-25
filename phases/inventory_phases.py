"""
Phases d'inventaire technique.

Analyse les endpoints API, variables d'environnement, et complexité cyclomatique.
Ces phases produisent un inventaire structuré, directement exploitable par les IA
qui utilisent les rapports comme contexte de travail.
"""

import ast as ast_module
import re
from pathlib import Path
from typing import Dict, Any, List

from .base_phase import BasePhase, AuditIssue, Severity


class InventoryPhases:
    """Regroupe les phases d'inventaire technique."""

    class APIInventoryPhase(BasePhase):
        """
        Inventorie tous les endpoints API du projet (FastAPI, Flask, Django, Express, Vite).

        Détecte les routes HTTP, les méthodes, les fichiers sources, et indique
        si chaque endpoint est protégé par une authentification.
        """

        def execute(self) -> Dict[str, Any]:
            endpoints = []

            # Patterns Python (FastAPI / Flask)
            py_patterns = [
                (r'@(?:router|app)\.(get)\s*\(\s*["\']([^"\']+)', 'GET'),
                (r'@(?:router|app)\.(post)\s*\(\s*["\']([^"\']+)', 'POST'),
                (r'@(?:router|app)\.(put)\s*\(\s*["\']([^"\']+)', 'PUT'),
                (r'@(?:router|app)\.(delete)\s*\(\s*["\']([^"\']+)', 'DELETE'),
                (r'@(?:router|app)\.(patch)\s*\(\s*["\']([^"\']+)', 'PATCH'),
            ]

            # Patterns TypeScript / JavaScript (Express, Vite, React Router)
            ts_patterns = [
                r'router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)',
                r'app\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)',
                r'Route\s+path=["\']([^"\']+)',
            ]

            auth_keywords = [
                'Depends(', 'get_current_user', 'auth_required', 'login_required',
                'jwt', 'token', 'authenticate', 'verify_token', 'require_auth',
                'isAuthenticated', 'requireAuth', 'middleware', 'guard'
            ]

            # Scan Python files
            for file_path in self.project_path.rglob("*.py"):
                if self.is_excluded(file_path):
                    continue
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    lines = content.split('\n')
                    for pattern, method in py_patterns:
                        for match in re.finditer(pattern, content, re.IGNORECASE):
                            line_num = content[:match.start()].count('\n') + 1
                            path = match.group(2)
                            surrounding = content[max(0, match.start() - 300):match.end() + 300]
                            authenticated = any(kw in surrounding for kw in auth_keywords)
                            try:
                                rel = str(file_path.relative_to(self.project_path))
                            except ValueError:
                                rel = str(file_path)
                            endpoints.append({
                                "method": method,
                                "path": path,
                                "file": rel,
                                "framework": "fastapi/flask",
                                "authenticated": authenticated,
                                "line": line_num
                            })
                except Exception:
                    continue

            # Scan TypeScript / JavaScript files
            for file_path in list(self.project_path.rglob("*.ts")) + list(self.project_path.rglob("*.tsx")) + list(self.project_path.rglob("*.js")):
                if self.is_excluded(file_path):
                    continue
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    for pattern in ts_patterns:
                        for match in re.finditer(pattern, content, re.IGNORECASE):
                            groups = match.groups()
                            if len(groups) == 2:
                                method, path = groups[0].upper(), groups[1]
                            else:
                                method, path = 'GET', groups[0]

                            line_num = content[:match.start()].count('\n') + 1
                            surrounding = content[max(0, match.start() - 200):match.end() + 200]
                            authenticated = any(kw in surrounding for kw in auth_keywords)
                            try:
                                rel = str(file_path.relative_to(self.project_path))
                            except ValueError:
                                rel = str(file_path)
                            endpoints.append({
                                "method": method,
                                "path": path,
                                "file": rel,
                                "framework": "express/react",
                                "authenticated": authenticated,
                                "line": line_num
                            })
                except Exception:
                    continue

            # Alertes sur les endpoints d'écriture non authentifiés
            unauthenticated_write = [
                e for e in endpoints
                if not e['authenticated'] and e['method'] in ('POST', 'PUT', 'DELETE', 'PATCH')
            ]
            for ep in unauthenticated_write:
                self.add_issue(AuditIssue(
                    phase="api_inventory",
                    severity=Severity.MAJOR,
                    category="unauthenticated_endpoint",
                    message=f"Endpoint d'écriture non authentifié: {ep['method']} {ep['path']}",
                    file_path=ep['file'],
                    line_number=ep['line'],
                    code_snippet=f"{ep['method']} {ep['path']}",
                    suggestion="Vérifier si cet endpoint doit être protégé par authentification",
                    priority_score=75,
                    estimated_fix_time="30 minutes - 1 heure"
                ))

            by_method: Dict[str, int] = {}
            for ep in endpoints:
                by_method[ep['method']] = by_method.get(ep['method'], 0) + 1

            return {
                "status": "success",
                "summary": f"API inventoriée — {len(endpoints)} endpoints, {len(unauthenticated_write)} non authentifiés (écriture)",
                "total_endpoints": len(endpoints),
                "unauthenticated_write_endpoints": len(unauthenticated_write),
                "endpoints": endpoints,
                "by_method": by_method
            }

    class EnvVarsPhase(BasePhase):
        """
        Inventorie toutes les variables d'environnement utilisées dans le projet.

        Détecte les appels à `os.getenv`, `os.environ`, et les configurations
        similaires pour produire une liste complète des variables requises et optionnelles.
        Génère une alerte si des variables requises n'ont pas de fichier `.env.example`.
        """

        def execute(self) -> Dict[str, Any]:
            env_vars: Dict[str, Dict] = {}

            for file_path in self.project_path.rglob("*.py"):
                if self.is_excluded(file_path):
                    continue
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    try:
                        rel = str(file_path.relative_to(self.project_path))
                    except ValueError:
                        rel = str(file_path)

                    # os.getenv("VAR") ou os.getenv("VAR", "default")
                    for match in re.finditer(
                        r'os\.getenv\(\s*["\']([^"\']+)["\'](?:\s*,\s*["\']([^"\']*)["\'])?\s*\)',
                        content
                    ):
                        var_name = match.group(1)
                        default = match.group(2)
                        if var_name not in env_vars:
                            env_vars[var_name] = {
                                "name": var_name,
                                "has_default": default is not None,
                                "default": default,
                                "files": [],
                                "required": default is None
                            }
                        else:
                            # Si une occurrence n'a pas de défaut, la var est requise
                            if default is None:
                                env_vars[var_name]["required"] = True
                        if rel not in env_vars[var_name]["files"]:
                            env_vars[var_name]["files"].append(rel)

                    # os.environ["VAR"] ou os.environ.get("VAR")
                    for match in re.finditer(
                        r'os\.environ(?:\.get)?\s*\[\s*["\']([^"\']+)["\']',
                        content
                    ):
                        var_name = match.group(1)
                        if var_name not in env_vars:
                            env_vars[var_name] = {
                                "name": var_name,
                                "has_default": False,
                                "default": None,
                                "files": [],
                                "required": True
                            }
                        if rel not in env_vars[var_name]["files"]:
                            env_vars[var_name]["files"].append(rel)

                except Exception:
                    continue

            required_vars = [v for v in env_vars.values() if v['required']]

            has_env_template = any([
                (self.project_path / ".env.example").exists(),
                (self.project_path / ".env.template").exists(),
                (self.project_path / "env.example").exists(),
                (self.project_path / ".env.sample").exists(),
            ])

            if required_vars and not has_env_template:
                self.add_issue(AuditIssue(
                    phase="env_vars",
                    severity=Severity.MINOR,
                    category="missing_env_template",
                    message=f"{len(required_vars)} variable(s) d'env requises sans fichier .env.example",
                    file_path=str(self.project_path),
                    suggestion="Créer un .env.example listant toutes les variables requises (sécurité + onboarding)",
                    priority_score=45,
                    estimated_fix_time="30 minutes"
                ))

            return {
                "status": "success",
                "summary": f"Env vars inventoriées — {len(env_vars)} variables ({len(required_vars)} requises)",
                "total_env_vars": len(env_vars),
                "required_env_vars": len(required_vars),
                "has_env_template": has_env_template,
                "env_vars": list(env_vars.values()),
                "required_vars_names": [v['name'] for v in required_vars]
            }

    class ComplexityPhase(BasePhase):
        """
        Calcule la complexité cyclomatique (CC) par fonction via analyse AST.

        La complexité cyclomatique mesure le nombre de chemins d'exécution indépendants
        dans une fonction. Une CC > 10 signale un code difficile à tester et à maintenir.
        Formule : CC = 1 + (if + for + while + except + with + assert + boolean_ops)
        """

        def execute(self) -> Dict[str, Any]:
            all_functions: List[Dict] = []

            for file_path in self.project_path.rglob("*.py"):
                if self.is_excluded(file_path):
                    continue
                try:
                    source = file_path.read_text(encoding='utf-8', errors='ignore')
                    try:
                        tree = ast_module.parse(source)
                    except SyntaxError:
                        continue

                    try:
                        rel = str(file_path.relative_to(self.project_path))
                    except ValueError:
                        rel = str(file_path)

                    for node in ast_module.walk(tree):
                        if not isinstance(node, (ast_module.FunctionDef, ast_module.AsyncFunctionDef)):
                            continue

                        # Calculer la complexité cyclomatique
                        cc = 1  # Base = 1
                        for child in ast_module.walk(node):
                            if isinstance(child, (
                                ast_module.If, ast_module.While, ast_module.For,
                                ast_module.ExceptHandler, ast_module.With,
                                ast_module.Assert, ast_module.comprehension
                            )):
                                cc += 1
                            elif isinstance(child, ast_module.BoolOp):
                                cc += len(child.values) - 1

                        risk = "HIGH" if cc > 10 else "MEDIUM" if cc > 5 else "LOW"
                        all_functions.append({
                            "function": node.name,
                            "file": rel,
                            "line": node.lineno,
                            "complexity": cc,
                            "risk": risk
                        })

                        if cc > 10:
                            self.add_issue(AuditIssue(
                                phase="complexity",
                                severity=Severity.MAJOR,
                                category="high_complexity",
                                message=f"Fonction '{node.name}' trop complexe (CC={cc}, seuil=10)",
                                file_path=str(file_path),
                                line_number=node.lineno,
                                code_snippet=f"def {node.name}(...)",
                                suggestion="Décomposer en sous-fonctions avec CC < 5 (principe Single Responsibility)",
                                priority_score=65,
                                estimated_fix_time="1-3 heures"
                            ))
                        elif cc > 5:
                            self.add_issue(AuditIssue(
                                phase="complexity",
                                severity=Severity.MINOR,
                                category="medium_complexity",
                                message=f"Fonction '{node.name}' de complexité modérée (CC={cc})",
                                file_path=str(file_path),
                                line_number=node.lineno,
                                code_snippet=f"def {node.name}(...)",
                                suggestion="Envisager une refactorisation pour améliorer la lisibilité",
                                priority_score=30,
                                estimated_fix_time="30-60 minutes"
                            ))

                except Exception:
                    continue

            all_functions.sort(key=lambda x: x['complexity'], reverse=True)
            avg_cc = sum(f['complexity'] for f in all_functions) / len(all_functions) if all_functions else 0

            return {
                "status": "success",
                "summary": f"Complexité analysée — {len(all_functions)} fonctions, CC moyen={avg_cc:.1f}",
                "total_functions": len(all_functions),
                "average_complexity": round(avg_cc, 2),
                "high_risk_functions": len([f for f in all_functions if f['risk'] == 'HIGH']),
                "medium_risk_functions": len([f for f in all_functions if f['risk'] == 'MEDIUM']),
                "top_10_most_complex": all_functions[:10],
                "complexity_distribution": {
                    "low_1_to_5": len([f for f in all_functions if f['complexity'] <= 5]),
                    "medium_6_to_10": len([f for f in all_functions if 5 < f['complexity'] <= 10]),
                    "high_above_10": len([f for f in all_functions if f['complexity'] > 10])
                }
            }
