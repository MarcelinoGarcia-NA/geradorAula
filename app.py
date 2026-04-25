from flask import Flask, request, render_template, Response, jsonify
from Gerador import gerar_plano_stream
import os, json, PyPDF2
from pdf_generator import gerar_pdf

app = Flask(__name__)
os.makedirs("cache", exist_ok=True)


# =========================
# 📄 EXTRAÇÃO PDF (MELHORADA)
# =========================
def extrair_texto_pdf(arquivo):
    texto = ""

    try:
        leitor = PyPDF2.PdfReader(arquivo)

        for pagina in leitor.pages:
            texto += (pagina.extract_text() or "") + "\n"

    except Exception as e:
        texto = f"Erro ao ler PDF: {e}"

    return texto


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/gerar", methods=["POST"])
def gerar():

    dados = {
        "disciplina": request.form.get("disciplina", ""),
        "curso": request.form.get("curso", ""),
        "carga": request.form.get("carga", ""),
        "objetivo": request.form.get("objetivo", "")
    }

    topico = request.form.get("topico", "")
    ia = request.form.get("ia", "gpt")

    cache_path = f"cache/{ia}_{topico.replace(' ', '_')}.json"

    # =========================
    # 🔥 CACHE
    # =========================
    if os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as f:
            data = json.load(f)

        def stream_cache():
            yield "[CACHE]\n\n"
            yield data["plano"]

        return Response(stream_cache(), mimetype="text/plain")

    # =========================
    # 📄 PDF
    # =========================
    arquivo = request.files.get("arquivo")
    texto_pdf = ""

    if arquivo and arquivo.filename:
        texto_pdf = extrair_texto_pdf(arquivo)

    # =========================
    # 🚀 STREAM
    # =========================
    def stream():
        buffer = ""

        for chunk in gerar_plano_stream(dados, topico, ia, texto_pdf):
            buffer += chunk
            yield chunk

        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump({
                "topico": topico,
                "ia": ia,
                "plano": buffer
            }, f, ensure_ascii=False, indent=2)

    return Response(stream(), mimetype="text/plain")


@app.route("/topicos")
def topicos():
    ia = request.args.get("ia", "gpt")

    lista = []

    for t in [
        "Variáveis e tipos de dados",
        "Estruturas condicionais",
        "Estruturas de repetição"
    ]:
        path = f"cache/{ia}_{t.replace(' ', '_')}.json"

        lista.append({
            "topico": t,
            "cache_existe": os.path.exists(path)
        })

    return jsonify(lista)
    
if __name__ == "__main__":
    app.run(debug=True)
