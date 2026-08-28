# BitFlow FEC 2026 — versão simplificada

Essa é uma versão enxuta do BitFlow, feita especialmente para explicar
como o sistema funciona por dentro. **Não é o código que roda em
produção de verdade** (aquele tem várias lojas, impressora térmica,
login com senha e banco de dados) — essa aqui é só a lógica essencial
de uma fila FIFO, para qualquer pessoa do grupo conseguir ler o
`server.py` de cima a baixo e entender exatamente o que está
acontecendo em cada linha.

## O conceito: fila FIFO

FIFO significa *First In, First Out* — o primeiro que entra é o
primeiro que sai. É a mesma lógica de uma fila de banco: quem chega
primeiro é atendido primeiro, sempre nessa ordem.

## Como rodar

1. Instale o Flask:
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
server.py          → toda a lógica (fila, geração de senha, chamada)
templates/
  totem.html        → tela onde o cliente pega a senha
  painel.html        → tela onde o atendente chama a próxima
  tv.html           → tela de exibição, mostra a senha chamada
requirements.txt      → dependências (só o Flask)
```

Todo o comentário explicando **por que** cada trecho existe está direto
no `server.py` — é o melhor lugar para começar a ler.

## De onde isso veio

- [Como começou](https://github.com/LeandroHBitencort/Gerenciamento_Fila) —
  o protótipo original do trabalho de Estrutura de Dados II (C + Python)
