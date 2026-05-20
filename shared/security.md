# Security rules

## Nunca commitar

- tokens;
- `.env`;
- `auth.json`;
- `state.db`;
- logs brutos;
- `config.yaml` com segredos;
- cookies, sessões, chaves privadas ou PATs.

## Pode commitar

- documentação;
- planos;
- runbooks;
- scripts sem segredos;
- templates sem valores reais;
- mapas de ambiente sem tokens.

## Onde ficam os segredos

- VPS: `~/.hermes/.env`, `~/.hermes/auth.json`, configs locais.
- GitHub: somente GitHub Secrets quando necessário.

## Rotina antes de push

Rodar verificações simples:

```bash
git status
python3 scripts/check-no-secrets.py
```

Se um token aparecer em chat ou arquivo, considerar revogar/regenerar.
