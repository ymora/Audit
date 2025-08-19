#!/usr/bin/env python3
"""
SYSTÈME DE NETTOYAGE AUTOMATIQUE - DOSSERS .PROJECT
===================================================

Système de nettoyage automatique pour les dossiers .project selon les mêmes
règles que les audits.
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class ProjectCleaner:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.project_dir = project_path / ".project"
        self.config_file = self.project_dir / "config" / "cleanup_config.json"
        
    def load_cleanup_config(self) -> Dict:
        """Charge la configuration de nettoyage."""
        default_config = {
            "enabled": True,
            "retention_days": {
                "logs": 30,
                "reports": 90,
                "tests": 60
            },
            "max_files": {
                "logs": 100,
                "reports": 50,
                "tests": 30
            },
            "archive_enabled": True,
            "archive_path": "archive",
            "cleanup_schedule": "daily"
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Fusionner avec la config par défaut
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                print(f"⚠️ Erreur lors du chargement de la config de nettoyage: {e}")
                return default_config
        else:
            # Créer la config par défaut
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def should_run_cleanup(self) -> bool:
        """Détermine si le nettoyage doit être exécuté."""
        config = self.load_cleanup_config()
        
        if not config.get("enabled", True):
            return False
        
        # Vérifier le planning de nettoyage
        schedule = config.get("cleanup_schedule", "daily")
        last_cleanup_file = self.project_dir / "last_cleanup.txt"
        
        if not last_cleanup_file.exists():
            return True
        
        try:
            with open(last_cleanup_file, 'r') as f:
                last_cleanup_str = f.read().strip()
                last_cleanup = datetime.fromisoformat(last_cleanup_str)
                
            now = datetime.now()
            
            if schedule == "daily":
                return (now - last_cleanup).days >= 1
            elif schedule == "weekly":
                return (now - last_cleanup).days >= 7
            elif schedule == "monthly":
                return (now - last_cleanup).days >= 30
            else:
                return True
        except Exception:
            return True
    
    def cleanup_project_directory(self) -> Dict:
        """Nettoie le dossier .project selon les règles configurées."""
        if not self.project_dir.exists():
            return {"status": "skipped", "reason": "Dossier .project inexistant"}
        
        config = self.load_cleanup_config()
        if not config.get("enabled", True):
            return {"status": "skipped", "reason": "Nettoyage désactivé"}
        
        print(f"🧹 Nettoyage automatique du projet: {self.project_path.name}")
        
        results = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "project": self.project_path.name,
            "cleaned": {},
            "archived": {},
            "errors": []
        }
        
        # Nettoyer chaque sous-dossier
        for subdir in ["logs", "reports", "tests"]:
            subdir_path = self.project_dir / subdir
            if subdir_path.exists():
                try:
                    subdir_results = self._cleanup_subdirectory(
                        subdir_path, 
                        subdir, 
                        config
                    )
                    results["cleaned"][subdir] = subdir_results
                except Exception as e:
                    error_msg = f"Erreur lors du nettoyage de {subdir}: {e}"
                    results["errors"].append(error_msg)
                    print(f"❌ {error_msg}")
        
        # Marquer la date du dernier nettoyage
        self._mark_cleanup_completed()
        
        return results
    
    def _cleanup_subdirectory(self, subdir_path: Path, subdir_name: str, config: Dict) -> Dict:
        """Nettoie un sous-dossier spécifique."""
        retention_days = config["retention_days"].get(subdir_name, 30)
        max_files = config["max_files"].get(subdir_name, 50)
        archive_enabled = config.get("archive_enabled", True)
        
        print(f"   📁 Nettoyage de {subdir_name}/...")
        
        results = {
            "files_checked": 0,
            "files_deleted": 0,
            "files_archived": 0,
            "space_freed": 0
        }
        
        # Lister tous les fichiers
        files = []
        for file_path in subdir_path.glob("*"):
            if file_path.is_file():
                files.append(file_path)
                results["files_checked"] += 1
        
        if not files:
            return results
        
        # Trier par date de modification (plus ancien en premier)
        files.sort(key=lambda x: x.stat().st_mtime)
        
        # Supprimer les fichiers trop anciens
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        files_to_delete = []
        
        for file_path in files:
            file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_mtime < cutoff_date:
                files_to_delete.append(file_path)
        
        # Supprimer les fichiers en excès (garder les plus récents)
        if len(files) > max_files:
            files_to_keep = files[-max_files:]  # Garder les plus récents
            files_to_delete.extend([f for f in files if f not in files_to_keep])
        
        # Supprimer les doublons
        files_to_delete = list(set(files_to_delete))
        
        # Archiver ou supprimer
        for file_path in files_to_delete:
            try:
                file_size = file_path.stat().st_size
                
                if archive_enabled and self._should_archive_file(file_path):
                    # Archiver le fichier
                    archive_path = self._archive_file(file_path, subdir_name)
                    if archive_path:
                        results["files_archived"] += 1
                        results["space_freed"] += file_size
                        print(f"      📦 Archivé: {file_path.name}")
                else:
                    # Supprimer directement
                    file_path.unlink()
                    results["files_deleted"] += 1
                    results["space_freed"] += file_size
                    print(f"      🗑️ Supprimé: {file_path.name}")
                    
            except Exception as e:
                error_msg = f"Erreur lors du traitement de {file_path.name}: {e}"
                print(f"      ❌ {error_msg}")
        
        print(f"      ✅ {subdir_name}: {results['files_deleted']} supprimés, {results['files_archived']} archivés")
        return results
    
    def _should_archive_file(self, file_path: Path) -> bool:
        """Détermine si un fichier doit être archivé."""
        # Archiver les rapports et logs importants
        important_extensions = ['.html', '.json', '.md', '.log']
        return file_path.suffix.lower() in important_extensions
    
    def _archive_file(self, file_path: Path, subdir_name: str) -> Optional[Path]:
        """Archive un fichier."""
        try:
            archive_dir = self.project_dir / "archive" / subdir_name
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            # Créer un nom d'archive avec timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
            archive_path = archive_dir / archive_name
            
            # Déplacer le fichier
            shutil.move(str(file_path), str(archive_path))
            return archive_path
        except Exception as e:
            print(f"      ⚠️ Erreur lors de l'archivage: {e}")
            return None
    
    def _mark_cleanup_completed(self):
        """Marque la date du dernier nettoyage."""
        last_cleanup_file = self.project_dir / "last_cleanup.txt"
        with open(last_cleanup_file, 'w') as f:
            f.write(datetime.now().isoformat())
    
    def get_cleanup_stats(self) -> Dict:
        """Obtient les statistiques de nettoyage."""
        if not self.project_dir.exists():
            return {"error": "Dossier .project inexistant"}
        
        stats = {
            "project": self.project_path.name,
            "total_size": 0,
            "subdirectories": {},
            "last_cleanup": None
        }
        
        # Vérifier la date du dernier nettoyage
        last_cleanup_file = self.project_dir / "last_cleanup.txt"
        if last_cleanup_file.exists():
            try:
                with open(last_cleanup_file, 'r') as f:
                    stats["last_cleanup"] = f.read().strip()
            except Exception:
                pass
        
        # Calculer les tailles
        for subdir in ["logs", "reports", "tests", "config", "archive"]:
            subdir_path = self.project_dir / subdir
            if subdir_path.exists():
                subdir_stats = self._calculate_directory_stats(subdir_path)
                stats["subdirectories"][subdir] = subdir_stats
                stats["total_size"] += subdir_stats["size"]
        
        return stats
    
    def _calculate_directory_stats(self, dir_path: Path) -> Dict:
        """Calcule les statistiques d'un répertoire."""
        stats = {
            "size": 0,
            "files": 0,
            "oldest_file": None,
            "newest_file": None
        }
        
        files = list(dir_path.glob("*"))
        if not files:
            return stats
        
        oldest_time = float('inf')
        newest_time = 0
        
        for file_path in files:
            if file_path.is_file():
                file_size = file_path.stat().st_size
                file_mtime = file_path.stat().st_mtime
                
                stats["size"] += file_size
                stats["files"] += 1
                
                if file_mtime < oldest_time:
                    oldest_time = file_mtime
                    stats["oldest_file"] = datetime.fromtimestamp(file_mtime).isoformat()
                
                if file_mtime > newest_time:
                    newest_time = file_mtime
                    stats["newest_file"] = datetime.fromtimestamp(file_mtime).isoformat()
        
        return stats

class GlobalProjectCleaner:
    """Gestionnaire global de nettoyage pour tous les projets."""
    
    def __init__(self, projects_dir: Path):
        self.projects_dir = projects_dir
    
    def cleanup_all_projects(self) -> Dict:
        """Nettoie tous les projets."""
        print("🧹 NETTOYAGE GLOBAL DES PROJETS")
        print("=" * 50)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "projects_processed": 0,
            "projects_cleaned": 0,
            "projects_skipped": 0,
            "total_space_freed": 0,
            "errors": [],
            "project_results": {}
        }
        
        if not self.projects_dir.exists():
            results["errors"].append("Dossier projects inexistant")
            return results
        
        for project_path in self.projects_dir.iterdir():
            if project_path.is_dir():
                project_name = project_path.name
                results["projects_processed"] += 1
                
                print(f"\n📁 Traitement du projet: {project_name}")
                
                try:
                    cleaner = ProjectCleaner(project_path)
                    
                    if cleaner.should_run_cleanup():
                        project_result = cleaner.cleanup_project_directory()
                        results["project_results"][project_name] = project_result
                        
                        if project_result["status"] == "success":
                            results["projects_cleaned"] += 1
                            # Calculer l'espace libéré
                            space_freed = sum(
                                subdir.get("space_freed", 0) 
                                for subdir in project_result.get("cleaned", {}).values()
                            )
                            results["total_space_freed"] += space_freed
                        else:
                            results["projects_skipped"] += 1
                    else:
                        results["projects_skipped"] += 1
                        print(f"   ⏭️ Nettoyage non nécessaire pour {project_name}")
                        
                except Exception as e:
                    error_msg = f"Erreur lors du nettoyage de {project_name}: {e}"
                    results["errors"].append(error_msg)
                    print(f"   ❌ {error_msg}")
        
        print(f"\n📊 RÉSUMÉ DU NETTOYAGE")
        print(f"   Projets traités: {results['projects_processed']}")
        print(f"   Projets nettoyés: {results['projects_cleaned']}")
        print(f"   Projets ignorés: {results['projects_skipped']}")
        print(f"   Espace libéré: {results['total_space_freed'] / (1024*1024):.2f} MB")
        
        if results["errors"]:
            print(f"   Erreurs: {len(results['errors'])}")
        
        return results
    
    def generate_cleanup_report(self, results: Dict) -> str:
        """Génère un rapport de nettoyage."""
        report_content = f"""# RAPPORT DE NETTOYAGE AUTOMATIQUE
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Résumé

- **Projets traités:** {results['projects_processed']}
- **Projets nettoyés:** {results['projects_cleaned']}
- **Projets ignorés:** {results['projects_skipped']}
- **Espace libéré:** {results['total_space_freed'] / (1024*1024):.2f} MB

## Détails par projet

"""
        
        for project_name, project_result in results.get("project_results", {}).items():
            report_content += f"""### {project_name}

- **Statut:** {project_result.get('status', 'unknown')}
- **Timestamp:** {project_result.get('timestamp', 'N/A')}

"""
            
            for subdir, subdir_result in project_result.get("cleaned", {}).items():
                report_content += f"""#### {subdir}/
- Fichiers vérifiés: {subdir_result.get('files_checked', 0)}
- Fichiers supprimés: {subdir_result.get('files_deleted', 0)}
- Fichiers archivés: {subdir_result.get('files_archived', 0)}
- Espace libéré: {subdir_result.get('space_freed', 0) / 1024:.2f} KB

"""
        
        if results.get("errors"):
            report_content += "## Erreurs\n\n"
            for error in results["errors"]:
                report_content += f"- {error}\n"
        
        return report_content

def main():
    """Fonction principale pour le nettoyage global."""
    projects_dir = Path(__file__).parent.parent / "projects"
    
    cleaner = GlobalProjectCleaner(projects_dir)
    results = cleaner.cleanup_all_projects()
    
    # Générer un rapport
    report_content = cleaner.generate_cleanup_report(results)
    
    # Sauvegarder le rapport
    report_file = projects_dir.parent / "docs" / f"cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n📄 Rapport généré: {report_file}")

if __name__ == "__main__":
    main()
