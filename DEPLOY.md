# Deploying StyleSense AI

Three pieces: a Postgres database, the backend as a Docker container, and the
frontend as a static site.

| Piece | Host | Why |
|---|---|---|
| Database | Neon | Free Postgres, no card, does not expire |
| Backend | Render (Docker) | Free container host; measured footprint is 356MB against a 512MB limit |
| Frontend | Vercel | Static build, global CDN |

### Why not Hugging Face or Vercel for the backend

Vercel's serverless functions cap a bundle at 250MB unzipped. MediaPipe,
OpenCV, scikit-learn and NumPy exceed that on their own.

Hugging Face Spaces was the original target, but free Spaces are static-only:
*"hosting Gradio and Docker Spaces on free cpu-basic requires a PRO
subscription."* If you have PRO, the Dockerfile works there unchanged — set
`app_port: 7860` in the Space README frontmatter.

### What the free Render plan costs you

- **Sleeps after 15 minutes idle.** The next request waits ~50s for a cold
  start, plus a few seconds for the landmarker models to load.
- **~0.1 CPU.** A single analysis takes tens of seconds rather than the two
  or three it takes on a real core.

Fine for a demo. Upgrade the instance type if it becomes something people
actually use.

---

## 1. Database — Neon

1. Sign up at [neon.tech](https://neon.tech) (GitHub login, no card)
2. Create a project; a database comes with it
3. Copy the **pooled** connection string:

```
postgresql://user:password@ep-something-pooler.region.aws.neon.tech/dbname?sslmode=require
```

Nothing else to do — the backend runs its own migrations at boot.

> The app rejects a SQLite URL when `FLASK_ENV=production`. On a host with an
> ephemeral filesystem, SQLite loses every account on each restart, so this
> fails loudly rather than quietly.

---

## 2. Backend — Render

### Create the service

1. Sign up at [render.com](https://render.com) with GitHub
2. **New → Blueprint**, pick this repository
3. Render reads [`render.yaml`](render.yaml) and proposes `stylesense-api`
4. Apply

The blueprint sets the Docker runtime, the free plan, `/api/health` as the
health check, and generates `JWT_SECRET_KEY` for you — nobody has to invent
or handle that value.

### Fill in the two secrets

**Dashboard → stylesense-api → Environment:**

| Key | Value |
|---|---|
| `DATABASE_URL` | The Neon pooled connection string |
| `CORS_ORIGINS` | Your Vercel URL, e.g. `https://stylesense-ai.vercel.app` |

Both are marked `sync: false` in the blueprint so they never live in git.
`CORS_ORIGINS` takes a comma-separated list — include every origin the
frontend is served from, including preview deployments if you use them.

You will not know the Vercel URL until step 3, so set a placeholder now and
come back.

### Verify

```bash
curl https://stylesense-api.onrender.com/api/health
```

Expect `{"service":"StyleSense AI API","status":"healthy"}`. The first
request after a deploy or a sleep is slow.

---

## 3. Frontend — Vercel

1. [Import the repo](https://vercel.com/new)
2. **Root directory: `frontend`** — this is the setting people miss; without
   it the build cannot find `package.json`
3. Framework preset: Vite (detected automatically)
4. Environment variable:

   | Name | Value |
   |---|---|
   | `VITE_API_URL` | `https://stylesense-api.onrender.com` |

   No trailing slash. It is baked in at build time, so changing it later
   needs a redeploy, not just a restart.

5. Deploy

`frontend/vercel.json` handles the SPA rewrites — without them a refresh on
`/dashboard` or a shared `/s/<token>` link 404s.

### Close the loop

Set `CORS_ORIGINS` on Render to the URL Vercel just gave you. Render restarts
on an environment change. Until you do this, every API call from the browser
fails CORS.

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
down, keep them — the container will build, boot and serve health checks
fine, then fail on the first analysis request.

**Service starts, then every browser request fails**
`CORS_ORIGINS` does not include the frontend's origin. Check the exact scheme
and host, and note that a Vercel preview URL differs from production.

**`RuntimeError: JWT_SECRET_KEY is still the development default`**
Working as intended. On Render the blueprint generates one; if you created
the service by hand instead, add it.

**First request takes a minute**
Free-plan cold start plus the lazy model load. Subsequent requests reuse both.

**Analysis is very slow but succeeds**
~0.1 CPU on the free plan. Upgrade the instance type.

**Deploy succeeds but the service restarts in a loop**
Migrations run in the start command, so a bad `DATABASE_URL` exits the
container. Check the Render logs for the `flask db upgrade` output.
