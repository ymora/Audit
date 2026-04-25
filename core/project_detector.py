"""
Auto-détection de projet
Analyse automatiquement le projet sans configuration manuelle
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ProjectInfo:
    """Informations sur le projet détectées automatiquement"""
    project_name: str
    project_type: str  # backend, frontend, fullstack, monorepo, etc.
    languages: List[str]
    frameworks: List[str]
    databases: List[str]
    architecture: str
    ports: List[int]
    services: List[str]
    has_docker: bool
    has_tests: bool
    has_ci_cd: bool


class ProjectDetector:
    """Détecteur automatique de projet"""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
    
    def detect(self) -> ProjectInfo:
        """Détecter automatiquement les informations du projet"""
        project_name = self.project_path.name
        
        # Détecter les langages
        languages = self._detect_languages()
        
        # Détecter les frameworks
        frameworks = self._detect_frameworks()
        
        # Détecter les bases de données
        databases = self._detect_databases()
        
        # Détecter l'architecture
        architecture = self._detect_architecture()
        
        # Détecter les ports
        ports = self._detect_ports()
        
        # Détecter les services
        services = self._detect_services()
        
        # Détecter Docker
        has_docker = self._has_docker()
        
        # Détecter les tests
        has_tests = self._has_tests()
        
        # Détecter CI/CD
        has_ci_cd = self._has_ci_cd()
        
        # Détecter le type de projet
        project_type = self._detect_project_type(languages, frameworks)
        
        return ProjectInfo(
            project_name=project_name,
            project_type=project_type,
            languages=languages,
            frameworks=frameworks,
            databases=databases,
            architecture=architecture,
            ports=ports,
            services=services,
            has_docker=has_docker,
            has_tests=has_tests,
            has_ci_cd=has_ci_cd
        )
    
    def _detect_languages(self) -> List[str]:
        """Détecter les langages utilisés"""
        languages = []
        extensions_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.tsx': 'TypeScript',
            '.jsx': 'JavaScript',
            '.go': 'Go',
            '.rs': 'Rust',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.rb': 'Ruby',
            '.php': 'PHP'
        }
        
        for file_path in self.project_path.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in extensions_map and extensions_map[ext] not in languages:
                    languages.append(extensions_map[ext])
        
        return languages
    
    def _detect_frameworks(self) -> List[str]:
        """Détecter les frameworks utilisés"""
        frameworks = []
        
        # Vérifier les fichiers de configuration
        config_files = {
            'package.json': ['React', 'Next.js', 'Vue', 'Angular', 'Express'],
            'requirements.txt': ['Django', 'Flask', 'FastAPI'],
            'go.mod': ['Go'],
            'Cargo.toml': ['Rust'],
            'pom.xml': ['Java/Maven'],
            'build.gradle': ['Java/Gradle'],
            'Gemfile': ['Ruby/Rails']
        }
        
        for config_file, possible_frameworks in config_files.items():
            if (self.project_path / config_file).exists():
                # Lire le fichier pour détecter le framework exact
                try:
                    with open(self.project_path / config_file, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        for framework in possible_frameworks:
                            if framework.lower() in content:
                                if framework not in frameworks:
                                    frameworks.append(framework)
                except Exception:
                    pass
        
        return frameworks
    
    def _detect_databases(self) -> List[str]:
        """Détecter les bases de données utilisées"""
        databases = []
        db_patterns = {
            'postgresql': ['postgres', 'psycopg2', 'sqlalchemy.postgresql'],
            'mysql': ['mysql', 'pymysql', 'sqlalchemy.mysql'],
            'sqlite': ['sqlite', 'sqlalchemy.sqlite'],
            'mongodb': ['mongodb', 'pymongo', 'motor'],
            'redis': ['redis', 'aioredis'],
            'elasticsearch': ['elasticsearch']
        }
        
        for file_path in self.project_path.rglob("*.py"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    for db, patterns in db_patterns.items():
                        if any(pattern in content for pattern in patterns):
                            if db not in databases:
                                databases.append(db)
                            break
            except Exception:
                continue
        
        return databases
    
    def _detect_architecture(self) -> List[str]:
        """Détecter l'architecture du projet"""
        architecture = []
        
        # Vérifier s'il y a un dossier backend/frontend
        if (self.project_path / 'backend').exists() and (self.project_path / 'frontend').exists():
            architecture.append('backend-frontend')
        elif (self.project_path / 'server').exists() and (self.project_path / 'client').exists():
            architecture.append('server-client')
        elif (self.project_path / 'api').exists() and (self.project_path / 'web').exists():
            architecture.append('api-web')
        else:
            architecture.append('monolithic')
        
        # Vérifier s'il y a des microservices
        if (self.project_path / 'services').exists():
            architecture.append('microservices')
        
        # Vérifier s'il y a des packages (monorepo)
        if (self.project_path / 'packages').exists() or (self.project_path / 'apps').exists():
            architecture.append('monorepo')
        
        return architecture
    
    def _detect_ports(self) -> List[int]:
        """Détecter les ports utilisés"""
        ports = []
        
        for file_path in self.project_path.rglob("*.py"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Chercher les patterns de ports
                    port_patterns = re.findall(r'port\s*=\s*(\d+)', content)
                    for port in port_patterns:
                        port_int = int(port)
                        if port_int not in ports and 1000 <= port_int <= 65535:
                            ports.append(port_int)
            except Exception:
                continue
        
        return sorted(ports)
    
    def _detect_services(self) -> List[str]:
        """Détecter les services présents"""
        services = []
        
        service_patterns = [
            'auth_service', 'user_service', 'chat_service', 'ai_service',
            'email_service', 'notification_service', 'file_service',
            'ocr_service', 'rag_service', 'knowledge_base_service'
        ]
        
        for file_path in self.project_path.rglob("*.py"):
            for pattern in service_patterns:
                if pattern in file_path.name.lower():
                    if pattern not in services:
                        services.append(pattern)
        
        return services
    
    def _has_docker(self) -> bool:
        """Vérifier si Docker est utilisé"""
        return (self.project_path / 'Dockerfile').exists() or \
               (self.project_path / 'docker-compose.yml').exists() or \
               (self.project_path / 'docker-compose.yaml').exists()
    
    def _has_tests(self) -> bool:
        """Vérifier s'il y a des tests"""
        test_files = list(self.project_path.rglob("test_*.py")) + \
                    list(self.project_path.rglob("*_test.py")) + \
                    list(self.project_path.rglob("tests/"))
        return len(test_files) > 0
    
    def _has_ci_cd(self) -> bool:
        """Vérifier s'il y a CI/CD"""
        return (self.project_path / '.github').exists() or \
               (self.project_path / '.gitlab-ci.yml').exists() or \
               (self.project_path / 'Jenkinsfile').exists()
    
    def _detect_project_type(self, languages: List[str], frameworks: List[str]) -> str:
        """Détecter le type de projet"""
        if 'TypeScript' in languages or 'JavaScript' in languages:
            if 'React' in frameworks or 'Next.js' in frameworks or 'Vue' in frameworks:
                return 'frontend'
            elif 'Express' in frameworks:
                return 'backend'
            else:
                return 'fullstack'
        elif 'Python' in languages:
            if 'Django' in frameworks or 'Flask' in frameworks or 'FastAPI' in frameworks:
                return 'backend'
            else:
                return 'script'
        elif 'Go' in languages:
            return 'backend'
        elif 'Rust' in languages:
            return 'backend'
        else:
            return 'unknown'
