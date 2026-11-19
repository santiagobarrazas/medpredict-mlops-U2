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

## Servicio de predicción de enfermedades

Servicio web donde un médico ingresa los datos de un paciente y obtiene uno de cinco estados: `NO ENFERMO`, `ENFERMEDAD LEVE`, `ENFERMEDAD AGUDA`, `ENFERMEDAD CRÓNICA` o `ENFERMEDAD TERMINAL`.

El modelo está simulado con reglas en `app/modelo.py`. Se puede usar desde un formulario web o con la API en `POST /predecir`. Cada predicción queda registrada y `GET /estadisticas` devuelve un reporte con esos registros.

### Entradas

| Campo | Descripción | Rango |
|---|---|---|
| `temperatura` | Temperatura en °C | 34 a 43 |
| `frecuencia_cardiaca` | Latidos por minuto | 30 a 220 |
| `dolor` | Intensidad del dolor | 0 a 10 |
| `dias_sintomas` | Días con síntomas | 0 a 3650 |

### Reglas

Se calcula un puntaje de severidad:

- Temperatura: 1 punto desde 37.5, 2 desde 38 y 3 desde 39.
- Frecuencia cardíaca: 1 punto sobre 100 y 2 sobre 120.
- Dolor: 1 punto desde 1, 2 desde 4 y 3 desde 7.

Con puntaje 0 el estado es `NO ENFERMO`. Si no, 90 días o más de síntomas con puntaje de 7 o más da `ENFERMEDAD TERMINAL`, 90 días o más con un puntaje menor da `ENFERMEDAD CRÓNICA`, un puntaje de 5 o más da `ENFERMEDAD AGUDA` y el resto da `ENFERMEDAD LEVE`.

### Construir la imagen

Desde la raíz del repositorio:

```bash
docker build -t prediccion-enfermedades:1.0 .
```

### Correr el contenedor

```bash
docker run -d --name prediccion -p 5000:5000 prediccion-enfermedades:1.0
```

Si el puerto 5000 está ocupado, cambie el primer número, por ejemplo `-p 8080:5000`.

Las predicciones se guardan en `/servicio/datos/predicciones.jsonl` dentro del contenedor. Para conservarlas aunque se borre el contenedor, monte un volumen:

```bash
docker run -d --name prediccion -p 5000:5000 -v prediccion-datos:/servicio/datos prediccion-enfermedades:1.0
```

### Obtener una predicción

En el navegador, abra <http://localhost:5000/>, llene los campos y presione Predecir.

Con la API:

```bash
curl -X POST http://localhost:5000/predecir -H "Content-Type: application/json" -d '{"temperatura": 39.5, "frecuencia_cardiaca": 125, "dolor": 8, "dias_sintomas": 3}'
```

Respuesta:

```json
{"entradas": {"dias_sintomas": 3.0, "dolor": 8.0, "frecuencia_cardiaca": 125.0, "temperatura": 39.5}, "estado": "ENFERMEDAD AGUDA", "puntaje_severidad": 8}
```

Si falta un campo o un valor está fuera de rango, responde 400 con el error.

Valores de ejemplo para cada estado:

| temperatura | frecuencia_cardiaca | dolor | dias_sintomas | Estado |
|---|---|---|---|---|
| 36.6 | 75 | 0 | 0 | NO ENFERMO |
| 37.8 | 85 | 3 | 2 | ENFERMEDAD LEVE |
| 39.5 | 125 | 8 | 3 | ENFERMEDAD AGUDA |
| 37.0 | 80 | 5 | 180 | ENFERMEDAD CRÓNICA |
| 39.5 | 125 | 8 | 200 | ENFERMEDAD TERMINAL |

### Estadísticas de predicciones

En el navegador, abra <http://localhost:5000/estadisticas> o use el enlace debajo del formulario. Con la API:

```bash
curl http://localhost:5000/estadisticas
```

Respuesta:

```json
{
  "fecha_ultima_prediccion": "2026-11-19T21:29:15",
  "total_por_categoria": {"ENFERMEDAD AGUDA": 1, "ENFERMEDAD CRÓNICA": 0, "ENFERMEDAD LEVE": 0, "ENFERMEDAD TERMINAL": 0, "NO ENFERMO": 0},
  "total_predicciones": 1,
  "ultimas_predicciones": [
    {"entradas": {"dias_sintomas": 3.0, "dolor": 8.0, "frecuencia_cardiaca": 125.0, "temperatura": 39.5}, "estado": "ENFERMEDAD AGUDA", "fecha": "2026-11-19T21:29:15", "puntaje_severidad": 8}
  ]
}
```

- `total_por_categoria`: número de predicciones de cada estado.
- `ultimas_predicciones`: las 5 más recientes, de la más nueva a la más antigua.
- `fecha_ultima_prediccion`: fecha y hora (UTC dentro del contenedor) de la última predicción, o `null` si no hay ninguna.

### Detener el contenedor

```bash
docker rm -f prediccion
```

### Pruebas

```bash
pip install -r requirements-dev.txt
python -m pytest
```
