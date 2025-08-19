#!/usr/bin/env python3
"""
TESTS UNITAIRES - SECURITY CHECKER IMPROVED
==========================================

Tests automatisés pour valider les patterns regex/AST et éviter les régressions.
"""

import unittest
import tempfile
import os
from pathlib import Path
from security_checker import SecurityChecker


class TestSecurityChecker(unittest.TestCase):
    """Tests unitaires pour SecurityChecker."""
    
    def setUp(self):
        """Initialisation avant chaque test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.checker = SecurityChecker(
            project_dir=self.temp_dir,
            verbose=False
        )
    
    def tearDown(self):
        """Nettoyage après chaque test."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_file(self, content: str, filename: str = "test.py", encoding: str = "utf-8") -> Path:
        """Crée un fichier de test temporaire."""
        file_path = self.temp_dir / filename
        file_path.write_text(content, encoding=encoding)
        return file_path
    
    def test_sql_injection_detection(self):
        """Test détection injection SQL."""
        # Cas positif - utiliser un pattern qui devrait être détecté par l'AST
        content = '''
def dangerous_function():
    user_input = "admin"
    cursor.execute("SELECT * FROM users WHERE id = " + user_input)
        '''
        file_path = self.create_test_file(content)
        vulns = self.checker.scan_file(file_path)
        
        # Vérifier que l'AST détecte l'injection SQL
        ast_vulns = [v for v in vulns if v['pattern'] == 'ast' and v['type'] == 'sql_injection']
        self.assertGreater(len(ast_vulns), 0, "Injection SQL non détectée par AST")
    
    def test_sql_injection_false_positive(self):
        """Test faux positif injection SQL (headers.update)."""
        content = '''
headers.update({"Content-Type": "application/json"})
        '''
        file_path = self.create_test_file(content)
        vulns = self.checker.scan_file(file_path)
        
        sql_vulns = [v for v in vulns if v['type'] == 'sql_injection']
        self.assertEqual(len(sql_vulns), 0, "Faux positif détecté pour headers.update")
    
    def test_sensitive_data_exposure(self):
        """Test détection données sensibles."""
        content = '''
test_api_key = "sk-1234567890abcdef"
test_password = "secret123"
        '''
        file_path = self.create_test_file(content)
        vulns = self.checker.scan_file(file_path)
        
        sensitive_vulns = [v for v in vulns if v['type'] == 'sensitive_data_exposure']
        self.assertGreater(len(sensitive_vulns), 0, "Données sensibles non détectées")
    
    def test_sensitive_data_exposure_false_positive(self):
        """Test faux positif données sensibles (paramètres de fonction)."""
        content = '''
def authenticate(password: str, token: str):
    return check_credentials(password, token)
        '''
        file_path = self.create_test_file(content)
        vulns = self.checker.scan_file(file_path)
        
        sensitive_vulns = [v for v in vulns if v['type'] == 'sensitive_data_exposure']
        self.assertEqual(len(sensitive_vulns), 0, "Faux positif détecté pour paramètres de fonction")
    
    def test_command_injection(self):
        """Test détection injection de commande."""
        content = '''
os.system("rm -rf " + user_input)
subprocess.run(["echo", user_input])
        '''
        file_path = self.create_test_file(content)
        vulns = self.checker.scan_file(file_path)
        
        cmd_vulns = [v for v in vulns if v['type'] == 'command_injection']
        self.assertGreater(len(cmd_vulns), 0, "Injection de commande non détectée")
    
    def test_command_injection_false_positive(self):
        """Test faux positif injection de commande (commande statique)."""
        content = '''
os.system("ls -la")
subprocess.run(["echo", "hello"])
        '''
        file_path = self.create_test_file(content)
        vulns = self.checker.scan_file(file_path)
        
        cmd_vulns = [v for v in vulns if v['type'] == 'command_injection']
        self.assertEqual(len(cmd_vulns), 0, "Faux positif détecté pour commande statique")
    
    def test_weak_cryptography(self):
        """Test détection cryptographie faible."""
        content = '''
import hashlib
hash = hashlib.md5(password.encode()).hexdigest()
        '''
        file_path = self.create_test_file(content)
        vulns = self.checker.scan_file(file_path)
        
        crypto_vulns = [v for v in vulns if v['type'] == 'weak_cryptography']
        self.assertGreater(len(crypto_vulns), 0, "Cryptographie faible non détectée")
    
    def test_encoding_fallback(self):
        """Test fallback d'encodage latin-1."""
        # Créer un fichier avec des caractères latin-1
        content = "password = 'mot_de_passe_avec_éàç'"
        file_path = self.create_test_file(content, encoding='latin-1')
        
        # Le scan devrait fonctionner sans erreur
        vulns = self.checker.scan_file(file_path)
        self.assertIsInstance(vulns, list, "Erreur lors du scan avec encodage latin-1")
    
    def test_config_file_scanning(self):
        """Test scan fichiers de configuration."""
        content = '''
API_KEY=sk-1234567890abcdef
SECRET_TOKEN=secret123
        '''
        file_path = self.create_test_file(content, filename="config.env")
        vulns = self.checker.scan_file(file_path)
        
        sensitive_vulns = [v for v in vulns if v['type'] == 'sensitive_data_exposure']
        self.assertGreater(len(sensitive_vulns), 0, "Secrets dans config non détectés")
    
    def test_shell_file_scanning(self):
        """Test scan scripts shell."""
        content = '''
#!/bin/bash
eval "$1"
echo `$2`
        '''
        file_path = self.create_test_file(content, filename="script.sh")
        vulns = self.checker.scan_file(file_path)
        
        cmd_vulns = [v for v in vulns if v['type'] == 'command_injection']
        self.assertGreater(len(cmd_vulns), 0, "Injection de commande shell non détectée")
    
    def test_ast_analysis(self):
        """Test analyse AST."""
        content = '''
def dangerous_function():
    password = "hardcoded_password"
    os.system("rm -rf " + user_input)
    cursor.execute("SELECT * FROM users WHERE id = " + user_id)
        '''
        file_path = self.create_test_file(content)
        vulns = self.checker.scan_file(file_path)
        
        # Vérifier que l'AST détecte les vulnérabilités
        ast_vulns = [v for v in vulns if v['pattern'] == 'ast']
        self.assertGreater(len(ast_vulns), 0, "Analyse AST ne détecte pas les vulnérabilités")
    
    def test_excluded_files(self):
        """Test exclusion des fichiers."""
        # Créer un fichier dans un dossier exclu
        excluded_dir = self.temp_dir / "venv"
        excluded_dir.mkdir()
        file_path = excluded_dir / "test.py"
        file_path.write_text("password = 'secret'")
        
        # Le fichier devrait être exclu
        self.assertTrue(self.checker.is_excluded_file(file_path), "Fichier dans venv non exclu")
    
    def test_parallel_scanning(self):
        """Test scan parallélisé."""
        # Créer plusieurs fichiers de test
        for i in range(5):
            content = f"password = 'secret{i}'"
            self.create_test_file(content, filename=f"test_{i}.py")
        
        vulns = self.checker.scan_vulnerabilities()
        self.assertIsInstance(vulns, list, "Erreur lors du scan parallélisé")


class TestSecurityCheckerCLI(unittest.TestCase):
    """Tests pour la CLI."""
    
    def test_cli_help(self):
        """Test affichage de l'aide."""
        import subprocess
        result = subprocess.run(
            ["python", "security_checker.py", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        self.assertEqual(result.returncode, 0, "Erreur lors de l'affichage de l'aide")
        self.assertIn("SecurityChecker", result.stdout)


if __name__ == "__main__":
    # Configuration des tests
    unittest.main(verbosity=2)
