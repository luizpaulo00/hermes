#!/usr/bin/env bash
set -euo pipefail

REPO="/home/luiz/hermes-github"
BACKUP_DIR="/home/luiz/backups/hermes-control-room"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
ARCHIVE="$BACKUP_DIR/hermes-control-room-$STAMP.tgz"
SHA_FILE="$ARCHIVE.sha256"

mkdir -p "$BACKUP_DIR"

cd "$REPO"

python3 scripts/check-no-secrets.py >/tmp/hermes-backup-secret-check.txt

COMMIT="$(git rev-parse --short HEAD)"
DIRTY="$(git status --short)"

git archive --format=tar.gz --prefix="hermes-control-room/" -o "$ARCHIVE" HEAD
sha256sum "$ARCHIVE" > "$SHA_FILE"

# Keep roughly the latest 12 weekly backups; old files are safe to prune.
find "$BACKUP_DIR" -maxdepth 1 -type f -name 'hermes-control-room-*.tgz' -printf '%T@ %p\n' \
  | sort -rn \
  | awk 'NR>12 {print $2}' \
  | xargs -r rm -f
find "$BACKUP_DIR" -maxdepth 1 -type f -name 'hermes-control-room-*.tgz.sha256' -printf '%T@ %p\n' \
  | sort -rn \
  | awk 'NR>12 {print $2}' \
  | xargs -r rm -f

SIZE="$(du -h "$ARCHIVE" | cut -f1)"
SHA="$(cut -d' ' -f1 "$SHA_FILE")"
COUNT="$(find "$BACKUP_DIR" -maxdepth 1 -type f -name 'hermes-control-room-*.tgz' | wc -l)"

{
  echo "✅ Backup semanal Hermes criado"
  echo "Arquivo: $ARCHIVE"
  echo "Tamanho: $SIZE"
  echo "Commit: $COMMIT"
  echo "SHA256: $SHA"
  echo "Backups mantidos: $COUNT"
  if [[ -n "$DIRTY" ]]; then
    echo "Aviso: repo tinha mudanças não commitadas; backup foi feito do HEAD commitado."
  else
    echo "Repo limpo no momento do backup."
  fi
  echo "Secret scan: OK"
}
