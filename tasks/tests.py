import os
from django.test import TestCase, RequestFactory
from django.conf import settings

from .models import Task
from .forms import TaskForm
from todo.context_processors import app_version
from tasks.loader import import_tasks_from_json
import unittest
import json
from pathlib import Path
from django.test.runner import DiscoverRunner

TEST_RESULTS = {}

def tc(id):
    def decorator(func):
        func.test_case_id = id
        return func
    return decorator


class TestTaskUrls(TestCase):

    def setUp(self):
        self.task = Task.objects.create(
            title="Test task",
            complete=False,
        )

    @tc("TC001")
    def test_task_str(self):
        self.assertEqual(str(self.task), self.task.title)

    @tc("TC002")
    def test_home_get(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("tasks", response.context)
        self.assertIn("form", response.context)

    @tc("TC003")
    def test_home_post_creates_task(self):
        data = {"title": "New task", "complete": False}
        response = self.client.post("/", data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/")
        self.assertTrue(Task.objects.filter(title="New task").exists())


    @tc("TC004")
    def test_update_task_get(self):
        url = f"/update_task/{self.task.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIsInstance(form, TaskForm)
        self.assertEqual(form.instance, self.task)

    @tc("TC005")
    def test_update_task_post_updates_task(self):
        url = f"/update_task/{self.task.id}/"
        data = {"title": "Updated task", "complete": True}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/")

        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Updated task")
        self.assertTrue(self.task.complete)

    @tc("TC006")
    def test_delete_task_get(self):
        url = f"/delete_task/{self.task.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["item"], self.task)

    @tc("TC007")
    def test_delete_task_post_deletes_task(self):
        url = f"/delete_task/{self.task.id}/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/")
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())


class TestContextProcessor(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @tc("TC008")
    def test_app_version_context_processor(self):
        request = self.factory.get("/")
        context = app_version(request)
        self.assertIn("APP_VERSION", context)
        self.assertEqual(context["APP_VERSION"], settings.APP_VERSION)


class TestDatasetImport(TestCase):

    @tc("TC009")
    def test_dataset_import(self):
        dataset_path = os.path.join(settings.BASE_DIR, "dataset.json")
        self.assertTrue(os.path.exists(dataset_path))

        import_tasks_from_json(dataset_path)

        self.assertTrue(Task.objects.filter(title="Task 1").exists())
        self.assertTrue(Task.objects.filter(title="Task 2").exists())
        self.assertEqual(Task.objects.count(), 3)

class JSONResult(unittest.TextTestResult):


    def _record(self, test, status: str) -> None:
        tc_id = getattr(test, "test_case_id", None)

        if tc_id is None:
            method_name = getattr(test, "_testMethodName", None)
            if method_name:
                method = getattr(test, method_name, None)
                tc_id = getattr(method, "test_case_id", None)

        if not tc_id:
            return

        TEST_RESULTS[tc_id] = status

    def addSuccess(self, test):
        super().addSuccess(test)
        self._record(test, "passed")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._record(test, "failed")

    def addError(self, test, err):
        super().addError(test, err)
        self._record(test, "failed")

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._record(test, "failed")


class JSONTestRunner(DiscoverRunner):

    def get_resultclass(self):
        return JSONResult

    def run_suite(self, suite, **kwargs):
        result = super().run_suite(suite, **kwargs)

        out_file = Path("result_test_auto.json")
        with out_file.open("w", encoding="utf-8") as f:
            json.dump(TEST_RESULTS, f, indent=2, ensure_ascii=False)

        print(f"\nRésultats auto exportés dans {out_file.resolve()}")
        return result