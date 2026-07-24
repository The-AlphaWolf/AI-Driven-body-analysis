# StyleSense AI backend — Hugging Face Spaces (Docker SDK)
#
# Spaces expects the app on port 7860 and runs the container as a non-root
# user with UID 1000. Everything below follows from those two constraints.
FROM python:3.12-slim

# MediaPipe's C bindings dlopen libGLESv2 and libEGL even for CPU-only
# inference on headless images, so libgles2/libegl1 are not optional — without
# them the container builds and serves fine and only fails on the first
# analyse request. libgomp is for scikit-learn, libglib for OpenCV.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libgles2 \
        libegl1 \
        libglib2.0-0 \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Spaces runs as UID 1000. Creating the user up front means the app never
# needs to write anywhere it does not own.
RUN useradd --create-home --uid 1000 appuser
USER appuser
ENV PATH="/home/appuser/.local/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOME=/home/appuser

WORKDIR /home/appuser/app

# Dependencies first so a source change does not re-download MediaPipe.
COPY --chown=appuser:appuser backend/requirements.txt ./
RUN pip install --no-cache-dir --user -r requirements.txt

COPY --chown=appuser:appuser backend/ ./

ENV FLASK_APP=wsgi.py \
    FLASK_ENV=production \
    PORT=7860

EXPOSE 7860

# Migrations run at boot rather than in the build: the build has no access
# to DATABASE_URL, and Spaces has no release phase to hang them off.
#
# One worker with threads, not multiple processes. Each worker would hold
# its own copy of the ~13MB of landmarker models plus the TFLite runtime,
# and the analysis endpoint is IO- and CPU-bound in C, not in the GIL.
# The timeout is generous because a cold request pays the model load.
CMD ["sh", "-c", "flask db upgrade && exec gunicorn wsgi:app \
    --bind 0.0.0.0:${PORT:-7860} \
    --workers 1 \
    --threads 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -"]
