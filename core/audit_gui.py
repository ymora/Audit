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
            # Effet de hover pour les boutons tk
            if tooltip_text:
                ButtonAnimator.show_tooltip(button, tooltip_text, event)
        
        def on_leave(event):
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
            yes_btn = tk.Button(button_frame, text="Oui", font=('Inter', 12, 'bold'),
                               bg='#ffffff', fg='#3b82f6', bd=1, relief='solid',
                               padx=16, pady=6, command=self.yes_clicked,
                               activebackground='#f0f9ff', activeforeground='#1d4ed8',
                               cursor='hand2')
            yes_btn.pack(side='left', padx=(0, 10))
            ButtonAnimator.add_hover_effects(yes_btn, "Confirmer l'action")
            
            no_btn = tk.Button(button_frame, text="Non", font=('Inter', 12, 'bold'),
                              bg='#ffffff', fg='#6b7280', bd=1, relief='solid',
                              padx=16, pady=6, command=self.no_clicked,
                              activebackground='#f9fafb', activeforeground='#4b5563',
                              cursor='hand2')
            no_btn.pack(side='left')
            ButtonAnimator.add_hover_effects(no_btn, "Annuler l'action")
        else:
            # Bouton OK avec style unifié
            ok_btn = tk.Button(button_frame, text="OK", font=('Inter', 12, 'bold'),
                              bg='#ffffff', fg='#3b82f6', bd=1, relief='solid',
                              padx=24, pady=6, command=self.ok_clicked,
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
                       font=('Inter', 12, 'medium'))
        
        style.configure('Info.TLabel',
                       background=self.colors['bg_medium'],
                       foreground=self.colors['text_secondary'],
                       font=('Inter', 10, 'normal'))
    
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
                       background='transparent',
                       foreground='#3b82f6',
                       bordercolor='#3b82f6',
                       **base_config)
        style.map('Primary.TButton',
                 background=[('active', 'transparent'), ('pressed', 'transparent')],
                 foreground=[('active', '#1d4ed8'), ('pressed', '#1d4ed8')],
                 bordercolor=[('active', '#1d4ed8'), ('pressed', '#1d4ed8')])
        
        # Bouton Secondary (Gris)
        style.configure('Secondary.TButton',
                       background='transparent',
                       foreground='#6b7280',
                       bordercolor='#6b7280',
                       **base_config)
        style.map('Secondary.TButton',
                 background=[('active', 'transparent'), ('pressed', 'transparent')],
                 foreground=[('active', '#4b5563'), ('pressed', '#4b5563')],
                 bordercolor=[('active', '#4b5563'), ('pressed', '#4b5563')])
        
        # Bouton Success (Vert)
        style.configure('Success.TButton',
                       background='transparent',
                       foreground='#10b981',
                       bordercolor='#10b981',
                       **base_config)
        style.map('Success.TButton',
                 background=[('active', 'transparent'), ('pressed', 'transparent')],
                 foreground=[('active', '#059669'), ('pressed', '#059669')],
                 bordercolor=[('active', '#059669'), ('pressed', '#059669')])
        
        # Bouton Warning (Jaune)
        style.configure('Warning.TButton',
                       background='transparent',
                       foreground='#f59e0b',
                       bordercolor='#f59e0b',
                       **base_config)
        style.map('Warning.TButton',
                 background=[('active', 'transparent'), ('pressed', 'transparent')],
                 foreground=[('active', '#d97706'), ('pressed', '#d97706')],
                 bordercolor=[('active', '#d97706'), ('pressed', '#d97706')])
        
        # Bouton Danger (Rouge)
        style.configure('Danger.TButton',
                       background='transparent',
                       foreground='#ef4444',
                       bordercolor='#ef4444',
                       **base_config)
        style.map('Danger.TButton',
                 background=[('active', 'transparent'), ('pressed', 'transparent')],
                 foreground=[('active', '#dc2626'), ('pressed', '#dc2626')],
                 bordercolor=[('active', '#dc2626'), ('pressed', '#dc2626')])
        
        # Bouton Info (Violet)
        style.configure('Info.TButton',
                       background='transparent',
                       foreground='#8b5cf6',
                       bordercolor='#8b5cf6',
                       **base_config)
        style.map('Info.TButton',
                 background=[('active', 'transparent'), ('pressed', 'transparent')],
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
        main_frame.columnconfigure(2, weight=2)  # Visualisation
        main_frame.rowconfigure(0, weight=1)
        
        # Panneau de contrôle (gauche)
        self.create_control_panel(main_frame)
        
        # Barre de séparation redimensionnable
        self.create_separator(main_frame)
        
        # Panneau de visualisation (droite)
        self.create_visualization_panel(main_frame)
    
    def create_separator(self, parent):
        """Crée une barre de séparation redimensionnable."""
        # Frame pour la barre de séparation
        separator_frame = ttk.Frame(parent, style='Dark.TFrame')
        separator_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=4)
        separator_frame.configure(width=8)
        
        # Barre de séparation
        self.separator = ttk.Separator(separator_frame, orient='vertical')
        self.separator.pack(fill=tk.Y, expand=True)
        
        # Curseur pour indiquer que c'est redimensionnable
        separator_frame.bind('<Enter>', lambda e: separator_frame.configure(cursor='sb_h_double_arrow'))
        separator_frame.bind('<Leave>', lambda e: separator_frame.configure(cursor=''))
        
        # Variables pour le redimensionnement
        self.separator_dragging = False
        self.separator_start_x = 0
        
        # Bindings pour le redimensionnement
        separator_frame.bind('<Button-1>', self.start_separator_drag)
        separator_frame.bind('<B1-Motion>', self.separator_drag)
        separator_frame.bind('<ButtonRelease-1>', self.stop_separator_drag)
    
    def start_separator_drag(self, event):
        """Démarre le redimensionnement de la barre de séparation."""
        self.separator_dragging = True
        self.separator_start_x = event.x_root
    
    def separator_drag(self, event):
        """Gère le redimensionnement de la barre de séparation."""
        if self.separator_dragging:
            delta_x = event.x_root - self.separator_start_x
            # Ajuster les poids des colonnes
            current_weights = self.root.grid_columnconfigure(0)['weight']
            # Limiter le redimensionnement
            if delta_x > 50:  # Minimum pour le panneau de contrôle
                pass  # Implémentation du redimensionnement
    
    def stop_separator_drag(self, event):
        """Arrête le redimensionnement de la barre de séparation."""
        self.separator_dragging = False
    
    def create_control_panel(self, parent):
        """Crée le panneau de contrôle."""
        control_frame = ttk.Frame(parent, style='Dark.TFrame')
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 16))
        control_frame.columnconfigure(0, weight=1)
        control_frame.rowconfigure(3, weight=1)  # Logs prennent l'espace restant
        
        # Titre
        title_frame = ttk.Frame(control_frame, style='Dark.TFrame')
        title_frame.grid(row=0, column=0, pady=(0, 20))
        title_frame.columnconfigure(0, weight=1)
        
        title_label = ttk.Label(title_frame, text="Audit Universel", style='Title.TLabel')
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Section projet
        self.create_project_section(control_frame)
        
        # Section projets récents (déplacée ici pour plus de fluidité)
        self.create_recent_projects_section(control_frame)
        
        # Section actions
        self.create_actions_section(control_frame)
        
        # Section logs
        self.create_logs_section(control_frame)
        
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
        
        browse_btn = tk.Button(project_frame, text="📂", command=self.browse_project, 
                              bg='#ffffff', fg='#3b82f6', font=('Inter', 14, 'bold'),
                              relief='solid', borderwidth=1, cursor='hand2',
                              activebackground='#f0f9ff', activeforeground='#1d4ed8')
        browse_btn.grid(row=0, column=2)
        ButtonAnimator.add_hover_effects(browse_btn, "Sélectionner un dossier de projet")
        
        # Informations du projet
        self.project_info_label = ttk.Label(project_frame, text="Aucun projet sélectionné", style='Info.TLabel')
        self.project_info_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(8, 0))
        
        # Explication
        explanation_label = ttk.Label(project_frame, 
                                     text="Sélectionnez le dossier racine du projet à auditer. L'audit analysera tous les fichiers du projet.",
                                     style='Info.TLabel', font=('TkDefaultFont', 9))
        explanation_label.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(4, 0))
    
    def create_actions_section(self, parent):
        """Crée la section des actions."""
        actions_frame = ttk.LabelFrame(parent, text="Actions", style='Dark.TLabelframe', padding="12")
        actions_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 16))
        
        # Boutons d'action
        button_frame = ttk.Frame(actions_frame, style='Dark.TFrame')
        button_frame.grid(row=0, column=0, pady=(0, 12))
        
        self.audit_btn = tk.Button(button_frame, text="🔍 Lancer l'Audit", 
                                   command=self.run_audit,
                                   bg='#ffffff', fg='#10b981', font=('Inter', 10, 'bold'),
                                   relief='solid', borderwidth=1, cursor='hand2', padx=8, pady=4,
                                   activebackground='#f0fdf4', activeforeground='#059669')
        self.audit_btn.pack(side='left', padx=(0, 6))
        ButtonAnimator.add_hover_effects(self.audit_btn, "Démarrer l'analyse complète du projet")
        
        self.stop_btn = tk.Button(button_frame, text="⏹️ Arrêter", 
                                  command=self.stop_audit,
                                  bg='#ffffff', fg='#ef4444', font=('Inter', 10, 'bold'),
                                  relief='solid', borderwidth=1, cursor='hand2', padx=8, pady=4,
                                  activebackground='#fef2f2', activeforeground='#dc2626')
        self.stop_btn.pack(side='left', padx=(0, 6))
        ButtonAnimator.add_hover_effects(self.stop_btn, "Interrompre l'audit en cours")
        
        self.view_btn = tk.Button(button_frame, text="📄 Voir Rapport", 
                                  command=self.view_report,
                                  bg='#ffffff', fg='#3b82f6', font=('Inter', 10, 'bold'),
                                  relief='solid', borderwidth=1, cursor='hand2', padx=8, pady=4,
                                  activebackground='#f0f9ff', activeforeground='#1d4ed8')
        self.view_btn.pack(side='left', padx=(0, 6))
        ButtonAnimator.add_hover_effects(self.view_btn, "Afficher le dernier rapport d'audit")
        
        self.folder_btn = tk.Button(button_frame, text="📂 Dossier", 
                                    command=self.open_folder,
                                    bg='#ffffff', fg='#3b82f6', font=('Inter', 10, 'bold'),
                                    relief='solid', borderwidth=1, cursor='hand2', padx=8, pady=4,
                                    activebackground='#f0f9ff', activeforeground='#1d4ed8')
        self.folder_btn.pack(side='left')
        ButtonAnimator.add_hover_effects(self.folder_btn, "Ouvrir le dossier d'audit du projet")
        
        # Barre de progression
        self.progress = ttk.Progressbar(actions_frame, mode='indeterminate', style='Dark.Horizontal.TProgressbar')
        self.progress.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(8, 0))
        
        # Explication des actions
        actions_explanation = ttk.Label(actions_frame, 
                                      text="🔍 Lancer l'Audit : Analyse complète du projet | ⏹️ Arrêter : Interrompre l'audit | 📄 Voir Rapport : Afficher les résultats | 📂 Dossier : Ouvrir le dossier d'audit",
                                      style='Info.TLabel', font=('TkDefaultFont', 9))
        actions_explanation.grid(row=2, column=0, sticky=tk.W, pady=(8, 0))
    
    def create_logs_section(self, parent):
        """Crée la section des logs."""
        logs_frame = ttk.LabelFrame(parent, text="Logs", style='Dark.TLabelframe', padding="12")
        logs_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 16))
        logs_frame.columnconfigure(0, weight=1)
        logs_frame.rowconfigure(0, weight=1)
        
        # Zone de texte pour les logs
        self.logs_text = scrolledtext.ScrolledText(
            logs_frame, 
            wrap=tk.WORD, 
            font=('JetBrains Mono', 10),
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
        
        clear_btn = tk.Button(logs_buttons_frame, text="Effacer", 
                              command=self.clear_logs,
                              bg='#ffffff', fg='#ef4444', font=('Inter', 12, 'bold'),
                              relief='solid', borderwidth=1, cursor='hand2', padx=12, pady=4,
                              activebackground='#fef2f2', activeforeground='#dc2626')
        clear_btn.pack(side='left', padx=(0, 8))
        ButtonAnimator.add_hover_effects(clear_btn, "Vider tous les logs")
        
        copy_btn = tk.Button(logs_buttons_frame, text="Copier", 
                             command=self.copy_logs,
                             bg='#ffffff', fg='#3b82f6', font=('Inter', 10, 'bold'),
                             relief='solid', borderwidth=1, cursor='hand2', padx=8, pady=4,
                             activebackground='#f0f9ff', activeforeground='#1d4ed8')
        copy_btn.pack(side='left')
        ButtonAnimator.add_hover_effects(copy_btn, "Copier les logs dans le presse-papiers")
        
        # Explication des logs
        logs_explanation = ttk.Label(logs_frame, 
                                   text="Les logs affichent les détails de l'exécution de l'audit en temps réel. Utilisez 'Effacer' pour vider et 'Copier' pour sauvegarder.",
                                   style='Info.TLabel', font=('TkDefaultFont', 9))
        logs_explanation.grid(row=2, column=0, sticky=tk.W, pady=(4, 0))
    
    def create_recent_projects_section(self, parent):
        """Crée la section des projets récents."""
        recent_frame = ttk.LabelFrame(parent, text="Projets Récents", style='Dark.TLabelframe', padding="12")
        recent_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 16))
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
            font=('Inter', 10)
        )
        self.recent_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 12))
        self.recent_listbox.bind('<Double-Button-1>', self.select_recent_project)
        
        # Boutons pour les projets récents
        recent_buttons_frame = ttk.Frame(recent_frame, style='Dark.TFrame')
        recent_buttons_frame.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        select_btn = tk.Button(recent_buttons_frame, text="Sélectionner", 
                               command=self.select_recent_project,
                               bg='#ffffff', fg='#3b82f6', font=('Inter', 10, 'bold'),
                               relief='solid', borderwidth=1, cursor='hand2', padx=8, pady=4,
                               activebackground='#f0f9ff', activeforeground='#1d4ed8')
        select_btn.pack(pady=(0, 8))
        ButtonAnimator.add_hover_effects(select_btn, "Charger le projet sélectionné")
        
        remove_btn = tk.Button(recent_buttons_frame, text="Supprimer", 
                               command=self.remove_recent_project,
                               bg='#ffffff', fg='#ef4444', font=('Inter', 10, 'bold'),
                               relief='solid', borderwidth=1, cursor='hand2', padx=8, pady=4,
                               activebackground='#fef2f2', activeforeground='#dc2626')
        remove_btn.pack()
        ButtonAnimator.add_hover_effects(remove_btn, "Retirer le projet de la liste")
        
        # Explication des projets récents
        recent_explanation = ttk.Label(recent_frame, 
                                     text="Liste des projets récemment audités. Double-cliquez ou utilisez 'Sélectionner' pour charger un projet.",
                                     style='Info.TLabel', font=('TkDefaultFont', 9))
        recent_explanation.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(8, 0))
    
    def create_status_bar(self, parent):
        """Crée la barre de statut."""
        self.status_var = tk.StringVar()
        self.status_var.set("Prêt")
        
        status_bar = ttk.Label(parent, textvariable=self.status_var, 
                              style='Info.TLabel', anchor=tk.W)
        status_bar.grid(row=5, column=0, sticky=(tk.W, tk.E))
    

    
    def create_visualization_panel(self, parent):
        """Crée le panneau de visualisation."""
        self.viz_frame = ttk.LabelFrame(parent, text="Visualisation", style='Dark.TLabelframe', padding="12")
        self.viz_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.viz_frame.columnconfigure(0, weight=1)
        self.viz_frame.rowconfigure(0, weight=1)
        
        # Zone de visualisation
        self.viz_text = scrolledtext.ScrolledText(
            self.viz_frame,
            wrap=tk.WORD,
            font=('JetBrains Mono', 11),
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
        viz_buttons_frame = ttk.Frame(self.viz_frame, style='Dark.TFrame')
        viz_buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(8, 0))
        
        load_btn = tk.Button(viz_buttons_frame, text="Charger Rapport", 
                             command=self.load_report,
                             bg='#ffffff', fg='#3b82f6', font=('Inter', 10, 'bold'),
                             relief='solid', borderwidth=1, cursor='hand2', padx=8, pady=4,
                             activebackground='#f0f9ff', activeforeground='#1d4ed8')
        load_btn.pack(side='left', padx=(0, 8))
        ButtonAnimator.add_hover_effects(load_btn, "Charger le rapport d'audit dans la visualisation")
        
        refresh_btn = tk.Button(viz_buttons_frame, text="Actualiser", 
                               command=self.refresh_viz,
                               bg='#ffffff', fg='#3b82f6', font=('Inter', 10, 'bold'),
                               relief='solid', borderwidth=1, cursor='hand2', padx=8, pady=4,
                               activebackground='#f0f9ff', activeforeground='#1d4ed8')
        refresh_btn.pack(side='left', padx=(0, 8))
        ButtonAnimator.add_hover_effects(refresh_btn, "Mettre à jour la visualisation")
        
        clear_viz_btn = tk.Button(viz_buttons_frame, text="Effacer", 
                                 command=self.clear_viz,
                                 bg='#ffffff', fg='#ef4444', font=('Inter', 10, 'bold'),
                                 relief='solid', borderwidth=1, cursor='hand2', padx=8, pady=4,
                                 activebackground='#fef2f2', activeforeground='#dc2626')
        clear_viz_btn.pack(side='left')
        ButtonAnimator.add_hover_effects(clear_viz_btn, "Vider la zone de visualisation")
        
        # Explication de la visualisation
        viz_explanation = ttk.Label(self.viz_frame, 
                                  text="Zone d'affichage des rapports d'audit. Les résultats s'affichent ici après l'exécution d'un audit.",
                                  style='Info.TLabel', font=('TkDefaultFont', 9))
        viz_explanation.grid(row=2, column=0, sticky=tk.W, pady=(8, 0))
        
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

💡 Conseil : Lancez un audit pour voir les résultats ici !"""
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
        reports_dir = audit_system_dir / "audit_results" / "audit_reports" / project_name
        
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
                
                # Charger automatiquement le rapport dans la visualisation
                if not self.audit_stopped:
                    self.root.after(0, self.load_report)
            elif not self.audit_stopped:
                self.log_message(f"❌ Audit échoué (code: {return_code})")
                self.status_var.set("Audit échoué")
                
        except Exception as e:
            if not self.audit_stopped:
                self.log_message(f"❌ Erreur lors de l'audit: {e}")
                self.status_var.set("Erreur lors de l'audit")
        
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
    
    def _audit_finished(self):
        """Appelé quand l'audit est terminé."""
        self.project_running = False
        self.audit_stopped = False
        
        self.audit_btn.config(state='normal')
        self.progress.stop()
    
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
        report_path = audit_system_dir / "audit_results" / "audit_reports" / project_name / "latest_report.html"
        
        if report_path.exists():
            try:
                # Lire le contenu HTML
                with open(report_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Créer un widget HTML pour afficher le rapport
                if hasattr(self, 'html_frame'):
                    self.html_frame.destroy()
                
                self.html_frame = tk.Frame(self.viz_frame, bg=self.colors['bg_light'])
                self.html_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
                self.viz_frame.columnconfigure(0, weight=1)
                self.viz_frame.rowconfigure(0, weight=1)
                
                # Créer un fichier temporaire pour le HTML
                import tempfile
                import webbrowser
                
                temp_html = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
                temp_html.write(html_content)
                temp_html.close()
                
                # Créer un widget WebView ou utiliser un navigateur intégré
                try:
                    # Essayer d'utiliser tkinterweb si disponible
                    import tkinterweb
                    webview = tkinterweb.HtmlFrame(self.html_frame)
                    webview.load_html(html_content)
                    webview.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
                    self.html_frame.columnconfigure(0, weight=1)
                    self.html_frame.rowconfigure(0, weight=1)
                except ImportError:
                    # Fallback: afficher le HTML dans un widget Text avec balises
                    html_text = tk.Text(self.html_frame, 
                                       bg=self.colors['bg_light'],
                                       fg=self.colors['text_primary'],
                                       font=('Consolas', 10),
                                       wrap=tk.WORD,
                                       padx=10, pady=10)
                    html_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
                    
                    # Ajouter une scrollbar
                    scrollbar = ttk.Scrollbar(self.html_frame, orient=tk.VERTICAL, command=html_text.yview)
                    scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
                    html_text.configure(yscrollcommand=scrollbar.set)
                    
                    # Insérer le HTML avec formatage basique
                    html_text.insert(tk.END, f"📄 RAPPORT D'AUDIT - {project_path.name}\n")
                    html_text.insert(tk.END, "=" * 60 + "\n\n")
                    html_text.insert(tk.END, html_content)
                    
                    # Désactiver l'édition
                    html_text.config(state=tk.DISABLED)
                
                self.log_message(f"📄 Rapport HTML chargé dans la visualisation: {report_path}")
                
            except Exception as e:
                self.log_message(f"❌ Erreur lors du chargement: {e}")
                ModernDialog(self.root, "Erreur", f"Erreur lors du chargement: {e}", "error")
        else:
            ModernDialog(self.root, "Attention", "Aucun rapport HTML trouvé.", "warning")
    

    
    def refresh_viz(self):
        """Actualise la visualisation."""
        self.load_report()
    
    def clear_viz(self):
        """Efface la zone de visualisation."""
        # Détruire le frame HTML s'il existe
        if hasattr(self, 'html_frame'):
            self.html_frame.destroy()
        
        # Recréer le widget de visualisation par défaut
        self.viz_text = tk.Text(self.viz_frame, 
                               bg=self.colors['bg_light'],
                               fg=self.colors['text_primary'],
                               font=('Inter', 12),
                               wrap=tk.WORD,
                               padx=10, pady=10)
        self.viz_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
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
        audit_path = audit_system_dir / "audit_results" / "audit_reports" / project_name
        
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
