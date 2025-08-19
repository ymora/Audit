#!/usr/bin/env python3
"""
Test de l'interface GUI pour le projet audit-universel.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tests"))

from generic.base_test import BaseProjectTest

class AuditGUITest(BaseProjectTest):
    """Test de l'interface GUI."""
    
    async def run_test(self):
        """Exécute le test de l'interface GUI."""
        print("🖥️ Test de l'interface GUI...")
        
        # Vérifier que tkinter est disponible
        try:
            import tkinter
            import tkinter.ttk
            self.log_success("tkinter disponible")
        except ImportError:
            self.log_failure("tkinter non disponible")
            return self.results
        
        # Vérifier que le script GUI existe
        gui_script = self.project_path / "core" / "audit_gui.py"
        if gui_script.exists():
            self.log_success("Script GUI trouvé")
        else:
            self.log_failure("Script GUI manquant")
        
        return self.results

async def run_test(project_path: Path, config: dict):
    test = AuditGUITest(project_path, config)
    return await test.run_test()
