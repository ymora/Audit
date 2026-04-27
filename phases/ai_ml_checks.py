"""
Checks IA/ML spécialisés.

Impémente `AIMLChecks` comme une phase `BasePhase` complète,
détectant les frameworks ML, intégrations LLM, bases vectorielles,
services OCR, et bibliothèques de traitement de données.
"""

import re
from pathlib import Path
from typing import Dict, List, Any

from .base_phase import BasePhase, AuditIssue, Severity


class AIMLChecks(BasePhase):
    """
    Phase de détection des composants IA/ML du projet.

    Hérite de `BasePhase` pour s'intégrer au pipeline unifié du moteur.
    Inventorie tous les composants IA/ML (frameworks, LLM, VectorDB, OCR,
    data processing) pour fournir un contexte complet aux IA auditeurs.
    """

    def __init__(self, project_path: Path, exclude_dirs: List[str] = None, exclude_files: List[str] = None):
        """
        Initialise les contrôles IA/ML.

        Args:
            project_path (Path): Chemin racine du projet.
            exclude_dirs (List[str], optional): Répertoires à ignorer.
            exclude_files (List[str], optional): Patterns de fichiers à ignorer.
        """
        super().__init__(project_path, exclude_dirs, exclude_files)
        self.ai_components: List[Dict] = []

    def execute(self) -> Dict[str, Any]:
        """
        Exécute tous les contrôles IA/ML et retourne le rapport structuré.

        Returns:
            Dict[str, Any]: Inventaire complet des composants IA/ML détectés.
        """
        self.ai_components = []
        self.get_all_components()

        # Typer les composants par catégorie
        by_type: Dict[str, List] = {}
        for comp in self.ai_components:
            t = comp.get("type", "other")
            by_type.setdefault(t, []).append(comp)

        return {
            "status": "success",
            "summary": f"IA/ML inventorié — {len(self.ai_components)} composants détectés",
            "components_found": len(self.ai_components),
            "by_type": {k: len(v) for k, v in by_type.items()},
            "components": self.ai_components
        }

    def get_all_components(self) -> List[Dict]:
        """
        Déclenche tous les contrôles IA/ML et retourne la liste consolidée.

        Returns:
            List[Dict]: Liste de tous les composants IA/ML détectés.
        """
        self.check_ml_frameworks()
        self.check_llm_integration()
        self.check_vector_databases()
        self.check_ocr_services()
        self.check_data_processing()
        return self.ai_components

    def check_ml_frameworks(self) -> List[Dict]:
        """Vérifier les frameworks ML utilisés"""
        ml_patterns = {
            'tensorflow': r'tensorflow',
            'pytorch': r'pytorch',
            'keras': r'keras',
            'sklearn': r'sklearn|scikit-learn',
            'xgboost': r'xgboost',
            'lightgbm': r'lightgbm'
        }
        
        for file_path in self.project_path.rglob("*.py"):
            if any(exclude_dir in file_path.parts for exclude_dir in self.exclude_dirs):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for framework, pattern in ml_patterns.items():
                        if re.search(pattern, content, re.IGNORECASE):
                            self.ai_components.append({
                                "file": str(file_path),
                                "framework": framework,
                                "type": "ml_framework"
                            })
            except Exception:
                continue
        
        return self.ai_components
    
    def check_llm_integration(self) -> List[Dict]:
        """Vérifier l'intégration LLM"""
        llm_patterns = {
            'openai': r'openai',
            'langchain': r'langchain',
            'anthropic': r'anthropic',
            'cohere': r'cohere',
            'huggingface': r'huggingface|transformers'
        }
        
        for file_path in self.project_path.rglob("*.py"):
            if any(exclude_dir in file_path.parts for exclude_dir in self.exclude_dirs):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for llm, pattern in llm_patterns.items():
                        if re.search(pattern, content, re.IGNORECASE):
                            self.ai_components.append({
                                "file": str(file_path),
                                "llm": llm,
                                "type": "llm_integration"
                            })
            except Exception:
                continue
        
        return self.ai_components
    
    def check_vector_databases(self) -> List[Dict]:
        """Vérifier les bases de données vectorielles"""
        vector_db_patterns = {
            'faiss': r'faiss',
            'chromadb': r'chromadb',
            'pinecone': r'pinecone',
            'weaviate': r'weaviate',
            'milvus': r'milvus',
            'qdrant': r'qdrant'
        }
        
        for file_path in self.project_path.rglob("*.py"):
            if any(exclude_dir in file_path.parts for exclude_dir in self.exclude_dirs):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for vector_db, pattern in vector_db_patterns.items():
                        if re.search(pattern, content, re.IGNORECASE):
                            self.ai_components.append({
                                "file": str(file_path),
                                "vector_db": vector_db,
                                "type": "vector_database"
                            })
            except Exception:
                continue
        
        return self.ai_components
    
    def check_ocr_services(self) -> List[Dict]:
        """Vérifier les services OCR"""
        ocr_patterns = {
            'tesseract': r'tesseract|pytesseract',
            'easyocr': r'easyocr',
            'paddleocr': r'paddleocr',
            'docling': r'docling',
            'pdfplumber': r'pdfplumber',
            'pymupdf': r'pymupdf|fitz'
        }
        
        for file_path in self.project_path.rglob("*.py"):
            if any(exclude_dir in file_path.parts for exclude_dir in self.exclude_dirs):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for ocr, pattern in ocr_patterns.items():
                        if re.search(pattern, content, re.IGNORECASE):
                            self.ai_components.append({
                                "file": str(file_path),
                                "ocr": ocr,
                                "type": "ocr_service"
                            })
            except Exception:
                continue
        
        return self.ai_components
    
    def check_data_processing(self) -> List[Dict]:
        """Vérifier les bibliothèques de traitement de données"""
        data_patterns = {
            'numpy': r'numpy',
            'pandas': r'pandas',
            'scipy': r'scipy',
            'polars': r'polars',
            'dask': r'dask'
        }
        
        for file_path in self.project_path.rglob("*.py"):
            if any(exclude_dir in file_path.parts for exclude_dir in self.exclude_dirs):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for lib, pattern in data_patterns.items():
                        if re.search(pattern, content, re.IGNORECASE):
                            self.ai_components.append({
                                "file": str(file_path),
                                "library": lib,
                                "type": "data_processing"
                            })
            except Exception:
                continue
        
        return self.ai_components
    
    def get_all_components(self) -> List[Dict]:
        """Exécuter tous les checks IA/ML"""
        self.check_ml_frameworks()
        self.check_llm_integration()
        self.check_vector_databases()
        self.check_ocr_services()
        self.check_data_processing()
        return self.ai_components
