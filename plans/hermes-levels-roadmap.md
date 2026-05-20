# Hermes Agent Fleet Roadmap

> **For Hermes:** Use este plano como guia para evoluir a operação do Luiz de um Hermes pessoal no Telegram para uma frota de agentes especialistas com orquestrador e automações.

**Goal:** Sair do Level 1 atual (um Hermes na VPS com Telegram) para Level 4 (time automatizado com especialistas, orquestrador, cron jobs e documentação no GitHub).

**Architecture:** O sistema será organizado como um “control room”: uma pasta/repositório com documentação, runbooks, inventário de agentes, comandos e regras de segurança. A VPS guarda runtime e segredos; o GitHub guarda apenas documentação, scripts seguros e templates sem segredos.

**Tech Stack:** Hermes Agent, Telegram Gateway, Linux VPS, GitHub, tmux/systemd, Hermes profiles, cron jobs.

---

## Estado atual

Confirmado até agora:

- VPS: sim, estamos rodando em Linux.
- Hermes CLI: sim.
- Telegram: configurado.
- Telegram allowlist: usuário `958140131`.
- Gateway: rodando manualmente em background; instalação via systemd user falhou com `Failed to connect to bus: No medium found`.
- GitHub: token autenticou como `luizpaulo00`, mas ainda falta escolher/criar/renomear um repositório acessível para salvar este control room.
- Level atual: Level 1 inicial.

## Regra de segurança

GitHub pode guardar:

- documentação
- planos
- runbooks
- scripts seguros
- templates sem segredos
- inventário de agentes

GitHub não pode guardar:

- token do Telegram
- GitHub PAT
- `.env`
- `auth.json`
- `state.db`
- logs brutos
- `config.yaml` com segredos
- qualquer chave de API

Segredos ficam apenas na VPS, em locais como:

- `~/.hermes/.env`
- `~/.hermes/config.yaml`
- `/srv/<agent-name>/data/.env` quando houver agentes separados

---

# Level 1 — Um Hermes pessoal estável

## Objetivo

Deixar o Hermes principal confiável, documentado, acessível pelo Telegram e salvo no GitHub.

## Resultado esperado

Ao final do Level 1:

- O bot responde no Telegram.
- Existe forma clara de iniciar/parar/ver status do gateway.
- Existe um control room local.
- O control room está salvo no GitHub.
- Nenhum segredo foi commitado.

---

## Task 1.1: Estabilizar o Telegram Gateway

**Objective:** Garantir que o gateway do Hermes esteja rodando de forma previsível e possa ser reiniciado facilmente.

**Files:**

- Create: `scripts/start-gateway.sh`
- Create: `scripts/stop-gateway.sh`
- Create: `scripts/status-gateway.sh`
- Modify/Create: `agents/hermes-main/runbook.md`

**Step 1: Verificar status atual**

Run:

```bash
hermes gateway status
```

Expected:

- Pode mostrar que o serviço systemd está parado.
- Pode mostrar que existe um processo manual rodando.

**Step 2: Usar tmux como fallback persistente**

Como systemd user falhou neste ambiente, usar tmux:

```bash
tmux new-session -d -s hermes-gateway 'hermes gateway run'
```

Ver tela:

```bash
tmux attach -t hermes-gateway
```

Sair sem parar:

```text
Ctrl+B, depois D
```

Parar:

```bash
tmux kill-session -t hermes-gateway
```

**Step 3: Criar scripts**

`scripts/start-gateway.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

if tmux has-session -t hermes-gateway 2>/dev/null; then
  echo "hermes-gateway already running in tmux"
  exit 0
fi

tmux new-session -d -s hermes-gateway 'hermes gateway run'
echo "started hermes gateway in tmux session: hermes-gateway"
```

`scripts/stop-gateway.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

if tmux has-session -t hermes-gateway 2>/dev/null; then
  tmux kill-session -t hermes-gateway
  echo "stopped tmux session: hermes-gateway"
else
  echo "tmux session hermes-gateway not found"
fi
```

`scripts/status-gateway.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

hermes gateway status || true

if tmux has-session -t hermes-gateway 2>/dev/null; then
  echo "tmux: hermes-gateway session is running"
else
  echo "tmux: hermes-gateway session is not running"
fi
```

**Step 4: Tornar scripts executáveis**

Run:

```bash
chmod +x scripts/start-gateway.sh scripts/stop-gateway.sh scripts/status-gateway.sh
```

**Step 5: Testar no Telegram**

Enviar uma mensagem para o bot no Telegram.

Expected:

- O Hermes responde.

**Step 6: Commit**

```bash
git add scripts/ agents/hermes-main/runbook.md
git commit -m "chore: add gateway runbook and helper scripts"
```

---

## Task 1.2: Criar control room local

**Objective:** Criar a estrutura de documentação da operação Hermes.

**Files:**

- Create: `README.md`
- Create: `plans/hermes-levels-roadmap.md`
- Create: `agents/hermes-main/inventory.md`
- Create: `agents/hermes-main/runbook.md`
- Create: `agents/hermes-main/env-map.md`
- Create: `agents/hermes-main/backup.md`
- Create: `shared/security.md`
- Create: `shared/commands.md`
- Create: `.gitignore`

**Step 1: Criar estrutura**

Run:

```bash
mkdir -p plans agents/hermes-main shared scripts
```

**Step 2: Criar `.gitignore`**

`.gitignore`:

```gitignore
.env
*.env
auth.json
state.db
*.db
logs/
*.log
config.yaml
secrets/
.sessions/
*.sqlite
*.sqlite3
```

**Step 3: Criar README**

`README.md`:

```markdown
# Hermes Control Room

Control room da operação Hermes do Luiz.

Este repositório documenta como o Hermes roda na VPS, como acessar pelo Telegram, como reiniciar, como evoluir de um agente pessoal para uma frota de agentes especialistas e quais regras de segurança seguir.

Não guardar segredos aqui.

Plano principal:

- `plans/hermes-levels-roadmap.md`
```

**Step 4: Criar inventário do agente principal**

`agents/hermes-main/inventory.md`:

```markdown
# hermes-main inventory

Função: assistente Hermes principal do Luiz.

Estado atual:

- Roda na VPS Linux.
- Acesso via CLI.
- Acesso via Telegram configurado.
- Telegram allowlist: usuário 958140131.

Canais:

- CLI: `hermes`
- Telegram: bot configurado via `hermes gateway setup`

Responsabilidades:

- Assistente geral.
- Operação inicial Level 1.
- Ajudar a administrar GitHub, VPS e documentação.

Limites:

- Não publicar segredos no GitHub.
- Não executar ações destrutivas sem confirmação.
```

**Step 5: Criar mapa de ambiente sem segredos**

`agents/hermes-main/env-map.md`:

```markdown
# hermes-main env map

Não colocar valores reais aqui.

Variáveis/segredos esperados:

- Telegram bot token: configurado pelo `hermes gateway setup`.
- GitHub token: usar temporariamente para operações, não salvar no repo.
- Provedor/modelo Hermes: configurado em `~/.hermes/config.yaml` e/ou `~/.hermes/.env`.

Arquivos sensíveis:

- `~/.hermes/.env`
- `~/.hermes/config.yaml`
- `~/.hermes/auth.json`
- `~/.hermes/state.db`
- `~/.hermes/logs/`
```

**Step 6: Criar regras de segurança**

`shared/security.md`:

```markdown
# Security rules

1. Nunca commitar tokens.
2. Nunca commitar `.env`.
3. Nunca commitar `auth.json`.
4. Nunca commitar `state.db` ou logs brutos.
5. GitHub guarda documentação, templates e scripts seguros.
6. Segredos ficam somente na VPS ou no GitHub Secrets quando necessário.
7. Se um token for colado em chat, revogar/regenerar depois.
```

**Step 7: Criar comandos úteis**

`shared/commands.md`:

```markdown
# Useful commands

## Hermes

```bash
hermes
hermes gateway status
hermes gateway run
hermes profile list
hermes config path
```

## Gateway tmux

```bash
tmux new-session -d -s hermes-gateway 'hermes gateway run'
tmux attach -t hermes-gateway
tmux kill-session -t hermes-gateway
```

## Logs

```bash
tail -f ~/.hermes/logs/gateway.log
```

## Git

```bash
git status
git add .
git commit -m "docs: update hermes control room"
git push
```
```

**Step 8: Commit**

```bash
git add .
git commit -m "docs: add hermes level 1 control room"
```

---

## Task 1.3: Resolver GitHub

**Objective:** Ter um repositório GitHub acessível para salvar o control room.

**Current issue:** O token autentica como `luizpaulo00`, mas não acessa `luizpaulo00/hermest_bot`. O repositório pode não existir, estar com outro nome, ou o token fine-grained não tem acesso.

**Preferred path:** Renomear manualmente `funil-de-vendas` para `hermes`, porque o token atual tem acesso a `funil-de-vendas`, mas não tem permissão de API para renomear.

**Step 1: Renomear manualmente no GitHub**

Abrir:

```text
https://github.com/luizpaulo00/funil-de-vendas/settings
```

Alterar nome para:

```text
hermes
```

**Step 2: Clonar**

```bash
git clone https://github.com/luizpaulo00/hermes.git /home/luiz/projects/hermes
```

**Step 3: Copiar control room para o repo**

```bash
rsync -av --exclude='.git' /home/luiz/hermes-control-room/ /home/luiz/projects/hermes/
```

**Step 4: Commit e push**

```bash
cd /home/luiz/projects/hermes
git add .
git commit -m "docs: add hermes control room"
git push
```

**Expected:** GitHub contém o control room sem segredos.

---

# Level 2 — Agentes especialistas diretos

## Objetivo

Criar agentes separados por função. Você ainda fala direto com cada um, sem orquestrador.

## Agentes sugeridos

### 1. hermes-main

Função: assistente geral e Telegram principal.

### 2. hermes-dev

Função:

- GitHub
- VPS
- scripts
- automações
- debugging
- deploy

### 3. hermes-marketing

Função:

- conteúdo
- copy
- posts
- ofertas
- funil
- campanhas

### 4. hermes-business

Função:

- ideias de negócio
- planejamento
- vendas
- CRM simples
- follow-up

---

## Task 2.1: Definir escopo dos especialistas

**Objective:** Documentar missão, limites e responsabilidades de cada agente.

**Files:**

- Create: `agents/hermes-dev/inventory.md`
- Create: `agents/hermes-marketing/inventory.md`
- Create: `agents/hermes-business/inventory.md`

**Template:**

```markdown
# <agent-name> inventory

Função: <função principal>

Responsabilidades:

- <responsabilidade 1>
- <responsabilidade 2>

Pode fazer:

- <ação permitida>

Precisa de aprovação para:

- <ação sensível>

Não pode fazer:

- publicar segredos
- apagar dados sem confirmação
- alterar produção sem aprovação

Canais:

- CLI profile: `<profile>`
- Telegram: a definir
```

**Commit:**

```bash
git add agents/
git commit -m "docs: define specialist agent scopes"
```

---

## Task 2.2: Criar Hermes profiles

**Objective:** Separar contexto e personalidade por função.

**Commands:**

```bash
hermes profile create dev --clone
hermes profile create marketing --clone
hermes profile create business --clone
```

**Verify:**

```bash
hermes profile list
```

Expected:

- `dev`
- `marketing`
- `business`

**Access:**

```bash
hermes -p dev
hermes -p marketing
hermes -p business
```

**Commit docs:**

```bash
git add agents/
git commit -m "docs: document specialist profiles"
```

---

## Task 2.3: Configurar personalidade e memória inicial

**Objective:** Dar identidade e foco para cada especialista.

**For each profile:**

- Ajustar personalidade/soul.
- Ajustar memória inicial.
- Habilitar apenas ferramentas necessárias.

**Suggested personality:**

`hermes-dev`:

```text
Você é um agente técnico objetivo. Prioriza segurança, versionamento, logs, rollback e automação simples.
```

`hermes-marketing`:

```text
Você é um estrategista de marketing direto. Prioriza clareza, oferta, gancho, distribuição e conversão.
```

`hermes-business`:

```text
Você é um operador de negócios. Prioriza próximos passos, receita, pipeline, follow-up e decisões práticas.
```

**Verification:**

Abrir cada profile e pedir:

```text
qual é sua função?
```

Expected: cada profile responde de acordo com seu papel.

---

# Level 3 — Orquestrador + especialistas

## Objetivo

Criar uma porta de entrada principal que recebe pedidos, entende a intenção e direciona para o especialista certo.

## Componentes

- `hermes-orchestrator`
- `hermes-dev`
- `hermes-marketing`
- `hermes-business`
- `hermes-main`
- `agents/registry.md`

---

## Task 3.1: Criar profile orquestrador

**Objective:** Criar um agente gerente que roteia tarefas.

**Command:**

```bash
hermes profile create orchestrator --clone
```

**Personality:**

```text
Você é o orquestrador da frota Hermes do Luiz. Sua função é entender pedidos, consultar o registry dos agentes, decidir quem deve executar, quebrar tarefas grandes, pedir confirmação em ações sensíveis e sintetizar resultados. Você não faz tudo sozinho quando um especialista for mais adequado.
```

**Verify:**

```bash
hermes -p orchestrator
```

Prompt de teste:

```text
quero criar uma campanha e uma landing page para vender um produto. quais agentes você chamaria?
```

Expected:

- marketing para campanha/copy
- business para oferta/estratégia
- dev para landing page/automação

---

## Task 3.2: Criar registry de agentes

**Objective:** Dar ao orquestrador uma fonte de verdade sobre os agentes.

**File:**

- Create: `agents/registry.md`

**Content:**

```markdown
# Agent Registry

## hermes-main

Profile: default
Função: assistente geral e Telegram principal.
Canal: Telegram/CLI.
Limites: não mexer em segredos sem aprovação.

## hermes-dev

Profile: dev
Função: GitHub, VPS, scripts, automações, debugging, deploy.

## hermes-marketing

Profile: marketing
Função: conteúdo, copy, funil, campanhas, posts.

## hermes-business

Profile: business
Função: estratégia, vendas, planejamento, CRM simples, follow-up.

## hermes-orchestrator

Profile: orchestrator
Função: roteamento, decomposição de tarefas, síntese e coordenação.
```

**Commit:**

```bash
git add agents/registry.md
git commit -m "docs: add hermes agent registry"
```

---

## Task 3.3: Handoff manual antes do task bus

**Objective:** Roteamento simples sem automação pesada.

**Manual flow:**

1. Você pede algo ao orquestrador.
2. Orquestrador decide especialistas.
3. Orquestrador gera prompts para cada especialista.
4. Você aprova.
5. Especialista executa.
6. Orquestrador resume.

**Example:**

Pedido:

```text
quero criar uma campanha para vender meu serviço X
```

Orquestrador deve produzir:

```markdown
Especialistas recomendados:

1. hermes-business
   Motivo: definir oferta, público, preço e promessa.

2. hermes-marketing
   Motivo: criar copy, posts e funil.

3. hermes-dev
   Motivo: criar landing page ou automação se necessário.
```

**Ready when:** Um pedido multi-etapas consegue passar pelo orquestrador sem confusão.

---

# Level 4 — Time automatizado com cron e rotinas

## Objetivo

Criar rotinas que rodam sozinhas e notificam no Telegram.

## Automações iniciais recomendadas

1. Health check diário da VPS.
2. Backup semanal seguro.
3. Revisão semanal do Hermes.
4. Monitor GitHub.
5. Pipeline de conteúdo.

---

## Task 4.1: Health check diário

**Objective:** Receber no Telegram um resumo diário da saúde da VPS e do Hermes.

**Checks:**

- gateway rodando
- disco
- memória
- processos Hermes
- logs recentes com erro

**Possible command:**

```bash
hermes cron create '0 9 * * *'
```

Prompt do cron:

```text
Faça um health check da VPS e do Hermes Gateway. Verifique status do gateway, uso de disco, memória, processos Hermes e erros recentes em ~/.hermes/logs/gateway.log. Resuma em português e envie somente o que importa. Se houver problema, inclua comandos de correção.
```

**Ready when:** Você recebe relatório diário no Telegram.

---

## Task 4.2: Backup semanal seguro

**Objective:** Gerar backup sem segredos.

**Include:**

- control room
- scripts
- docs
- configs sanitizadas

**Exclude:**

- `.env`
- tokens
- `auth.json`
- `state.db`
- logs sensíveis

**Suggested backup path:**

```text
/home/luiz/backups/hermes-control-room/
```

**Ready when:** Existe backup restaurável sem vazar segredo.

---

## Task 4.3: Revisão semanal de evolução

**Objective:** Impedir que a operação vire bagunça.

Toda semana revisar:

- memórias
- skills criadas
- runbooks
- automações novas
- estado do GitHub
- próximos gargalos

Prompt do cron:

```text
Faça uma revisão semanal da operação Hermes. Verifique o control room, identifique documentação desatualizada, sugira melhorias, liste riscos e proponha uma automação nova de maior impacto. Responda em português com checklist curto.
```

**Ready when:** Você recebe uma revisão semanal útil e acionável.

---

# Ordem recomendada agora

## Próximas 7 ações práticas

1. Resolver GitHub:
   - renomear manualmente `funil-de-vendas` para `hermes`, ou criar repo novo `hermes`, ou dar acesso correto ao token.

2. Criar control room local:
   - `/home/luiz/hermes-control-room`

3. Criar arquivos Level 1:
   - README
   - roadmap
   - runbook
   - security
   - commands
   - inventory
   - env-map
   - `.gitignore`

4. Salvar no GitHub:
   - commit `docs: add hermes level 1 control room`

5. Estabilizar gateway via tmux:
   - scripts de start/stop/status

6. Criar Level 2:
   - profiles `dev`, `marketing`, `business`

7. Criar Level 3:
   - profile `orchestrator`
   - `agents/registry.md`

---

# Resumo

Estamos aqui:

```text
Level 1 inicial:
Hermes pessoal + Telegram + VPS
```

Próximo marco:

```text
Level 1 completo:
Hermes documentado + gateway estável + GitHub control room
```

Depois:

```text
Level 2:
Agentes especialistas diretos
```

Depois:

```text
Level 3:
Orquestrador
```

Depois:

```text
Level 4:
Automações recorrentes e time de agentes
```

Recomendação: resolver GitHub e salvar o control room antes de criar especialistas. Sem isso, a operação cresce rápido e vira bagunça.
