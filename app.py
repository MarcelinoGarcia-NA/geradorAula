from flask import Flask, request, render_template, Response, jsonify
from Gerador import gerar_plano_stream
import os, json, PyPDF2, requests as http_requests

app = Flask(__name__)
os.makedirs("cache", exist_ok=True)

# =========================
# 📄 PDF DO SERVIDOR
# =========================
PDF_PATH = os.environ.get("PDF_PATH", "material_referencia.pdf")

def extrair_texto_pdf_servidor():
    if not os.path.exists(PDF_PATH):
        return ""
    try:
        with open(PDF_PATH, "rb") as f:
            leitor = PyPDF2.PdfReader(f)
            texto = ""
            for pagina in leitor.pages:
                texto += (pagina.extract_text() or "") + "\n"
        return texto
    except Exception as e:
        return ""

TEXTO_PDF_SERVIDOR = extrair_texto_pdf_servidor()

# =========================
# 🔬 SEQUÊNCIA IMUTÁVEL
# =========================
SEQUENCIA = [
    {"etapa": 1, "ia": "gpt",    "topico": "Variáveis e tipos de dados"},
    {"etapa": 2, "ia": "gpt",    "topico": "Estruturas condicionais"},
    {"etapa": 3, "ia": "gpt",    "topico": "Estruturas de repetição"},
    {"etapa": 4, "ia": "claude", "topico": "Variáveis e tipos de dados"},
    {"etapa": 5, "ia": "claude", "topico": "Estruturas condicionais"},
    {"etapa": 6, "ia": "claude", "topico": "Estruturas de repetição"},
]

# =========================
# 📊 GOOGLE SHEETS
# =========================
SHEETS_URL = os.environ.get(
    "SHEETS_URL",
    "https://script.google.com/macros/s/AKfycbyD837s9-FLPbX5uLJF8Dg7wTea3qnpnm82NcT-2F4I9cZb0KUOLLNDU6_tdsTz2MEq/exec"
)

def enviar_para_sheets(payload):
    try:
        resp = http_requests.post(SHEETS_URL, json=payload, timeout=15)
        return True
    except Exception as e:
        return False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/sequencia")
def sequencia():
    """Frontend busca a sequência e confirma que o servidor está online."""
    return jsonify({"sequencia": SEQUENCIA, "nome_pdf": os.path.basename(PDF_PATH)})


# =========================
# 🚀 GERAR — recebe etapa pelo frontend, valida no backend
# =========================
@app.route("/gerar", methods=["POST"])
def gerar():
    body = request.get_json(force=True, silent=True) or {}
    etapa_num = body.get("etapa")

    # Valida que a etapa é da sequência
    seq_item = next((s for s in SEQUENCIA if s["etapa"] == etapa_num), None)
    if not seq_item:
        return jsonify({"erro": f"Etapa inválida: {etapa_num}"}), 400

    ia     = seq_item["ia"]
    topico = seq_item["topico"]

    dados = {
        "disciplina": "Algoritmos e Lógica de Programação",
        "curso":      "Ciência da Computação",
        "carga":      "60h",
        "objetivo":   "Introduzir conceitos básicos de programação para iniciantes.",
        "ementa":     "Variáveis, tipos de dados, estruturas condicionais e repetição."
    }

    cache_path = f"cache/{ia}_{topico.replace(' ', '_')}.json"

    if os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as f:
            cached = json.load(f)

        def stream_cache():
            yield "[CACHE]\n\n"
            yield cached["plano"]

        return Response(stream_cache(), mimetype="text/plain")

    def stream():
        buffer = ""
        for chunk in gerar_plano_stream(dados, topico, ia, TEXTO_PDF_SERVIDOR):
            buffer += chunk
            yield chunk
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump({"topico": topico, "ia": ia, "plano": buffer},
                      f, ensure_ascii=False, indent=2)

    return Response(stream(), mimetype="text/plain")


# =========================
# 📊 AVANCAR — salva avaliação, sem sessão
# =========================
@app.route("/experimento/avancar", methods=["POST"])
def avancar_etapa():
    try:
        body = request.get_json(force=True, silent=True) or {}

        etapa_num   = body.get("etapa")
        avaliador   = body.get("avaliador", {})
        avaliacao   = body.get("avaliacao", {})
        plano_texto = body.get("planoTexto", "")
        nome_pdf    = body.get("nomePDF", os.path.basename(PDF_PATH))

        if not etapa_num:
            return jsonify({"erro": "Campo 'etapa' obrigatório."}), 400
        if not avaliacao:
            return jsonify({"erro": "Campo 'avaliacao' obrigatório."}), 400

        seq_item = next((s for s in SEQUENCIA if s["etapa"] == etapa_num), None)
        if not seq_item:
            return jsonify({"erro": f"Etapa {etapa_num} inválida."}), 400

        registro = {
            "etapa":        etapa_num,
            "ia":           seq_item["ia"],
            "topico":       seq_item["topico"],
            "nome_pdf":     nome_pdf,
            "avaliador_id": avaliador.get("id", ""),
            "formacao":     avaliador.get("formacao", ""),
            "area":         avaliador.get("area", ""),
            "experiencia":  avaliador.get("experiencia", ""),
            "avaliacao":    avaliacao,
            "planoTexto":   plano_texto,
            "timestamp":    body.get("timestamp", ""),
        }

        sheets_ok = enviar_para_sheets({"tipo": "avaliacao_etapa", "registro": registro})

        concluido = etapa_num >= 6
        if concluido:
            enviar_para_sheets({
                "tipo":         "experimento_completo",
                "avaliador_id": avaliador.get("id", ""),
                "nome_pdf":     nome_pdf,
                "total_etapas": etapa_num,
                "timestamp":    body.get("timestamp", ""),
            })

        return jsonify({
            "ok":        True,
            "concluido": concluido,
            "sheets_ok": sheets_ok,
        })

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/experimento/reiniciar", methods=["POST"])
def reiniciar_experimento():
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
