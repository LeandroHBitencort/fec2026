# =============================================================================
# BitFlow - VERSÃO FEC 2026
#
# Essa versão reproduz o que o totem da feira realmente faz: gera senha
# normal ou preferencial, intercala as duas de forma justa na hora de
# chamar, imprime um cupom pelo navegador (sem precisar de app nativo) e
# mostra um QR code no cupom. O código de produção é outro (atende várias
# lojas de verdade, com login, impressora Bluetooth e monitoramento) -
# aqui está só a lógica da fila em si, pra qualquer pessoa conseguir ler
# de cima a baixo e entender exatamente o que está acontecendo.
# =============================================================================

from flask import Flask, render_template, jsonify, request, Response
import io

# qrcode é opcional: se não estiver instalado, o resto do site continua
# funcionando normal, só o QR code do cupom não aparece. Isso evita que
# uma dependência faltando derrube o site inteiro (já aconteceu de verdade
# aqui no projeto real, então virou hábito fazer assim).
try:
    import qrcode
except ImportError:
    qrcode = None

app = Flask(__name__)

# -----------------------------------------------------------------------
# O ESTADO DA FILA
# -----------------------------------------------------------------------
# Diferente da versão mais simples, aqui temos DUAS filas separadas (uma
# pra senha normal, outra pra preferencial) mais um contador que controla
# a intercalação entre elas na hora de chamar.
estado = {
    "fila_normal": [],
    "fila_preferencial": [],
    "contador_normal": 0,
    "contador_preferencial": 0,
    "chamando_agora": None,

    # Regra de prioridade: a cada quantas senhas NORMAIS chamadas, intercala
    # uma preferencial (se tiver alguma esperando). Ex: com valor 3, o
    # padrão de chamada fica algo como N, N, N, P, N, N, N, P...
    "regra_prioridade": 3,
    "normais_chamadas_desde_ultima_preferencial": 0,
}


def gerar_senha(tipo):
    """Cria uma senha nova (normal ou preferencial) e coloca no FIM da
    fila correspondente."""
    if tipo == "preferencial":
        estado["contador_preferencial"] += 1
        numero = "P" + str(estado["contador_preferencial"]).zfill(3)
        estado["fila_preferencial"].append(numero)
    else:
        estado["contador_normal"] += 1
        numero = "N" + str(estado["contador_normal"]).zfill(3)
        estado["fila_normal"].append(numero)
    return numero


def chamar_proxima():
    """Decide qual fila puxar a próxima senha, aplicando a regra de
    intercalação, e tira essa senha do início dela (FIFO dentro de cada
    fila - a preferencial não fura a preferencial, só tem prioridade
    sobre a normal)."""
    tem_normal = len(estado["fila_normal"]) > 0
    tem_preferencial = len(estado["fila_preferencial"]) > 0

    if not tem_normal and not tem_preferencial:
        return None  # as duas filas estão vazias, não tem quem chamar

    # Chegou a vez de intercalar uma preferencial? Só faz isso se
    # realmente existir alguém preferencial esperando - senão a regra não
    # tem efeito nenhum (não faz sentido "pular a vez" pra uma fila vazia).
    vez_da_preferencial = (
        estado["normais_chamadas_desde_ultima_preferencial"] >= estado["regra_prioridade"]
    )

    if tem_preferencial and (vez_da_preferencial or not tem_normal):
        senha = estado["fila_preferencial"].pop(0)
        estado["normais_chamadas_desde_ultima_preferencial"] = 0
    else:
        senha = estado["fila_normal"].pop(0)
        estado["normais_chamadas_desde_ultima_preferencial"] += 1

    estado["chamando_agora"] = senha
    return senha


# -----------------------------------------------------------------------
# AS PÁGINAS DO SITE (ROTAS)
# -----------------------------------------------------------------------

@app.route("/")
def totem():
    """Tela do totem - o cliente escolhe normal ou preferencial aqui."""
    return render_template("totem.html")


@app.route("/gerar", methods=["POST"])
def rota_gerar():
    """O totem chama esse endereço quando o cliente escolhe o tipo de
    senha. O tipo vem no corpo do pedido, em JSON: {"tipo": "normal"} ou
    {"tipo": "preferencial"}."""
    dados = request.get_json(silent=True) or {}
    tipo = dados.get("tipo", "normal")
    if tipo not in ("normal", "preferencial"):
        tipo = "normal"
    senha = gerar_senha(tipo)
    return jsonify({"senha": senha, "tipo": tipo})


@app.route("/painel")
def painel():
    """Tela do atendente - de onde ele chama a próxima senha."""
    return render_template("painel.html")


@app.route("/chamar", methods=["POST"])
def rota_chamar():
    """O painel chama esse endereço quando o atendente aperta "Chamar
    próximo" - a decisão de qual fila puxar é toda feita no servidor,
    o painel só mostra o resultado."""
    senha = chamar_proxima()
    return jsonify({"senha": senha})


@app.route("/tv")
def tv():
    """Tela de exibição - fica num monitor grande, mostrando a última
    senha chamada, pra quem está esperando acompanhar sem precisar ficar
    perguntando pro atendente."""
    return render_template("tv.html")


@app.route("/status")
def status():
    """Devolve o estado atual da fila em JSON - totem, painel e TV
    consultam esse endereço a cada poucos segundos (polling) pra manter a
    tela sempre atualizada, sem precisar recarregar a página."""
    return jsonify({
        "chamando_agora": estado["chamando_agora"],
        "esperando_normal": len(estado["fila_normal"]),
        "esperando_preferencial": len(estado["fila_preferencial"]),
    })


@app.route("/qrcode.png")
def qrcode_png():
    """Gera a imagem do QR code do cupom na hora, a partir do texto
    recebido em ?dados=... - assim o cupom impresso pode levar um QR
    apontando pra qualquer link (aqui, pra essa mesma página /sobre)."""
    if qrcode is None:
        return "Biblioteca qrcode não instalada no servidor", 501

    texto = request.args.get("dados", "")
    imagem = qrcode.make(texto)

    # Gera a imagem em memória (sem salvar em disco) e devolve os bytes
    # dela direto como resposta HTTP, com o tipo certo (image/png) pra
    # o navegador saber que é uma imagem e não texto.
    buffer = io.BytesIO()
    imagem.save(buffer, format="PNG")
    return Response(buffer.getvalue(), mimetype="image/png")


# -----------------------------------------------------------------------
# LIGA O SERVIDOR
# -----------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)
