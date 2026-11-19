import logging
import os

from flask import Flask, jsonify, render_template, request

from app.modelo import RANGOS, predecir, validar
from app.registro import estadisticas, registrar

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("servicio")

app = Flask(__name__)
app.json.ensure_ascii = False
app.config["REGISTRO"] = os.environ.get("REGISTRO_PREDICCIONES", "datos/predicciones.jsonl")


@app.get("/salud")
def salud():
    return jsonify(estado="ok")


@app.route("/", methods=["GET", "POST"])
def formulario():
    resultado, error, valores = None, None, {}
    if request.method == "POST":
        valores = request.form.to_dict()
        try:
            entradas = validar(valores)
            resultado = predecir(**entradas)
            registrar(app.config["REGISTRO"], resultado, entradas)
        except ValueError as exc:
            error = str(exc)
    return render_template("index.html", rangos=RANGOS, valores=valores, resultado=resultado, error=error)


@app.post("/predecir")
def api_predecir():
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return jsonify(error="El cuerpo debe ser un objeto JSON."), 400
    try:
        entradas = validar(datos)
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    pred = predecir(**entradas)
    registrar(app.config["REGISTRO"], pred, entradas)
    log.info("prediccion estado=%s puntaje=%s", pred.estado, pred.puntaje)
    return jsonify(estado=pred.estado, puntaje_severidad=pred.puntaje, entradas=entradas)


@app.get("/estadisticas")
def api_estadisticas():
    return jsonify(estadisticas(app.config["REGISTRO"]))
