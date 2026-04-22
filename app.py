from flask import Flask, request, render_template, Response, jsonify
from Gerador import gerar_plano_stream
import os
import PyPDF2
import csv
import io
import zipfile
import json
import re

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

os.makedirs("resultados", exist_ok=True)


# ================= PDF =================
def gerar_pdf_bytes(texto):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()
    story = []

    for linha in texto.split("\n"):
        story.append(Paragraph(linha, styles["Normal"]))
        story.append(Spacer(1, 5))

    doc.build(story)
    buffer.seek(0)
    return buffer


# ================= CSV =================
def gerar_csv_bytes(dados):
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    writer.writerow(dados.keys())
    writer.writerow(dados.values())

    return buffer.getvalue().encode("utf-8")


# ================= PDF LEITURA =================
def extrair_texto_pdf(arquivo):
    texto = ""
    try:
        leitor = PyPDF2.PdfReader(arquivo)
        for pagina in leitor.pages:
            texto += pagina.extract_text() or ""
    except Exception as e:
        texto = f"Erro ao ler PDF: {e}"
    return texto


# ================= FORMATAÇÃO =================
def formatar_plano_para_exportacao(plano_texto):
    linhas = plano_texto.split("\n")
    resultado = []

    for linha in linhas:
        linha = linha.strip()

        if not linha:
            continue

        if "AULA" in linha and "===" in linha:
            resultado.append("\n📘 " + linha + "\n")
            continue

        if linha.startswith("Conteúdo:"):
            resultado.append("\n📌 " + linha)
        elif linha.startswith("Recursos"):
            resultado.append("📚 " + linha)
        elif linha.startswith("Metodologia"):
            resultado.append("🧠 " + linha)
        elif linha.startswith("Atividade"):
            resultado.append("🛠 " + linha)
        elif linha.startswith("Avaliação"):
            resultado.append("🧾 " + linha)
        else:
            resultado.append(linha)

    return "\n".join(resultado)


def estruturar_plano(plano_texto):
    aulas = re.split(r"📘 === AULA \d+ ===", plano_texto)

    resultado = []

    for i, aula in enumerate(aulas):
        aula = aula.strip()

        if not aula:
            continue

        resultado.append({
            "aula": i + 1,
            "conteudo_bruto": aula
        })

    return resultado


# ================= HOME =================
@app.route("/")
def index():
    return render_template("index.html")


# ================= DOWNLOAD ZIP =================
@app.route("/download_plano", methods=["POST"])
def download_plano():

    dados = request.get_json()

    plano = dados.get("plano", "")
    avaliacao = dados.get("avaliacao", {})
    formulario = dados.get("formulario", {})

    # ===== FORMATAÇÃO =====
    plano_formatado = formatar_plano_para_exportacao(plano)
    plano_estrutura = estruturar_plano(plano)

    # ===== JSON =====
    payload = {
        "plano_bruto": plano,
        "plano_formatado": plano_formatado,
        "plano_estruturado": plano_estrutura,
        "avaliacao": avaliacao,
        "formulario": formulario
    }

    json_data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")

    # ===== CSV =====
    csv_data = gerar_csv_bytes(formulario)

    # ===== PDF =====
    pdf_buffer = gerar_pdf_bytes(plano_formatado)

    # ===== ZIP =====
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr("plano.json", json_data)
        zipf.writestr("formulario.csv", csv_data)

        pdf_buffer.seek(0)
        zipf.writestr("plano.pdf", pdf_buffer.read())

    zip_buffer.seek(0)

    return Response(
        zip_buffer.getvalue(),
        mimetype="application/zip",
        headers={
            "Content-Disposition": "attachment; filename=plano_completo.zip"
        }
    )


# ================= GERAR PLANO =================
@app.route("/gerar", methods=["POST"])
def gerar():

    try:
        dados = {
            "disciplina": request.form.get("disciplina", ""),
            "curso": request.form.get("curso", ""),
            "carga": request.form.get("carga", ""),
            "qtd_aulas": request.form.get("qtd_aulas", "1"),
            "duracao": request.form.get("duracao", ""),
            "ementa": request.form.get("ementa", ""),
            "objetivo": request.form.get("objetivo", "")
        }

        ia = request.form.get("ia", "gpt")

        # ===== PDF INPUT =====
        arquivo = request.files.get("arquivo")
        texto_arquivo = ""

        if arquivo and arquivo.filename != "":
            texto_arquivo = extrair_texto_pdf(arquivo)

        dados["texto_arquivo"] = texto_arquivo

        # ===== STREAM =====
        def stream():
            try:
                for chunk in gerar_plano_stream(
                    dados,
                    int(dados.get("qtd_aulas", 1)),
                    ia
                ):
                    if chunk:
                        yield chunk
            except Exception as e:
                yield f"\n[ERRO STREAM] {str(e)}"

        return Response(stream(), mimetype='text/plain')

    except Exception as e:
        print("ERRO /gerar:", e)
        return jsonify({"erro": str(e)}), 500


# ================= SALVAR AVALIAÇÃO =================
@app.route("/salvar_avaliacao", methods=["POST"])
def salvar_avaliacao():

    try:
        dados = request.get_json()

        with open("avaliacoes.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                dados.get("professor"),
                dados.get("questao"),
                dados.get("fluidez"),
                dados.get("capacidade"),
                dados.get("diversidade"),
                dados.get("complexidade"),
                dados.get("relevancia"),
                dados.get("media"),
                dados.get("incompleta"),
                dados.get("observacoes")
            ])

        return jsonify({"status": "ok"})

    except Exception as e:
        print("ERRO salvar_avaliacao:", e)
        return jsonify({"status": "erro", "erro": str(e)}), 500


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
