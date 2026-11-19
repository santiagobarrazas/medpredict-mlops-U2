# medpredict-mlops-U2

## Problema

Un médico necesita estimar el estado de salud de un paciente a partir de unos pocos datos clínicos (temperatura, frecuencia cardíaca, intensidad del dolor y días con síntomas). En la unidad 1 se construyó un servicio local en Docker con un modelo simulado que devuelve el estado estimado del paciente.

## Propósito

Mantener ese servicio bajo control de versiones en GitHub y llevar los cambios a `main` mediante ramas y pull requests. Sobre esta base se agregan nuevos requerimientos de los médicos y un pipeline de CI/CD con GitHub Actions.

## Estructura

| Ruta | Contenido |
|---|---|
| `app/` | Servicio Flask con el modelo simulado y el formulario web |
| `tests/` | Pruebas unitarias con pytest |
| `Dockerfile` | Imagen del servicio |
| `.github/workflows/` | Pipeline de CI/CD |

## Flujo de trabajo

1. `solución-inicial`: archivos de la unidad 1.
2. Ramas de nuevos requerimientos: nueva categoría de predicción y reporte de estadísticas.
3. `añadir-github-actions`: pipeline de CI/CD.

Cada rama entra a `main` con un pull request.
