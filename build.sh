#!/usr/bin/env bash
set -euo pipefail

# --- 1. Récupérer le numéro de version passé en paramètre ---
# Usage attendu : ./build.sh version=1.0.1

if [ $# -ne 1 ]; then
  echo "Usage: $0 version=X.Y.Z"
  exit 1
fi

RAW="$1"
VERSION="${RAW#version=}"

# Si l'argument n'était pas sous la forme "version=..."
if [ -z "$VERSION" ] || [ "$RAW" = "$VERSION" ]; then
  echo "Usage: $0 version=X.Y.Z"
  exit 1
fi

echo "➡ Version demandée : $VERSION"

# --- 2. Vérifier que le dépôt Git est propre ---

if ! git diff-index --quiet HEAD --; then
  echo "❌ Le dépôt n'est pas propre (des fichiers modifiés non commit)."
  echo "   Merci de committer ou stasher avant de lancer le build."
  exit 1
fi

# --- 3. Mettre à jour le fichier VERSION.txt ---

echo "$VERSION" > VERSION.txt
echo "✅ VERSION.txt mis à jour avec $VERSION"

# --- 4. Commit du bump de version ---

git add VERSION.txt
git commit -m "chore: bump version to $VERSION"
echo "✅ Commit créé pour la version $VERSION"

# --- 5. Créer le tag Git ---

git tag "$VERSION"
echo "✅ Tag Git $VERSION créé"

# --- 6. Générer l'archive zip de cette version ---

ARCHIVE_NAME="../todolist-$VERSION.zip"
git archive --format=zip --output "$ARCHIVE_NAME" "$VERSION"
echo "✅ Archive créée : $ARCHIVE_NAME"

echo "🎉 Build terminé pour la version $VERSION"
