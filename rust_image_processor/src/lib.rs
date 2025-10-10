use pyo3::prelude::*;
use pyo3::types::PyBytes;
use std::io::Cursor;

/// Créer une miniature d'image en Rust (beaucoup plus rapide que PIL)
#[pyfunction]
fn create_thumbnail_fast(py: Python, image_path: &str, width: u32, height: u32) -> PyResult<PyObject> {
    match image::open(image_path) {
        Ok(img) => {
            // Redimensionner avec un algorithme rapide
            let thumbnail = img.thumbnail(width, height);

            // Convertir en PNG bytes
            let mut buffer = Vec::new();
            let mut cursor = Cursor::new(&mut buffer);

            match thumbnail.write_to(&mut cursor, image::ImageOutputFormat::Png) {
                Ok(_) => Ok(PyBytes::new(py, &buffer).into()),
                Err(e) => Err(PyErr::new::<pyo3::exceptions::PyIOError, _>(
                    format!("Erreur conversion PNG: {}", e)
                ))
            }
        },
        Err(e) => Err(PyErr::new::<pyo3::exceptions::PyIOError, _>(
            format!("Erreur ouverture image: {}", e)
        ))
    }
}

/// Obtenir les dimensions d'une image rapidement
#[pyfunction]
fn get_image_dimensions(image_path: &str) -> PyResult<(u32, u32)> {
    match image::io::Reader::open(image_path) {
        Ok(reader) => {
            match reader.into_dimensions() {
                Ok((width, height)) => Ok((width, height)),
                Err(e) => Err(PyErr::new::<pyo3::exceptions::PyIOError, _>(
                    format!("Erreur lecture dimensions: {}", e)
                ))
            }
        },
        Err(e) => Err(PyErr::new::<pyo3::exceptions::PyIOError, _>(
            format!("Erreur ouverture fichier: {}", e)
        ))
    }
}

/// Calculer le hash d'une image rapidement
#[pyfunction]
fn calculate_image_hash(image_path: &str) -> PyResult<String> {
    use std::collections::hash_map::DefaultHasher;
    use std::hash::{Hash, Hasher};
    use std::fs;

    match fs::read(image_path) {
        Ok(data) => {
            let mut hasher = DefaultHasher::new();
            data.hash(&mut hasher);
            Ok(format!("{:x}", hasher.finish()))
        },
        Err(e) => Err(PyErr::new::<pyo3::exceptions::PyIOError, _>(
            format!("Erreur lecture fichier: {}", e)
        ))
    }
}

/// Module Python
#[pymodule]
fn rust_image_processor(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(create_thumbnail_fast, m)?)?;
    m.add_function(wrap_pyfunction!(get_image_dimensions, m)?)?;
    m.add_function(wrap_pyfunction!(calculate_image_hash, m)?)?;
    Ok(())
}
