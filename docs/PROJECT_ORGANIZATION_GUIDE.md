# GUIDE D'ORGANISATION DES PROJETS
Date: 2025-08-19 11:44:30

## Structure claire recommandée pour chaque projet

```
projet_exemple/
├── config.json              # Configuration du projet
├── src/                     # Code source du projet
├── tests/                   # Tests du projet (fonctionnels, unitaires)
│   └── README.md           # Documentation des tests
├── logs/                    # Logs du programme en cours d'exécution
│   └── README.md           # Documentation des logs
├── reports/                 # Rapports générés par le programme
│   └── README.md           # Documentation des rapports
├── docs/                    # Documentation du projet
└── .audit/                  # Dossier d'audit (caché)
    ├── README.md           # Documentation de l'audit
    ├── config/              # Configuration spécifique à l'audit
    ├── logs/                # Logs des sessions d'audit
    ├── reports/             # Rapports d'audit générés
    └── tests/               # Tests spécifiques à l'audit (optionnel)
```

## Distinctions importantes

### 📝 Logs
- **logs/** : Logs du programme en cours d'exécution
- **.audit/logs/** : Logs des sessions d'audit

### 📋 Rapports
- **reports/** : Rapports générés par le programme
- **.audit/reports/** : Rapports d'audit générés

### 🧪 Tests
- **tests/** : Tests du projet (fonctionnels, unitaires)
- **.audit/tests/** : Tests spécifiques à l'audit (optionnel)

## Avantages

1. **Clarté** : Pas de confusion possible
2. **Simplicité** : Structure prévisible
3. **Documentation** : README explicatifs dans chaque dossier
4. **Séparation** : Programme et audit bien distincts
5. **Maintenabilité** : Organisation logique et cohérente

## Utilisation

- **Développement** : Utiliser les dossiers à la racine
- **Audit** : Utiliser le dossier .audit/
- **Documentation** : Consulter les README.md dans chaque dossier
