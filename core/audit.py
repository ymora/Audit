#!/usr/bin/env python3
"""
AUDIT UNIVERSEL - SYSTÈME D'AUDIT GÉNÉRIQUE
==========================================

Script principal d'audit générique qui peut être utilisé pour tous les projets.
Détecte automatiquement le type de projet et lance les tests appropriés.

FONCTIONNALITÉS :
- Détection automatique du type de projet
- Chargement dynamique des tests spécifiques
- Interface unifiée pour tous les projets
- Rapports standardisés
- Configuration flexible
- Stockage des rapports dans chaque projet
"""

import os
import sys
import json
import asyncio
import importlib.util
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class UniversalAuditor:
    """Auditeur universel pour tous les types de projets."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.audit_dir = Path(__file__).parent
        self.project_name = self._detect_project_name()
        self.project_type = self._detect_project_type()
        self.config = self._load_project_config()
        
        # Créer la structure d'audit dans le projet
        self.project_audit_dir = self._setup_project_audit_structure()
        
    def _detect_project_name(self) -> str:
        """Détecte le nom du projet depuis le répertoire."""
        return self.project_path.name.lower().replace(' ', '_').replace('-', '_')
    
    def _detect_project_type(self) -> str:
        """Détecte automatiquement le type de projet."""
        project_files = [f.name.lower() for f in self.project_path.iterdir() if f.is_file()]
        
        # Détection Python/Django/Flask
        if any(f in project_files for f in ['requirements.txt', 'pyproject.toml', 'setup.py']):
            if 'manage.py' in project_files:
                return 'django'
            elif any(f.startswith('app.py') or f.startswith('main.py') for f in project_files):
                return 'flask'
            else:
                return 'python'
        
        # Détection Node.js/React/Vue
        if 'package.json' in project_files:
            if any(f in project_files for f in ['next.config.js', 'nuxt.config.js']):
                return 'nextjs' if 'next.config.js' in project_files else 'nuxtjs'
            elif any(f in project_files for f in ['vite.config.js', 'vite.config.ts']):
                return 'vite'
            else:
                return 'nodejs'
        
        # Détection Java/Maven/Gradle
        if any(f in project_files for f in ['pom.xml', 'build.gradle']):
            return 'java'
        
        # Détection PHP
        if any(f in project_files for f in ['composer.json', 'index.php']):
            return 'php'
        
        # Détection Go
        if 'go.mod' in project_files:
            return 'go'
        
        # Détection Rust
        if 'Cargo.toml' in project_files:
            return 'rust'
        
        # Par défaut
        return 'generic'
    
    def _setup_project_audit_structure(self) -> Path:
        """Configure la structure d'audit dans le projet."""
        project_audit_dir = self.project_path / ".audit"
        
        # Créer la structure de dossiers
        directories = [
            project_audit_dir,
            project_audit_dir / "reports",
            project_audit_dir / "logs",
            project_audit_dir / "config",
            project_audit_dir / "tests"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Copier la configuration du projet si elle existe
        source_config = self.audit_dir / "projects" / self.project_name / "config.json"
        target_config = project_audit_dir / "config" / "project_config.json"
        
        if source_config.exists():
            shutil.copy2(source_config, target_config)
        
        # Copier les tests spécifiques au projet
        source_tests_dir = self.audit_dir / "projects" / self.project_name / "tests"
        target_tests_dir = project_audit_dir / "tests"
        
        if source_tests_dir.exists():
            for test_file in source_tests_dir.glob("*.py"):
                shutil.copy2(test_file, target_tests_dir / test_file.name)
        
        return project_audit_dir
    
    def _load_project_config(self) -> Dict[str, Any]:
        """Charge la configuration spécifique au projet."""
        # Priorité 1: Configuration dans le projet
        project_config_path = self.project_path / ".audit" / "config" / "project_config.json"
        
        # Priorité 2: Configuration dans le système d'audit
        audit_config_path = self.audit_dir / "projects" / self.project_name / "config.json"
        
        if project_config_path.exists():
            with open(project_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif audit_config_path.exists():
            with open(audit_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Configuration par défaut basée sur le type de projet
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Retourne la configuration par défaut selon le type de projet."""
        configs = {
            'python': {
                'test_patterns': ['test_*.py', '*_test.py', 'tests/'],
                'ignore_patterns': ['__pycache__/', '*.pyc', 'venv/', '.venv/'],
                'quality_tools': ['pylint', 'flake8', 'black'],
                'security_tools': ['bandit', 'safety'],
                'coverage_tool': 'coverage'
            },
            'django': {
                'test_patterns': ['test_*.py', '*_test.py', 'tests/', 'test.py'],
                'ignore_patterns': ['__pycache__/', '*.pyc', 'venv/', '.venv/', 'migrations/'],
                'quality_tools': ['pylint', 'flake8', 'black'],
                'security_tools': ['bandit', 'safety', 'django-check'],
                'coverage_tool': 'coverage',
                'django_specific': True
            },
            'flask': {
                'test_patterns': ['test_*.py', '*_test.py', 'tests/'],
                'ignore_patterns': ['__pycache__/', '*.pyc', 'venv/', '.venv/'],
                'quality_tools': ['pylint', 'flake8', 'black'],
                'security_tools': ['bandit', 'safety'],
                'coverage_tool': 'coverage'
            },
            'nodejs': {
                'test_patterns': ['test/', '__tests__/', '*.test.js', '*.spec.js'],
                'ignore_patterns': ['node_modules/', 'dist/', 'build/'],
                'quality_tools': ['eslint', 'prettier'],
                'security_tools': ['npm audit', 'snyk'],
                'coverage_tool': 'nyc'
            },
            'vite': {
                'test_patterns': ['test/', '__tests__/', '*.test.js', '*.spec.js'],
                'ignore_patterns': ['node_modules/', 'dist/', 'build/'],
                'quality_tools': ['eslint', 'prettier'],
                'security_tools': ['npm audit', 'snyk'],
                'coverage_tool': 'vitest'
            },
            'generic': {
                'test_patterns': ['test/', 'tests/', '*test*'],
                'ignore_patterns': ['node_modules/', '__pycache__/', 'dist/', 'build/'],
                'quality_tools': [],
                'security_tools': [],
                'coverage_tool': None
            }
        }
        
        return configs.get(self.project_type, configs['generic'])
    
    def _get_project_tests(self) -> List[str]:
        """Récupère la liste des tests spécifiques au projet."""
        # Priorité 1: Tests dans le projet
        project_tests_dir = self.project_audit_dir / "tests"
        
        # Priorité 2: Tests dans le système d'audit
        audit_tests_dir = self.audit_dir / "projects" / self.project_name / "tests"
        
        tests = []
        
        # Chercher dans le projet d'abord
        if project_tests_dir.exists():
            for test_file in project_tests_dir.glob("*.py"):
                if test_file.name.startswith("test_") and test_file.name != "__init__.py":
                    tests.append(test_file.stem)
        
        # Si aucun test dans le projet, chercher dans le système d'audit
        if not tests and audit_tests_dir.exists():
            for test_file in audit_tests_dir.glob("*.py"):
                if test_file.name.startswith("test_") and test_file.name != "__init__.py":
                    tests.append(test_file.stem)
        
        return tests
    
    def _load_test_module(self, test_name: str) -> Optional[Any]:
        """Charge dynamiquement un module de test."""
        # Priorité 1: Test dans le projet
        project_test_path = self.project_audit_dir / "tests" / f"{test_name}.py"
        
        # Priorité 2: Test dans le système d'audit
        audit_test_path = self.audit_dir / "projects" / self.project_name / "tests" / f"{test_name}.py"
        
        test_path = None
        if project_test_path.exists():
            test_path = project_test_path
        elif audit_test_path.exists():
            test_path = audit_test_path
        
        if not test_path:
            return None
        
        try:
            spec = importlib.util.spec_from_file_location(test_name, test_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            print(f"❌ Erreur chargement test {test_name}: {e}")
            return None
    
    def _setup_logging(self):
        """Configure la journalisation pour ce projet."""
        import logging
        
        # Créer le logger pour ce projet
        logger = logging.getLogger(f"audit_{self.project_name}")
        logger.setLevel(logging.INFO)
        
        # Créer le gestionnaire de fichier
        log_file = self.project_audit_dir / "logs" / f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Créer le formateur
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Ajouter le gestionnaire au logger
        logger.addHandler(file_handler)
        
        return logger, log_file
    
    async def run_project_tests(self) -> Dict[str, Any]:
        """Exécute tous les tests spécifiques au projet."""
        print(f"🧪 Exécution des tests spécifiques à {self.project_name}...")
        
        # Configurer la journalisation
        logger, log_file = self._setup_logging()
        
        results = {
            "project_name": self.project_name,
            "project_type": self.project_type,
            "tests_executed": [],
            "tests_passed": 0,
            "tests_failed": 0,
            "total_tests": 0,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "log_file": str(log_file)
        }
        
        test_modules = self._get_project_tests()
        
        if not test_modules:
            print(f"ℹ️ Aucun test spécifique trouvé pour {self.project_name}")
            logger.info("Aucun test spécifique trouvé")
            return results
        
        for test_name in test_modules:
            print(f"  🔍 Exécution du test: {test_name}")
            logger.info(f"Exécution du test: {test_name}")
            
            module = self._load_test_module(test_name)
            if not module:
                results["tests_failed"] += 1
                logger.error(f"Impossible de charger le test: {test_name}")
                continue
            
            try:
                # Vérifier si le module a une fonction run_test
                if hasattr(module, 'run_test'):
                    test_result = await module.run_test(self.project_path, self.config)
                    results["tests_executed"].append({
                        "name": test_name,
                        "success": test_result.get("success", False),
                        "message": test_result.get("message", ""),
                        "details": test_result.get("details", {})
                    })
                    
                    if test_result.get("success", False):
                        results["tests_passed"] += 1
                        logger.info(f"Test {test_name} réussi: {test_result.get('message', '')}")
                    else:
                        results["tests_failed"] += 1
                        logger.warning(f"Test {test_name} échoué: {test_result.get('message', '')}")
                    
                    results["total_tests"] += 1
                else:
                    print(f"  ⚠️ Module {test_name} n'a pas de fonction run_test")
                    logger.warning(f"Module {test_name} n'a pas de fonction run_test")
                    
            except Exception as e:
                print(f"  ❌ Erreur lors de l'exécution du test {test_name}: {e}")
                logger.error(f"Erreur lors de l'exécution du test {test_name}: {e}")
                results["tests_executed"].append({
                    "name": test_name,
                    "success": False,
                    "message": f"Erreur d'exécution: {str(e)}",
                    "details": {}
                })
                results["tests_failed"] += 1
                results["total_tests"] += 1
        
        results["end_time"] = datetime.now().isoformat()
        return results
    
    async def run_generic_audit(self) -> Dict[str, Any]:
        """Exécute l'audit générique basé sur le type de projet."""
        print(f"🔍 Exécution de l'audit générique pour {self.project_type}...")
        
        # Charger les outils d'audit génériques
        generic_audit_path = self.audit_dir / "tools" / "generic_auditor.py"
        
        if generic_audit_path.exists():
            try:
                spec = importlib.util.spec_from_file_location("generic_auditor", generic_audit_path)
                generic_auditor = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(generic_auditor)
                
                if hasattr(generic_auditor, 'run_generic_audit'):
                    return await generic_auditor.run_generic_audit(self.project_path, self.config)
            except Exception as e:
                print(f"❌ Erreur lors de l'audit générique: {e}")
        
        return {
            "generic_audit": {
                "success": False,
                "message": "Audit générique non disponible",
                "details": {}
            }
        }
    
    async def run_full_audit(self) -> Dict[str, Any]:
        """Exécute l'audit complet du projet."""
        print(f"🚀 Démarrage de l'audit complet pour {self.project_name}")
        print(f"📁 Projet: {self.project_path}")
        print(f"🏷️ Type: {self.project_type}")
        print(f"⚙️ Configuration: {self.config.get('name', 'Par défaut')}")
        print(f"📂 Dossier d'audit: {self.project_audit_dir}")
        print()
        
        # Exécuter les tests spécifiques au projet
        project_results = await self.run_project_tests()
        
        # Exécuter l'audit générique
        generic_results = await self.run_generic_audit()
        
        # Combiner les résultats
        full_results = {
            "audit_info": {
                "project_name": self.project_name,
                "project_type": self.project_type,
                "timestamp": datetime.now().isoformat(),
                "audit_version": "2.0.0",
                "audit_directory": str(self.project_audit_dir)
            },
            "project_tests": project_results,
            "generic_audit": generic_results,
            "summary": {
                "total_tests": project_results["total_tests"],
                "tests_passed": project_results["tests_passed"],
                "tests_failed": project_results["tests_failed"],
                "success_rate": (project_results["tests_passed"] / max(project_results["total_tests"], 1)) * 100
            }
        }
        
        # Sauvegarder les résultats dans le projet
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reports_dir = self.project_audit_dir / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = reports_dir / f"audit_report_{timestamp}.json"
        html_file = reports_dir / f"audit_report_{timestamp}.html"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(full_results, f, indent=2, ensure_ascii=False)
        
        # Générer le rapport HTML
        html_report = self._generate_html_report(full_results)
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        # Créer un lien vers le rapport le plus récent
        latest_report = reports_dir / "latest_report.json"
        latest_html = reports_dir / "latest_report.html"
        
        shutil.copy2(report_file, latest_report)
        shutil.copy2(html_file, latest_html)
        
        print(f"\n✅ Audit terminé avec succès!")
        print(f"📊 Résultats:")
        print(f"   - Tests exécutés: {project_results['total_tests']}")
        print(f"   - Tests réussis: {project_results['tests_passed']}")
        print(f"   - Tests échoués: {project_results['tests_failed']}")
        print(f"   - Taux de succès: {full_results['summary']['success_rate']:.1f}%")
        print(f"📄 Rapports:")
        print(f"   - JSON: {report_file}")
        print(f"   - HTML: {html_file}")
        print(f"   - Log: {project_results.get('log_file', 'N/A')}")
        print(f"🔗 Rapport le plus récent:")
        print(f"   - {latest_report}")
        print(f"   - {latest_html}")
        
        return full_results
    
    def _generate_html_report(self, results: Dict[str, Any]) -> str:
        """Génère un rapport HTML pour les résultats."""
        project_name = results["audit_info"]["project_name"]
        timestamp = results["audit_info"]["timestamp"]
        success_rate = results["summary"]["success_rate"]
        
        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Audit - {project_name}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 2.5em; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
        .content {{ padding: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .summary-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #667eea; }}
        .summary-card h3 {{ margin: 0 0 10px 0; color: #333; }}
        .summary-card .value {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .tests-section {{ margin-top: 30px; }}
        .test-item {{ background: #f8f9fa; margin: 10px 0; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745; }}
        .test-item.failed {{ border-left-color: #dc3545; }}
        .test-item h4 {{ margin: 0 0 10px 0; color: #333; }}
        .test-item .status {{ font-weight: bold; }}
        .test-item .status.success {{ color: #28a745; }}
        .test-item .status.failed {{ color: #dc3545; }}
        .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; border-top: 1px solid #dee2e6; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Audit Universel</h1>
            <p>Rapport d'audit pour {project_name} - {timestamp}</p>
        </div>
        
        <div class="content">
            <div class="summary">
                <div class="summary-card">
                    <h3>Tests Totaux</h3>
                    <div class="value">{results['summary']['total_tests']}</div>
                </div>
                <div class="summary-card">
                    <h3>Tests Réussis</h3>
                    <div class="value">{results['summary']['tests_passed']}</div>
                </div>
                <div class="summary-card">
                    <h3>Tests Échoués</h3>
                    <div class="value">{results['summary']['tests_failed']}</div>
                </div>
                <div class="summary-card">
                    <h3>Taux de Succès</h3>
                    <div class="value">{success_rate:.1f}%</div>
                </div>
            </div>
            
            <div class="tests-section">
                <h2>🧪 Tests Exécutés</h2>
                """
        
        for test in results["project_tests"]["tests_executed"]:
            status_class = "success" if test["success"] else "failed"
            item_class = "test-item" if test["success"] else "test-item failed"
            
            html += f"""
                <div class="{item_class}">
                    <h4>{test['name']}</h4>
                    <div class="status {status_class}">
                        {'✅ Réussi' if test['success'] else '❌ Échoué'}
                    </div>
                    <p>{test['message']}</p>
                </div>
            """
        
        html += """
            </div>
        </div>
        
        <div class="footer">
            <p>Rapport généré automatiquement par le système d'audit universel</p>
        </div>
    </div>
</body>
</html>"""
        
        return html

async def main():
    """Fonction principale."""
    try:
        # Détecter le chemin du projet (répertoire parent du dossier audit)
        audit_dir = Path(__file__).parent
        project_path = audit_dir.parent
        
        print(f"🎯 Audit Universel - Détection automatique du projet")
        print(f"📁 Projet détecté: {project_path}")
        print()
        
        # Créer l'auditeur
        auditor = UniversalAuditor(project_path)
        
        # Exécuter l'audit complet
        await auditor.run_full_audit()
        
    except KeyboardInterrupt:
        print("\n⚠️ Audit interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur lors de l'audit: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
