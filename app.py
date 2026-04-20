from flask import Flask, request, render_template, Response
from Gerador import gerar_plano_stream
import json
import os
import PyPDF2

app = Flask(__name__)

os.makedirs("resultados", exist_ok=True)

def extrair_texto_pdf(arquivo):
    texto = ""
    try:
        leitor = PyPDF2.PdfReader(arquivo)
        for pagina in leitor.pages:
            texto += pagina.extract_text() or ""
    except Exception as e:
        texto = f"Erro ao ler PDF: {e}"
    return texto


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

    ia = request.form.get("ia", "gpt")
    quantidade = int(request.form.get("quantidade", 1))

    arquivo = request.files.get("arquivo")
    texto_arquivo = ""

    if arquivo and arquivo.filename != "":
        texto_arquivo = extrair_texto_pdf(arquivo)

    dados["texto_arquivo"] = texto_arquivo

    def stream():
        for chunk in gerar_plano_stream(dados, quantidade, ia):
            yield chunk

    return Response(stream(), content_type='text/plain')


@app.route("/avaliar", methods=["POST"])
def avaliar():
    registro = {
        "plano": request.form["plano"],
        "nota": request.form["nota"],
        "comentario": request.form["comentario"]
    }

    with open("resultados/dados.json", "a") as f:
        f.write(json.dumps(registro) + "\n")

    return "Avaliação salva com sucesso!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
