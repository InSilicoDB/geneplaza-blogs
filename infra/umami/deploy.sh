#!/usr/bin/env bash
# One-shot Umami deploy. Run on a fresh Ubuntu host as a sudo-capable user.
#   scp -r infra/umami user@host:~/umami && ssh user@host 'cd umami && ./deploy.sh'
set -euo pipefail

DOMAIN="${DOMAIN:-analytics.geneplaza.com}"

if ! command -v docker >/dev/null; then
  echo "==> installing docker"
  curl -fsSL https://get.docker.com | sudo sh
  sudo usermod -aG docker "$USER" || true
fi

if [ ! -f .env ]; then
  echo "==> generating secrets"
  {
    echo "APP_SECRET=$(openssl rand -hex 32)"
    echo "POSTGRES_PASSWORD=$(openssl rand -hex 24)"
  } > .env
  chmod 600 .env
  echo "    wrote .env (keep it; losing POSTGRES_PASSWORD means losing the database)"
fi

sed -i "s/analytics\.geneplaza\.com/${DOMAIN}/g" Caddyfile
mkdir -p backups

echo "==> starting"
sudo docker compose -f docker-compose.prod.yml --env-file .env up -d

echo
echo "==> waiting for Umami"
for i in $(seq 1 30); do
  if sudo docker compose -f docker-compose.prod.yml exec -T umami wget -qO- http://localhost:3000 >/dev/null 2>&1; then
    echo "    up"
    break
  fi
  sleep 5
done

cat <<MSG

Done.

  1. Point DNS:  A record, name 'analytics', value $(curl -s -m 5 ifconfig.me || echo '<this host IP>')
  2. Caddy issues the TLS certificate automatically once DNS resolves
  3. Open https://${DOMAIN} and log in as admin / umami
  4. CHANGE THE ADMIN PASSWORD IMMEDIATELY
  5. Add website 'blog.geneplaza.com', copy its Website ID
  6. Put the ID in site/content/_data/site.json and push

MSG
