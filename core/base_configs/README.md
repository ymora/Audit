# ⚙️ Configurations de Base

## 📋 Configurations disponibles

### Configuration générique
- **`generic_config.json`** - Configuration par défaut pour tous projets

## 🎯 Utilisation

```bash
# Utiliser la configuration générique
python ../engines/configurable_audit.py ../base_configs/generic_config.json
```

## 📧 Adapter pour un nouveau projet

1. Copier `generic_config.json`
2. Renommer selon le projet
3. Modifier les paramètres :
   - `project_name`
   - `paths.root`
   - `project_type`
   - Seuils de qualité
   - Exclusions spécifiques

## 🔧 Paramètres clés

### Chemins
```json
"paths": {
  "root": ".",
  "backend": "src",
  "frontend": "frontend"
}
```

### Seuils
```json
"quality_thresholds": {
  "max_file_size_mb": 2,
  "max_lines_per_file": 500,
  "min_test_coverage": 80
}
```
