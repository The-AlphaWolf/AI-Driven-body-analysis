---
title: StyleSense AI API
emoji: 🎨
colorFrom: purple
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: Face shape, skin tone and body proportion analysis API
---

# StyleSense AI — Backend API

Computer-vision backend for [StyleSense AI](https://github.com/The-AlphaWolf/AI-Driven-body-analysis).
Analyses an uploaded photo for face shape (MediaPipe Face Mesh), skin tone
(k-means in LAB space) and body proportions (MediaPipe Pose), then returns
weighted style recommendations.

This Space hosts the API only. The user interface is deployed separately.

## Endpoints

| Method | Path | Notes |
|---|---|---|
| `GET` | `/api/health` | Liveness check |
| `POST` | `/api/auth/register` | |
| `POST` | `/api/auth/login` | |
| `POST` | `/api/analysis/analyze` | Multipart: `face_image`, `body_image` |
| `GET` | `/api/history` | JWT required |
| `GET` | `/api/public/<token>` | Shared analysis, no auth |

## Required secrets

Set these in **Settings → Variables and secrets**:

| Name | Purpose |
|---|---|
| `DATABASE_URL` | Postgres connection string |
| `JWT_SECRET_KEY` | Token signing secret |
| `CORS_ORIGINS` | Comma-separated frontend origins |

The container refuses to start in production without a real `JWT_SECRET_KEY`
and a non-SQLite `DATABASE_URL` — an ephemeral filesystem would lose every
account on each restart.

## Note on uploaded photos

Photos are decoded in memory and never written to disk. Only a 200×200
thumbnail is retained, stored in the database and served exclusively to the
account that created it.
