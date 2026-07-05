# 🎨 StyleSense AI — Personal Style & Body Analysis System

> AI-powered fashion recommendations based on your unique face shape, skin tone, and body proportions.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-green.svg)](https://flask.palletsprojects.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791.svg)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Overview

StyleSense AI analyzes uploaded photos using computer vision to detect:
- **Face Shape** — Oval, round, square, heart, oblong, or diamond classification using MediaPipe Face Mesh landmark geometry
- **Skin Tone** — Depth (fair → deep) and undertone (warm/cool/neutral) via k-means clustering in LAB color space
- **Body Proportions** — Hourglass, pear, apple, rectangle, or inverted triangle classification using MediaPipe Pose

These attributes feed into a **weighted recommendation engine** that generates personalized styling advice across clothing silhouettes, necklines, color palettes, patterns, accessories, and hairstyles — each with an explanation of *why* it suits your features.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│              React + Vite + TailwindCSS v4                   │
│         (Landing, Auth, Upload, Results, Dashboard)          │
│                    Deployed to Vercel                         │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST API (JSON + Multipart)
                       │ JWT Auth Header
┌──────────────────────▼──────────────────────────────────────┐
│                        Backend                               │
│                   Python Flask API                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐ │
│  │   Auth   │  │   Face   │  │   Skin   │  │    Body     │ │
│  │  Routes  │  │ Analysis │  │ Analysis │  │  Analysis   │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────────┘ │
│                ┌──────────────────────────┐                   │
│                │  Recommendation Engine   │                   │
│                │  (Weighted Scoring)      │                   │
│                └──────────────────────────┘                   │
│                    Deployed to Render                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
          ┌────────────▼────────────┐
          │      PostgreSQL         │
          │  (Users + Analyses)     │
          │  Render / Neon / Local  │
          └─────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Frontend** | React 18 + Vite | Fast HMR, modern build tooling |
| **Styling** | TailwindCSS v4 | Utility-first, rapid UI development |
| **Backend** | Flask 3.x | Lightweight, flexible Python API framework |
| **ORM** | SQLAlchemy + Flask-Migrate | Type-safe models, auto-generated migrations |
| **Database** | PostgreSQL | Relational integrity, JSON columns, free cloud tiers |
| **Auth** | JWT (Flask-JWT-Extended) | Stateless, token-based authentication |
| **Computer Vision** | OpenCV + MediaPipe | Face mesh (478 landmarks), pose estimation — all local, no paid APIs |
| **ML** | scikit-learn (k-means) | Skin tone clustering in LAB color space |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 15+

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

# Create database
psql -U postgres -c "CREATE DATABASE stylesense;"

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL and JWT_SECRET_KEY

# Run migrations
flask db upgrade

# Start dev server
flask run --debug
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 📸 Screenshots

> _Screenshots will be added after the UI is complete._

---

## 🔮 Future Improvements

### Upgrading the Recommendation Engine to a Trained Model

The current recommendation engine uses a **weighted feature-vector scoring algorithm** that matches user attributes against a structured rules dataset. This architecture was intentionally designed to be **model-ready**:

1. **Current**: Rules-based scoring with category-dependent weights
2. **Next step**: Train a collaborative filtering or content-based model on user feedback (which recommendations they saved/liked)
3. **Advanced**: Fine-tune a multimodal model that takes the raw image features (not just classifications) as input

The scoring function in `recommendation.py` accepts a standardized feature vector, making it a drop-in replacement to swap the rules engine for a trained classifier.

---

## 📄 License

MIT
