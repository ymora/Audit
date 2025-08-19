# AUDITS SPÉCIFIQUES PAR PROJET

Ce répertoire contient les tests et configurations spécifiques à chaque projet audité.

## Structure

```
project_audits/
├── projet_a/              # Tests spécifiques au projet A
│   ├── custom_tests.py    # Tests personnalisés
│   ├── config.json        # Configuration spécifique
│   └── README.md          # Documentation du projet
├── projet_b/              # Tests spécifiques au projet B
│   ├── custom_tests.py
│   ├── config.json
│   └── README.md
└── README.md              # Ce fichier
```

## Fonctionnement

1. **Détection automatique** : Le système d'audit détecte automatiquement le type de projet
2. **Création des tests** : Les tests spécifiques sont créés automatiquement ici
3. **Configuration** : Chaque projet peut avoir sa propre configuration d'audit
4. **Rapports** : Les rapports sont générés dans `projects/nom_du_projet/`

## Avantages

- ✅ **Projets propres** : Pas de pollution des projets audités
- ✅ **Centralisation** : Tous les tests d'audit au même endroit
- ✅ **Flexibilité** : Tests personnalisés par projet
- ✅ **Maintenance** : Gestion unifiée des audits

## Utilisation

```bash
# Auditer un projet (les tests spécifiques sont créés automatiquement)
python audit.py --cli C:\Users\ymora\Desktop\mon_projet

# Les tests spécifiques apparaissent dans :
# project_audits/mon_projet/
```

---

*Géré automatiquement par le système d'audit universel*
