set -e

PYTHON_VERSIONS=("3.13" "3.9" "2.7")
DJANGO_VERSIONS=("5.0" "4.2" "3.2" "1.11")

echo "------ Running test ------"

for py in "${PYTHON_VERSIONS[@]}"; do
    echo ""
    echo "------ Version $py ------ "

    pipenv --rm >/dev/null 2>&1 || true
    pipenv --python $py

    for dj in "${DJANGO_VERSIONS[@]}"; do
        echo ""
        echo "--- Testing Django $dj with Python $py ---"

        if [[ "$py" == "2.7" && "$dj" != "1.11" ]]; then
            echo "Django $dj incompatible avec Python 2.7 "
            continue
        fi

        pipenv install "django==$dj" --skip-lock

        if pipenv run python manage.py test; then
            echo " SUCCESS Python $py + Django $dj"
        else
            echo "FAILURE Python $py + Django $dj"
        fi
    done
done
