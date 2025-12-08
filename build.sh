set -euo pipefail

# 1. Récupérer le numéro de version -> Usage : ./build.sh 1.1.0
VERSION="${1:-}"

if [[ -z "$VERSION" ]]; then
    echo "Usage: $0 X.Y.Z"
    exit 1
fi

# 2. Lancer le linter Ruff et s'arrêter en cas d'erreur
echo "➡ Vérification du code avec Ruff..."
pipenv run ruff check .
echo "Linter OK, build possible."

# 3. Mettre à jour VERSION.txt
echo "$VERSION" > VERSION.txt
echo "VERSION.txt mis à jour avec $VERSION"

# 4. Créer le tag Git sur le commit actuel
git tag "$VERSION"
echo "Tag Git $VERSION créé"

# 5. Générer l’archive ZIP de la version
ARCHIVE_NAME="todolist-$VERSION.zip"
git archive --format=zip --output "$ARCHIVE_NAME" HEAD
echo "Archive créée : $ARCHIVE_NAME"

echo "Build terminé pour la version $VERSION"
