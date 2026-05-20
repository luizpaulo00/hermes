# hermes-main backup notes

## Objetivo

Backups devem permitir restaurar a documentação e scripts operacionais sem vazar segredos.

## Fonte do backup

Repo/control room local:

```text
/home/luiz/hermes-github
```

## Destino

```text
/home/luiz/backups/hermes-control-room/
```

## Pode entrar no backup

- `README.md`
- `plans/`
- `agents/`
- `shared/`
- `scripts/`
- arquivos versionados seguros do control room

## Não pode entrar no backup

- `~/.hermes/.env`
- `~/.hermes/auth.json`
- `~/.hermes/state.db`
- `~/.hermes/logs/`
- `.git/`
- qualquer token, PAT, cookie ou chave privada

## Script seguro

```bash
/home/luiz/hermes-github/scripts/weekly-backup.sh
```

O script:

1. roda `scripts/check-no-secrets.py`;
2. usa `git archive` do `HEAD`, evitando `.git/` e arquivos não versionados;
3. gera `.tgz` e `.sha256` em `/home/luiz/backups/hermes-control-room/`;
4. mantém os 12 backups mais recentes;
5. imprime um resumo seguro para Telegram.

## Cron job

```bash
hermes cron list
hermes cron run 1453330e293a
```

Job:

- ID: `1453330e293a`
- Nome: `Hermes weekly safe backup`
- Schedule: `0 8 * * 1`
- Entrega: Telegram de origem/home do Luiz

## Restaurar

```bash
mkdir -p /tmp/hermes-restore
sha256sum -c /home/luiz/backups/hermes-control-room/<arquivo>.tgz.sha256
tar -xzf /home/luiz/backups/hermes-control-room/<arquivo>.tgz -C /tmp/hermes-restore
```
