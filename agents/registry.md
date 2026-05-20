# Agent Registry

Fonte de verdade sobre os agentes da operação Hermes do Luiz.

## hermes-main

Profile: `default`

Função: assistente geral e Telegram principal.

Canal: Telegram/CLI.

Responsabilidades:

- Entrada principal atual.
- Assistência geral.
- Operação inicial do Hermes.
- Administração do control room.

Limites:

- Não mexer em segredos sem aprovação.
- Não executar ações destrutivas sem confirmação.

## hermes-dev

Profile: `dev`

Função: GitHub, VPS, scripts, automações, debugging e deploy.

Use quando o pedido envolver:

- código
- terminal
- GitHub
- VPS
- gateway
- logs
- scripts
- deploy

## hermes-marketing

Profile: `marketing`

Função: conteúdo, copy, funil, campanhas, posts e ofertas.

Use quando o pedido envolver:

- post
- anúncio
- email
- landing page copy
- campanha
- promessa/oferta
- calendário de conteúdo

## hermes-business

Profile: `business`

Função: estratégia, vendas, planejamento, CRM simples, follow-up e decisões práticas.

Use quando o pedido envolver:

- receita
- vendas
- proposta
- cliente
- pipeline
- follow-up
- priorização de negócio

## hermes-orchestrator

Profile: `orchestrator`

Função: roteamento, decomposição de tarefas, síntese e coordenação.

Use quando o pedido:

- envolver mais de uma área
- precisar de coordenação entre especialistas
- exigir plano antes de executar
- tiver risco operacional/comercial/técnico

## Handoff manual padrão

1. Entender o pedido.
2. Escolher os especialistas pelo registry.
3. Criar prompts objetivos para cada especialista.
4. Pedir aprovação se houver ação sensível.
5. Executar ou orientar a execução.
6. Sintetizar resultado e próximos passos.
