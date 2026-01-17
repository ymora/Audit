// Audit complet du projet OTT avec Node.js
const fs = require('fs');
const path = require('path');

// Fonction pour scanner les fichiers récursivement
function scanFiles(dir, extension) {
    let files = [];
    const items = fs.readdirSync(dir);
    
    for (const item of items) {
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory() && !item.startsWith('.') && item !== 'node_modules') {
            files = files.concat(scanFiles(fullPath, extension));
        } else if (stat.isFile() && item.endsWith(extension)) {
            files.push(fullPath);
        }
    }
    
    return files;
}

// Fonction pour compter les fichiers par type
function countFiles() {
    const stats = {
        php: scanFiles('.', '.php').length,
        js: scanFiles('.', '.js').length,
        sql: scanFiles('.', '.sql').length,
        md: scanFiles('.', '.md').length,
        ps1: scanFiles('.', '.ps1').length,
        json: scanFiles('.', '.json').length,
        yml: scanFiles('.', '.yml').length
    };
    
    return stats;
}

// Fonction pour scanner les problèmes dans les fichiers PHP
function scanPhpIssues() {
    const phpFiles = scanFiles('.', '.php');
    const issues = [];
    
    for (const file of phpFiles) {
        try {
            const content = fs.readFileSync(file, 'utf8');
            const relativePath = file.replace(process.cwd() + '\\', '').replace(/\//g, '\\');
            
            // Vérifier echo json_encode avec succès=false
            if (content.match(/echo json_encode.*success.*false.*error/)) {
                issues.push({
                    file: relativePath,
                    type: 'Sécurité',
                    problem: 'echo json_encode avec succès=false détecté'
                });
            }
            
            // Vérifier var_dump/print_r en production
            if (content.match(/var_dump|print_r/) && !content.match(/\/\/.*var_dump/)) {
                issues.push({
                    file: relativePath,
                    type: 'Qualité',
                    problem: 'Code de debug en production détecté'
                });
            }
            
            // Vérifier les requêtes SQL sans prepare
            if (content.match(/\$_GET\[|\$_POST\[/) && !content.match(/prepare|execute/)) {
                issues.push({
                    file: relativePath,
                    type: 'Sécurité',
                    problem: 'Requête SQL sans prepare/execute détectée'
                });
            }
            
        } catch (error) {
            console.log(`Erreur lecture fichier ${file}: ${error.message}`);
        }
    }
    
    return issues;
}

// Fonction pour scanner les problèmes dans les fichiers JS
function scanJsIssues() {
    const jsFiles = scanFiles('.', '.js');
    const issues = [];
    
    for (const file of jsFiles) {
        try {
            const content = fs.readFileSync(file, 'utf8');
            const relativePath = file.replace(process.cwd() + '\\', '').replace(/\//g, '\\');
            
            // Vérifier console.log en production
            if (content.match(/console\.log/) && !content.match(/\/\/.*console\.log/)) {
                issues.push({
                    file: relativePath,
                    type: 'Performance',
                    problem: 'console.log en production détecté'
                });
            }
            
            // Vérifier les variables non utilisées
            if (content.match(/duplicateUser|duplicateDevice|duplicatePatient|noAuthRequest|invalidAuthRequest/)) {
                issues.push({
                    file: relativePath,
                    type: 'Qualité',
                    problem: 'Variables non utilisées détectées'
                });
            }
            
            // Vérifier useEffect sans dépendances
            if (content.match(/useEffect\(\s*\)/) && !content.match(/useEffect\(\s*\[/)) {
                issues.push({
                    file: relativePath,
                    type: 'Performance',
                    problem: 'useEffect sans tableau de dépendances'
                });
            }
            
        } catch (error) {
            console.log(`Erreur lecture fichier ${file}: ${error.message}`);
        }
    }
    
    return issues;
}

// Fonction pour vérifier la configuration
function checkConfiguration() {
    const config = {
        dockerCompose: fs.existsSync('./docker-compose.yml'),
        packageJson: fs.existsSync('./package.json'),
        readme: fs.existsSync('./README.md'),
        jestConfig: fs.existsSync('./jest.config.js'),
        envExample: fs.existsSync('./env.example'),
        nextConfig: fs.existsSync('./next.config.js'),
        tailwindConfig: fs.existsSync('./tailwind.config.js')
    };
    
    return config;
}

// Fonction pour vérifier les tests
function checkTests() {
    const testFiles = scanFiles('.', '.test.js');
    const specFiles = scanFiles('.', '.spec.js');
    
    return {
        unitTests: testFiles.length,
        specTests: specFiles.length,
        total: testFiles.length + specFiles.length
    };
}

// Fonction pour calculer le score
function calculateScore(stats, phpIssues, jsIssues, config, tests) {
    let score = 100;
    
    // Déductions pour les problèmes
    score -= phpIssues.length * 2;
    score -= jsIssues.length * 1;
    
    // Déductions pour les éléments manquants
    if (!config.dockerCompose) score -= 5;
    if (!config.packageJson) score -= 5;
    if (!config.readme) score -= 3;
    if (!config.jestConfig) score -= 3;
    if (tests.total === 0) score -= 5;
    
    return Math.max(0, score);
}

// Audit principal
function runAudit() {
    console.log('🚀 AUDIT COMPLET DU PROJET OTT');
    console.log('================================');
    
    // 1. Structure des fichiers
    console.log('\n📁 STRUCTURE DES FICHIERS');
    const stats = countFiles();
    console.log(`  PHP: ${stats.php}`);
    console.log(`  JS: ${stats.js}`);
    console.log(`  SQL: ${stats.sql}`);
    console.log(`  MD: ${stats.md}`);
    console.log(`  PS1: ${stats.ps1}`);
    console.log(`  JSON: ${stats.json}`);
    console.log(`  YAML: ${stats.yml}`);
    
    // 2. Scan PHP
    console.log('\n🐘 SCAN PHP');
    const phpIssues = scanPhpIssues();
    console.log(`  Problèmes PHP: ${phpIssues.length}`);
    
    if (phpIssues.length > 0) {
        phpIssues.forEach(issue => {
            console.log(`  ${issue.type === 'Sécurité' ? '❌' : '⚠️'} ${issue.file}: ${issue.problem}`);
        });
    }
    
    // 3. Scan JS
    console.log('\n📱 SCAN JS');
    const jsIssues = scanJsIssues();
    console.log(`  Problèmes JS: ${jsIssues.length}`);
    
    if (jsIssues.length > 0) {
        jsIssues.forEach(issue => {
            console.log(`  ${issue.type === 'Sécurité' ? '❌' : '⚠️'} ${issue.file}: ${issue.problem}`);
        });
    }
    
    // 4. Configuration
    console.log('\n⚙️ CONFIGURATION');
    const config = checkConfiguration();
    console.log(`  docker-compose.yml: ${config.dockerCompose ? '✅' : '❌'} ${config.dockerCompose ? 'Trouvé' : 'Non trouvé'}`);
    console.log(`  package.json: ${config.packageJson ? '✅' : '❌'} ${config.packageJson ? 'Trouvé' : 'Non trouvé'}`);
    console.log(`  README.md: ${config.readme ? '✅' : '❌'} ${config.readme ? 'Trouvé' : 'Non trouvé'}`);
    console.log(`  jest.config.js: ${config.jestConfig ? '✅' : '❌'} ${config.jestConfig ? 'Trouvé' : 'Non trouvé'}`);
    console.log(`  env.example: ${config.envExample ? '✅' : '❌'} ${config.envExample ? 'Trouvé' : 'Non trouvé'}`);
    console.log(`  next.config.js: ${config.nextConfig ? '✅' : '❌'} ${config.nextConfig ? 'Trouvé' : 'Non trouvé'}`);
    console.log(`  tailwind.config.js: ${config.tailwindConfig ? '✅' : '❌'} ${config.tailwindConfig ? 'Trouvé' : 'Non trouvé'}`);
    
    // 5. Tests
    console.log('\n🧪 TESTS');
    const tests = checkTests();
    console.log(`  Tests unitaires: ${tests.unitTests}`);
    console.log(`  Tests spec: ${tests.specTests}`);
    console.log(`  Total tests: ${tests.total}`);
    
    // 6. Score final
    console.log('\n📊 SCORE FINAL');
    const score = calculateScore(stats, phpIssues, jsIssues, config, tests);
    console.log(`  Score: ${score}/100`);
    
    // 7. Conclusion
    console.log('\n🎯 CONCLUSION');
    if (score >= 90) {
        console.log('✅ EXCELLENT - Projet en très bon état');
    } else if (score >= 70) {
        console.log('✅ BON - Projet en bon état avec quelques améliorations possibles');
    } else {
        console.log('❌ À AMÉLIORER - Projet nécessite des corrections importantes');
    }
    
    // 8. Recommandations
    console.log('\n🚀 RECOMMANDATIONS PRIORITAIRES');
    
    if (phpIssues.length > 0) {
        console.log('1. 🔒 Corriger les problèmes de sécurité PHP');
        phpIssues.filter(i => i.type === 'Sécurité').forEach(issue => {
            console.log(`   - ${issue.file}: ${issue.problem}`);
        });
    }
    
    if (jsIssues.length > 0) {
        console.log('2. ⚡ Optimiser les performances JavaScript');
        jsIssues.filter(i => i.type === 'Performance').forEach(issue => {
            console.log(`   - ${issue.file}: ${issue.problem}`);
        });
    }
    
    if (tests.total === 0) {
        console.log('3. 🧪 Implémenter les tests unitaires et d\'intégration');
    }
    
    if (!config.jestConfig) {
        console.log('4. 📚 Configurer Jest pour les tests');
    }
    
    if (!config.readme) {
        console.log('5. 📚 Créer un README.md');
    }
    
    console.log('\n🎉 AUDIT TERMINÉ');
    
    return {
        stats,
        phpIssues,
        jsIssues,
        config,
        tests,
        score
    };
}

// Lancer l'audit
runAudit();
