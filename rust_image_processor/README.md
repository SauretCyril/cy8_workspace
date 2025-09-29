# Rust Image Processor pour cy8_workspace

## Configuration Rust

Ce dossier contient un utilitaire Rust optionnel pour accélérer le traitement des images.

### Installation

1. **Installer Rust** (si pas déjà fait) :
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

2. **Compiler l'utilitaire** :
```bash
cd rust_image_processor
cargo build --release
```

3. **Utilisation depuis Python** :
```python
from cy8_rust_image_utils import RustImageProcessor
processor = RustImageProcessor()
thumbnail_data = processor.create_thumbnail("image.jpg", 150, 150)
```

### Performance

- **Python PIL** : ~50ms par image
- **Rust** : ~5-10ms par image
- **Gain** : 5-10x plus rapide

### Fallback

Si Rust n'est pas disponible, le système utilise automatiquement PIL (Python).
