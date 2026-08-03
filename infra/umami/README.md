# Umami — self-hosted, cookieless analytics

Chosen over GA4 because it sets no cookies and collects no personal data, so under
GDPR/ePrivacy it needs **no consent banner** — which means it measures ~100% of
visitors instead of the ~50% who accept a GA4 banner. For a company selling on
genetic-privacy trust, "we don't track you" is also worth saying out loud.

## Run it locally

```bash
cd infra/umami
docker compose up -d
open http://localhost:3000        # admin / umami — change this immediately
```

## Production hosting

Vercel's free Hobby tier is **non-commercial only**, so it is not an option for
GenePlaza. Realistic choices:

| Host | Cost | Notes |
|---|---|---|
| **AWS Lightsail** | ~$5/mo | You already run S3 + CloudFront; same console, same billing |
| **The existing WordPress box** (`46.225.143.92`) | free | Idle since the blog moved to Pages. Best value *if you still control it* |
| Fly.io | ~$3–5/mo | Fine, another vendor to manage |
| Railway | ~$5/mo | Easiest deploy, another vendor |
| Vercel Pro | $20/mo | More than Plausible's €9 — no reason to pick this |

Whatever you choose, serve it from **`analytics.geneplaza.com`**. First-party means
ad-blockers do not strip it; a third-party domain would lose a chunk of traffic.
The compose file also renames the tracker to `/gp.js`, because blocklists target
`/umami.js` and `/script.js` by name.

## Deploying (Lightsail or any Docker host)

1. Create a $5 Ubuntu instance, open ports 80/443
2. Install Docker, copy `docker-compose.yml` across
3. Set real secrets:
   ```bash
   export APP_SECRET=$(openssl rand -hex 32)
   # and change POSTGRES_PASSWORD from the default
   ```
4. Put Caddy or nginx in front for TLS:
   ```
   analytics.geneplaza.com {
       reverse_proxy localhost:3000
   }
   ```
5. GoDaddy DNS → `A` record, name `analytics`, value = the instance IP
6. Log in, change the admin password, add website `blog.geneplaza.com`
7. Copy the **Website ID** into `site/content/_data/site.json`

## Wiring the blog to it

```json
"analytics": {
  "provider": "umami",
  "umamiSrc": "https://analytics.geneplaza.com/gp.js",
  "umamiWebsiteId": "<website id>"
}
```

Push; CI deploys. No consent banner is rendered for cookieless providers.

## What to actually watch

Umami answers the question that justifies the spend:

- **Referrers** — where readers come from
- **Pages** — which of the 51 posts earn traffic
- **Outbound links** — clicks to `geneplaza.com/app-store/<id>`, tracked automatically,
  which is the closest thing to attribution before checkout

Set up a goal on outbound clicks to the app store. That converts "the blog gets
traffic" into "the blog sent N people to a product page this month".

## Backups

The Postgres volume holds all history. On any Docker host:

```bash
docker compose exec db pg_dump -U umami umami | gzip > umami-$(date +%F).sql.gz
```

Analytics history cannot be reconstructed. Put this on a weekly cron.
