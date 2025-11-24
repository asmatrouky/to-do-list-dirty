import json
from .models import Task


def import_tasks_from_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for entry in data:
        Task.objects.create(
            title=entry.get("title", ""),
            complete=entry.get("complete", False),
        )
