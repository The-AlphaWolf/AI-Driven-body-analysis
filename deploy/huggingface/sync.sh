#!/usr/bin/env bash
#
# Push the backend to a Hugging Face Space.
#
# A Space is its own git repo and needs a README with Space frontmatter at
# its root, which this repo's README cannot carry. So rather than pushing
# this repo directly, the script assembles the subset a Space needs into a
# scratch directory and pushes that as a single commit.
#
# Usage:
#   HF_TOKEN=hf_xxx ./deploy/huggingface/sync.sh <username>/<space-name>
#
# The token needs write access to the Space. Create one at
# https://huggingface.co/settings/tokens
set -euo pipefail

SPACE="${1:-}"
if [[ -z "$SPACE" ]]; then
  echo "usage: $0 <username>/<space-name>" >&2
  exit 1
fi

if [[ -z "${HF_TOKEN:-}" ]]; then
  echo "HF_TOKEN is not set." >&2
  exit 1
fi

REPO_ROOT="$(git rev-parse --show-toplevel)"
STAGING="$(mktemp -d)"
trap 'rm -rf "$STAGING"' EXIT

echo "Assembling Space contents..."
cp "$REPO_ROOT/Dockerfile"                      "$STAGING/"
cp "$REPO_ROOT/.dockerignore"                   "$STAGING/"
cp "$REPO_ROOT/deploy/huggingface/README.md"    "$STAGING/"
cp -r "$REPO_ROOT/backend"                      "$STAGING/backend"

# Never ship local state or secrets to a public Space.
rm -rf "$STAGING/backend/venv" \
       "$STAGING/backend/instance" \
       "$STAGING/backend/.pytest_cache"
find "$STAGING/backend" -name '__pycache__' -type d -prune -exec rm -rf {} +
find "$STAGING/backend" -name '*.db' -delete
rm -f "$STAGING/backend/.env"

cd "$STAGING"
git init -q
git checkout -q -b main
git lfs install --local >/dev/null 2>&1 || true
# Spaces require the landmarker models to go through LFS.
git lfs track "*.task" >/dev/null 2>&1 || true
[[ -f .gitattributes ]] && git add .gitattributes

git add -A
git -c user.email=deploy@stylesense.local \
    -c user.name="StyleSense Deploy" \
    commit -qm "Deploy backend from $(git -C "$REPO_ROOT" rev-parse --short HEAD)"

echo "Pushing to https://huggingface.co/spaces/$SPACE ..."
git push -q --force "https://user:${HF_TOKEN}@huggingface.co/spaces/${SPACE}" main

echo "Done. Build logs: https://huggingface.co/spaces/${SPACE}?logs=build"
