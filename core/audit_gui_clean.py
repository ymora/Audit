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
import math

class ModernDialog:
    """Fenêtre contextuelle moderne avec effets glassmorphism."""
    
    def __init__(self, parent, title, message, dialog_type="info"):
        self.parent = parent
        self.title = title
        self.message = message
        self.dialog_type = dialog_type
        self.result = None
        
        # Créer la fenêtre contextuelle
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrer la fenêtre
        self.center_window()
        
        # Configuration du style
        self.setup_dialog_style()
        
        # Créer l'interface
        self.create_dialog_widgets()
        
        # Effet de focus
        self.dialog.focus_set()
        self.dialog.wait_window()
    
    def center_window(self):
        """Centre la fenêtre sur l'écran."""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_dialog_style(self):
        """Configure le style de la fenêtre contextuelle."""
        self.dialog.configure(bg='#0a0a0a')
        
        # Couleurs selon le type de dialogue
        if self.dialog_type == "success":
            self.accent_color = '#10b981'
            self.icon = "✅"
        elif self.dialog_type == "warning":
            self.accent_color = '#f59e0b'
            self.icon = "⚠️"
        elif self.dialog_type == "error":
            self.accent_color = '#ef4444'
            self.icon = "❌"
        else:
            self.accent_color = '#3b82f6'
            self.icon = "ℹ️"
    
    def create_dialog_widgets(self):
        """Crée les widgets de la fenêtre contextuelle."""
        # Frame principal avec effet glassmorphism
        main_frame = tk.Frame(self.dialog, bg='#1a1a1a', relief='flat', bd=0)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Icône et titre
        icon_label = tk.Label(main_frame, text=self.icon, font=('Inter', 32), 
                             bg='#1a1a1a', fg=self.accent_color)
        icon_label.pack(pady=(0, 10))
        
        title_label = tk.Label(main_frame, text=self.title, font=('Inter', 16, 'bold'),
                              bg='#1a1a1a', fg='#ffffff')
        title_label.pack(pady=(0, 15))
        
        # Message
        message_label = tk.Label(main_frame, text=self.message, font=('Inter', 11),
                                bg='#1a1a1a', fg='#e2e8f0', wraplength=350, justify='center')
        message_label.pack(pady=(0, 25))
        
        # Boutons
        button_frame = tk.Frame(main_frame, bg='#1a1a1a')
        button_frame.pack()
        
        if self.dialog_type == "confirm":
            # Boutons Oui/Non pour confirmation avec style moderne
            yes_btn = tk.Button(button_frame, text="Oui", font=('Inter', 11, 'bold'),
                               bg='#1a1a1a', fg=self.accent_color, bd=2, relief='solid',
                               padx=20, pady=8, command=self.yes_clicked,
                               activebackground='#2a2a2a', activeforeground=self.accent_color)
            yes_btn.pack(side='left', padx=(0, 10))
            
            no_btn = tk.Button(button_frame, text="Non", font=('Inter', 11, 'bold'),
                              bg='#1a1a1a', fg='#64748b', bd=2, relief='solid',
                              padx=20, pady=8, command=self.no_clicked,
                              activebackground='#2a2a2a', activeforeground='#64748b')
            no_btn.pack(side='left')
        else:
            # Bouton OK pour info/success/warning/error avec style moderne
            ok_btn = tk.Button(button_frame, text="OK", font=('Inter', 11, 'bold'),
                              bg='#1a1a1a', fg=self.accent_color, bd=2, relief='solid',
                              padx=30, pady=8, command=self.ok_clicked,
                              activebackground='#2a2a2a', activeforeground=self.accent_color)
            ok_btn.pack()
        
        # Effets de survol pour les boutons
        for widget in button_frame.winfo_children():
            if isinstance(widget, tk.Button):
                widget.bind('<Enter>', lambda e, btn=widget: self.on_button_hover(btn, True))
                widget.bind('<Leave>', lambda e, btn=widget: self.on_button_hover(btn, False))
    
    def on_button_hover(self, button, entering):
        """Effet de survol pour les boutons."""
        if entering:
            if button.cget('text') in ['Oui', 'OK']:
                button.configure(bg='#2a2a2a', relief='solid', bd=2)
            else:
                button.configure(bg='#2a2a2a', relief='solid', bd=2)
        else:
            if button.cget('text') in ['Oui', 'OK']:
                button.configure(bg='#1a1a1a', relief='solid', bd=2)
            else:
                button.configure(bg='#1a1a1a', relief='solid', bd=2)
    
    def yes_clicked(self):
        """Appelé quand l'utilisateur clique sur 'Oui'."""
        self.result = True
        self.dialog.destroy()
    
    def no_clicked(self):
        """Appelé quand l'utilisateur clique sur 'Non'."""
        self.result = False
        self.dialog.destroy()
    
    def ok_clicked(self):
        """Appelé quand l'utilisateur clique sur 'OK'."""
        self.result = True
        self.dialog.destroy()


class RoundedButton(tk.Canvas):
    """Bouton personnalisé avec coins arrondis et effets modernes."""
    
    def __init__(self, parent, text, command=None, bg_color='#3b82f6', fg_color='#ffffff', 
                 width=120, height=40, corner_radius=25, **kwargs):
        super().__init__(parent, width=width, height=height, bg='#0a0a0a', 
                        highlightthickness=0, relief='flat', **kwargs)
        
        self.text = text
        self.command = command
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.corner_radius = corner_radius
        self.is_pressed = False
        
        # Créer le bouton
        self.draw_button()
        
        # Bindings pour les effets
        self.bind('<Button-1>', self.on_click)
        self.bind('<ButtonRelease-1>', self.on_release)
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
    
    def draw_button(self, pressed=False):
        """Dessine le bouton avec les coins arrondis et contour subtil."""
        self.delete("all")
        
        # Couleur de contour selon l'état
        if pressed:
            outline_color = self.darken_color(self.bg_color, 0.3)
            fill_color = self.bg_color + '20'  # Très légère transparence
        else:
            outline_color = self.bg_color
            fill_color = ''  # Pas de remplissage
        
        # Dessiner le rectangle arrondi avec contour
        self.create_rounded_rectangle(0, 0, self.winfo_reqwidth(), self.winfo_reqheight(),
                                    self.corner_radius, fill=fill_color, outline=outline_color, width=2)
        
        # Ajouter le texte
        self.create_text(self.winfo_reqwidth()/2, self.winfo_reqheight()/2,
                        text=self.text, fill=self.bg_color, font=('Inter', 11, 'bold'))
    
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        """Crée un rectangle avec coins arrondis."""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def darken_color(self, color, factor):
        """Assombrit une couleur hexadécimale."""
        # Convertir hex en RGB
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        
        # Assombrir
        r = int(r * (1 - factor))
        g = int(g * (1 - factor))
        b = int(b * (1 - factor))
        
        # Reconvertir en hex
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def on_click(self, event):
        """Appelé quand le bouton est cliqué."""
        self.is_pressed = True
        self.draw_button(pressed=True)
    
    def on_release(self, event):
        """Appelé quand le bouton est relâché."""
        self.is_pressed = False
        self.draw_button(pressed=False)
        if self.command:
            self.command()
    
    def on_enter(self, event):
        """Appelé quand la souris entre dans le bouton."""
        if not self.is_pressed:
            # Effet de lueur
            self.configure(cursor='hand2')
    
    def on_leave(self, event):
        """Appelé quand la souris quitte le bouton."""
        self.configure(cursor='')


class AuditGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🔍 Système d'Audit Universel")
        
        # Taille adaptée à l'écran (80% de la résolution)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        
        # Centrer la fenêtre
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(1000, 600)
        
        # Rendre la fenêtre redimensionnable
        self.root.resizable(True, True)
        
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
        """Configure les styles de l'interface avec un thème moderne 2025."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Palette de couleurs moderne 2025 avec effets glassmorphism
        self.colors = {
            # Couleurs de fond avec transparence
            'bg_900': '#0a0a0a',      # Fond principal très sombre
            'bg_800': '#1a1a1a',      # Fond secondaire
            'bg_700': '#2a2a2a',      # Fond tertiaire
            'bg_600': '#3a3a3a',      # Fond quaternaire
            'bg_glass': '#ffffff08',  # Fond glassmorphism
            'bg_glass_dark': '#00000020', # Fond glassmorphism sombre
            
            # Couleurs d'accent avec gradients
            'blue_500': '#3b82f6',    # Bleu principal
            'blue_600': '#2563eb',    # Bleu foncé
            'blue_gradient': 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
            'emerald_500': '#10b981', # Vert succès
            'emerald_600': '#059669', # Vert foncé
            'emerald_gradient': 'linear-gradient(135deg, #10b981 0%, #047857 100%)',
            'amber_500': '#f59e0b',   # Orange avertissement
            'amber_600': '#d97706',   # Orange foncé
            'amber_gradient': 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
            'red_500': '#ef4444',     # Rouge erreur
            'red_600': '#dc2626',     # Rouge foncé
            'red_gradient': 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
            'purple_500': '#8b5cf6',  # Violet accent
            'purple_600': '#7c3aed',  # Violet foncé
            'purple_gradient': 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
            
            # Couleurs de texte
            'text_50': '#ffffff',     # Texte très clair
            'text_100': '#f8fafc',    # Texte clair
            'text_200': '#e2e8f0',    # Texte moyen-clair
            'text_300': '#cbd5e1',    # Texte moyen
            'text_400': '#94a3b8',    # Texte moyen-foncé
            'text_500': '#64748b',    # Texte foncé
            
            # Bordures avec effets
            'border_600': '#374151',  # Bordure principale
            'border_500': '#4b5563',  # Bordure secondaire
            'border_400': '#6b7280',  # Bordure claire
            'border_glass': '#ffffff20', # Bordure glassmorphism
            
            # Ombres et effets modernes
            'shadow_soft': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
            'shadow_medium': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
            'shadow_large': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
            'glow_blue': '0 0 20px rgba(59, 130, 246, 0.3)',
            'glow_green': '0 0 20px rgba(16, 185, 129, 0.3)',
            'glow_red': '0 0 20px rgba(239, 68, 68, 0.3)',
            
            # Effets de transparence
            'backdrop_blur': 'blur(10px)',
            'backdrop_blur_light': 'blur(5px)'
        }
        
        # Configuration du thème moderne 2025 avec glassmorphism
        self.root.configure(bg=self.colors['bg_900'])
        
        # Style pour les frames avec effets glassmorphism
        style.configure('Dark.TFrame', background=self.colors['bg_900'])
        style.configure('Medium.TFrame', background=self.colors['bg_800'])
        style.configure('Light.TFrame', background=self.colors['bg_700'])
        style.configure('Glass.TFrame', background=self.colors['bg_glass'])
        
        # Style pour les labels avec typographie moderne
        style.configure('Title.TLabel', 
                       background=self.colors['bg_900'], 
                       foreground=self.colors['text_50'],
                       font=('Inter', 24, 'bold'))
        
        style.configure('Subtitle.TLabel', 
                       background=self.colors['bg_800'], 
                       foreground=self.colors['text_300'],
                       font=('Inter', 12, 'medium'))
        
        style.configure('Info.TLabel',
                       background=self.colors['bg_800'],
                       foreground=self.colors['text_200'],
                       font=('Inter', 10))
        
        # Style pour les boutons avec design moderne 2025 (arrondis avec effets)
        style.configure('Primary.TButton',
                       background=self.colors['blue_500'],
                       foreground=self.colors['text_50'],
                       borderwidth=0,
                       focuscolor='none',
                       font=('Inter', 11, 'bold'),
                       padding=(20, 12))
        
        style.map('Primary.TButton',
                 background=[('active', self.colors['blue_600']),
                            ('pressed', self.colors['blue_600'])])
        
        style.configure('Success.TButton',
                       background=self.colors['emerald_500'],
                       foreground=self.colors['text_50'],
                       borderwidth=0,
                       focuscolor='none',
                       font=('Inter', 11, 'bold'),
                       padding=(20, 12))
        
        style.map('Success.TButton',
                 background=[('active', self.colors['emerald_600']),
                            ('pressed', self.colors['emerald_600'])])
        
        style.configure('Warning.TButton',
                       background=self.colors['amber_500'],
                       foreground=self.colors['text_50'],
                       borderwidth=0,
                       focuscolor='none',
                       font=('Inter', 11, 'bold'),
                       padding=(20, 12))
        
        style.map('Warning.TButton',
                 background=[('active', self.colors['amber_600']),
                            ('pressed', self.colors['amber_600'])])
        
        style.configure('Danger.TButton',
                       background=self.colors['red_500'],
                       foreground=self.colors['text_50'],
                       borderwidth=0,
                       focuscolor='none',
                       font=('Inter', 11, 'bold'),
                       padding=(20, 12))
        
        style.map('Danger.TButton',
                 background=[('active', self.colors['red_600']),
                            ('pressed', self.colors['red_600'])])
        
        # Style pour les labelframes avec design glassmorphism
        style.configure('Dark.TLabelframe',
                       background=self.colors['bg_800'],
                       foreground=self.colors['text_50'],
                       borderwidth=1,
                       relief='solid',
                       bordercolor=self.colors['border_glass'])
        
        style.configure('Dark.TLabelframe.Label',
                       background=self.colors['bg_800'],
                       foreground=self.colors['blue_500'],
                       font=('Inter', 12, 'bold'))
        
        # Style pour les entry avec design moderne
        style.configure('Dark.TEntry',
                       fieldbackground=self.colors['bg_700'],
                       foreground=self.colors['text_100'],
                       borderwidth=1,
                       relief='solid',
                       bordercolor=self.colors['border_600'],
                       padding=(12, 8))
        
        # Style pour les listbox avec design moderne
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
                       padding=(12, 6))
    
    def create_widgets(self):
        """Crée tous les widgets de l'interface avec un design moderne."""
        # Frame principal épuré avec padding réduit
        main_frame = ttk.Frame(self.root, style='Dark.TFrame', padding="12")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration du grid pour redimensionnabilité optimale
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=4)  # Logs prennent 4x plus d'espace
        main_frame.rowconfigure(4, weight=1)  # Projets récents compacts
        
        # Titre épuré et compact
        title_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 16))
        
        title_label = ttk.Label(title_frame, text="Audit Universel", 
                               style='Title.TLabel')
        title_label.pack()
        
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
        """Crée la section de sélection de projet compacte."""
        # Frame pour la sélection de projet
        project_frame = ttk.LabelFrame(parent, text="Projet", 
                                      style='Dark.TLabelframe', padding="12")
        project_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 12))
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
        """Crée la section des actions compacte."""
        actions_frame = ttk.LabelFrame(parent, text="Actions", 
                                      style='Dark.TLabelframe', padding="12")
        actions_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 12))
        
        # Boutons d'action avec design moderne et espacement
        button_frame = tk.Frame(actions_frame, bg=self.colors['bg_800'])
        button_frame.grid(row=0, column=0, columnspan=3, pady=(0, 16))
        
        self.project_btn = RoundedButton(button_frame, text="🔍 Lancer l'Audit", 
                                       command=self.run_audit, bg_color=self.colors['emerald_500'],
                                       width=140, height=45, corner_radius=22)
        self.project_btn.pack(side='left', padx=(0, 16))
        
        self.open_report_btn = RoundedButton(button_frame, text="📄 Ouvrir Rapport", 
                                           command=self.open_latest_report, 
                                           bg_color=self.colors['blue_500'], width=140, height=45, corner_radius=22)
        self.open_report_btn.pack(side='left', padx=(0, 16))
        
        self.open_folder_btn = RoundedButton(button_frame, text="📂 Ouvrir Dossier", 
                                           command=self.open_audit_folder, 
                                           bg_color=self.colors['blue_500'], width=140, height=45, corner_radius=22)
        self.open_folder_btn.pack(side='left')
        
        # Barre de progression avec design moderne
        self.progress = ttk.Progressbar(actions_frame, mode='indeterminate', 
                                       style='Dark.Horizontal.TProgressbar')
        self.progress.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(16, 0))
    
    def create_logs_section(self, parent):
        """Crée la section des logs extensible avec design épuré."""
        logs_frame = ttk.LabelFrame(parent, text="Logs", 
                                   style='Dark.TLabelframe', padding="12")
        logs_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 12))
        logs_frame.columnconfigure(0, weight=1)
        logs_frame.rowconfigure(0, weight=1)
        parent.rowconfigure(3, weight=1)
        
        # Zone de texte pour les logs avec design moderne et extensible
        self.logs_text = scrolledtext.ScrolledText(
            logs_frame, 
            wrap=tk.WORD, 
            font=('JetBrains Mono', 9),
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
        
        # Boutons pour les logs compacts
        logs_buttons_frame = ttk.Frame(logs_frame, style='Dark.TFrame')
        logs_buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(8, 0))
        
        ttk.Button(logs_buttons_frame, text="Effacer", 
                   command=self.clear_logs, style='Danger.TButton').pack(side=tk.LEFT, padx=(0, 8))
        
        ttk.Button(logs_buttons_frame, text="Copier", 
                   command=self.copy_logs, style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 8))
        
        ttk.Button(logs_buttons_frame, text="Sauvegarder", 
                   command=self.save_logs, style='Primary.TButton').pack(side=tk.LEFT)
    
    def create_recent_projects_section(self, parent):
        """Crée la section des projets récents compacte."""
        recent_frame = ttk.LabelFrame(parent, text="Récents", 
                                     style='Dark.TLabelframe', padding="12")
        recent_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 12))
        recent_frame.columnconfigure(0, weight=1)
        
        # Liste des projets récents compacte
        self.recent_listbox = tk.Listbox(
            recent_frame, 
            height=2,  # Hauteur réduite
            bg=self.colors['bg_700'],
            fg=self.colors['text_100'],
            selectbackground=self.colors['blue_500'],
            selectforeground=self.colors['text_50'],
            relief='flat',
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.colors['border_600'],
            highlightcolor=self.colors['blue_500'],
            font=('Inter', 9)
        )
        self.recent_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 12))
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
            self.open_report_btn.bg_color = self.colors['blue_500']
            self.open_folder_btn.bg_color = self.colors['blue_500']
            self.open_report_btn.draw_button()
            self.open_folder_btn.draw_button()
        else:
            self.project_info_label.config(
                text=f"ℹ️ Nouveau projet - {project_path.name}",
                foreground=self.colors['blue_500']
            )
            
            # Désactiver les boutons
            self.open_report_btn.bg_color = self.colors['text_500']
            self.open_folder_btn.bg_color = self.colors['text_500']
            self.open_report_btn.draw_button()
            self.open_folder_btn.draw_button()
    
    def run_audit(self):
        """Lance l'audit du projet sélectionné."""
        project_path = self.selected_project.get()
        
        if not project_path:
            ModernDialog(self.root, "Attention", "Veuillez sélectionner un projet.", "warning")
            return
        
        if self.project_running:
            ModernDialog(self.root, "Information", "Un audit est déjà en cours.", "info")
            return
        
        # Confirmation avec dialogue moderne
        dialog = ModernDialog(self.root, "Confirmation", 
                             f"Lancer l'audit pour le projet :\n{project_path}", "confirm")
        if not dialog.result:
            return
        
        # Lancer l'audit dans un thread séparé
        self.project_running = True
        # Désactiver le bouton en changeant sa couleur
        self.project_btn.bg_color = self.colors['text_500']
        self.project_btn.draw_button()
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
            
            # Lancer l'audit avec gestion d'encodage robuste
            result = subprocess.run([
                sys.executable, str(self.project_dir / "audit.py"),
                project_path
            ], capture_output=True, text=True, encoding='utf-8', errors='replace')
            
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
        # Réactiver le bouton en restaurant sa couleur
        self.project_btn.bg_color = self.colors['emerald_500']
        self.project_btn.draw_button()
        self.progress.stop()
    
    def ask_open_report(self):
        """Demande si l'utilisateur veut ouvrir le rapport."""
        dialog = ModernDialog(self.root, "Rapport", "L'audit est terminé. Voulez-vous ouvrir le rapport?", "confirm")
        if dialog.result:
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
            ModernDialog(self.root, "Attention", "Aucun rapport HTML trouvé.", "warning")
    
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
                ModernDialog(self.root, "Succès", f"Logs sauvegardés dans {filename}", "success")
            except Exception as e:
                ModernDialog(self.root, "Erreur", f"Erreur lors de la sauvegarde: {e}", "error")
    
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
        dialog = ModernDialog(self.root, "Confirmation", "Effacer tous les projets récents?", "confirm")
        if dialog.result:
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
