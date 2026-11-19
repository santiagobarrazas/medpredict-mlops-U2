import json
from datetime import datetime
from pathlib import Path

from app.modelo import AGUDA, CRONICA, LEVE, NO_ENFERMO, TERMINAL, Prediccion

ESTADOS = (NO_ENFERMO, LEVE, AGUDA, CRONICA, TERMINAL)
ULTIMAS = 5


def registrar(ruta: str, pred: Prediccion, entradas: dict) -> None:
    archivo = Path(ruta)
    archivo.parent.mkdir(parents=True, exist_ok=True)
    fila = {
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "estado": pred.estado,
        "puntaje_severidad": pred.puntaje,
        "entradas": entradas,
    }
    with archivo.open("a", encoding="utf-8") as f:
        f.write(json.dumps(fila, ensure_ascii=False) + "\n")


def _leer(ruta: str) -> list[dict]:
    archivo = Path(ruta)
    if not archivo.exists():
        return []
    with archivo.open(encoding="utf-8") as f:
        return [json.loads(linea) for linea in f if linea.strip()]


def estadisticas(ruta: str) -> dict:
    filas = _leer(ruta)
    totales = {estado: 0 for estado in ESTADOS}
    for fila in filas:
        totales[fila["estado"]] = totales.get(fila["estado"], 0) + 1
    return {
        "total_predicciones": len(filas),
        "total_por_categoria": totales,
        "ultimas_predicciones": filas[-ULTIMAS:][::-1],
        "fecha_ultima_prediccion": filas[-1]["fecha"] if filas else None,
    }
