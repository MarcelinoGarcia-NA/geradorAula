from flask import Flask, request, render_template
from Gerador import gerar_plano
import json
import os

app = Flask(__name__)

os.makedirs("resultados", exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/gerar", methods=["POST"])
def gerar():
    dados = {
        "disciplina": request.form["disciplina"],
        "curso": request.form["curso"],
        "carga": request.form["carga"],
        "qtd_aulas": request.form["qtd_aulas"],
        "duracao": request.form["duracao"],
        "ementa": request.form["ementa"],
        "objetivo": request.form["objetivo"]
    }

    plano = gerar_plano(dados)

    return render_template("resultado.html", plano=plano)

@app.route("/avaliar", methods=["POST"])
def avaliar():
    registro = {
        "plano": request.form["plano"],
        "nota": request.form["nota"],
        "comentario": request.form["comentario"]
    }

    with open("resultados/dados.json", "a") as f:
        f.write(json.dumps(registro) + "\\n")

    return "Avaliação salva com sucesso!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
