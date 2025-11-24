import os
from django.test import TestCase, RequestFactory
from django.conf import settings

from .models import Task
from .forms import TaskForm
from todo.context_processors import app_version
from tasks.loader import import_tasks_from_json

class TestTaskUrls(TestCase):
    def setUp(self):
        self.task = Task.objects.create(
            title="Test task",
            complete=False,
        )

    def test_task_str(self):
        self.assertEqual(str(self.task), self.task.title)

    def test_home_get(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("tasks", response.context)
        self.assertIn("form", response.context)

    def test_home_post_creates_task(self):
        data = {"title": "New task", "complete": False}
        response = self.client.post("/", data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/")
        self.assertTrue(Task.objects.filter(title="New task").exists())

    def test_update_task_get(self):
        url = f"/update_task/{self.task.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIsInstance(form, TaskForm)
        self.assertEqual(form.instance, self.task)

    def test_update_task_post_updates_task(self):
        url = f"/update_task/{self.task.id}/"
        data = {"title": "Updated task", "complete": True}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/")

        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Updated task")
        self.assertTrue(self.task.complete)

    def test_delete_task_get(self):
        url = f"/delete_task/{self.task.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["item"], self.task)

    def test_delete_task_post_deletes_task(self):
        url = f"/delete_task/{self.task.id}/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/")
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())


class TestContextProcessor(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_app_version_context_processor(self):
        request = self.factory.get("/")
        context = app_version(request)
        self.assertIn("APP_VERSION", context)
        self.assertEqual(context["APP_VERSION"], settings.APP_VERSION)

class TestDatasetImport(TestCase):
    def test_dataset_import(self):
        dataset_path = os.path.join(settings.BASE_DIR, "dataset.json")
        
        self.assertTrue(os.path.exists(dataset_path))

        import_tasks_from_json(dataset_path)

        self.assertTrue(Task.objects.filter(title="Task 1").exists())
        self.assertTrue(Task.objects.filter(title="Task 2").exists())

        self.assertEqual(Task.objects.count(), 3)