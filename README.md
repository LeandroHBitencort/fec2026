# BitFlow - VERSÃO FEC 2026

Essa é a versão do BitFlow feita para a FEC 2026, pensada para explicar
como o sistema funciona por dentro. O código de produção é outro
(atende várias lojas, com impressora térmica, login e banco de dados)
— aqui está a lógica essencial de uma fila FIFO, para qualquer pessoa
do grupo conseguir ler o `server.py` de cima a baixo e entender
exatamente o que está acontecendo em cada linha.

## O conceito: fila FIFO (com prioridade)

FIFO significa *First In, First Out* — o primeiro que entra é o
primeiro que sai. É a mesma lógica de uma fila de banco: quem chega
primeiro é atendido primeiro, sempre nessa ordem — mas com uma regra a
mais, igual ao totem real: senha **preferencial** é intercalada com a
normal (por padrão, a cada 3 normais chamadas, 1 preferencial), em vez
de furar a fila toda ou de nunca ser chamada.

## O que também está aqui

- Impressão do cupom **pelo próprio navegador** (`window.print()`), sem
  precisar de aplicativo nativo — é assim que o totem real do FEC
  imprime, usando uma impressora comum ligada por cabo
- QR code gerado na hora, embutido no cupom impresso

## Como rodar

1. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
2. Rode o servidor:
   ```
   python server.py
   ```
3. Abra três navegadores (ou três abas):
   - `http://localhost:5001/` — o totem, onde o cliente pega a senha
   - `http://localhost:5001/painel` — o painel, de onde o atendente
     chama a próxima senha
   - `http://localhost:5001/tv` — a tela de exibição, mostrando a
     senha chamada (pensada pra ficar num monitor grande, à vista de
     quem está esperando)

## Estrutura do projeto

```
server.py          → toda a lógica (fila, prioridade, QR code)
templates/
  totem.html        → tela onde o cliente pega a senha e imprime o cupom
  painel.html        → tela onde o atendente chama a próxima
  tv.html           → tela de exibição, mostra a senha chamada
requirements.txt      → dependências (Flask + qrcode)
```

Todo o comentário explicando **por que** cada trecho existe está direto
no `server.py` — é o melhor lugar para começar a ler.

## De onde isso veio

- [Como começou](https://github.com/LeandroHBitencort/Gerenciamento_Fila) —
  o protótipo original do trabalho de Estrutura de Dados II (C + Python)

## Equipe

**Leandro H. Bitencort** — idealizador do projeto

Grupo:
- Arnaldo Goulart da Silva Neto
- Isabela Yukie Furuyama
- Jafé Vinícius Antonio
- João Vitor Deodato Haddad
- João Ricardo da Conceição
- Isis Marcelle da Silva
