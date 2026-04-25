"""
Phases d'audit d'Architecture - Spécifique DocuSense Béton
"""

import re
from pathlib import Path
from typing import Dict, Any, List
from .base_phase import BasePhase, AuditIssue, Severity

class ArchitecturePhases:
    """Vérifications architecturales pour DocuSense"""
    
    class SchemaValidationPhase(BasePhase):
        """Vérifie que les modèles SQLAlchemy spécifient bien un schéma."""
        
        def execute(self) -> Dict[str, Any]:
            for file_path in self.project_path.rglob("models.py"):
                if self.is_excluded(file_path): continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Chercher les classes qui héritent de Base (ou autre base SQLAlchemy)
                        classes = re.findall(r'class\s+(\w+)\(Base\):', content)
                        
                        for class_name in classes:
                            # Chercher si __table_args__ avec schema est défini pour cette classe
                            # On cherche dans le bloc de la classe
                            class_pattern = rf'class\s+{class_name}\(Base\):(.*?)(?=class|$)'
                            class_block = re.search(class_pattern, content, re.DOTALL)
                            
                            if class_block:
                                block_text = class_block.group(1)
                                if "__table_args__" not in block_text or "schema" not in block_text:
                                    self.add_issue(AuditIssue(
                                        phase="architecture",
                                        severity=Severity.MAJOR,
                                        category="missing_schema",
                                        message=f"La table '{class_name}' ne spécifie pas de schéma PostgreSQL.",
                                        file_path=str(file_path),
                                        suggestion="Ajoutez __table_args__ = {'schema': 'user_data'} (ou autre) pour respecter l'Architecture Béton.",
                                        priority_score=85,
                                        estimated_fix_time="10 minutes"
                                    ))
                except Exception: continue
                
            return self.get_results()

    class ConfigNamingPhase(BasePhase):
        """Vérifie que la configuration suit le nouveau standard snake_case pour les chemins."""
        
        def execute(self) -> Dict[str, Any]:
            config_file = self.project_path / "backend" / "app" / "core" / "config.py"
            if not config_file.exists(): return self.get_results()
            
            forbidden_uppers = ["EXPORT_DIR", "DATA_DIR", "USER_CASES_DIR", "FAISS_INDEX_PATH", "TESSERACT_CMD"]
            
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for var in forbidden_uppers:
                        if f"{var}:" in content or f"{var} =" in content:
                            self.add_issue(AuditIssue(
                                phase="architecture",
                                severity=Severity.MINOR,
                                category="legacy_config",
                                message=f"Variable de config obsolète détectée : {var}",
                                file_path=str(config_file),
                                suggestion=f"Renommer en {var.lower()}",
                                priority_score=40,
                                estimated_fix_time="5 minutes"
                            ))
            except Exception: pass
            return self.get_results()
