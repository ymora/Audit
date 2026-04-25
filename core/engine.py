"""
Moteur d'audit principal — Architecture Grâal v4.0

Orchestre 30+ phases d'analyse organisées en 4 niveaux :
  1. Core (11 phases)      — Fondamentaux qualité, sécurité, métriques
  2. Advanced (13 phases)  — DevOps, UX, documentation, innovation
  3. Inventory (3 phases)  — Endpoints API, variables d'env, complexité CC
  4. Specialist (3 phases) — Sécurité/Performance/IA extended (BasePhase)

Produit un rapport JSON enrichi avec :
  - executive_summary   : texte naturel exploitable par les IA
  - issues_aggregated   : issues groupées (pas 128 entrées identiques)
  - recommendations     : plan d'action priorisé
"""

import json
import time
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from phases import (
    CorePhases, AdvancedPhases, SecurityChecks, AIMLChecks,
    PerformanceChecks, ArchitecturePhases, InventoryPhases
)
from phases.base_phase import AuditIssue, Severity
from .project_detector import ProjectDetector


class AuditEngine:
    """
    Moteur d'audit principal — Architecture Grâal v4.0.

    Orchestre le pipeline complet d'analyse et produit un rapport JSON
    directement exploitable par des systèmes IA (résumé exécutif,
    issues agrégées, plan d'action priorisé).
    """

    def __init__(self, project_path: Path, config_path: Optional[Path] = None):
        """
        Initialise le moteur d'audit pour un projet spécifique.

        Args:
            project_path (Path): Chemin racine du projet à auditer.
            config_path (Path, optional): Chemin vers un fichier de configuration.
        """
        self.project_path = project_path
        self.project_info = ProjectDetector(project_path).detect()
        self.start_time = datetime.now()
        self.results = {
            "metadata": {
                "project_name": project_path.name,
                "project_path": str(project_path),
                "timestamp": self.start_time.isoformat(),
                "engine_version": "graal-4.0",
                "duration_seconds": 0
            },
            "project_info": {
                "project_type": self.project_info.project_type,
                "languages": self.project_info.languages,
                "frameworks": self.project_info.frameworks,
                "databases": self.project_info.databases,
                "architecture": self.project_info.architecture,
                "ports": self.project_info.ports,
                "services": self.project_info.services,
                "has_docker": self.project_info.has_docker,
                "has_tests": self.project_info.has_tests,
                "has_ci_cd": self.project_info.has_ci_cd
            },
            "phases": {},
            "issues": [],
            "scores": {},
            "executive_summary": "",
            "issues_aggregated": [],
            "recommendations": []
        }
        # Répertoires à exclure systématiquement
        self.exclude_dirs = [
            "node_modules", ".git", "__pycache__", "venv", "env", ".venv",
            "build", "dist", ".next", "coverage", "migrations",
            "reports",        # Exclure les rapports générés (JSON contient du code auditable)
            ".pytest_cache",  # Cache pytest
            "tmp", "temp",    # Dossiers temporaires
            "tests",          # Tests intentionnellement "dangereux" (fixtures)
            "scripts"         # Scripts utilitaires non-production
        ]
        # Fichiers/patterns à exclure pour éviter les faux positifs
        self.exclude_files = [
            "check_*.py", "diagnose.py", "seed/*.py", "scripts/*.py",
            "test_*.py", "*_test.py", "conftest.py"
        ]
    
    def run_audit(self) -> Dict[str, Any]:
        """
        Exécute le pipeline d'audit complet — Architecture Grâal v4.0.

        Pipeline :
            1. Phases core (qualité, sécurité, métriques)
            2. Phases avancées (DevOps, UX, excellence)
            3. Phases d'inventaire (API, env vars, complexité)
            4. Checks spécialistes (sécurité/perf/IA extended)
            5. Calcul des scores
            6. Synthèse IA (résumé, agrégation, plan d'action)

        Returns:
            Dict[str, Any]: Rapport complet exploitable par les systèmes IA.
        """
        print(f"\n{'='*80}")
        print(f"LANCEMENT AUDIT SYSTÈME - {self.project_path.name.upper()}")
        print(f"{'='*80}")
        print(f"Début : {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")
        
        # Exécuter toutes les phases dans l'ordre
        self._run_core_phases()
        self._run_advanced_phases()
        self._run_inventory_phases()
        self._run_specialist_phases()

        # Calculer les scores
        self._calculate_scores()

        # Synthèse IA (doit être après les scores)
        self._synthesize()

        # Durée totale
        duration = (datetime.now() - self.start_time).total_seconds()
        self.results["metadata"]["duration_seconds"] = duration

        # Afficher la synthèse finale
        self._display_results()

        return self.results
    
    def _run_core_phases(self):
        """
        Exécute les phases fondamentales (initialisation, validité, qualité, sécurité).
        """
        core_phases = [
            ("initialization", CorePhases.InitializationPhase),
            ("discovery", CorePhases.DiscoveryPhase),
            ("validation", CorePhases.ValidationPhase),
            ("structure", CorePhases.StructurePhase),
            ("quality", CorePhases.QualityPhase),
            ("unification", CorePhases.UnificationPhase),
            ("optimization", CorePhases.OptimizationPhase),
            ("security", CorePhases.SecurityPhase),
            ("metrics", CorePhases.MetricsPhase),
            ("architecture", ArchitecturePhases.SchemaValidationPhase),
            ("config_naming", ArchitecturePhases.ConfigNamingPhase)
        ]
        
        for phase_name, phase_class in core_phases:
            print(f"\n[*] PHASE: {phase_name.upper()}")
            
            phase = phase_class(self.project_path, self.exclude_dirs, self.exclude_files)
            st = time.time()
            result = phase.execute()
            duration = time.time() - st
            
            self.results["phases"][phase_name] = {
                "result": result,
                "duration": duration
            }
            
            # Afficher les problèmes détectés si présents
            if hasattr(phase, 'issues') and phase.issues:
                print(f"    [!] {len(phase.issues)} problèmes détectés")
                for i, issue in enumerate(phase.issues[:5], 1):  # Synthèse de 5 issues max par phase
                    severity = issue.severity.name if hasattr(issue.severity, 'name') else str(issue.severity)
                    print(f"    {i:2d}. [{severity:<8}] {issue.message}")
                if len(phase.issues) > 5:
                    print(f"    ... (+{len(phase.issues) - 5} autres)")
                    
                self.results["issues"].extend(phase.issues)
    
    def _run_advanced_phases(self):
        """
        Exécute les phases avancées (DevOps, UX, Documentation, Maintenance).
        """
        advanced_phases = [
            ("devops", AdvancedPhases.DevOpsPhase),
            ("ux", AdvancedPhases.UXPhase),
            ("documentation", AdvancedPhases.DocumentationPhase),
            ("project_management", AdvancedPhases.ProjectManagementPhase),
            ("maintenance", AdvancedPhases.MaintenancePhase),
            ("scalability", AdvancedPhases.ScalabilityPhase),
            ("innovation", AdvancedPhases.InnovationPhase),
            ("git_history", AdvancedPhases.GitHistoryPhase),
            ("knowledge", AdvancedPhases.KnowledgePhase),
            ("research", AdvancedPhases.ResearchPhase),
            ("excellence", AdvancedPhases.ExcellencePhase),
            ("ai_ml", AdvancedPhases.AIMLPhase),
            ("reporting", AdvancedPhases.ReportingPhase),
            ("finalization", AdvancedPhases.FinalizationPhase)
        ]
        
        for phase_name, phase_class in advanced_phases:
            print(f"\n[*] PHASE: {phase_name.upper()}")
            phase = phase_class(self.project_path, self.exclude_dirs, self.exclude_files)
            st = time.time()
            result = phase.execute()
            duration = time.time() - st
            
            self.results["phases"][phase_name] = {
                "result": result,
                "duration": duration
            }
            
            if hasattr(phase, 'issues') and phase.issues:
                print(f"    [!] {len(phase.issues)} problèmes détectés")
                for i, issue in enumerate(phase.issues[:3], 1):
                    sev = issue.severity.name if hasattr(issue.severity, 'name') else str(issue.severity)
                    print(f"    {i:2d}. [{sev:<8}] {issue.message}")
                self.results["issues"].extend(phase.issues)
            else:
                summary = result.get("summary", "")
                if summary:
                    print(f"    [OK] {summary}")
    
    def _run_inventory_phases(self):
        """
        Exécute les phases d'inventaire technique (API, env vars, complexité).

        Ces phases produisent des données structurées directement exploitables
        par les IA pour comprendre l'architecture du projet auditié.
        """
        inventory_phases = [
            ("api_inventory", InventoryPhases.APIInventoryPhase),
            ("env_vars", InventoryPhases.EnvVarsPhase),
            ("complexity", InventoryPhases.ComplexityPhase),
        ]
        for phase_name, phase_class in inventory_phases:
            print(f"\n[*] PHASE: {phase_name.upper()}")
            phase = phase_class(self.project_path, self.exclude_dirs, self.exclude_files)
            st = time.time()
            result = phase.execute()
            duration = time.time() - st
            self.results["phases"][phase_name] = {"result": result, "duration": duration}
            if hasattr(phase, 'issues') and phase.issues:
                print(f"    [!] {len(phase.issues)} problèmes détectés")
                for i, issue in enumerate(phase.issues[:3], 1):
                    sev = issue.severity.name if hasattr(issue.severity, 'name') else str(issue.severity)
                    print(f"    {i:2d}. [{sev:<8}] {issue.message}")
                self.results["issues"].extend(phase.issues)
            else:
                # Afficher un résumé positif
                summary = result.get("summary", "")
                if summary:
                    print(f"    [OK] {summary}")

    def _run_specialist_phases(self):
        """
        Exécute les phases spécialisées (sécurité, performance, IA/ML étendus).

        Ces phases héritent de BasePhase et s'intègrent au pipeline unifié.
        Elles complètent les phases core avec des analyses approfondies.
        """
        specialist_phases = [
            ("security_extended", SecurityChecks),
            ("performance_extended", PerformanceChecks),
            ("aiml_extended", AIMLChecks),
        ]
        for phase_name, phase_class in specialist_phases:
            print(f"\n[*] PHASE: {phase_name.upper()}")
            phase = phase_class(self.project_path, self.exclude_dirs, self.exclude_files)
            st = time.time()
            result = phase.execute()
            duration = time.time() - st
            self.results["phases"][phase_name] = {"result": result, "duration": duration}
            if hasattr(phase, 'issues') and phase.issues:
                print(f"    [!] {len(phase.issues)} problèmes détectés")
                for i, issue in enumerate(phase.issues[:3], 1):
                    sev = issue.severity.name if hasattr(issue.severity, 'name') else str(issue.severity)
                    print(f"    {i:2d}. [{sev:<8}] {issue.message}")
                self.results["issues"].extend(phase.issues)
            else:
                summary = result.get("summary", "")
                if summary:
                    print(f"    [OK] {summary}")

    def _synthesize(self):
        """
        Génère le résumé exécutif, agrège les issues et crée le plan d'action.

        Ce bloc transforme le rapport brut en document directement exploitable
        par des systèmes IA :
          - `executive_summary` : texte naturel décrivant le projet et son état
          - `issues_aggregated` : issues groupées par (catégorie, message) avec count
          - `recommendations`   : plan d'action trié par priorité décroissante
        """
        issues = self.results["issues"]
        scores = self.results["scores"]
        project_info = self.results.get("project_info", {})
        project_name = self.results["metadata"]["project_name"]

        # ── 1. Agrégation des issues ──────────────────────────────────────────
        aggregated: Dict[str, Any] = {}
        for issue in issues:
            sev_name = issue.severity.name if hasattr(issue.severity, 'name') else str(issue.severity)
            key = f"{issue.category}::{issue.message}"
            if key not in aggregated:
                aggregated[key] = {
                    "category": issue.category,
                    "severity": sev_name,
                    "message": issue.message,
                    "count": 0,
                    "affected_files": [],
                    "suggestion": issue.suggestion or "",
                    "priority_score": issue.priority_score or 0,
                    "phase": issue.phase
                }
            aggregated[key]["count"] += 1
            fp = issue.file_path or ""
            if fp and fp not in aggregated[key]["affected_files"]:
                aggregated[key]["affected_files"].append(fp)

        # Tri : critiques d'abord, puis par priority_score desc, puis par count desc
        sev_order = {"CRITICAL": 0, "MAJOR": 1, "MINOR": 2, "INFO": 3}
        agg_list = sorted(
            aggregated.values(),
            key=lambda x: (sev_order.get(x["severity"], 9), -x["priority_score"], -x["count"])
        )
        self.results["issues_aggregated"] = agg_list

        # ── 2. Résumé exécutif en langage naturel ───────────────────────────
        langs = ", ".join(project_info.get("languages", [])) or "inconnu"
        frameworks = ", ".join(project_info.get("frameworks", [])) or "aucun détecté"
        dbs = ", ".join(project_info.get("databases", [])) or "aucune"
        ptype = project_info.get("project_type", "inconnu")
        has_docker = project_info.get("has_docker", False)
        has_tests = project_info.get("has_tests", False)
        has_ci = project_info.get("has_ci_cd", False)

        global_score = scores.get("global_score", 0)
        health = (
            "EXCELLENT" if global_score >= 90 else
            "BON" if global_score >= 70 else
            "MOYEN" if global_score >= 50 else
            "FAIBLE" if global_score >= 30 else "CRITIQUE"
        )
        criticals = scores.get("critical_issues", 0)
        majors = scores.get("major_issues", 0)
        minors = scores.get("minor_issues", 0)

        # Infos des phases d'inventaire
        api_data = self.results["phases"].get("api_inventory", {}).get("result", {})
        env_data = self.results["phases"].get("env_vars", {}).get("result", {})
        cplx_data = self.results["phases"].get("complexity", {}).get("result", {})
        aiml_data = self.results["phases"].get("aiml_extended", {}).get("result", {})

        api_count = api_data.get("total_endpoints", 0)
        api_unauth = api_data.get("unauthenticated_write_endpoints", 0)
        env_count = env_data.get("total_env_vars", 0)
        required_vars = env_data.get("required_vars_names", [])
        avg_cc = cplx_data.get("average_complexity", 0)
        high_cc = cplx_data.get("high_risk_functions", 0)
        aiml_components = aiml_data.get("components_found", 0)

        # Top issues critiques/majeures pour le résumé
        top_issues = [a for a in agg_list if a["severity"] in ("CRITICAL", "MAJOR")][:3]
        top_issues_text = (
            " | ".join(f"{i['message']} (x{i['count']})"
            for i in top_issues) if top_issues else "aucun problème critique détecté"
        )

        infra_flags = []
        if has_docker: infra_flags.append("Docker")
        if has_tests: infra_flags.append("Tests")
        if has_ci: infra_flags.append("CI/CD")
        infra_str = ", ".join(infra_flags) if infra_flags else "aucune infrastructure détectée"

        summary = (
            f"Projet '{project_name}' ({ptype}) | "
            f"Technologies: {langs} | Frameworks: {frameworks} | DB: {dbs}. "
            f"Infrastructure: {infra_str}. "
            f"Santé globale: {health} ({global_score}/100) | "
            f"Sécurité: {scores.get('security_score', 0)}/100 | "
            f"Qualité: {scores.get('quality_score', 0)}/100. "
            f"Findings: {criticals} critique(s), {majors} majeur(s), {minors} mineur(s). "
            f"Problèmes prioritaires: {top_issues_text}. "
            f"API: {api_count} endpoint(s) détecté(s){', ' + str(api_unauth) + ' non authentifié(s) en écriture' if api_unauth else ''}. "
            f"Variables d'env: {env_count} ({', '.join(required_vars[:5]) if required_vars else 'aucune requise sans défaut'}). "
            f"Complexité CC moyenne: {avg_cc:.1f} ({high_cc} fonctions à risque élevé). "
            f"Composants IA/ML: {aiml_components} détecté(s)."
        )
        self.results["executive_summary"] = summary

        # ── 3. Plan d'action priorisé ─────────────────────────────────────────
        recommendations = []
        priority = 1

        impact_map = {"CRITICAL": "BLOQUANT", "MAJOR": "IMPORTANT", "MINOR": "AMÉLIORATION", "INFO": "INFORMATIF"}
        effort_map = {"CRITICAL": "1-4 heures", "MAJOR": "2-8 heures", "MINOR": "15-60 minutes", "INFO": "<30 minutes"}

        for issue_group in agg_list:
            sev = issue_group["severity"]
            if sev not in ("CRITICAL", "MAJOR"):
                continue  # Les MINOR/INFO viennent après
            recommendations.append({
                "priority": priority,
                "impact": impact_map.get(sev, "INCONNU"),
                "severity": sev,
                "category": issue_group["category"],
                "action": f"Corriger: {issue_group['message']}",
                "details": (
                    f"Affecte {issue_group['count']} occurrence(s) "
                    f"dans {len(issue_group['affected_files'])} fichier(s)"
                ),
                "suggestion": issue_group["suggestion"],
                "affected_files": issue_group["affected_files"][:5],
                "effort_estimate": effort_map.get(sev, "N/A")
            })
            priority += 1

        # Top 5 améliorations mineures
        for issue_group in [g for g in agg_list if g["severity"] == "MINOR"][:5]:
            recommendations.append({
                "priority": priority,
                "impact": "AMÉLIORATION",
                "severity": "MINOR",
                "category": issue_group["category"],
                "action": f"Améliorer: {issue_group['message']}",
                "details": (
                    f"Affecte {issue_group['count']} occurrence(s) "
                    f"dans {len(issue_group['affected_files'])} fichier(s)"
                ),
                "suggestion": issue_group["suggestion"],
                "affected_files": issue_group["affected_files"][:5],
                "effort_estimate": "15-60 minutes"
            })
            priority += 1

        self.results["recommendations"] = recommendations

    def _calculate_scores(self):
        """
        Calcule les scores de santé globaux en pondérant par sévérité.
        
        Pénalités :
        - Critique : -25 points
        - Majeur : -10 points
        - Mineur : -1 point (logarithmique après 100 issues)
        """
        total_issues = len(self.results["issues"])
        critical_issues = sum(1 for issue in self.results["issues"] if issue.severity == Severity.CRITICAL)
        major_issues = sum(1 for issue in self.results["issues"] if issue.severity == Severity.MAJOR)
        minor_issues = sum(1 for issue in self.results["issues"] if issue.severity == Severity.MINOR)
        
        # Calcul du score global
        penalty = (critical_issues * 25) + (major_issues * 10)
        # Échelle logarithmique pour les issues mineures pour ne pas écraser le score
        minor_penalty = minor_issues if minor_issues < 20 else 20 + int((minor_issues - 20) ** 0.5)
        
        global_score = max(0, 100 - penalty - minor_penalty)
        
        # Score de sécurité spécifique
        security_penalty = (critical_issues * 40) + (major_issues * 15)
        security_score = max(0, 100 - security_penalty)
        
        self.results["scores"] = {
            "global_score": global_score,
            "security_score": security_score,
            "quality_score": max(0, 100 - (major_issues * 5) - minor_penalty),
            "total_issues": total_issues,
            "critical_issues": critical_issues,
            "major_issues": major_issues,
            "minor_issues": minor_issues
        }
    
    def _display_results(self):
        """
        Affiche la synthèse de l'audit dans la console.
        """
        scores = self.results["scores"]
        print(f"\n{'='*80}")
        print(f"SYNTHÈSE FINALE DE L'AUDIT")
        print(f"{'='*80}")
        print(f"  Note Globale   : {scores['global_score']}/100")
        print(f"  Note Sécurité  : {scores['security_score']}/100")
        print(f"  Note Qualité   : {scores['quality_score']}/100")
        print("-" * 80)
        print(f"  Total Findings : {scores['total_issues']}")
        print(f"    - Critiques  : {scores['critical_issues']}")
        print(f"    - Majeures   : {scores['major_issues']}")
        print(f"    - Mineures   : {scores['minor_issues']}")
        print(f"{'='*80}")
        print(f"Durée : {self.results['metadata']['duration_seconds']:.2f}s")
        print(f"{'='*80}\n")
    
    def save_report(self, output_dir: Path = None) -> Path:
        """
        Sauvegarde le rapport d'audit (JSON + HTML Premium).

        Args:
            output_dir (Path, optional): Dossier de destination.

        Returns:
            Path: Chemin complet du fichier JSON généré.
        """
        if output_dir is None:
            project_name = self.project_path.name.lower()
            output_dir = Path(__file__).parent.parent / "reports" / project_name
        
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. Rapport JSON (Machine-Readable)
        report_file = output_dir / f"audit_{timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
        
        # 2. Rapport HTML Dashboard (Human-Readable Premium)
        html_file = output_dir / f"dashboard_{timestamp}.html"
        self._generate_html_report(html_file)
        
        return report_file

    def _generate_html_report(self, output_path: Path):
        """Génère le dashboard HTML premium avec les données réelles."""
        scores = self.results.get("scores", {})
        summary = self.results.get("executive_summary", "Résumé non disponible.")
        recs = self.results.get("recommendations", [])
        
        # Formater les recommandations pour HTML
        recs_html = ""
        for r in recs:
            impact_cls = "priority-high" if r["severity"] in ("CRITICAL", "MAJOR") else ""
            badge_cls = "badge-danger" if r["severity"] == "CRITICAL" else "badge-warning" if r["severity"] == "MAJOR" else "badge-success"
            
            recs_html += f"""
            <div class="action-item {impact_cls}">
                <div>
                    <span class="badge {badge_cls}" style="margin-bottom: 0.5rem; display:inline-block;">{r['severity']}</span>
                    <div style="font-weight: 600; font-size: 1.1rem; margin-bottom: 0.3rem;">{r['action']}</div>
                    <div style="color: #94a3b8; font-size: 0.9rem;">{r['details']}</div>
                    <div style="margin-top: 0.5rem; font-style: italic; color: var(--primary);">Conseil: {r['suggestion']}</div>
                </div>
                <div style="text-align: right; min-width: 150px;">
                    <div style="font-size: 0.8rem; color: #64748b;">IMPACT</div>
                    <div style="font-weight: bold; color: { 'var(--danger)' if r['severity'] == 'CRITICAL' else 'var(--warning)' if r['severity'] == 'MAJOR' else 'var(--success)' };">{r['impact']}</div>
                    <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.5rem;">EFFORT ESTIMÉ</div>
                    <div style="font-weight: 500;">{r['effort_estimate']}</div>
                </div>
            </div>
            """

        html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Graal Audit — {self.project_path.name}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #0b0f1a; --card: #161e31; --text: #f1f5f9;
            --primary: #38bdf8; --success: #22c55e; --warning: #eab308; --danger: #ef4444; --info: #6366f1;
        }}
        body {{ font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; margin: 0; padding: 2rem; }}
        .glass {{ background: rgba(22, 30, 49, 0.8); backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.05); border-radius: 1.25rem; padding: 2rem; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
        header {{ display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 3rem; }}
        h1 {{ color: var(--text); margin: 0; font-size: 3rem; font-weight: 800; letter-spacing: -1px; }}
        .badge {{ padding: 0.4rem 0.8rem; border-radius: 0.5rem; font-weight: 700; font-size: 0.75rem; text-transform: uppercase; }}
        .badge-success {{ background: rgba(34, 197, 94, 0.15); color: var(--success); border: 1px solid rgba(34, 197, 94, 0.2); }}
        .badge-warning {{ background: rgba(234, 179, 8, 0.15); color: var(--warning); border: 1px solid rgba(234, 179, 8, 0.2); }}
        .badge-danger {{ background: rgba(239, 68, 68, 0.15); color: var(--danger); border: 1px solid rgba(239, 68, 68, 0.2); }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-bottom: 2.5rem; }}
        .metric {{ text-align: center; transition: transform 0.2s; }}
        .metric:hover {{ transform: translateY(-5px); }}
        .metric-val {{ font-size: 3.5rem; font-weight: 800; color: var(--primary); display: block; line-height: 1; margin-bottom: 0.5rem; }}
        .metric-label {{ color: #64748b; text-transform: uppercase; letter-spacing: 2px; font-size: 0.75rem; font-weight: 600; }}
        .section-title {{ border-left: 5px solid var(--primary); padding-left: 1.2rem; margin: 3rem 0 1.5rem; font-size: 1.75rem; font-weight: 800; }}
        .summary-box {{ border-left: 5px solid var(--success); background: linear-gradient(90deg, rgba(34, 197, 94, 0.05) 0%, transparent 100%); font-size: 1.1rem; color: #cbd5e1; }}
        .action-item {{ margin-bottom: 1.25rem; padding: 1.5rem; border-radius: 1rem; background: rgba(255,255,255,0.02); display: flex; justify-content: space-between; align-items: center; border: 1px solid rgba(255,255,255,0.03); }}
        .priority-high {{ background: rgba(239, 68, 68, 0.03); border-left: 6px solid var(--danger); }}
        .timestamp {{ color: #475569; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }}
        .footer {{ text-align: center; margin-top: 4rem; color: #475569; font-size: 0.9rem; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 2rem; }}
    </style>
</head>
<body>
    <header>
        <div>
            <p class="timestamp">Audit System v4.0 Graal Core</p>
            <h1>{self.project_path.name}</h1>
        </div>
        <div class="badge badge-success">SANTÉ: { "EXCELLENT" if scores.get('global_score',0) >= 90 else "STABLE" if scores.get('global_score',0) >= 70 else "DETTE" }</div>
    </header>

    <div class="grid">
        <div class="glass metric">
            <span class="metric-val">{scores.get('global_score', 0)}/100</span>
            <span class="metric-label">Score Global</span>
        </div>
        <div class="glass metric">
            <span class="metric-val">{scores.get('security_score', 0)}/100</span>
            <span class="metric-label">Indice Sécurité</span>
        </div>
        <div class="glass metric">
            <span class="metric-val">{len(self.results.get('issues',[]))}</span>
            <span class="metric-label">Points d'Attention</span>
        </div>
    </div>

    <div class="section-title">Synthèse IA</div>
    <div class="glass summary-box">
        {summary}
    </div>

    <div class="section-title">Plan d'Action Prioritaire</div>
    <div class="glass" style="padding: 1rem;">
        {recs_html if recs_html else '<div style="padding: 1rem; text-align: center; color: #64748b;">Aucune action critique requise. Le projet est conforme aux standards.</div>'}
    </div>

    <div class="footer">
        Généré par Antigravity Audit Engine — Architecture Graal v4.0.0<br>
        Source: {self.project_path} | Date: {datetime.now().strftime("%d %B %Y, %H:%M")}
    </div>
</body>
</html>"""
        output_path.write_text(html_content, encoding='utf-8')
