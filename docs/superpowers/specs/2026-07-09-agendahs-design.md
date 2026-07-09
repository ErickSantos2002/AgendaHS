# AgendaHS — Documento de Design

**Data:** 2026-07-09
**Autor:** Erick Santos (com Claude Code)
**Status:** Aprovado para planejamento

## Resumo

AgendaHS é um sistema simples de agendamento de eventos por disponibilidade, no
estilo Doodle/When2meet. O dono (Erick) cria um evento com várias datas
candidatas, compartilha um link secreto, e as pessoas convidadas informam o nome
e marcam em quais dessas datas conseguem participar. O dono acompanha as
respostas num painel privado com calendário, vendo quem está disponível em cada
data e qual data reúne mais gente.

Objetivo de simplicidade: **backend, frontend e banco no mesmo lugar, entregues
num único Dockerfile**, para deploy na VPS do Erick via EasyPanel.

## Objetivos e não-objetivos

### Objetivos
- Criar eventos com múltiplas datas candidatas.
- Gerar um link público secreto por evento para coleta de respostas.
- Coletar nome + disponibilidade (quais datas a pessoa topa) sem exigir cadastro.
- Painel privado (protegido por senha) com calendário, lista de eventos e
  detalhamento de quem está disponível por data, com destaque para a melhor data.
- Rodar como um único container Docker, com dados persistidos em SQLite.

### Não-objetivos (YAGNI)
- Contas de usuário / login por email para quem responde.
- Notificações por email/push.
- Edição colaborativa ou múltiplos administradores.
- Fusos horários avançados / recorrência de eventos.
- Frontend SPA (React) e etapa de build de frontend.

## Stack e arquitetura

- **Linguagem/Framework:** Python + Flask.
- **Templates:** Jinja2 (HTML renderizado no servidor). Sem etapa de build de
  frontend.
- **Estilo/interatividade:** um arquivo CSS caprichado e responsivo (funciona bem
  no celular) + um pouco de JavaScript puro para os poucos momentos interativos
  (copiar link, marcar/adicionar datas).
- **Banco:** SQLite, arquivo em `/app/data/eventos.db`.
- **Servidor de produção:** Gunicorn, escutando numa porta interna.
- **Empacotamento:** um único Dockerfile (estágio único, base `python:3-slim`).
- **Deploy:** VPS do Erick via EasyPanel. O EasyPanel cuida do proxy reverso e do
  HTTPS; a pasta `/app/data` é mapeada num volume persistente; a senha do painel
  entra como variável de ambiente.

O app é um único processo Flask que serve tanto as páginas do painel privado
quanto as páginas públicas de resposta, e lê/grava no SQLite local.

## Modelo de dados (SQLite)

Quatro tabelas:

### `evento`
| Coluna      | Tipo    | Notas                                        |
|-------------|---------|----------------------------------------------|
| id          | TEXT PK | Slug secreto curto (ex.: `k7m2x9`)           |
| titulo      | TEXT    | Obrigatório                                   |
| descricao   | TEXT    | Opcional                                      |
| criado_em   | TEXT    | Timestamp ISO 8601                            |

### `evento_data`
| Coluna      | Tipo       | Notas                                     |
|-------------|------------|-------------------------------------------|
| id          | INTEGER PK | Autoincremento                            |
| evento_id   | TEXT FK    | → `evento.id`                             |
| data        | TEXT       | Data candidata (ISO `YYYY-MM-DD`)         |
| horario     | TEXT       | Opcional (`HH:MM`), pode ficar nulo       |

### `participante`
| Coluna      | Tipo       | Notas                                     |
|-------------|------------|-------------------------------------------|
| id          | INTEGER PK | Autoincremento                            |
| evento_id   | TEXT FK    | → `evento.id`                             |
| nome        | TEXT       | Obrigatório                               |
| criado_em   | TEXT       | Timestamp ISO 8601                        |

### `participante_data`
| Coluna            | Tipo       | Notas                                        |
|-------------------|------------|----------------------------------------------|
| participante_id   | INTEGER FK | → `participante.id`                          |
| evento_data_id    | INTEGER FK | → `evento_data.id`                           |

A presença de uma linha em `participante_data` significa "essa pessoa está
disponível nessa data". Chave primária composta (`participante_id`,
`evento_data_id`).

O schema é criado automaticamente na primeira execução, caso as tabelas não
existam.

## Telas e fluxo

### 1. Login (`/`, quando não autenticado)
Tela simples pedindo a senha única do painel. A senha é conferida contra uma
variável de ambiente (`AGENDAHS_SENHA`). Ao acertar, grava um cookie de sessão
que mantém o Erick logado. Senha errada mostra "senha incorreta".

### 2. Painel (`/`, autenticado)
O mural privado do dono:
- **Calendário do mês** com os dias que têm evento destacados; navegação entre
  meses com ‹ ›.
- **Lista de eventos** criados (título, nº de datas, nº de respostas).
- Botão **"+ Criar evento"**.
- Clicar num evento abre o **detalhe do evento**: as datas, uma tabela
  *pessoas × datas* mostrando quem topou cada data, a contagem por data e a
  **melhor data destacada** (a com mais disponíveis). Também exibe o **link
  público** com botão "copiar link".

### 3. Criar evento (dentro do painel)
Formulário: título, descrição opcional, e adicionar quantas datas quiser
(seletor de data + botão "+ adicionar data", com horário opcional). Ao salvar,
gera o slug secreto e leva ao detalhe do evento já com o link para compartilhar.

### 4. Página pública do evento (`/e/<slug>`)
Sem senha. Mostra o título, a descrição e as datas. A pessoa informa o **nome** e
marca as **datas que topa** (checkboxes), e envia. Exibe uma confirmação
simpática ("valeu, sua resposta foi registrada!"). **A pessoa não vê quem mais
respondeu** — o resumo completo fica apenas no painel privado.

Se a mesma pessoa (mesmo nome, no mesmo evento) responder novamente, a resposta
anterior é **atualizada** em vez de duplicar.

## Rotas (esboço)

| Método | Rota                     | Protegida | Descrição                                  |
|--------|--------------------------|-----------|--------------------------------------------|
| GET    | `/`                      | —         | Login (se deslogado) ou painel (se logado) |
| POST   | `/login`                 | —         | Confere senha, cria sessão                 |
| POST   | `/logout`                | sim       | Encerra sessão                             |
| GET    | `/eventos/novo`          | sim       | Formulário de criar evento                 |
| POST   | `/eventos`               | sim       | Cria evento + datas                        |
| GET    | `/eventos/<slug>`        | sim       | Detalhe/resumo do evento (painel)          |
| GET    | `/e/<slug>`              | —         | Página pública de resposta                 |
| POST   | `/e/<slug>/responder`    | —         | Registra/atualiza resposta                 |

(Nomes finais podem ser ajustados na implementação.)

## Tratamento de erros
- Slug de evento inexistente → página **404 amigável** ("evento não encontrado").
- Responder sem nome → validação pedindo o nome.
- Marcar zero datas → **permitido**; registra a pessoa sem nenhuma
  disponibilidade (significa "nenhuma dessas datas serve").
- Senha errada no login → mensagem "senha incorreta".
- Rotas protegidas acessadas sem sessão → redireciona para o login.

## Testes (pytest)
Cobrir o essencial:
- Criar evento com datas.
- Responder a um evento (nome + datas) e conferir persistência.
- Atualizar resposta ao reenviar com o mesmo nome (não duplica).
- Proteção por senha: painel bloqueado sem sessão; login com senha certa/errada.
- Evento inexistente retorna 404.

## Empacotamento e deploy (Dockerfile único)
- Base `python:3-slim`; instala dependências (Flask, Gunicorn); copia o app.
- Comando de start: Gunicorn servindo o app Flask numa porta interna.
- Banco em `/app/data/eventos.db`; `/app/data` mapeado num **volume persistente**
  do EasyPanel.
- Senha do painel via variável de ambiente `AGENDAHS_SENHA` (configurada no
  EasyPanel, não no código).
- Schema do SQLite criado automaticamente na primeira execução.

## Estrutura de pastas (proposta)
```
AgendaHS/
├── app/
│   ├── __init__.py         # cria o app Flask, registra rotas
│   ├── db.py               # conexão SQLite + criação do schema
│   ├── rotas.py            # rotas do painel e públicas
│   ├── templates/          # HTML Jinja2
│   └── static/             # CSS e JS
├── tests/                  # pytest
├── docs/superpowers/specs/ # este documento
├── requirements.txt
├── Dockerfile
└── README.md
```
(A organização final dos módulos pode ser refinada no plano de implementação.)
