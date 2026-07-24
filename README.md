# 🎨 StyleSense AI — Personal Style & Body Analysis System

> AI-powered fashion recommendations based on your unique face shape, skin tone, and body proportions.

[![CI](https://github.com/The-AlphaWolf/AI-Driven-body-analysis/actions/workflows/ci.yml/badge.svg)](https://github.com/The-AlphaWolf/AI-Driven-body-analysis/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-green.svg)](https://flask.palletsprojects.com)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791.svg)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Overview

StyleSense AI analyses uploaded photos using computer vision to detect:

- **Face shape** — oval, round, square, heart, oblong or diamond, from MediaPipe Face Mesh landmark geometry
- **Skin tone** — depth (fair → deep) and undertone (warm/cool/neutral), via k-means clustering in LAB colour space
- **Body proportions** — hourglass, pear, apple, rectangle or inverted triangle, from MediaPipe Pose

Those attributes feed a **weighted recommendation engine** that produces styling
advice across silhouettes, necklines, colour palettes, patterns, accessories and
hairstyles — each with an explanation of *why* it suits you.

You can keep or reject each suggestion, collect the ones you liked, export the
whole thing as a PDF, and share a read-only link that omits your photo.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│              React + Vite + TailwindCSS v4                   │
│    (Landing, Auth, Upload, Results, Dashboard, Saved,        │
│                  Public share pages)                         │
│                    Deployed to Vercel                        │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST (JSON + multipart), JWT in header
┌──────────────────────▼──────────────────────────────────────┐
│                        Backend                               │
│                    Python Flask API                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐  │
│  │   Auth   │  │   Face   │  │   Skin   │  │    Body     │  │
│  │  Routes  │  │ Analysis │  │ Analysis │  │  Analysis   │  │
│  └──────────┘  └──────────┘  └──────────┘  └─────────────┘  │
│  ┌──────────────────────┐  ┌───────────┐  ┌──────────────┐  │
│  │ Recommendation Engine│  │  Feedback │  │ PDF + Share  │  │
│  │  (weighted scoring)  │  │   Loop    │  │              │  │
│  └──────────────────────┘  └───────────┘  └──────────────┘  │
│              Docker container on Render                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
          ┌────────────▼────────────┐
          │      PostgreSQL         │
          │  Users · Analyses ·     │
          │  Feedback · Blocklist   │
          │        (Neon)           │
          └─────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Frontend** | React 19 + Vite | Fast HMR, modern build tooling |
| **Styling** | TailwindCSS v4 | Utility-first, rapid UI development |
| **Backend** | Flask 3.x | Lightweight, flexible Python API framework |
| **ORM** | SQLAlchemy + Flask-Migrate | Typed models, generated migrations |
| **Database** | PostgreSQL | Relational integrity, JSON columns, free cloud tiers |
| **Auth** | JWT (Flask-JWT-Extended) | Stateless tokens, database-backed revocation |
| **Computer vision** | OpenCV + MediaPipe | Face mesh (478 landmarks), pose estimation — all local, no paid APIs |
| **ML** | scikit-learn (k-means) | Skin tone clustering in LAB colour space |
| **PDF** | ReportLab | No headless browser, no system libraries |

---

## ✨ Features

- **Analyse a face photo, a body photo, or both.** Each is optional; the engine adapts to whatever it can detect.
- **Confidence scores** on every detection, with a warning when lighting makes the skin reading unreliable.
- **Explained recommendations** — every suggestion carries the reasons it was chosen for you.
- **Keep or reject** any suggestion. Liked items collect on a Saved page.
- **PDF export** — a printable report you can take shopping.
- **Revocable share links** that expose the advice but not your photo.
- **History** of every analysis, with thumbnails.

### On your photos

Uploaded images are decoded in memory and **never written to disk**. Only a
200×200 thumbnail is kept, stored in the database, and served exclusively to
the account that created it. A share link does not include it.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 15+ (or nothing — it falls back to SQLite locally)

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

cp .env.example .env         # then edit it
flask db upgrade
python seed_demo.py          # optional sample data

flask run --port 5000
```

The seed script creates `demo@stylesense.ai` / `demo1234` with five example
analyses, so you can look at a populated dashboard without uploading anything.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local   # defaults to http://localhost:5000
npm run dev
```

### Tests

```bash
cd backend && pytest         # 149 tests, ~20s
cd frontend && npm run lint && npm run build
```

---

## 🌍 Deployment

See **[DEPLOY.md](DEPLOY.md)** for the full walkthrough — Neon for Postgres,
a Docker service on Render for the API, Vercel for the frontend.

The backend needs a container host. It cannot run on Vercel's serverless
functions, where MediaPipe, OpenCV, scikit-learn and NumPy blow past the
250MB bundle limit on their own; and free Hugging Face Spaces are static-only
now, with Docker behind PRO. The image is a plain Dockerfile binding `$PORT`,
so it moves to any container host without changes.

Measured footprint: **158MB idle, 356MB peak** with both landmarker models
loaded — comfortably inside Render's 512MB free plan.

---

## 🔮 Future Improvements

### Upgrading the recommendation engine to a trained model

The engine currently scores a structured rules dataset against a standardised
feature vector, which was a deliberate choice — it is the same shape a model
would take.

1. **Now**: weighted rules scoring with category-dependent weights, and hard
   exclusion when a rule contradicts the attribute its category is about
2. **Next**: train on the feedback the app now collects — which recommendations
   real people kept and which they rejected, joined to the attributes that
   produced them
3. **Later**: a multimodal model taking raw image features rather than
   classifications

The `feedback` table exists to make step 2 possible; it is the dataset.

---

## 📄 License

MIT — see [LICENSE](LICENSE).
