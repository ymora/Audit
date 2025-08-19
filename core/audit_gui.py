#!/usr/bin/env python3
"""
INTERFACE GRAPHIQUE - SYSTÈME D'AUDIT UNIVERSEL
==============================================

Interface utilisateur graphique épurée et professionnelle pour le système d'audit universel.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import json
import os
import time
from pathlib import Path
from datetime import datetime
import sys

class ButtonAnimator:
    """Classe pour gérer les animations des boutons."""
    
    @staticmethod
    def add_hover_effects(button, tooltip_text=None):
        """Ajoute des effets de hover et tooltip contextuel."""
        def on_enter(event):
            button.configure(relief='raised')
            if tooltip_text:
                ButtonAnimator.show_tooltip(button, tooltip_text, event)
        
        def on_leave(event):
            button.configure(relief='solid')
            ButtonAnimator.hide_tooltip()
        
        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)
    
    @staticmethod
    def show_tooltip(widget, text, event):
        """Affiche un tooltip contextuel."""
        # Créer le tooltip
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        
        # Style du tooltip
        tooltip.configure(bg='#1f2937', relief='solid', borderwidth=1)
        
        label = tk.Label(tooltip, text=text, 
                       bg='#1f2937', 
                       fg='#ffffff',
                       font=('Inter', 12),
                       padx=8, pady=4)
        label.pack()
        
        # Stocker la référence pour pouvoir la fermer
        ButtonAnimator.current_tooltip = tooltip
        
        # Fermer automatiquement après 3 secondes
        tooltip.after(3000, ButtonAnimator.hide_tooltip)
    
    @staticmethod
    def hide_tooltip():
        """Cache le tooltip actuel."""
        if hasattr(ButtonAnimator, 'current_tooltip') and ButtonAnimator.current_tooltip:
            try:
                ButtonAnimator.current_tooltip.destroy()
            except:
                pass
            ButtonAnimator.current_tooltip = None

class ModernDialog:
    """Fenêtre contextuelle moderne et épurée."""
    
    def __init__(self, parent, title, message, dialog_type="info"):
        self.parent = parent
        self.title = title
        self.message = message
        self.dialog_type = dialog_type
        self.result = None
        
        # Créer la fenêtre
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrer la fenêtre
        self.center_window()
        
        # Configuration du style
        self.setup_style()
        
        # Créer l'interface
        self.create_widgets()
        
        # Focus et attente
        self.dialog.focus_set()
        self.dialog.wait_window()
    
    def center_window(self):
        """Centre la fenêtre sur l'écran."""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_style(self):
        """Configure le style de la fenêtre."""
        self.dialog.configure(bg='#ffffff')
        
        # Couleurs selon le type
        if self.dialog_type == "success":
            self.accent_color = '#16a34a'
            self.icon = "✓"
        elif self.dialog_type == "warning":
            self.accent_color = '#ca8a04'
            self.icon = "⚠"
        elif self.dialog_type == "error":
            self.accent_color = '#dc2626'
            self.icon = "✗"
        else:
            self.accent_color = '#2563eb'
            self.icon = "ℹ"
    
    def create_widgets(self):
        """Crée les widgets de la fenêtre."""
        # Frame principal
        main_frame = tk.Frame(self.dialog, bg='#ffffff', relief='flat', bd=0)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
                # Icône et titre
        icon_label = tk.Label(main_frame, text=self.icon, font=('Inter', 24, 'bold'), 
                             bg='#ffffff', fg=self.accent_color)
        icon_label.pack(pady=(0, 10))
        
        title_label = tk.Label(main_frame, text=self.title, font=('Inter', 18, 'semibold'),
                               bg='#ffffff', fg='#18181b')
        title_label.pack(pady=(0, 15))
        
        # Message
        message_label = tk.Label(main_frame, text=self.message, font=('Inter', 14, 'normal'),
                                bg='#ffffff', fg='#71717a', wraplength=350, justify='center')
        message_label.pack(pady=(0, 25))
        
        # Boutons
        button_frame = tk.Frame(main_frame, bg='#ffffff')
        button_frame.pack()
        
        if self.dialog_type == "confirm":
            # Boutons Oui/Non avec styles unifiés
            yes_btn = tk.Button(button_frame, text="Oui", font=('Inter', 14, 'medium'),
                               bg='#ffffff', fg='#3b82f6', bd=1, relief='solid',
                               padx=20, pady=6, command=self.yes_clicked,
                               activebackground='#f0f9ff', activeforeground='#1d4ed8',
                               cursor='hand2')
            yes_btn.pack(side='left', padx=(0, 10))
            ButtonAnimator.add_hover_effects(yes_btn, "Confirmer l'action")
            
            no_btn = tk.Button(button_frame, text="Non", font=('Inter', 14, 'medium'),
                              bg='#ffffff', fg='#6b7280', bd=1, relief='solid',
                              padx=20, pady=6, command=self.no_clicked,
                              activebackground='#f9fafb', activeforeground='#4b5563',
                              cursor='hand2')
            no_btn.pack(side='left')
            ButtonAnimator.add_hover_effects(no_btn, "Annuler l'action")
        else:
            # Bouton OK avec style unifié
            ok_btn = tk.Button(button_frame, text="OK", font=('Inter', 14, 'medium'),
                              bg='#ffffff', fg='#3b82f6', bd=1, relief='solid',
                              padx=30, pady=6, command=self.ok_clicked,
                              activebackground='#f0f9ff', activeforeground='#1d4ed8',
                              cursor='hand2')
            ok_btn.pack()
            ButtonAnimator.add_hover_effects(ok_btn, "Fermer la fenêtre")
    
    def yes_clicked(self):
        self.result = True
        self.dialog.destroy()
    
    def no_clicked(self):
        self.result = False
        self.dialog.destroy()
    
    def ok_clicked(self):
        self.result = True
        self.dialog.destroy()

class AuditGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Audit Universel")
        
        # Configuration de la fenêtre
        self.setup_window()
        
        # Variables
        self.selected_project = tk.StringVar()
        self.project_running = False
        self.audit_stopped = False
        self.project_dir = Path(__file__).parent
        
        # Variables pour l'indicateur IA
        self.ai_count = 0
        self.ai_status = "idle"  # idle, active, busy
        
        # Configuration du style
        self.setup_styles()
        
        # Création de l'interface
        self.create_widgets()
        
        # Charger les projets récents
        self.load_recent_projects()
    
    def setup_window(self):
        """Configure la fenêtre principale."""
        # Taille adaptée à l'écran
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.75)
        window_height = int(screen_height * 0.75)
        
        # Centrer la fenêtre
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(900, 600)
        self.root.resizable(True, True)
    
    def setup_styles(self):
        """Configure les styles de l'interface."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Initialiser les couleurs
        self._setup_colors()
        
        # Configuration du thème
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Configurer les styles
        self._setup_frame_styles(style)
        self._setup_label_styles(style)
        self._setup_button_styles(style)
        self._setup_widget_styles(style)
    
    def _setup_colors(self):
        """Configure la palette de couleurs moderne claire."""
        self.colors = {
            'bg_dark': '#ffffff',      # Fond principal - blanc
            'bg_medium': '#f4faff',    # Surfaces/panneaux - bleu très clair
            'bg_light': '#ffffff',     # Fond clair - blanc
            'text_primary': '#18181b', # Texte principal - noir
            'text_secondary': '#71717a', # Texte secondaire - gris foncé
            'text_muted': '#a1a1aa',   # Texte atténué - gris moyen
            'accent_blue': '#2563eb',  # Bleu principal foncé
            'accent_green': '#16a34a', # Vert succès foncé
            'accent_red': '#dc2626',   # Rouge erreur foncé
            'accent_yellow': '#ca8a04', # Jaune avertissement foncé
            'accent_orange': '#ea580c', # Orange
            'accent_purple': '#7c3aed', # Violet
            'border': '#b6c6e3'        # Bordures - gris bleuté clair
        }
    
    def _setup_frame_styles(self, style):
        """Configure les styles pour les frames."""
        style.configure('Dark.TFrame', background=self.colors['bg_dark'])
        style.configure('Medium.TFrame', background=self.colors['bg_medium'])
    
    def _setup_label_styles(self, style):
        """Configure les styles pour les labels."""
        style.configure('Title.TLabel', 
                       background=self.colors['bg_dark'], 
                       foreground=self.colors['text_primary'],
                       font=('Inter', 24, 'bold'))
        
        style.configure('Subtitle.TLabel', 
                       background=self.colors['bg_medium'], 
                       foreground=self.colors['text_secondary'],
                       font=('Inter', 14, 'medium'))
        
        style.configure('Info.TLabel',
                       background=self.colors['bg_medium'],
                       foreground=self.colors['text_secondary'],
                       font=('Inter', 12, 'normal'))
    
    def _setup_button_styles(self, style):
        """Configure les styles pour les boutons unifiés avec animations."""
        # Configuration de base pour tous les boutons
        base_config = {
            'borderwidth': 1,
            'relief': 'solid',
            'focuscolor': 'none',
            'font': ('Inter', 14, 'medium'),
            'padding': (16, 8),
            'cursor': 'hand2'  # Curseur pointer
        }
        
        # Bouton Primary (Bleu)
        style.configure('Primary.TButton',
                       background='#ffffff',
                       foreground='#3b82f6',
                       bordercolor='#3b82f6',
                       **base_config)
        style.map('Primary.TButton',
                 background=[('active', '#f0f9ff'), ('pressed', '#e0f2fe')],
                 foreground=[('active', '#1d4ed8'), ('pressed', '#1d4ed8')],
                 bordercolor=[('active', '#1d4ed8'), ('pressed', '#1d4ed8')])
        
        # Bouton Secondary (Gris)
        style.configure('Secondary.TButton',
                       background='#ffffff',
                       foreground='#6b7280',
                       bordercolor='#6b7280',
                       **base_config)
        style.map('Secondary.TButton',
                 background=[('active', '#f9fafb'), ('pressed', '#f3f4f6')],
                 foreground=[('active', '#4b5563'), ('pressed', '#4b5563')],
                 bordercolor=[('active', '#4b5563'), ('pressed', '#4b5563')])
        
        # Bouton Success (Vert)
        style.configure('Success.TButton',
                       background='#ffffff',
                       foreground='#10b981',
                       bordercolor='#10b981',
                       **base_config)
        style.map('Success.TButton',
                 background=[('active', '#f0fdf4'), ('pressed', '#dcfce7')],
                 foreground=[('active', '#059669'), ('pressed', '#059669')],
                 bordercolor=[('active', '#059669'), ('pressed', '#059669')])
        
        # Bouton Warning (Jaune)
        style.configure('Warning.TButton',
                       background='#ffffff',
                       foreground='#f59e0b',
                       bordercolor='#f59e0b',
                       **base_config)
        style.map('Warning.TButton',
                 background=[('active', '#fffbeb'), ('pressed', '#fef3c7')],
                 foreground=[('active', '#d97706'), ('pressed', '#d97706')],
                 bordercolor=[('active', '#d97706'), ('pressed', '#d97706')])
        
        # Bouton Danger (Rouge)
        style.configure('Danger.TButton',
                       background='#ffffff',
                       foreground='#ef4444',
                       bordercolor='#ef4444',
                       **base_config)
        style.map('Danger.TButton',
                 background=[('active', '#fef2f2'), ('pressed', '#fee2e2')],
                 foreground=[('active', '#dc2626'), ('pressed', '#dc2626')],
                 bordercolor=[('active', '#dc2626'), ('pressed', '#dc2626')])
        
        # Bouton Info (Violet)
        style.configure('Info.TButton',
                       background='#ffffff',
                       foreground='#8b5cf6',
                       bordercolor='#8b5cf6',
                       **base_config)
        style.map('Info.TButton',
                 background=[('active', '#faf5ff'), ('pressed', '#f3e8ff')],
                 foreground=[('active', '#7c3aed'), ('pressed', '#7c3aed')],
                 bordercolor=[('active', '#7c3aed'), ('pressed', '#7c3aed')])
    
    def _setup_widget_styles(self, style):
        """Configure les styles pour les autres widgets."""
        # Labelframes
        style.configure('Dark.TLabelframe',
                       background=self.colors['bg_medium'],
                       foreground=self.colors['text_primary'],
                       borderwidth=1,
                       relief='solid',
                       bordercolor=self.colors['border'])
        
        style.configure('Dark.TLabelframe.Label',
                       background=self.colors['bg_medium'],
                       foreground=self.colors['accent_blue'],
                       font=('Inter', 14, 'semibold'))
        
        # Entry
        style.configure('Dark.TEntry',
                       fieldbackground='#ffffff',
                       foreground=self.colors['text_primary'],
                       borderwidth=1,
                       relief='solid',
                       bordercolor=self.colors['border'],
                       padding=(8, 6))
        
        # Listbox
        style.configure('Dark.TListbox',
                       background='#ffffff',
                       foreground=self.colors['text_primary'],
                       selectbackground=self.colors['accent_blue'],
                       selectforeground='#ffffff',
                       borderwidth=1,
                       relief='solid',
                       bordercolor=self.colors['border'])
        
        # Progressbar
        style.configure('Dark.Horizontal.TProgressbar',
                       background=self.colors['accent_blue'],
                       troughcolor='#e2e8f0',
                       borderwidth=0)
    
    def create_widgets(self):
        """Crée tous les widgets de l'interface."""
        # Frame principal avec deux colonnes
        main_frame = ttk.Frame(self.root, style='Dark.TFrame', padding="16")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration du grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)  # Panneau de contrôle
        main_frame.columnconfigure(1, weight=2)  # Visualisation
        main_frame.rowconfigure(0, weight=1)
        
        # Panneau de contrôle (gauche)
        self.create_control_panel(main_frame)
        
        # Panneau de visualisation (droite)
        self.create_visualization_panel(main_frame)
    
    def create_control_panel(self, parent):
        """Crée le panneau de contrôle."""
        control_frame = ttk.Frame(parent, style='Dark.TFrame')
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 16))
        control_frame.columnconfigure(0, weight=1)
        control_frame.rowconfigure(3, weight=1)  # Logs prennent l'espace restant
        
        # Titre avec indicateur IA
        title_frame = ttk.Frame(control_frame, style='Dark.TFrame')
        title_frame.grid(row=0, column=0, pady=(0, 20))
        title_frame.columnconfigure(1, weight=1)
        
        title_label = ttk.Label(title_frame, text="Audit Universel", style='Title.TLabel')
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Indicateur IA
        self.create_ai_indicator(title_frame)
        
        # Section projet
        self.create_project_section(control_frame)
        
        # Section actions
        self.create_actions_section(control_frame)
        
        # Section logs
        self.create_logs_section(control_frame)
        
        # Section projets récents
        self.create_recent_projects_section(control_frame)
        
        # Barre de statut
        self.create_status_bar(control_frame)
    
    def create_project_section(self, parent):
        """Crée la section de sélection de projet."""
        project_frame = ttk.LabelFrame(parent, text="Projet", style='Dark.TLabelframe', padding="12")
        project_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 16))
        project_frame.columnconfigure(1, weight=1)
        
        # Label et entry
        ttk.Label(project_frame, text="Chemin:", style='Subtitle.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 12))
        
        self.project_entry = ttk.Entry(project_frame, textvariable=self.selected_project, style='Dark.TEntry')
        self.project_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 12))
        
        browse_btn = ttk.Button(project_frame, text="📂", command=self.browse_project, style='Primary.TButton')
        browse_btn.grid(row=0, column=2)
        ButtonAnimator.add_hover_effects(browse_btn, "Sélectionner un dossier de projet")
        
        # Informations du projet
        self.project_info_label = ttk.Label(project_frame, text="Aucun projet sélectionné", style='Info.TLabel')
        self.project_info_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(12, 0))
    
    def create_actions_section(self, parent):
        """Crée la section des actions."""
        actions_frame = ttk.LabelFrame(parent, text="Actions", style='Dark.TLabelframe', padding="12")
        actions_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 16))
        
        # Boutons d'action
        button_frame = ttk.Frame(actions_frame, style='Dark.TFrame')
        button_frame.grid(row=0, column=0, pady=(0, 12))
        
        self.audit_btn = ttk.Button(button_frame, text="🔍 Lancer l'Audit", 
                                   command=self.run_audit, style='Success.TButton')
        self.audit_btn.pack(side='left', padx=(0, 8))
        ButtonAnimator.add_hover_effects(self.audit_btn, "Démarrer l'analyse complète du projet")
        
        self.stop_btn = ttk.Button(button_frame, text="⏹️ Arrêter", 
                                  command=self.stop_audit, style='Danger.TButton')
        self.stop_btn.pack(side='left', padx=(0, 8))
        ButtonAnimator.add_hover_effects(self.stop_btn, "Interrompre l'audit en cours")
        
        self.view_btn = ttk.Button(button_frame, text="📄 Voir Rapport", 
                                  command=self.view_report, style='Primary.TButton')
        self.view_btn.pack(side='left', padx=(0, 8))
        ButtonAnimator.add_hover_effects(self.view_btn, "Afficher le dernier rapport d'audit")
        
        self.folder_btn = ttk.Button(button_frame, text="📂 Dossier", 
                                    command=self.open_folder, style='Primary.TButton')
        self.folder_btn.pack(side='left')
        ButtonAnimator.add_hover_effects(self.folder_btn, "Ouvrir le dossier d'audit du projet")
        
        # Barre de progression
        self.progress = ttk.Progressbar(actions_frame, mode='indeterminate', style='Dark.Horizontal.TProgressbar')
        self.progress.grid(row=1, column=0, sticky=(tk.W, tk.E))
    
    def create_logs_section(self, parent):
        """Crée la section des logs."""
        logs_frame = ttk.LabelFrame(parent, text="Logs", style='Dark.TLabelframe', padding="12")
        logs_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 16))
        logs_frame.columnconfigure(0, weight=1)
        logs_frame.rowconfigure(0, weight=1)
        
        # Zone de texte pour les logs
        self.logs_text = scrolledtext.ScrolledText(
            logs_frame, 
            wrap=tk.WORD, 
            font=('JetBrains Mono', 12),
            bg='#ffffff',
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_primary'],
            selectbackground=self.colors['accent_blue'],
            selectforeground='#ffffff',
            relief='flat',
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['accent_blue']
        )
        self.logs_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Boutons pour les logs
        logs_buttons_frame = ttk.Frame(logs_frame, style='Dark.TFrame')
        logs_buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(8, 0))
        
        clear_btn = ttk.Button(logs_buttons_frame, text="Effacer", 
                              command=self.clear_logs, style='Danger.TButton')
        clear_btn.pack(side='left', padx=(0, 8))
        ButtonAnimator.add_hover_effects(clear_btn, "Vider tous les logs")
        
        copy_btn = ttk.Button(logs_buttons_frame, text="Copier", 
                             command=self.copy_logs, style='Primary.TButton')
        copy_btn.pack(side='left')
        ButtonAnimator.add_hover_effects(copy_btn, "Copier les logs dans le presse-papiers")
    
    def create_recent_projects_section(self, parent):
        """Crée la section des projets récents."""
        recent_frame = ttk.LabelFrame(parent, text="Projets Récents", style='Dark.TLabelframe', padding="12")
        recent_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 16))
        recent_frame.columnconfigure(0, weight=1)
        
        # Liste des projets récents
        self.recent_listbox = tk.Listbox(
            recent_frame, 
            height=3,
            bg='#ffffff',
            fg=self.colors['text_primary'],
            selectbackground=self.colors['accent_blue'],
            selectforeground='#ffffff',
            relief='flat',
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['accent_blue'],
            font=('Inter', 12)
        )
        self.recent_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 12))
        self.recent_listbox.bind('<Double-Button-1>', self.select_recent_project)
        
        # Boutons pour les projets récents
        recent_buttons_frame = ttk.Frame(recent_frame, style='Dark.TFrame')
        recent_buttons_frame.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        select_btn = ttk.Button(recent_buttons_frame, text="Sélectionner", 
                               command=self.select_recent_project, style='Primary.TButton')
        select_btn.pack(pady=(0, 8))
        ButtonAnimator.add_hover_effects(select_btn, "Charger le projet sélectionné")
        
        remove_btn = ttk.Button(recent_buttons_frame, text="Supprimer", 
                               command=self.remove_recent_project, style='Danger.TButton')
        remove_btn.pack()
        ButtonAnimator.add_hover_effects(remove_btn, "Retirer le projet de la liste")
    
    def create_status_bar(self, parent):
        """Crée la barre de statut."""
        self.status_var = tk.StringVar()
        self.status_var.set("Prêt")
        
        status_bar = ttk.Label(parent, textvariable=self.status_var, 
                              style='Info.TLabel', anchor=tk.W)
        status_bar.grid(row=5, column=0, sticky=(tk.W, tk.E))
    
    def create_ai_indicator(self, parent):
        """Crée l'indicateur d'IA dans le panneau supérieur."""
        # Frame pour l'indicateur IA
        ai_frame = ttk.Frame(parent, style='Dark.TFrame')
        ai_frame.grid(row=0, column=2, sticky=tk.E, padx=(20, 0))
        
        # Label "IA"
        ai_label = ttk.Label(ai_frame, text="IA", style='Info.TLabel')
        ai_label.pack(side='left', padx=(0, 8))
        
        # Indicateur circulaire
        self.ai_indicator = tk.Canvas(ai_frame, width=20, height=20, 
                                     bg=self.colors['bg_medium'], 
                                     highlightthickness=0, relief='flat')
        self.ai_indicator.pack(side='left', padx=(0, 8))
        
        # Compteur
        self.ai_count_var = tk.StringVar()
        self.ai_count_var.set("0")
        ai_count_label = ttk.Label(ai_frame, textvariable=self.ai_count_var, 
                                   style='Info.TLabel', font=('Inter', 14, 'bold'))
        ai_count_label.pack(side='left')
        
        # Dessiner l'indicateur initial
        self.update_ai_indicator()
        
        # Tooltip au survol
        self.create_ai_tooltip()
    
    def update_ai_indicator(self):
        """Met à jour l'indicateur IA."""
        self.ai_indicator.delete("all")
        
        # Couleur selon le statut
        if self.ai_status == "idle":
            color = self.colors['text_muted']  # Gris
        elif self.ai_status == "active":
            color = self.colors['accent_green']  # Vert
        elif self.ai_status == "busy":
            color = self.colors['accent_yellow']  # Jaune
        else:
            color = self.colors['accent_red']  # Rouge
        
        # Dessiner le cercle
        self.ai_indicator.create_oval(2, 2, 18, 18, 
                                     fill=color, outline=color)
        
        # Mettre à jour le compteur
        self.ai_count_var.set(str(self.ai_count))
    
    def create_ai_tooltip(self):
        """Crée un tooltip pour l'indicateur IA."""
        def show_tooltip(event):
            status_text = {
                "idle": "Aucune IA active",
                "active": f"{self.ai_count} IA(s) active(s)",
                "busy": f"{self.ai_count} IA(s) occupée(s)"
            }
            tooltip_text = status_text.get(self.ai_status, "Statut inconnu")
            
            # Créer le tooltip
            tooltip = tk.Toplevel(self.root)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=tooltip_text, 
                           bg='#ffffff', 
                           fg=self.colors['text_primary'],
                           font=('Inter', 12),
                           relief='solid', borderwidth=1)
            label.pack()
            
            def hide_tooltip(event):
                tooltip.destroy()
            
            self.ai_indicator.bind('<Leave>', hide_tooltip)
            tooltip.bind('<Leave>', hide_tooltip)
        
        self.ai_indicator.bind('<Enter>', show_tooltip)
    
    def set_ai_status(self, status, count=0):
        """Définit le statut de l'IA."""
        self.ai_status = status
        self.ai_count = count
        self.update_ai_indicator()
    
    def create_visualization_panel(self, parent):
        """Crée le panneau de visualisation."""
        viz_frame = ttk.LabelFrame(parent, text="Visualisation", style='Dark.TLabelframe', padding="12")
        viz_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        viz_frame.columnconfigure(0, weight=1)
        viz_frame.rowconfigure(0, weight=1)
        
        # Zone de visualisation
        self.viz_text = scrolledtext.ScrolledText(
            viz_frame,
            wrap=tk.WORD,
            font=('JetBrains Mono', 14),
            bg='#ffffff',
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_primary'],
            selectbackground=self.colors['accent_blue'],
            selectforeground='#ffffff',
            relief='flat',
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['accent_blue']
        )
        self.viz_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Boutons de contrôle
        viz_buttons_frame = ttk.Frame(viz_frame, style='Dark.TFrame')
        viz_buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(8, 0))
        
        load_btn = ttk.Button(viz_buttons_frame, text="Charger Rapport", 
                             command=self.load_report, style='Primary.TButton')
        load_btn.pack(side='left', padx=(0, 8))
        ButtonAnimator.add_hover_effects(load_btn, "Charger le rapport d'audit dans la visualisation")
        
        refresh_btn = ttk.Button(viz_buttons_frame, text="Actualiser", 
                               command=self.refresh_viz, style='Primary.TButton')
        refresh_btn.pack(side='left', padx=(0, 8))
        ButtonAnimator.add_hover_effects(refresh_btn, "Mettre à jour la visualisation")
        
        clear_viz_btn = ttk.Button(viz_buttons_frame, text="Effacer", 
                                 command=self.clear_viz, style='Danger.TButton')
        clear_viz_btn.pack(side='left')
        ButtonAnimator.add_hover_effects(clear_viz_btn, "Vider la zone de visualisation")
        
        # Message d'accueil
        welcome_text = """🔍 SYSTÈME D'AUDIT UNIVERSEL

Bienvenue dans le panneau de visualisation !

📋 Fonctionnalités :
• Charger Rapport : Affiche le dernier rapport d'audit
• Actualiser : Met à jour la visualisation
• Effacer : Vide la zone de visualisation

📊 Contenu affiché :
• Rapports d'audit détaillés
• Résultats d'analyse
• Métriques et statistiques
• Recommandations

💡 Conseil : Lancez un audit pour voir les résultats ici !
"""
        self.viz_text.insert(tk.END, welcome_text)
        self.viz_text.config(state=tk.DISABLED)
    
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
        """Met à jour les informations du projet."""
        project_path = self.selected_project.get()
        
        if not project_path:
            self.project_info_label.config(text="Aucun projet sélectionné")
            return
        
        project_path = Path(project_path)
        
        if not project_path.exists():
            self.project_info_label.config(text="❌ Dossier introuvable")
            return
        
        # Vérifier si c'est un projet avec audit
        audit_system_dir = self.project_dir.parent
        project_name = project_path.name.lower().replace(' ', '_').replace('-', '_')
        reports_dir = audit_system_dir / "projects" / project_name / "reports"
        
        if reports_dir.exists():
            report_count = len(list(reports_dir.glob("*.html")))
            self.project_info_label.config(text=f"✅ Projet avec audit ({report_count} rapport(s)) - {project_path.name}")
        else:
            self.project_info_label.config(text=f"ℹ️ Nouveau projet - {project_path.name}")
    
    def run_audit(self):
        """Lance l'audit du projet."""
        project_path = self.selected_project.get()
        
        if not project_path:
            ModernDialog(self.root, "Attention", "Veuillez sélectionner un projet.", "warning")
            return
        
        if self.project_running:
            ModernDialog(self.root, "Information", "Un audit est déjà en cours.", "info")
            return
        
        # Ajouter aux récents
        self.add_recent_project(project_path)
        
        # Lancer l'audit
        self.project_running = True
        self.audit_stopped = False
        
        self.audit_btn.config(state='disabled')
        self.progress.start()
        self.status_var.set("Audit en cours...")
        
        # Mettre à jour l'indicateur IA
        self.set_ai_status("active", 1)
        
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
            process = subprocess.Popen([
                sys.executable, str(self.project_dir / "audit.py"),
                project_path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
               text=True, encoding='utf-8', errors='replace', bufsize=1, universal_newlines=True)
            
            # Lire les logs en temps réel
            while process.poll() is None:
                if self.audit_stopped:
                    process.terminate()
                    self.log_message("⏹️ Audit arrêté par l'utilisateur")
                    return
                
                # Lire la sortie
                stdout_line = process.stdout.readline()
                if stdout_line:
                    self.log_message(f"📤 {stdout_line.strip()}")
                
                # Lire les erreurs
                stderr_line = process.stderr.readline()
                if stderr_line:
                    self.log_message(f"⚠️ {stderr_line.strip()}")
                
                time.sleep(0.1)
            
            # Récupérer le code de retour
            return_code = process.poll()
            
            # Lire les dernières lignes
            remaining_stdout, remaining_stderr = process.communicate()
            
            if remaining_stdout:
                for line in remaining_stdout.split('\n'):
                    if line.strip():
                        self.log_message(f"📤 {line.strip()}")
            
            if remaining_stderr:
                for line in remaining_stderr.split('\n'):
                    if line.strip():
                        self.log_message(f"⚠️ {line.strip()}")
            
            # Afficher le résultat
            if return_code == 0 and not self.audit_stopped:
                self.log_message("✅ Audit terminé avec succès!")
                self.status_var.set("Audit terminé avec succès")
                
                # Mettre à jour les informations
                self.root.after(0, self.update_project_info)
                
                # Charger automatiquement le rapport
                if not self.audit_stopped:
                    self.root.after(0, self.load_report)
                    
                # Mettre à jour l'indicateur IA
                self.root.after(0, lambda: self.set_ai_status("idle", 0))
            elif not self.audit_stopped:
                self.log_message(f"❌ Audit échoué (code: {return_code})")
                self.status_var.set("Audit échoué")
                
                # Mettre à jour l'indicateur IA
                self.root.after(0, lambda: self.set_ai_status("idle", 0))
                
        except Exception as e:
            if not self.audit_stopped:
                self.log_message(f"❌ Erreur lors de l'audit: {e}")
                self.status_var.set("Erreur lors de l'audit")
                
                # Mettre à jour l'indicateur IA
                self.root.after(0, lambda: self.set_ai_status("idle", 0))
        
        finally:
            # Réactiver l'interface
            self.root.after(0, self._audit_finished)
    
    def stop_audit(self):
        """Arrête l'audit en cours."""
        if not self.project_running:
            return
        
        self.audit_stopped = True
        self.log_message("⏹️ Arrêt de l'audit demandé...")
        self.status_var.set("Arrêt en cours...")
        
        # Mettre à jour l'indicateur IA
        self.set_ai_status("busy", 0)
    
    def _audit_finished(self):
        """Appelé quand l'audit est terminé."""
        self.project_running = False
        self.audit_stopped = False
        
        self.audit_btn.config(state='normal')
        self.progress.stop()
        
        # Mettre à jour l'indicateur IA
        self.set_ai_status("idle", 0)
    
    def view_report(self):
        """Affiche le rapport dans la visualisation."""
        self.load_report()
    
    def load_report(self):
        """Charge le rapport dans la zone de visualisation."""
        project_path = self.selected_project.get()
        
        if not project_path:
            ModernDialog(self.root, "Attention", "Veuillez sélectionner un projet.", "warning")
            return
        
        project_path = Path(project_path)
        project_name = project_path.name.lower().replace(' ', '_').replace('-', '_')
        audit_system_dir = self.project_dir.parent
        report_path = audit_system_dir / "projects" / project_name / "reports" / "latest_report.html"
        
        if report_path.exists():
            try:
                # Lire le contenu HTML
                with open(report_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Convertir HTML en texte
                text_content = self.html_to_text(html_content)
                
                # Afficher dans la visualisation
                self.viz_text.config(state=tk.NORMAL)
                self.viz_text.delete(1.0, tk.END)
                self.viz_text.insert(tk.END, f"📄 RAPPORT D'AUDIT - {project_path.name}\n")
                self.viz_text.insert(tk.END, "=" * 60 + "\n\n")
                self.viz_text.insert(tk.END, text_content)
                self.viz_text.config(state=tk.DISABLED)
                
                self.log_message(f"📄 Rapport chargé: {report_path}")
                
                # Ouvrir automatiquement le rapport HTML dans le navigateur
                try:
                    import webbrowser
                    self.log_message("🌐 Ouverture du rapport HTML dans le navigateur...")
                    webbrowser.open(f"file://{report_path.absolute()}")
                    self.log_message("✅ Rapport HTML ouvert dans le navigateur")
                except Exception as e:
                    self.log_message(f"⚠️ Impossible d'ouvrir le rapport HTML: {e}")
                
            except Exception as e:
                self.log_message(f"❌ Erreur lors du chargement: {e}")
                ModernDialog(self.root, "Erreur", f"Erreur lors du chargement: {e}", "error")
        else:
            ModernDialog(self.root, "Attention", "Aucun rapport HTML trouvé.", "warning")
    
    def html_to_text(self, html_content):
        """Convertit le HTML en texte lisible."""
        import re
        
        # Supprimer les balises HTML
        text = re.sub(r'<[^>]+>', '', html_content)
        
        # Nettoyer les espaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remplacer les entités HTML
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&amp;', '&')
        
        # Formater les sections
        text = re.sub(r'([A-Z][A-Z\s]+:)', r'\n\n\1', text)
        
        return text.strip()
    
    def refresh_viz(self):
        """Actualise la visualisation."""
        self.load_report()
    
    def clear_viz(self):
        """Efface la zone de visualisation."""
        self.viz_text.config(state=tk.NORMAL)
        self.viz_text.delete(1.0, tk.END)
        
        welcome_text = """🔍 SYSTÈME D'AUDIT UNIVERSEL

Zone de visualisation effacée.

💡 Conseil : Lancez un audit pour voir les résultats ici !
"""
        self.viz_text.insert(tk.END, welcome_text)
        self.viz_text.config(state=tk.DISABLED)
    
    def open_folder(self):
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
                self.log_message(f"❌ Erreur lors de l'ouverture: {e}")
        else:
            ModernDialog(self.root, "Attention", "Dossier d'audit introuvable.", "warning")
    
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
                ModernDialog(self.root, "Succès", "Logs copiés dans le presse-papiers!", "success")
            else:
                ModernDialog(self.root, "Attention", "Aucun log à copier.", "warning")
        except Exception as e:
            ModernDialog(self.root, "Erreur", f"Erreur lors de la copie: {e}", "error")
    
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
                self.log_message(f"⚠️ Erreur lors du chargement: {e}")
    
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
            self.log_message(f"⚠️ Erreur lors de la sauvegarde: {e}")
    
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
            self.add_recent_project(project_path)
    
    def remove_recent_project(self):
        """Supprime un projet de la liste des projets récents."""
        selection = self.recent_listbox.curselection()
        if selection:
            self.recent_listbox.delete(selection[0])
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
    root.mainloop()

if __name__ == "__main__":
    main()
