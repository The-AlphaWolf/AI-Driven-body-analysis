# Deploying StyleSense AI

Three pieces: a Postgres database, the backend as a Docker container, and the
frontend as a static site.

| Piece | Host | Why |
|---|---|---|
| Database | Neon | Free tier, no card, survives redeploys |
| Backend | Hugging Face Spaces (Docker) | 16GB RAM and no card; the CV dependencies unzip to ~250MB, which is over Vercel's serverless function limit |
| Frontend | Vercel | Static build, global CDN |

---

## 1. Database

Create a Postgres database on [Neon](https://neon.tech) and copy the pooled
connection string. It looks like:

```
postgresql://user:password@ep-something-pooler.region.aws.neon.tech/dbname?sslmode=require
```

Nothing else to do — the backend runs its migrations at boot.

> The app rejects a SQLite URL when `FLASK_ENV=production`. On a host with an
> ephemeral filesystem, SQLite loses every account on each restart, so this
> fails loudly rather than quietly.

---

## 2. Backend — Hugging Face Space

### Create the Space

1. [New Space](https://huggingface.co/new-space)
2. **SDK: Docker**, blank template
3. Visibility: public or private, either works

### Add the secrets

**Settings → Variables and secrets → New secret:**

| Name | Value |
|---|---|
| `DATABASE_URL` | The Neon connection string |
| `JWT_SECRET_KEY` | `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `CORS_ORIGINS` | Your Vercel URL, e.g. `https://stylesense.vercel.app` |

Set these **before** the first build. The container refuses to start in
production with the development JWT secret — a shipped default means anyone
who has read the repo can mint a token for any account.

`CORS_ORIGINS` takes a comma-separated list. Include every origin the
frontend is served from, including preview deployments if you use them.

### Push the code

A Space is its own git repo and needs a README carrying Space frontmatter at
its root, which this repo's README cannot also be. So the sync script
assembles what a Space needs and pushes that:

```bash
HF_TOKEN=hf_your_write_token ./deploy/huggingface/sync.sh your-username/your-space
```

Create the token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
with **write** access.

To do it automatically on every push to `master`, add `HF_TOKEN` and
`HF_SPACE` as repository secrets and the included
[`deploy-space.yml`](.github/workflows/deploy-space.yml) workflow handles it.

### Verify

```bash
curl https://your-username-your-space.hf.space/api/health
```

Expect `{"service":"StyleSense AI API","status":"healthy"}`. The first
request after a build is slow — the landmarker models load lazily.

---

## 3. Frontend — Vercel

1. [Import the repo](https://vercel.com/new)
2. **Root directory: `frontend`** — this is the setting people miss; without
   it the build cannot find `package.json`
3. Framework preset: Vite (detected automatically)
4. Environment variable:

   | Name | Value |
   |---|---|
   | `VITE_API_URL` | `https://your-username-your-space.hf.space` |

   No trailing slash. It is baked in at build time, so changing it later
   needs a redeploy, not just a restart.

5. Deploy

`vercel.json` handles the SPA rewrites — without them a refresh on
`/dashboard` or a shared `/s/<token>` link 404s.

### Close the loop

Set `CORS_ORIGINS` on the Space to the Vercel URL Vercel just gave you, then
restart the Space. Until you do, every API call from the browser fails CORS.

---

## Running it locally

```bash
# Backend
cd backend
python -m venv venv
venv/Scripts/activate          # Windows
# source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
cp .env.example .env           # then edit it
flask db upgrade
python seed_demo.py            # optional: demo@stylesense.ai / demo1234
flask run --port 5000
```

```bash
# Frontend
cd frontend
npm install
cp .env.example .env.local     # defaults to http://localhost:5000
npm run dev
```

### With Docker

```bash
docker build -t stylesense-backend .
docker run -p 7860:7860 \
  -e DATABASE_URL="postgresql://..." \
  -e JWT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')" \
  -e CORS_ORIGINS="http://localhost:5173" \
  stylesense-backend
```

---

## Troubleshooting

**`OSError: libGLESv2.so.2: cannot open shared object file`**
MediaPipe's C bindings dlopen GLES and EGL even for CPU-only inference. The
Dockerfile installs `libgles2` and `libegl1` for this. If you slim the image
down, keep them — the container will build and serve fine and then fail on
the first analysis request.

**Space starts, then every browser request fails**
`CORS_ORIGINS` does not include the frontend's origin. Check the exact
scheme and host, and note that a Vercel preview URL differs from production.

**`RuntimeError: JWT_SECRET_KEY is still the development default`**
Working as intended. Set the secret.

**First analysis takes 10–30 seconds**
The landmarker models load on the first request that needs them. Subsequent
requests reuse them. A Space that has gone to sleep pays this again.

**Migrations did not run**
They run in the container's start command. If `DATABASE_URL` is wrong the
container exits during `flask db upgrade` — check the Space's build and
container logs.
