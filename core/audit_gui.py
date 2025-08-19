#!/usr/bin/env python3
"""
INTERFACE GRAPHIQUE - SYSTÈME D'AUDIT UNIVERSEL
==============================================

Interface utilisateur graphique pour le système d'audit universel.
Permet de sélectionner un projet, lancer l'audit et ouvrir les rapports.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import webbrowser
import threading
import json
import os
from pathlib import Path
from datetime import datetime
import sys

class AuditGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🔍 Système d'Audit Universel")
        self.root.geometry("1000x700")
        self.root.minsize(800, 500)
        
        # Variables
        self.selected_project = tk.StringVar()
        self.project_running = False
        self.project_dir = Path(__file__).parent
        
        # Configuration du style
        self.setup_styles()
        
        # Création de l'interface
        self.create_widgets()
        
        # Charger les projets récents
        self.load_recent_projects()
    
    def setup_styles(self):
        """Configure les styles de l'interface avec un thème Tailwind CSS sombre."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Palette de couleurs Tailwind CSS sombre
        self.colors = {
            # Couleurs de fond
            'bg_900': '#111827',      # Fond principal très sombre
            'bg_800': '#1f2937',      # Fond secondaire
            'bg_700': '#374151',      # Fond tertiaire
            'bg_600': '#4b5563',      # Fond quaternaire
            
            # Couleurs d'accent
            'blue_500': '#3b82f6',    # Bleu principal
            'blue_600': '#2563eb',    # Bleu foncé
            'emerald_500': '#10b981', # Vert succès
            'emerald_600': '#059669', # Vert foncé
            'amber_500': '#f59e0b',   # Orange avertissement
            'amber_600': '#d97706',   # Orange foncé
            'red_500': '#ef4444',     # Rouge erreur
            'red_600': '#dc2626',     # Rouge foncé
            'purple_500': '#8b5cf6',  # Violet accent
            'purple_600': '#7c3aed',  # Violet foncé
            
            # Couleurs de texte
            'text_50': '#f9fafb',     # Texte très clair
            'text_100': '#f3f4f6',    # Texte clair
            'text_200': '#e5e7eb',    # Texte moyen-clair
            'text_300': '#d1d5db',    # Texte moyen
            'text_400': '#9ca3af',    # Texte moyen-foncé
            'text_500': '#6b7280',    # Texte foncé
            
            # Bordures
            'border_600': '#4b5563',  # Bordure principale
            'border_500': '#6b7280',  # Bordure secondaire
            'border_400': '#9ca3af',  # Bordure claire
            
            # Ombres et effets
            'shadow': '#00000040',    # Ombre subtile
            'glow': '#3b82f620'       # Lueur bleue
        }
        
        # Configuration du thème sombre moderne
        self.root.configure(bg=self.colors['bg_900'])
        
        # Style pour les frames
        style.configure('Dark.TFrame', background=self.colors['bg_900'])
        style.configure('Medium.TFrame', background=self.colors['bg_800'])
        style.configure('Light.TFrame', background=self.colors['bg_700'])
        
        # Style pour les labels
        style.configure('Title.TLabel', 
                       background=self.colors['bg_900'], 
                       foreground=self.colors['text_50'],
                       font=('Inter', 20, 'bold'))
        
        style.configure('Subtitle.TLabel', 
                       background=self.colors['bg_800'], 
                       foreground=self.colors['text_300'],
                       font=('Inter', 11))
        
        style.configure('Info.TLabel',
                       background=self.colors['bg_800'],
                       foreground=self.colors['text_200'],
                       font=('Inter', 10))
        
        # Style pour les boutons avec design moderne
        style.configure('Primary.TButton',
                       background=self.colors['blue_500'],
                       foreground=self.colors['text_50'],
                       borderwidth=0,
                       focuscolor='none',
                       font=('Inter', 10, 'bold'),
                       padding=(16, 8))
        
        style.map('Primary.TButton',
                 background=[('active', self.colors['blue_600']),
                            ('pressed', self.colors['blue_600'])])
        
        style.configure('Success.TButton',
                       background=self.colors['emerald_500'],
                       foreground=self.colors['text_50'],
                       borderwidth=0,
                       focuscolor='none',
                       font=('Inter', 10, 'bold'),
                       padding=(16, 8))
        
        style.map('Success.TButton',
                 background=[('active', self.colors['emerald_600']),
                            ('pressed', self.colors['emerald_600'])])
        
        style.configure('Warning.TButton',
                       background=self.colors['amber_500'],
                       foreground=self.colors['text_50'],
                       borderwidth=0,
                       focuscolor='none',
                       font=('Inter', 10, 'bold'),
                       padding=(16, 8))
        
        style.map('Warning.TButton',
                 background=[('active', self.colors['amber_600']),
                            ('pressed', self.colors['amber_600'])])
        
        style.configure('Danger.TButton',
                       background=self.colors['red_500'],
                       foreground=self.colors['text_50'],
                       borderwidth=0,
                       focuscolor='none',
                       font=('Inter', 10, 'bold'),
                       padding=(16, 8))
        
        style.map('Danger.TButton',
                 background=[('active', self.colors['red_600']),
                            ('pressed', self.colors['red_600'])])
        
        # Style pour les labelframes avec design moderne
        style.configure('Dark.TLabelframe',
                       background=self.colors['bg_800'],
                       foreground=self.colors['text_50'],
                       borderwidth=1,
                       relief='solid',
                       bordercolor=self.colors['border_600'])
        
        style.configure('Dark.TLabelframe.Label',
                       background=self.colors['bg_800'],
                       foreground=self.colors['blue_500'],
                       font=('Inter', 11, 'bold'))
        
        # Style pour les entry avec design moderne
        style.configure('Dark.TEntry',
                       fieldbackground=self.colors['bg_700'],
                       foreground=self.colors['text_100'],
                       borderwidth=1,
                       relief='solid',
                       bordercolor=self.colors['border_600'],
                       padding=(8, 6))
        
        # Style pour les listbox
        style.configure('Dark.TListbox',
                       background=self.colors['bg_700'],
                       foreground=self.colors['text_100'],
                       selectbackground=self.colors['blue_500'],
                       selectforeground=self.colors['text_50'],
                       borderwidth=1,
                       relief='solid',
                       bordercolor=self.colors['border_600'])
        
        # Style pour la progressbar avec design moderne
        style.configure('Dark.Horizontal.TProgressbar',
                       background=self.colors['blue_500'],
                       troughcolor=self.colors['bg_700'],
                       borderwidth=0,
                       lightcolor=self.colors['blue_500'],
                       darkcolor=self.colors['blue_500'])
        
        # Style pour la barre de statut
        style.configure('Status.TLabel',
                       background=self.colors['bg_700'],
                       foreground=self.colors['text_300'],
                       font=('Inter', 9),
                       padding=(8, 4))
    
    def create_widgets(self):
        """Crée tous les widgets de l'interface avec un design moderne."""
        # Frame principal avec padding moderne
        main_frame = ttk.Frame(self.root, style='Dark.TFrame', padding="24")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration du grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)  # Donner plus d'espace aux logs
        
        # Titre moderne avec icône
        title_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 32))
        
        title_label = ttk.Label(title_frame, text="🔍 Système d'Audit Universel", 
                               style='Title.TLabel')
        title_label.pack()
        
        # Sous-titre descriptif
        subtitle_label = ttk.Label(title_frame, text="Analyse complète et moderne de vos projets", 
                                  style='Info.TLabel')
        subtitle_label.pack(pady=(4, 0))
        
        # Section sélection de projet
        self.create_project_section(main_frame)
        
        # Section actions
        self.create_actions_section(main_frame)
        
        # Section logs (plus grande)
        self.create_logs_section(main_frame)
        
        # Section projets récents (plus petite)
        self.create_recent_projects_section(main_frame)
        
        # Barre de statut
        self.create_status_bar(main_frame)
    
    def create_project_section(self, parent):
        """Crée la section de sélection de projet avec design moderne."""
        # Frame pour la sélection de projet
        project_frame = ttk.LabelFrame(parent, text="📁 Sélection du Projet", 
                                      style='Dark.TLabelframe', padding="20")
        project_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        project_frame.columnconfigure(1, weight=1)
        
        # Label et entry pour le chemin avec design moderne
        ttk.Label(project_frame, text="Chemin du projet:", 
                 style='Subtitle.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 16))
        
        self.project_entry = ttk.Entry(project_frame, textvariable=self.selected_project, 
                                      style='Dark.TEntry', width=50)
        self.project_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 16))
        
        # Bouton parcourir avec icône moderne
        browse_btn = ttk.Button(project_frame, text="📂 Parcourir", 
                               command=self.browse_project, style='Primary.TButton')
        browse_btn.grid(row=0, column=2)
        
        # Informations du projet avec design moderne
        self.project_info_label = ttk.Label(project_frame, text="Aucun projet sélectionné", 
                                           style='Info.TLabel')
        self.project_info_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(12, 0))
    
    def create_actions_section(self, parent):
        """Crée la section des actions avec design moderne."""
        actions_frame = ttk.LabelFrame(parent, text="⚡ Actions", 
                                      style='Dark.TLabelframe', padding="20")
        actions_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Boutons d'action avec design moderne et espacement
        self.project_btn = ttk.Button(actions_frame, text="🔍 Lancer l'Audit", 
                                    command=self.run_audit, style='Success.TButton')
        self.project_btn.grid(row=0, column=0, padx=(0, 16))
        
        self.open_report_btn = ttk.Button(actions_frame, text="📄 Ouvrir Rapport", 
                                          command=self.open_latest_report, 
                                          style='Primary.TButton', state='disabled')
        self.open_report_btn.grid(row=0, column=1, padx=(0, 16))
        
        self.open_folder_btn = ttk.Button(actions_frame, text="📂 Ouvrir Dossier", 
                                          command=self.open_audit_folder, 
                                          style='Primary.TButton', state='disabled')
        self.open_folder_btn.grid(row=0, column=2, padx=(0, 16))
        
        # Barre de progression avec design moderne
        self.progress = ttk.Progressbar(actions_frame, mode='indeterminate', 
                                       style='Dark.Horizontal.TProgressbar')
        self.progress.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(16, 0))
    
    def create_logs_section(self, parent):
        """Crée la section des logs avec design moderne."""
        logs_frame = ttk.LabelFrame(parent, text="📝 Logs d'Audit", 
                                   style='Dark.TLabelframe', padding="20")
        logs_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        logs_frame.columnconfigure(0, weight=1)
        logs_frame.rowconfigure(0, weight=1)
        parent.rowconfigure(3, weight=1)
        
        # Zone de texte pour les logs avec design moderne
        self.logs_text = scrolledtext.ScrolledText(
            logs_frame, 
            height=15, 
            wrap=tk.WORD, 
            font=('JetBrains Mono', 10),
            bg=self.colors['bg_700'],
            fg=self.colors['text_100'],
            insertbackground=self.colors['text_100'],
            selectbackground=self.colors['blue_500'],
            selectforeground=self.colors['text_50'],
            relief='flat',
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.colors['border_600'],
            highlightcolor=self.colors['blue_500']
        )
        self.logs_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Boutons pour les logs avec design moderne
        logs_buttons_frame = ttk.Frame(logs_frame, style='Dark.TFrame')
        logs_buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(12, 0))
        
        ttk.Button(logs_buttons_frame, text="🗑️ Effacer", 
                   command=self.clear_logs, style='Danger.TButton').pack(side=tk.LEFT, padx=(0, 12))
        
        ttk.Button(logs_buttons_frame, text="📋 Copier", 
                   command=self.copy_logs, style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 12))
        
        ttk.Button(logs_buttons_frame, text="💾 Sauvegarder", 
                   command=self.save_logs, style='Primary.TButton').pack(side=tk.LEFT)
    
    def create_recent_projects_section(self, parent):
        """Crée la section des projets récents avec design moderne."""
        recent_frame = ttk.LabelFrame(parent, text="🕒 Projets Récents", 
                                     style='Dark.TLabelframe', padding="20")
        recent_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        recent_frame.columnconfigure(0, weight=1)
        
        # Liste des projets récents avec design moderne
        self.recent_listbox = tk.Listbox(
            recent_frame, 
            height=3,
            bg=self.colors['bg_700'],
            fg=self.colors['text_100'],
            selectbackground=self.colors['blue_500'],
            selectforeground=self.colors['text_50'],
            relief='flat',
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.colors['border_600'],
            highlightcolor=self.colors['blue_500'],
            font=('Inter', 10)
        )
        self.recent_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 16))
        self.recent_listbox.bind('<Double-Button-1>', self.select_recent_project)
        
        # Boutons pour les projets récents avec design moderne
        recent_buttons_frame = ttk.Frame(recent_frame, style='Dark.TFrame')
        recent_buttons_frame.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        ttk.Button(recent_buttons_frame, text="📁 Sélectionner", 
                   command=self.select_recent_project, style='Primary.TButton').pack(pady=(0, 8))
        
        ttk.Button(recent_buttons_frame, text="🗑️ Supprimer", 
                   command=self.remove_recent_project, style='Danger.TButton').pack(pady=(0, 8))
        
        ttk.Button(recent_buttons_frame, text="🗑️ Tout Effacer", 
                   command=self.clear_recent_projects, style='Danger.TButton').pack()
    
    def create_status_bar(self, parent):
        """Crée la barre de statut avec design moderne."""
        self.status_var = tk.StringVar()
        self.status_var.set("Prêt")
        
        status_bar = ttk.Label(parent, textvariable=self.status_var, 
                              style='Status.TLabel', anchor=tk.W)
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(12, 0))
    
    def browse_project(self):
        """Ouvre le dialogue de sélection de dossier."""
        project_path = filedialog.askdirectory(
            title="Sélectionner le dossier du projet",
            initialdir=os.path.expanduser("~")
        )
        
        if project_path:
            self.selected_project.set(project_path)
            self.update_project_info()
            self.add_recent_project(project_path)
    
    def update_project_info(self):
        """Met à jour les informations du projet sélectionné avec design moderne."""
        project_path = self.selected_project.get()
        
        if not project_path:
            self.project_info_label.config(text="Aucun projet sélectionné", 
                                          foreground=self.colors['text_400'])
            return
        
        project_path = Path(project_path)
        
        if not project_path.exists():
            self.project_info_label.config(text="❌ Dossier introuvable", 
                                          foreground=self.colors['red_500'])
            return
        
        # Vérifier si c'est un projet avec audit dans le système d'audit
        audit_system_dir = self.project_dir.parent
        project_name = project_path.name.lower().replace(' ', '_').replace('-', '_')
        reports_dir = audit_system_dir / "projects" / project_name / "reports"
        
        if reports_dir.exists():
            # Compter les rapports
            report_count = len(list(reports_dir.glob("*.html")))
            
            self.project_info_label.config(
                text=f"✅ Projet avec audit ({report_count} rapport(s)) - {project_path.name}",
                foreground=self.colors['emerald_500']
            )
            
            # Activer les boutons
            self.open_report_btn.config(state='normal')
            self.open_folder_btn.config(state='normal')
        else:
            self.project_info_label.config(
                text=f"ℹ️ Nouveau projet - {project_path.name}",
                foreground=self.colors['blue_500']
            )
            
            # Désactiver les boutons
            self.open_report_btn.config(state='disabled')
            self.open_folder_btn.config(state='disabled')
    
    def run_audit(self):
        """Lance l'audit du projet sélectionné."""
        project_path = self.selected_project.get()
        
        if not project_path:
            messagebox.showwarning("Attention", "Veuillez sélectionner un projet.")
            return
        
        if self.project_running:
            messagebox.showinfo("Information", "Un audit est déjà en cours.")
            return
        
        # Confirmation
        if not messagebox.askyesno("Confirmation", 
                                  f"Lancer l'audit pour le projet :\n{project_path}"):
            return
        
        # Lancer l'audit dans un thread séparé
        self.project_running = True
        self.project_btn.config(state='disabled')
        self.progress.start()
        self.status_var.set("Audit en cours...")
        
        thread = threading.Thread(target=self._run_audit_thread, args=(project_path,))
        thread.daemon = True
        thread.start()
    
    def _run_audit_thread(self, project_path):
        """Exécute l'audit dans un thread séparé."""
        try:
            self.log_message("🚀 Démarrage de l'audit...")
            self.log_message(f"📁 Projet: {project_path}")
            
            # Changer vers le répertoire du projet
            os.chdir(project_path)
            
            # Lancer l'audit
            result = subprocess.run([
                sys.executable, str(self.project_dir / "audit.py"),
                project_path
            ], capture_output=True, text=True, encoding='utf-8')
            
            # Afficher les résultats
            if result.stdout:
                self.log_message("📤 Sortie standard:")
                self.log_message(result.stdout)
            
            if result.stderr:
                self.log_message("⚠️ Erreurs:")
                self.log_message(result.stderr)
            
            if result.returncode == 0:
                self.log_message("✅ Audit terminé avec succès!")
                self.status_var.set("Audit terminé avec succès")
                
                # Mettre à jour les informations du projet
                self.root.after(0, self.update_project_info)
                
                # Demander si on veut ouvrir le rapport
                self.root.after(0, lambda: self.ask_open_report())
            else:
                self.log_message(f"❌ Audit échoué (code: {result.returncode})")
                self.status_var.set("Audit échoué")
                
        except Exception as e:
            self.log_message(f"❌ Erreur lors de l'audit: {e}")
            self.status_var.set("Erreur lors de l'audit")
        
        finally:
            # Réactiver l'interface
            self.root.after(0, self._audit_finished)
    
    def _audit_finished(self):
        """Appelé quand l'audit est terminé."""
        self.project_running = False
        self.project_btn.config(state='normal')
        self.progress.stop()
    
    def ask_open_report(self):
        """Demande si l'utilisateur veut ouvrir le rapport."""
        if messagebox.askyesno("Rapport", "L'audit est terminé. Voulez-vous ouvrir le rapport?"):
            self.open_latest_report()
    
    def open_latest_report(self):
        """Ouvre le dernier rapport HTML."""
        project_path = Path(self.selected_project.get())
        project_name = project_path.name.lower().replace(' ', '_').replace('-', '_')
        audit_system_dir = self.project_dir.parent
        report_path = audit_system_dir / "projects" / project_name / "reports" / "latest_report.html"
        
        if report_path.exists():
            try:
                webbrowser.open(f"file://{report_path.absolute()}")
                self.log_message(f"📄 Rapport ouvert: {report_path}")
            except Exception as e:
                self.log_message(f"❌ Erreur lors de l'ouverture du rapport: {e}")
        else:
            messagebox.showwarning("Attention", "Aucun rapport HTML trouvé.")
    
    def open_audit_folder(self):
        """Ouvre le dossier d'audit du projet."""
        project_path = Path(self.selected_project.get())
        project_name = project_path.name.lower().replace(' ', '_').replace('-', '_')
        audit_system_dir = self.project_dir.parent
        audit_path = audit_system_dir / "projects" / project_name
        
        if audit_path.exists():
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(audit_path)
                else:  # Linux/Mac
                    subprocess.run(['xdg-open', str(audit_path)])
                
                self.log_message(f"📂 Dossier ouvert: {audit_path}")
            except Exception as e:
                self.log_message(f"❌ Erreur lors de l'ouverture du dossier: {e}")
        else:
            messagebox.showwarning("Attention", "Dossier d'audit introuvable.")
    
    def log_message(self, message):
        """Ajoute un message aux logs."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.root.after(0, lambda: self.logs_text.insert(tk.END, log_entry))
        self.root.after(0, lambda: self.logs_text.see(tk.END))
    
    def clear_logs(self):
        """Efface les logs."""
        self.logs_text.delete(1.0, tk.END)
    
    def copy_logs(self):
        """Copie les logs dans le presse-papiers."""
        try:
            logs_content = self.logs_text.get(1.0, tk.END)
            if logs_content.strip():
                self.root.clipboard_clear()
                self.root.clipboard_append(logs_content)
                messagebox.showinfo("Succès", "Logs copiés dans le presse-papiers!")
            else:
                messagebox.showwarning("Attention", "Aucun log à copier.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la copie: {e}")
    
    def save_logs(self):
        """Sauvegarde les logs dans un fichier."""
        filename = filedialog.asksaveasfilename(
            title="Sauvegarder les logs",
            defaultextension=".log",
            filetypes=[("Fichiers log", "*.log"), ("Tous les fichiers", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.logs_text.get(1.0, tk.END))
                messagebox.showinfo("Succès", f"Logs sauvegardés dans {filename}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {e}")
    
    def load_recent_projects(self):
        """Charge la liste des projets récents."""
        config_file = self.project_dir / "gui_config.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    recent_projects = config.get('recent_projects', [])
                    
                    for project in recent_projects:
                        if Path(project).exists():
                            self.recent_listbox.insert(tk.END, project)
            except Exception as e:
                self.log_message(f"⚠️ Erreur lors du chargement des projets récents: {e}")
    
    def save_recent_projects(self):
        """Sauvegarde la liste des projets récents."""
        config_file = self.project_dir / "gui_config.json"
        
        try:
            recent_projects = list(self.recent_listbox.get(0, tk.END))
            
            config = {
                'recent_projects': recent_projects,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.log_message(f"⚠️ Erreur lors de la sauvegarde des projets récents: {e}")
    
    def add_recent_project(self, project_path):
        """Ajoute un projet à la liste des projets récents."""
        # Supprimer s'il existe déjà
        for i in range(self.recent_listbox.size()):
            if self.recent_listbox.get(i) == project_path:
                self.recent_listbox.delete(i)
                break
        
        # Ajouter au début
        self.recent_listbox.insert(0, project_path)
        
        # Limiter à 10 projets
        while self.recent_listbox.size() > 10:
            self.recent_listbox.delete(tk.END)
        
        # Sauvegarder
        self.save_recent_projects()
    
    def select_recent_project(self, event=None):
        """Sélectionne un projet de la liste des projets récents."""
        selection = self.recent_listbox.curselection()
        if selection:
            project_path = self.recent_listbox.get(selection[0])
            self.selected_project.set(project_path)
            self.update_project_info()
    
    def remove_recent_project(self):
        """Supprime un projet de la liste des projets récents."""
        selection = self.recent_listbox.curselection()
        if selection:
            self.recent_listbox.delete(selection[0])
            self.save_recent_projects()
    
    def clear_recent_projects(self):
        """Efface tous les projets récents."""
        if messagebox.askyesno("Confirmation", "Effacer tous les projets récents?"):
            self.recent_listbox.delete(0, tk.END)
            self.save_recent_projects()

def main():
    """Fonction principale."""
    root = tk.Tk()
    app = AuditGUI(root)
    
    # Gestion de la fermeture
    def on_closing():
        app.save_recent_projects()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Centrer la fenêtre
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
