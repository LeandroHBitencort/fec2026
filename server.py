# =============================================================================
# BitFlow FEC 2026 - versão simplificada, feita pra explicar como uma fila
# de senhas funciona por dentro. Essa NÃO é a versão que roda em produção de
# verdade (aquela tem várias lojas, impressora térmica, login com senha,
# banco de dados) - essa aqui é só a lógica essencial, pra qualquer pessoa
# conseguir ler de cima a baixo e entender o que está acontecendo.
#
# A ideia central é uma fila FIFO (First In, First Out - "primeiro que
# entra é o primeiro que sai"): quem pega uma senha primeiro é chamado
# primeiro, sempre nessa ordem, sem exceção.
# =============================================================================

# Flask é o "framework" que transforma esse arquivo Python num site de
# verdade, capaz de responder a pedidos feitos pelo navegador.
from flask import Flask, render_template, jsonify

# Cria a aplicação Flask. É esse objeto "app" que vamos usar pra registrar
# cada página/rota do site daqui pra frente.
app = Flask(__name__)

# -----------------------------------------------------------------------
# O ESTADO DA FILA
# -----------------------------------------------------------------------
# Esse dicionário é onde a fila realmente "mora" - tudo o que o sistema
# sabe sobre a fila está guardado aqui, na memória do próprio programa.
# (Em produção de verdade isso fica salvo num banco de dados, pra não se
# perder se o servidor reiniciar - mas pra aprender o conceito, guardar
# na memória é mais simples e mais fácil de ler.)
estado = {
    "fila": [],       # lista com as senhas que ainda esperam ser chamadas,
                       # NA ORDEM DE CHEGADA - a primeira da lista é a
                       # próxima a ser chamada.
    "contador": 0,     # quantas senhas já foram geradas no total, usado
                       # só pra numerar a próxima senha (N001, N002...).
    "chamando_agora": None,   # qual senha está sendo atendida agora
                               # (aparece no painel do atendente).
}


def gerar_senha():
    """Cria uma senha nova e coloca ela no FIM da fila."""
    # Soma 1 no contador - isso garante que cada senha tem um número
    # diferente e sempre crescente (N001, depois N002, depois N003...).
    estado["contador"] += 1

    # Monta o texto da senha: "N" de "normal" + o número, sempre com 3
    # dígitos (por isso o zfill(3): o número 7 vira "007").
    numero_senha = "N" + str(estado["contador"]).zfill(3)

    # .append() adiciona um item no FINAL de uma lista Python - é
    # literalmente o "entra pelo fim" da definição de FIFO.
    estado["fila"].append(numero_senha)

    return numero_senha


def chamar_proxima():
    """Tira a senha mais antiga da fila (a que está esperando há mais
    tempo) e marca ela como "sendo atendida agora"."""
    # Se a fila estiver vazia, não tem ninguém pra chamar - devolve None
    # pra quem chamou essa função saber que não havia nada a fazer.
    if len(estado["fila"]) == 0:
        return None

    # .pop(0) remove e devolve o PRIMEIRO item da lista (posição 0) - é
    # literalmente o "sai pelo início" da definição de FIFO. Se fosse
    # .pop() sem argumento, tiraria o ÚLTIMO item (isso seria uma pilha,
    # LIFO - "Last In, First Out" - o oposto do que queremos aqui).
    senha_chamada = estado["fila"].pop(0)

    estado["chamando_agora"] = senha_chamada
    return senha_chamada


# -----------------------------------------------------------------------
# AS PÁGINAS DO SITE (ROTAS)
# -----------------------------------------------------------------------
# Cada "@app.route(...)" abaixo liga um endereço (URL) a uma função Python.
# Quando alguém acessa aquele endereço no navegador, a função roda e o que
# ela devolver (geralmente um HTML) é o que aparece na tela.

@app.route("/")
def totem():
    """Tela do totem - é aqui que o cliente pega a senha dele."""
    # render_template pega um arquivo HTML dentro da pasta "templates/"
    # e manda ele pro navegador de quem pediu essa página.
    return render_template("totem.html")


@app.route("/gerar", methods=["POST"])
def rota_gerar():
    """O totem chama esse endereço (via JavaScript) quando o cliente
    aperta o botão de pegar senha."""
    senha = gerar_senha()

    # jsonify transforma um dicionário Python em JSON - o formato de
    # texto que o JavaScript do navegador consegue entender e usar.
    return jsonify({"senha": senha})


@app.route("/painel")
def painel():
    """Tela do atendente - de onde ele chama a próxima senha."""
    return render_template("painel.html")


@app.route("/tv")
def tv():
    """Tela de exibição - fica num monitor grande, visível pra quem tá
    esperando na fila, mostrando qual senha está sendo chamada agora.
    Não tem nenhum botão aqui - só mostra informação, ninguém interage
    com essa tela diretamente."""
    return render_template("tv.html")


@app.route("/chamar", methods=["POST"])
def rota_chamar():
    """O painel chama esse endereço quando o atendente aperta
    "Chamar próximo"."""
    senha = chamar_proxima()
    return jsonify({"senha": senha})


@app.route("/status")
def status():
    """Devolve o estado atual da fila em JSON - tanto o totem quanto o
    painel consultam esse endereço a cada poucos segundos (polling) pra
    manter a tela sempre atualizada, sem precisar recarregar a página."""
    return jsonify({
        "chamando_agora": estado["chamando_agora"],
        "quantidade_esperando": len(estado["fila"]),
    })


# -----------------------------------------------------------------------
# LIGA O SERVIDOR
# -----------------------------------------------------------------------
# Esse bloco só roda quando você executa "python server.py" diretamente
# (não roda se esse arquivo for importado de dentro de outro programa).
if __name__ == "__main__":
    # debug=True reinicia o servidor sozinho toda vez que você salva uma
    # alteração no código, e mostra erros detalhados na tela - ótimo pra
    # estudar e testar, mas não deveria ser usado em produção de verdade.
    app.run(debug=True, port=5001)
