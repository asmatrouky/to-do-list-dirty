# 1. Récupérer le numéro de version
VERSION="$1"

if [ -z "$VERSION" ]; then
    echo "Usage: $0 X.Y.Z"
    exit 1
fi

# 2. Mettre à jour VERSION.txt
echo "$VERSION" > VERSION.txt
echo "VERSION.txt mis à jour avec $VERSION"

# 3. Taguer le commit actuel
git tag "$VERSION"
echo "Tag $VERSION créé"

# 4. Générer l’archive ZIP
ARCHIVE_NAME="todolist-$VERSION.zip"
git archive --format=zip --output "$ARCHIVE_NAME" HEAD
echo "Archive créée : $ARCHIVE_NAME"

echo "Build terminé pour la version $VERSION"
