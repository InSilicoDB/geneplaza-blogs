# Deploying the blog to geneplaza.com/blog

Serves the 11ty blog from `geneplaza.com/blog/*` without adding a route to the Ember
app. CloudFront matches cache behaviours by path pattern **before** origin or error
handling, so a dedicated `/blog/*` behaviour returns real 200s and the SPA fallback
never fires.

```
CloudFront (geneplaza.com)
├── behaviour "/blog/*"  → origin B: S3 bucket with the 11ty build   ← new
└── behaviour "*"        → origin A: Ember S3 bucket + SPA fallback   ← untouched
```

## Verified current state

| Property | Value |
|---|---|
| `geneplaza.com` | S3 origin behind CloudFront (`server: AmazonS3`, `via: CloudFront`) |
| Unknown paths | 200 + `x-cache: Error from cloudfront` — SPA fallback via custom error responses |
| `geneplaza.com/blog` | 301 → `blog.geneplaza.com/blog/` (remove this in step 6) |
| `blog.geneplaza.com` | WordPress, nginx 1.19, PHP 7.0.15 |
| WP canonical URLs | already `https://www.geneplaza.com/blog/<lang>/<slug>/` |

## Steps

### 1. Build

The production site is `Blogs/blog_geneplaza/`.

```bash
cd Blogs/blog_geneplaza
npm run check     # markdown gate + build gate
npm run build
```

**`pathPrefix` stays `"/"`.** Every post's `permalink` already begins with `blog/`,
so the build emits `_site/blog/<lang>/<slug>/index.html`. Setting `pathPrefix` to
`/blog/` as well would produce `/blog/blog/...`.

For the same reason images are referenced as `/blog/images/...`, not
`/images/blog/...` — anything outside `/blog/*` falls through to the Ember origin.

### 2. Create the origin bucket

```bash
aws s3 mb s3://geneplaza-blog-static
aws s3 sync _site/ s3://geneplaza-blog-static/ --delete
```

Sync to the bucket **root**, not to `/blog/` — the `blog/` prefix is already baked
into the build output. Verify before pointing CloudFront at it:

```bash
aws s3 ls s3://geneplaza-blog-static/blog/en/ | head
```

Keep the bucket private and reach it through an Origin Access Control, matching how
the Ember bucket is served.

### 3. Add the CloudFront function

`blog-redirects.js` in this directory does two jobs: 301s the 18 legacy WordPress
URLs consolidated during migration, and rewrites directory URIs to `/index.html`
(S3 origins do not do this for sub-paths).

```bash
aws cloudfront create-function \
  --name blog-redirects \
  --function-config Comment="blog 301s + index rewrite",Runtime=cloudfront-js-2.0 \
  --function-code fileb://blog-redirects.js

aws cloudfront publish-function --name blog-redirects --if-match <ETag>
```

### 4. Add the cache behaviour

On the `geneplaza.com` distribution:

- **Path pattern**: `/blog/*`
- **Origin**: the new bucket
- **Viewer protocol policy**: redirect HTTP to HTTPS
- **Function association**: viewer-request → `blog-redirects`
- **Precedence**: above the default `*` behaviour

### 5. Invalidate

```bash
aws cloudfront create-invalidation --distribution-id <ID> --paths "/blog/*"
```

### 6. Remove the outbound redirect

Delete the rule sending `geneplaza.com/blog` → `blog.geneplaza.com/blog/`. WordPress
already believes it lives at `/blog`, so this redirect is the anomaly.

### 7. Redirect the old subdomain

On `blog.geneplaza.com` (nginx):

```nginx
location / {
    return 301 https://www.geneplaza.com/blog$request_uri;
}
```

Keep WordPress reachable read-only until traffic settles, then retire it.

### 8. Retire genesofthrones.com as a blog

Point it at a product landing page for the app instead. It should not host content
competing with `geneplaza.com/blog`.

## Verification

```bash
curl -sI https://www.geneplaza.com/blog/en/cheddar-man-dark-skin-blue-eyes/ | head -1
# expect: HTTP/2 200

curl -sI https://www.geneplaza.com/blog/fr/adn/ | grep -i location
# expect: /blog/fr/press/

curl -sI https://www.geneplaza.com/app-store/61 | head -1
# expect: HTTP/2 200 - Ember still works
```

That third check matters most: it confirms the new behaviour did not shadow the app.

Also confirm the sitemap:

```bash
curl -s https://www.geneplaza.com/blog/sitemap.xml | grep -c '<url>'
# expect: 52
```

### Submit the sitemap

`/blog/sitemap.xml` carries all 52 URLs with reciprocal `xhtml:link hreflang`
entries. Add it in Google Search Console, and fold the rules from
`_site/blog/robots.txt` into the site-wide `robots.txt` at the domain root —
crawlers only read `/robots.txt`.

## Ordering note

Do this **before** publishing the app-post backlog. Migrating 27 URLs is cheap;
migrating 80 indexed URLs later means eating a ranking dip.
