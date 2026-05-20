# hermes-main backup notes

## Objetivo

Backups devem permitir restaurar a documentação e scripts operacionais sem vazar segredos.

## Pode entrar no backup

- `/home/luiz/hermes-control-room/README.md`
- `/home/luiz/hermes-control-room/plans/`
- `/home/luiz/hermes-control-room/agents/`
- `/home/luiz/hermes-control-room/shared/`
- `/home/luiz/hermes-control-room/scripts/`

## Não pode entrar no backup

- `~/.hermes/.env`
- `~/.hermes/auth.json`
- `~/.hermes/state.db`
- `~/.hermes/logs/`
- qualquer token, PAT, cookie ou chave privada

## Comando seguro inicial

```bash
tar --exclude='.git' --exclude='*.log' --exclude='*.db' --exclude='.env' -czf ~/hermes-control-room-backup.tgz -C /home/luiz hermes-control-room
```

## Próximo passo futuro

No Level 4, criar job semanal para gerar backup seguro e reportar no Telegram.
