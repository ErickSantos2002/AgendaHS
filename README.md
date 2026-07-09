# AgendaHS

Sistema simples de agendamento por disponibilidade (estilo Doodle). Você cria um
evento com várias datas candidatas, compartilha um link secreto, e as pessoas
informam o nome e marcam as datas que topam. Você acompanha as respostas num
painel privado com calendário, vendo quem está disponível em cada data e qual
reúne mais gente.

## Stack
Flask + Jinja2 + SQLite, empacotado num Dockerfile único. HTML renderizado no
servidor, sem etapa de build de frontend. Deploy na VPS via EasyPanel.

## Como funciona
- **Painel privado** (`/`) — protegido por senha; calendário do mês, lista de
  eventos e detalhe com a grade de disponibilidade.
- **Página pública** (`/e/<slug>`) — sem senha; a pessoa só informa o nome e
  marca as datas. Não vê as respostas dos outros.

## Rodar local
```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export AGENDAHS_SENHA="suasenha"
export AGENDAHS_SECRET_KEY="algo-aleatorio"
export AGENDAHS_DB="./data/eventos.db"
gunicorn --bind 0.0.0.0:8000 wsgi:app
# abra http://localhost:8000
```

## Testes
```bash
python -m pytest -v
```

## Variáveis de ambiente
| Variável              | Obrigatória | Descrição                                   |
|-----------------------|-------------|---------------------------------------------|
| `AGENDAHS_SENHA`      | sim         | Senha do painel. Sem ela, o app não inicia. |
| `AGENDAHS_SECRET_KEY` | recomendada | Chave aleatória para assinar a sessão.      |
| `AGENDAHS_DB`         | não         | Caminho do SQLite (default `/app/data/eventos.db`). |

## Deploy no EasyPanel
1. Criar um app apontando para este repositório (build pelo `Dockerfile`).
2. Definir as variáveis de ambiente `AGENDAHS_SENHA` e `AGENDAHS_SECRET_KEY`.
3. Montar um **volume persistente** em `/app/data` (para o SQLite sobreviver a
   rebuilds).
4. Porta interna **8000** — o EasyPanel cuida do proxy reverso e do HTTPS.

## Build/execução com Docker
```bash
docker build -t agendahs .
docker run --rm -p 8000:8000 \
  -e AGENDAHS_SENHA=teste -e AGENDAHS_SECRET_KEY=x \
  -v "$PWD/data:/app/data" agendahs
```
