#!/usr/bin/env python3
"""
Script d'audit du code cy8_workspace
Détecte les fonctions fantômes, doublons, et problèmes potentiels
"""
import os
import ast
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple


class CodeAuditor:
    """Auditeur de code pour détecter les problèmes"""

    def __init__(self, src_dir: str = "src"):
        self.src_dir = Path(src_dir)
        self.functions = defaultdict(list)  # fonction -> [(fichier, ligne)]
        self.classes = defaultdict(list)  # classe -> [(fichier, ligne)]
        self.imports = defaultdict(set)  # fichier -> set(imports)
        self.function_calls = defaultdict(set)  # fonction -> set(fichiers_appelants)
        self.file_info = {}  # fichier -> info
        
    def analyze_file(self, filepath: Path):
        """Analyser un fichier Python"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content, filename=str(filepath))
                
            # Utiliser un chemin relatif simple
            try:
                relative_path = filepath.relative_to(Path.cwd())
            except ValueError:
                # Si ça échoue, utiliser juste le nom du fichier avec src/
                relative_path = Path("src") / filepath.name
            
            # Informations du fichier
            self.file_info[str(relative_path)] = {
                'lines': len(content.splitlines()),
                'functions': [],
                'classes': [],
                'imports': []
            }
            
            # Analyser l'arbre AST
            for node in ast.walk(tree):
                # Fonctions
                if isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    self.functions[func_name].append((str(relative_path), node.lineno))
                    self.file_info[str(relative_path)]['functions'].append({
                        'name': func_name,
                        'line': node.lineno,
                        'is_private': func_name.startswith('_'),
                        'is_dunder': func_name.startswith('__') and func_name.endswith('__')
                    })
                
                # Classes
                elif isinstance(node, ast.ClassDef):
                    class_name = node.name
                    self.classes[class_name].append((str(relative_path), node.lineno))
                    self.file_info[str(relative_path)]['classes'].append({
                        'name': class_name,
                        'line': node.lineno
                    })
                
                # Imports
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        import_name = alias.name
                        self.imports[str(relative_path)].add(import_name)
                        self.file_info[str(relative_path)]['imports'].append(import_name)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.imports[str(relative_path)].add(node.module)
                        self.file_info[str(relative_path)]['imports'].append(node.module)
                
                # Appels de fonction
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        func_name = node.func.id
                        self.function_calls[func_name].add(str(relative_path))
                    elif isinstance(node.func, ast.Attribute):
                        func_name = node.func.attr
                        self.function_calls[func_name].add(str(relative_path))
                        
        except Exception as e:
            print(f"❌ Erreur lors de l'analyse de {filepath}: {e}")
    
    def scan_directory(self):
        """Scanner tous les fichiers Python"""
        print(f"🔍 Scan du répertoire: {self.src_dir}")
        py_files = list(self.src_dir.rglob("*.py"))
        print(f"📁 {len(py_files)} fichiers Python trouvés\n")
        
        for filepath in py_files:
            print(f"   Analyse: {filepath.name}")
            self.analyze_file(filepath)
    
    def find_duplicate_functions(self) -> Dict[str, List[Tuple[str, int]]]:
        """Trouver les fonctions en doublon"""
        duplicates = {}
        for func_name, locations in self.functions.items():
            if len(locations) > 1:
                # Filtrer les méthodes de classe (probablement légitimes)
                if not func_name.startswith('__'):
                    duplicates[func_name] = locations
        return duplicates
    
    def find_orphan_functions(self) -> Dict[str, List[Tuple[str, int]]]:
        """Trouver les fonctions jamais appelées (potentiellement fantômes)"""
        orphans = {}
        for func_name, locations in self.functions.items():
            # Ignorer les fonctions spéciales et privées
            if func_name.startswith('__') or func_name in ['main', 'run', 'setup']:
                continue
            
            # Vérifier si la fonction est appelée
            if func_name not in self.function_calls:
                orphans[func_name] = locations
            else:
                # Vérifier si elle est appelée ailleurs que dans son propre fichier
                defining_files = {loc[0] for loc in locations}
                calling_files = self.function_calls[func_name]
                if calling_files.issubset(defining_files):
                    # Seulement appelée dans son propre fichier
                    orphans[func_name] = locations
        
        return orphans
    
    def find_duplicate_classes(self) -> Dict[str, List[Tuple[str, int]]]:
        """Trouver les classes en doublon"""
        duplicates = {}
        for class_name, locations in self.classes.items():
            if len(locations) > 1:
                duplicates[class_name] = locations
        return duplicates
    
    def get_statistics(self) -> Dict:
        """Obtenir les statistiques globales"""
        total_lines = sum(info['lines'] for info in self.file_info.values())
        total_functions = sum(len(info['functions']) for info in self.file_info.values())
        total_classes = sum(len(info['classes']) for info in self.file_info.values())
        
        return {
            'total_files': len(self.file_info),
            'total_lines': total_lines,
            'total_functions': total_functions,
            'total_classes': total_classes,
            'unique_function_names': len(self.functions),
            'unique_class_names': len(self.classes)
        }
    
    def generate_report(self) -> str:
        """Générer un rapport complet"""
        report = []
        report.append("# 🔍 RAPPORT D'AUDIT DU CODE - cy8_workspace")
        report.append("=" * 70)
        report.append("")
        
        # Statistiques
        stats = self.get_statistics()
        report.append("## 📊 STATISTIQUES GLOBALES")
        report.append("-" * 70)
        report.append(f"📁 Fichiers Python: {stats['total_files']}")
        report.append(f"📝 Lignes de code totales: {stats['total_lines']:,}")
        report.append(f"⚙️  Fonctions totales: {stats['total_functions']}")
        report.append(f"🏗️  Classes totales: {stats['total_classes']}")
        report.append(f"🔤 Noms de fonctions uniques: {stats['unique_function_names']}")
        report.append(f"🔤 Noms de classes uniques: {stats['unique_class_names']}")
        report.append("")
        
        # Fonctions en doublon
        duplicates = self.find_duplicate_functions()
        report.append("## 🔄 FONCTIONS EN DOUBLON")
        report.append("-" * 70)
        if duplicates:
            report.append(f"⚠️  {len(duplicates)} fonctions définies plusieurs fois:")
            report.append("")
            for func_name, locations in sorted(duplicates.items()):
                report.append(f"### `{func_name}` ({len(locations)} définitions)")
                for filepath, lineno in locations:
                    report.append(f"   - {filepath}:{lineno}")
                report.append("")
        else:
            report.append("✅ Aucune fonction en doublon détectée")
        report.append("")
        
        # Classes en doublon
        class_duplicates = self.find_duplicate_classes()
        report.append("## 🔄 CLASSES EN DOUBLON")
        report.append("-" * 70)
        if class_duplicates:
            report.append(f"⚠️  {len(class_duplicates)} classes définies plusieurs fois:")
            report.append("")
            for class_name, locations in sorted(class_duplicates.items()):
                report.append(f"### `{class_name}` ({len(locations)} définitions)")
                for filepath, lineno in locations:
                    report.append(f"   - {filepath}:{lineno}")
                report.append("")
        else:
            report.append("✅ Aucune classe en doublon détectée")
        report.append("")
        
        # Fonctions orphelines (fantômes)
        orphans = self.find_orphan_functions()
        report.append("## 👻 FONCTIONS ORPHELINES (POTENTIELLEMENT FANTÔMES)")
        report.append("-" * 70)
        if orphans:
            report.append(f"⚠️  {len(orphans)} fonctions jamais appelées (ou seulement en interne):")
            report.append("")
            
            # Grouper par fichier
            by_file = defaultdict(list)
            for func_name, locations in orphans.items():
                for filepath, lineno in locations:
                    by_file[filepath].append((func_name, lineno))
            
            for filepath in sorted(by_file.keys()):
                report.append(f"### {filepath}")
                for func_name, lineno in sorted(by_file[filepath], key=lambda x: x[1]):
                    report.append(f"   - `{func_name}` (ligne {lineno})")
                report.append("")
        else:
            report.append("✅ Toutes les fonctions sont utilisées")
        report.append("")
        
        # Détail par fichier
        report.append("## 📁 DÉTAIL PAR FICHIER")
        report.append("-" * 70)
        for filepath in sorted(self.file_info.keys()):
            info = self.file_info[filepath]
            report.append(f"### {filepath}")
            report.append(f"   📝 Lignes: {info['lines']}")
            report.append(f"   ⚙️  Fonctions: {len(info['functions'])}")
            report.append(f"   🏗️  Classes: {len(info['classes'])}")
            report.append(f"   📦 Imports: {len(info['imports'])}")
            
            # Lister les fonctions publiques
            public_funcs = [f for f in info['functions'] if not f['is_private'] and not f['is_dunder']]
            if public_funcs:
                report.append(f"   🔓 Fonctions publiques: {', '.join(f['name'] for f in public_funcs[:10])}")
                if len(public_funcs) > 10:
                    report.append(f"      ... et {len(public_funcs) - 10} autres")
            report.append("")
        
        return "\n".join(report)


def main():
    """Point d'entrée principal"""
    print("🚀 AUDIT DU CODE cy8_workspace")
    print("=" * 70)
    print()
    
    auditor = CodeAuditor("src")
    auditor.scan_directory()
    
    print("\n" + "=" * 70)
    print("📝 Génération du rapport...")
    
    report = auditor.generate_report()
    
    # Sauvegarder le rapport
    report_path = Path("docs/CODE_AUDIT_REPORT.md")
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Rapport sauvegardé: {report_path}")
    print()
    
    # Afficher le rapport
    print(report)
    
    # Sauvegarder les données JSON pour analyse ultérieure
    json_path = Path("docs/code_audit_data.json")
    audit_data = {
        'statistics': auditor.get_statistics(),
        'duplicates': {k: v for k, v in auditor.find_duplicate_functions().items()},
        'class_duplicates': {k: v for k, v in auditor.find_duplicate_classes().items()},
        'orphans': {k: v for k, v in auditor.find_orphan_functions().items()},
        'files': auditor.file_info
    }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(audit_data, f, indent=2, ensure_ascii=False)
    
    print(f"📊 Données JSON sauvegardées: {json_path}")
    print()
    print("=" * 70)
    print("✅ AUDIT TERMINÉ")


if __name__ == "__main__":
    main()
