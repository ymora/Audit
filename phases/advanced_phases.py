"""
Phases avancées d'audit - phases spécialisées
"""

import re
from pathlib import Path
from typing import Dict, Any, List
from .base_phase import BasePhase, AuditIssue, Severity


class AdvancedPhases:
    """Regroupe les phases avancées spécialisées"""
    
    class DevOpsPhase(BasePhase):
        """Phase DevOps - CI/CD, Docker"""
        
        def execute(self) -> Dict[str, Any]:
            ci_files = ['.github/workflows', '.gitlab-ci.yml', 'Jenkinsfile', 'Dockerfile', 'docker-compose.yml']
            found_ci = any((self.project_path / ci_file).exists() for ci_file in ci_files)
            
            if not found_ci:
                self.add_issue(AuditIssue(
                    phase="devops",
                    severity=Severity.INFO,
                    category="ci_cd",
                    message="Aucun fichier CI/CD détecté",
                    file_path=str(self.project_path),
                    suggestion="Ajouter GitHub Actions ou GitLab CI pour l'automatisation",
                    priority_score=40,
                    estimated_fix_time="1-2 heures"
                ))
            
            return {
                "status": "success",
                "summary": f"Analyse DevOps terminée - {len(self.issues)} problèmes détectés",
                "issues_found": len(self.issues),
                "ci_cd_present": found_ci
            }
    
    class UXPhase(BasePhase):
        """Phase UX - accessibilité, responsive design"""
        
        def execute(self) -> Dict[str, Any]:
            html_files = list(self.project_path.rglob("*.html"))
            jsx_files = list(self.project_path.rglob("*.jsx"))
            tsx_files = list(self.project_path.rglob("*.tsx"))
            
            for file_path in html_files + jsx_files + tsx_files:
                if self.is_excluded(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if not re.search(r'alt=', content):
                            self.add_issue(AuditIssue(
                                phase="ux",
                                severity=Severity.MINOR,
                                category="accessibility",
                                message="Attribut alt manquant sur les images",
                                file_path=str(file_path),
                                suggestion="Ajouter des attributs alt pour l'accessibilité",
                                priority_score=30,
                                estimated_fix_time="30 minutes"
                            ))
                except Exception:
                    continue
            
            return self.get_results()
    
    class DocumentationPhase(BasePhase):
        """Phase d'analyse de documentation"""
        
        def execute(self) -> Dict[str, Any]:
            total_files = 0
            documented_files = 0
            
            for file_path in self.project_path.rglob("*.py"):
                if self.is_excluded(file_path):
                    continue
                
                total_files += 1
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if '"""' in content or "'''" in content:
                            documented_files += 1
                except Exception:
                    continue
            
            coverage = (documented_files / total_files * 100) if total_files > 0 else 0
            
            if coverage < 50:
                self.add_issue(AuditIssue(
                    phase="documentation",
                    severity=Severity.MINOR,
                    category="documentation_coverage",
                    message=f"Couverture documentation faible: {coverage:.1f}%",
                    file_path=str(self.project_path),
                    suggestion="Améliorer la documentation des fonctions et classes",
                    priority_score=30,
                    estimated_fix_time="2-4 heures"
                ))
            
            return {
                "status": "success",
                "summary": f"Analyse documentation terminée - {len(self.issues)} problèmes détectés",
                "issues_found": len(self.issues),
                "coverage": coverage,
                "documented_files": documented_files,
                "total_files": total_files
            }
    
    class ProjectManagementPhase(BasePhase):
        """Phase de gestion de projet"""
        
        def execute(self) -> Dict[str, Any]:
            pm_files = ['README.md', 'CHANGELOG.md', 'CONTRIBUTING.md', 'LICENSE']
            missing_pm = [pm_file for pm_file in pm_files if not (self.project_path / pm_file).exists()]
            
            if missing_pm:
                self.add_issue(AuditIssue(
                    phase="project_management",
                    severity=Severity.INFO,
                    category="documentation",
                    message=f"Fichiers de gestion de projet manquants: {', '.join(missing_pm)}",
                    file_path=str(self.project_path),
                    suggestion="Ajouter README.md, CHANGELOG.md pour améliorer la gestion",
                    priority_score=25,
                    estimated_fix_time="1 heure"
                ))
            
            return {
                "status": "success",
                "summary": f"Gestion de projet analysée - {len(self.issues)} problèmes détectés",
                "issues_found": len(self.issues),
                "missing_files": missing_pm
            }
    
    class MaintenancePhase(BasePhase):
        """Phase de maintenance - dette technique"""
        
        def execute(self) -> Dict[str, Any]:
            total_complexity = 0
            for f in self.project_path.rglob("*.py"):
                if not any(exclude_dir in str(f) for exclude_dir in self.exclude_dirs):
                    try:
                        with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                            total_complexity += len(re.findall(r'\bif\b|\bfor\b|\bwhile\b', file.read()))
                    except Exception:
                        continue
            
            maintenance_score = max(0, 100 - total_complexity / 10)
            
            return {
                "status": "success",
                "summary": "Analyse de maintenance terminée",
                "maintenance_score": maintenance_score,
                "technical_debt_level": "LOW" if maintenance_score > 70 else "MEDIUM" if maintenance_score > 40 else "HIGH"
            }
    
    class ScalabilityPhase(BasePhase):
        """Phase de scalabilité"""
        
        def execute(self) -> Dict[str, Any]:
            scaling_patterns = ['cache', 'queue', 'async', 'load_balancer', 'redis']
            found_scaling = False
            
            for file_path in self.project_path.rglob("*.py"):
                if self.is_excluded(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        if any(pattern in content for pattern in scaling_patterns):
                            found_scaling = True
                            break
                except Exception:
                    continue
            
            if not found_scaling:
                self.add_issue(AuditIssue(
                    phase="scalability",
                    severity=Severity.INFO,
                    category="scalability",
                    message="Aucun mécanisme de scaling détecté",
                    file_path=str(self.project_path),
                    suggestion="Considérer l'ajout de cache, queues ou async pour la scalabilité",
                    priority_score=35,
                    estimated_fix_time="2-4 heures"
                ))
            
            return {
                "status": "success",
                "summary": f"Analyse de scalabilité terminée - {len(self.issues)} problèmes détectés",
                "issues_found": len(self.issues),
                "scaling_mechanisms": found_scaling
            }

    class InnovationPhase(BasePhase):
        """Phase d'innovation - veille technologique"""
        
        def execute(self) -> Dict[str, Any]:
            modern_tech_patterns = ['async', 'await', 'typing', 'dataclass', 'type hints']
            found_modern = False
            
            for file_path in self.project_path.rglob("*.py"):
                if self.is_excluded(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        if any(pattern in content for pattern in modern_tech_patterns):
                            found_modern = True
                            break
                except Exception:
                    continue
            
            if not found_modern:
                self.add_issue(AuditIssue(
                    phase="innovation",
                    severity=Severity.INFO,
                    category="innovation",
                    message="Technologies modernes non détectées",
                    file_path=str(self.project_path),
                    suggestion="Considérer l'ajout de type hints, async/await, dataclasses",
                    priority_score=25,
                    estimated_fix_time="2-4 heures"
                ))
            
            return {
                "status": "success",
                "summary": f"Analyse d'innovation terminée - {len(self.issues)} problèmes détectés",
                "issues_found": len(self.issues),
                "modern_tech_detected": found_modern
            }

    class GitHistoryPhase(BasePhase):
        """
        Phase d'historique Git — analyse l'évolution et la santé temporelle du projet.
        
        Récupère les statistiques de commits, les auteurs principaux, et identifie
        les fichiers avec un taux de rotation (churn) élevé, souvent signes de dette.
        """
        
        def execute(self) -> Dict[str, Any]:
            import subprocess
            git_dir = self.project_path / ".git"
            
            if not git_dir.exists():
                return {
                    "status": "info",
                    "summary": "Pas un dépôt Git — analyse historique ignorée",
                    "has_git": False
                }
            
            try:
                # 1. Nombre total de commits
                total_commits = subprocess.check_output(
                    ["git", "rev-list", "--count", "HEAD"], 
                    cwd=self.project_path, stderr=subprocess.DEVNULL
                ).decode().strip()
                
                # 2. Top 3 auteurs
                authors = subprocess.check_output(
                    ["git", "shortlog", "-sn", "--all", "HEAD"], 
                    cwd=self.project_path, stderr=subprocess.DEVNULL
                ).decode().strip().split('\n')
                top_authors = [a.strip() for a in authors[:3] if a.strip()]
                
                # 3. Fichiers les plus modifiés (Churn)
                churn = subprocess.check_output(
                    ["git", "log", "--format=", "--name-only"], 
                    cwd=self.project_path, stderr=subprocess.DEVNULL
                ).decode().split('\n')
                from collections import Counter
                most_modified = Counter([f for f in churn if f.endswith('.py')]).most_common(5)
                
                return {
                    "status": "success",
                    "summary": f"Historique Git analysé — {total_commits} commits détectés",
                    "has_git": True,
                    "total_commits": int(total_commits),
                    "top_authors": top_authors,
                    "file_churn": [{"file": f, "changes": c} for f, c in most_modified]
                }
            except Exception as e:
                return {
                    "status": "warning",
                    "summary": f"Analyse Git partielle : {str(e)}",
                    "has_git": True
                }
    
    class KnowledgePhase(BasePhase):
        """
        Phase de base de connaissance — vérifie la présence de documentation et de wiki.
        """
        
        def execute(self) -> Dict[str, Any]:
            kb_files = ['docs/', 'wiki/', 'knowledge_base/', 'README.md']
            found_kb = any((self.project_path / kb_file).exists() for kb_file in kb_files)
            
            if not found_kb:
                self.add_issue(AuditIssue(
                    phase="knowledge",
                    severity=Severity.INFO,
                    category="knowledge_base",
                    message="Base de connaissance non détectée (docs/, wiki/, README.md)",
                    file_path=str(self.project_path),
                    suggestion="Ajouter docs/ ou wiki/ pour centraliser la documentation",
                    priority_score=30,
                    estimated_fix_time="1-2 heures"
                ))
            
            return {
                "status": "success",
                "summary": f"Base de connaissance analysée - {len(self.issues)} problèmes",
                "issues_found": len(self.issues),
                "knowledge_base_present": found_kb
            }
    
    class ResearchPhase(BasePhase):
        """
        Phase de recherche — vérifie la présence de tests automatisés.
        """
        
        def execute(self) -> Dict[str, Any]:
            test_files = (
                list(self.project_path.rglob("test_*.py")) +
                list(self.project_path.rglob("*_test.py"))
            )
            
            if not test_files:
                self.add_issue(AuditIssue(
                    phase="research",
                    severity=Severity.INFO,
                    category="testing",
                    message="Aucun fichier de test Python détecté",
                    file_path=str(self.project_path),
                    suggestion="Ajouter des tests unitaires avec pytest",
                    priority_score=40,
                    estimated_fix_time="2-4 heures"
                ))
            
            return {
                "status": "success",
                "summary": f"Tests analysés - {len(test_files)} fichiers trouvés",
                "issues_found": len(self.issues),
                "test_files_count": len(test_files)
            }
    
    class ExcellencePhase(BasePhase):
        """
        Phase d'excellence — évalue les facteurs de qualité globale du projet.
        """
        
        def execute(self) -> Dict[str, Any]:
            factors = {
                'has_git': (self.project_path / '.git').exists(),
                'has_readme': (self.project_path / 'README.md').exists(),
                'has_license': (self.project_path / 'LICENSE').exists(),
                'has_requirements': (self.project_path / 'requirements.txt').exists()
            }
            score = sum(factors.values()) / len(factors) * 100
            
            return {
                "status": "success",
                "summary": f"Excellence évaluée - score {score:.0f}%",
                "excellence_score": score,
                "factors": factors,
                "excellence_level": "HIGH" if score > 75 else "MEDIUM" if score > 50 else "LOW"
            }
    
    class AIMLPhase(BasePhase):
        """
        Phase IA/ML — détecte les composants d'intelligence artificielle.
        """
        
        def execute(self) -> Dict[str, Any]:
            ai_patterns = [
                r'tensorflow', r'pytorch', r'sklearn', r'keras',
                r'ollama', r'openai', r'faiss', r'langchain',
                r'numpy', r'pandas', r'scipy'
            ]
            
            ai_components = []
            for file_path in self.project_path.rglob("*.py"):
                if self.is_excluded(file_path):
                    continue
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    for pattern in ai_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            ai_components.append({"file": str(file_path), "pattern": pattern})
                except Exception:
                    continue
            
            return {
                "status": "success",
                "summary": f"IA/ML analysé - {len(ai_components)} composants détectés",
                "ai_components_found": len(ai_components),
                "ai_components": ai_components[:20]
            }
    
    class SustainabilityPhase(BasePhase):
        """
        Phase de durabilité — délègue à DocumentationPhase pour éviter la duplication.
        
        Maintenue pour compatibilité avec les rapports existants.
        """
        
        def execute(self) -> Dict[str, Any]:
            doc_phase = AdvancedPhases.DocumentationPhase(
                self.project_path, self.exclude_dirs, self.exclude_files
            )
            result = doc_phase.execute()
            result["summary"] = result.get("summary", "").replace("documentation", "durabilité")
            return result

    class ReportingPhase(BasePhase):
        """
        Phase de préparation du reporting PREMIUM.
        
        Initialise les structures nécessaires à la génération du dashboard visuel
        et du rapport JSON consolidé.
        """
        
        def execute(self) -> Dict[str, Any]:
            return {
                "status": "success",
                "summary": "Structure de reporting Graal v4.0 prête pour finalisation",
                "formats": ["JSON", "HTML (Premium Dashboard)"]
            }
    
    class FinalizationPhase(BasePhase):
        """
        Phase de finalisation — calcule les statistiques globales.
        """
        
        def execute(self) -> Dict[str, Any]:
            try:
                all_files = [f for f in self.project_path.rglob("*") if f.is_file() and not self.is_excluded(f)]
                py_files = [f for f in all_files if f.suffix == '.py']
                total_size_mb = sum(f.stat().st_size for f in all_files) / 1024 / 1024
                
                extensions = {}
                for f in all_files:
                    ext = f.suffix.lower() or "(sans extension)"
                    extensions[ext] = extensions.get(ext, 0) + 1
                top_ext = sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:5]
                
                return {
                    "status": "success",
                    "summary": "Finalisation et consolidation terminées",
                    "total_files": len(all_files),
                    "python_files": len(py_files),
                    "total_size_mb": round(total_size_mb, 2),
                    "top_extensions": dict(top_ext)
                }
            except Exception as e:
                return {"status": "error", "summary": f"Finalisation échouée : {e}"}
