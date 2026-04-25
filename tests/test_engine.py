"""
Tests unitaires du moteur d'audit — Architecture Graal v4.0.

Couvre le pipeline complet (30 phases), les nouvelles phases d'inventaire
(API, env vars, complexité), et la synthèse IA (résumé exécutif,
issues agrégées, plan d'action priorisé).
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from core.engine import AuditEngine
from phases.base_phase import BasePhase, Severity, AuditIssue
from phases.core_phases import CorePhases
from phases.security_checks import SecurityChecks
from phases.performance_checks import PerformanceChecks
from phases.inventory_phases import InventoryPhases


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Crée un mini-projet Python/FastAPI temporaire pour les tests."""
    (tmp_path / "main.py").write_text(
        'import os\n\ndef hello():\n    print("world")\n    api_key = os.getenv("API_KEY")\n    db_url = os.getenv("DATABASE_URL", "sqlite:///dev.db")\n',
        encoding="utf-8"
    )
    (tmp_path / "routes.py").write_text(
        '"""API routes module."""\nfrom fastapi import APIRouter\nrouter = APIRouter()\n\n@router.get("/items")\ndef list_items():\n    """List all items."""\n    return []\n\n@router.post("/items")\ndef create_item():\n    """Create item."""\n    return {}\n',
        encoding="utf-8"
    )
    (tmp_path / "utils.py").write_text(
        '"""Utilities module."""\n\ndef add(a, b):\n    """Add two numbers."""\n    return a + b\n',
        encoding="utf-8"
    )
    (tmp_path / "README.md").write_text("# Test Project\n", encoding="utf-8")
    (tmp_path / "requirements.txt").write_text("# no deps\n", encoding="utf-8")
    return tmp_path


@pytest.fixture
def engine(tmp_project: Path) -> AuditEngine:
    """Retourne un moteur instancié sur le projet temporaire."""
    return AuditEngine(tmp_project)


@pytest.fixture
def results(engine: AuditEngine) -> dict:
    """Exécute l'audit complet et retourne les résultats."""
    return engine.run_audit()


# ---------------------------------------------------------------------------
# Tests du moteur — structure de base
# ---------------------------------------------------------------------------

class TestAuditEngine:
    """Tests de l'orchestrateur principal."""

    def test_engine_instantiation(self, engine: AuditEngine):
        """Le moteur doit s'instancier sans erreur."""
        assert engine is not None
        assert engine.project_path.exists()

    def test_run_audit_returns_required_keys(self, results: dict):
        """run_audit doit retourner un dict avec les 8 clés attendues."""
        for key in ["metadata", "project_info", "phases", "issues", "scores",
                    "executive_summary", "issues_aggregated", "recommendations"]:
            assert key in results, f"Clé manquante : {key}"

    def test_engine_version_is_graal(self, results: dict):
        """La version doit indiquer graal-4.0."""
        assert "graal" in results["metadata"]["engine_version"].lower()

    def test_scores_have_required_keys(self, results: dict):
        """Les scores doivent contenir les 6 métriques obligatoires."""
        for key in ["global_score", "security_score", "quality_score",
                    "total_issues", "critical_issues", "major_issues"]:
            assert key in results["scores"], f"Clé manquante : {key}"

    def test_scores_are_bounded(self, results: dict):
        """Les scores doivent être entre 0 et 100."""
        for key in ["global_score", "security_score", "quality_score"]:
            assert 0 <= results["scores"][key] <= 100

    def test_duration_is_recorded(self, results: dict):
        """La durée doit être mesurée et non nulle."""
        assert results["metadata"]["duration_seconds"] > 0

    def test_save_report_creates_valid_json(self, engine: AuditEngine, tmp_path: Path):
        """save_report doit créer un fichier JSON valide avec les nouveaux champs."""
        engine.run_audit()
        rp = engine.save_report(output_dir=tmp_path / "reports")
        assert rp.exists()
        data = json.loads(rp.read_text(encoding="utf-8"))
        assert "executive_summary" in data
        assert "recommendations" in data
        assert "issues_aggregated" in data


# ---------------------------------------------------------------------------
# Tests du pipeline — complétude des phases
# ---------------------------------------------------------------------------

class TestPipelineCompleteness:
    """Vérifie que toutes les phases du pipeline sont exécutées."""

    EXPECTED_PHASES = [
        # Core (11)
        "initialization", "discovery", "validation", "structure", "quality",
        "unification", "optimization", "security", "metrics", "architecture", "config_naming",
        # Advanced (13)
        "devops", "ux", "documentation", "project_management", "maintenance",
        "scalability", "innovation", "knowledge", "research", "excellence", "ai_ml",
        "reporting", "finalization",
        # Inventory (3)
        "api_inventory", "env_vars", "complexity",
        # Specialist (3)
        "security_extended", "performance_extended", "aiml_extended",
    ]

    def test_all_30_phases_executed(self, results: dict):
        """Toutes les 30 phases attendues doivent être dans le rapport."""
        phases = results["phases"]
        for name in self.EXPECTED_PHASES:
            assert name in phases, f"Phase manquante : {name}"

    def test_minimum_30_phases(self, results: dict):
        """Il doit y avoir au moins 30 phases dans le rapport."""
        assert len(results["phases"]) >= 30

    def test_all_phases_have_duration(self, results: dict):
        """Chaque phase doit avoir une durée mesurée."""
        for name, data in results["phases"].items():
            assert "duration" in data, f"Phase {name}: 'duration' manquante"

    def test_all_phases_have_status(self, results: dict):
        """Chaque phase doit avoir un status dans son résultat."""
        for name, data in results["phases"].items():
            assert "result" in data
            assert "status" in data["result"], f"Phase {name}: 'status' manquant"


# ---------------------------------------------------------------------------
# Tests des phases d'inventaire
# ---------------------------------------------------------------------------

class TestInventoryPhases:
    """Tests des nouvelles phases d'inventaire technique."""

    def test_api_inventory_detects_fastapi_routes(self, tmp_project: Path):
        """APIInventoryPhase doit détecter les routes @router.get/post."""
        phase = InventoryPhases.APIInventoryPhase(tmp_project)
        result = phase.execute()
        assert result["total_endpoints"] > 0, "Aucun endpoint détecté"

    def test_env_vars_detects_os_getenv(self, tmp_project: Path):
        """EnvVarsPhase doit détecter os.getenv."""
        phase = InventoryPhases.EnvVarsPhase(tmp_project)
        result = phase.execute()
        assert result["total_env_vars"] > 0
        names = [v["name"] for v in result["env_vars"]]
        assert "API_KEY" in names
        assert "DATABASE_URL" in names

    def test_env_vars_distinguishes_required_optional(self, tmp_project: Path):
        """EnvVarsPhase doit savoir si une var a un défaut ou non."""
        phase = InventoryPhases.EnvVarsPhase(tmp_project)
        result = phase.execute()
        required = result["required_vars_names"]
        assert "API_KEY" in required       # pas de défaut → requise
        assert "DATABASE_URL" not in required  # a un défaut → optionnelle

    def test_complexity_phase_detects_functions(self, tmp_project: Path):
        """ComplexityPhase doit analyser toutes les fonctions via AST."""
        phase = InventoryPhases.ComplexityPhase(tmp_project)
        result = phase.execute()
        assert result["total_functions"] > 0
        assert "average_complexity" in result
        assert "top_10_most_complex" in result

    def test_complexity_in_pipeline_results(self, results: dict):
        """La phase complexity doit être dans les résultats du pipeline."""
        cplx = results["phases"]["complexity"]["result"]
        assert "total_functions" in cplx
        assert "average_complexity" in cplx
        assert "complexity_distribution" in cplx


# ---------------------------------------------------------------------------
# Tests de la synthèse IA
# ---------------------------------------------------------------------------

class TestSynthesis:
    """Tests du bloc de synthèse IA — le coeur de l'exploitabilité."""

    def test_executive_summary_is_string(self, results: dict):
        """Le résumé exécutif doit être une chaîne non vide."""
        s = results["executive_summary"]
        assert isinstance(s, str) and len(s) > 50

    def test_executive_summary_mentions_project_name(self, tmp_project: Path, results: dict):
        """Le résumé doit mentionner le nom du projet."""
        assert tmp_project.name in results["executive_summary"]

    def test_executive_summary_mentions_scores(self, results: dict):
        """Le résumé doit mentionner les scores /100."""
        assert "/100" in results["executive_summary"]

    def test_issues_aggregated_is_list(self, results: dict):
        """issues_aggregated doit être une liste."""
        assert isinstance(results["issues_aggregated"], list)

    def test_issues_aggregated_have_count(self, results: dict):
        """Chaque groupe d'issues doit avoir count > 0."""
        for g in results["issues_aggregated"]:
            assert g["count"] > 0

    def test_issues_aggregated_less_or_equal_raw(self, results: dict):
        """Il doit y avoir au plus autant de groupes que d'issues brutes."""
        raw = len(results["issues"])
        agg = len(results["issues_aggregated"])
        assert agg <= raw

    def test_recommendations_is_list(self, results: dict):
        """recommendations doit être une liste."""
        assert isinstance(results["recommendations"], list)

    def test_recommendations_have_required_fields(self, results: dict):
        """Chaque recommandation doit avoir les champs clés."""
        for rec in results["recommendations"]:
            for field in ["priority", "impact", "severity", "category", "action",
                          "details", "suggestion", "effort_estimate"]:
                assert field in rec, f"Recommandation sans champ '{field}'"

    def test_recommendations_sorted_by_priority(self, results: dict):
        """Les recommandations doivent être triées par priorité croissante."""
        priorities = [r["priority"] for r in results["recommendations"]]
        assert priorities == sorted(priorities)


# ---------------------------------------------------------------------------
# Tests des phases core
# ---------------------------------------------------------------------------

class TestCorePhases:
    """Tests des phases fondamentales."""

    def test_initialization_phase_ok(self, tmp_project: Path):
        result = CorePhases.InitializationPhase(tmp_project).execute()
        assert result["status"] == "success"

    def test_initialization_phase_missing_path(self, tmp_path: Path):
        result = CorePhases.InitializationPhase(tmp_path / "nonexistent").execute()
        assert result["status"] == "error"

    def test_quality_phase_detects_print(self, tmp_project: Path):
        phase = CorePhases.QualityPhase(tmp_project)
        phase.execute()
        assert any("print" in i.message.lower() or "Print" in i.message for i in phase.issues)

    def test_quality_phase_detects_missing_docstring(self, tmp_project: Path):
        phase = CorePhases.QualityPhase(tmp_project)
        phase.execute()
        assert "missing_docstring" in [i.category for i in phase.issues]


# ---------------------------------------------------------------------------
# Tests architecture — interface unifiée BasePhase
# ---------------------------------------------------------------------------

class TestUnifiedInterface:
    """Vérifie que tous les checks spécialistes héritent de BasePhase."""

    def test_security_checks_is_base_phase(self):
        assert issubclass(SecurityChecks, BasePhase)

    def test_performance_checks_is_base_phase(self):
        assert issubclass(PerformanceChecks, BasePhase)

    def test_ai_ml_checks_is_base_phase(self):
        from phases.ai_ml_checks import AIMLChecks
        assert issubclass(AIMLChecks, BasePhase)

    def test_security_execute_returns_dict(self, tmp_project: Path):
        result = SecurityChecks(tmp_project).execute()
        assert isinstance(result, dict) and "status" in result

    def test_performance_execute_returns_dict(self, tmp_project: Path):
        result = PerformanceChecks(tmp_project).execute()
        assert isinstance(result, dict) and "async_patterns_detected" in result

    def test_security_detects_hardcoded_secret(self, tmp_project: Path):
        """SecurityChecks doit détecter le mot 'password' assigné à une valeur."""
        (tmp_project / "conf.py").write_text('password = "mysecret"\n', encoding="utf-8")
        sec = SecurityChecks(tmp_project)
        issues = sec.get_all_issues()
        assert any(i.severity == Severity.CRITICAL for i in issues)
