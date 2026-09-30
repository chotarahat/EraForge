import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.models import Scene, ScenePlan


client = TestClient(app)


def make_scene_plan() -> dict:
    return {
        "title": "Test History",
        "summary": "A test project.",
        "total_duration": 5,
        "aspect_ratio": "9:16",
        "style": "documentary",
        "scenes": [
            {
                "id": "scene-1",
                "title": "The Beginning",
                "start": 0,
                "end": 5,
                "narration": "A historical event begins.",
                "caption": "The Beginning",
                "visual": "Historical city",
                "animation": "fade_in",
                "camera": "static",
            }
        ],
    }


class TestProjectsAPI(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.projects_root = Path(self.temp_dir.name)

        self.patch = patch(
            "app.project_store.PROJECTS_ROOT",
            self.projects_root,
        )
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self.temp_dir.cleanup()

    def test_create_project(self):
        response = client.post(
            "/api/projects",
            json={
                "name": "My History",
                "scene_plan": make_scene_plan(),
            },
        )

        self.assertEqual(response.status_code, 201)

        data = response.json()

        self.assertEqual(data["name"], "My History")
        self.assertIsNotNone(data["id"])
        self.assertIsNotNone(data["scene_plan"])

    def test_create_project_without_scene_plan(self):
        response = client.post(
            "/api/projects",
            json={
                "name": "Empty Project",
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertIsNone(response.json()["scene_plan"])

    def test_create_project_with_empty_name(self):
        response = client.post(
            "/api/projects",
            json={
                "name": "   ",
            },
        )

        self.assertEqual(response.status_code, 400)

    def test_list_projects(self):
        client.post(
            "/api/projects",
            json={"name": "Project A"},
        )
        client.post(
            "/api/projects",
            json={"name": "Project B"},
        )

        response = client.get("/api/projects")

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(len(data), 2)
        self.assertEqual(
            {project["name"] for project in data},
            {"Project A", "Project B"},
        )

    def test_get_project(self):
        created = client.post(
            "/api/projects",
            json={"name": "History"},
        ).json()

        response = client.get(
            f"/api/projects/{created['id']}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["name"],
            "History",
        )

    def test_get_missing_project(self):
        response = client.get(
            "/api/projects/missing-project"
        )

        self.assertEqual(response.status_code, 404)

    def test_update_project_name(self):
        created = client.post(
            "/api/projects",
            json={"name": "Old Name"},
        ).json()

        response = client.put(
            f"/api/projects/{created['id']}",
            json={
                "name": "New Name",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["name"],
            "New Name",
        )

    def test_update_project_scene_plan(self):
        created = client.post(
            "/api/projects",
            json={"name": "History"},
        ).json()

        response = client.put(
            f"/api/projects/{created['id']}",
            json={
                "scene_plan": make_scene_plan(),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["scene_plan"]["title"],
            "Test History",
        )

    def test_update_missing_project(self):
        response = client.put(
            "/api/projects/missing-project",
            json={"name": "New Name"},
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_project(self):
        created = client.post(
            "/api/projects",
            json={"name": "Delete Me"},
        ).json()

        response = client.delete(
            f"/api/projects/{created['id']}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["deleted"])

        get_response = client.get(
            f"/api/projects/{created['id']}"
        )

        self.assertEqual(get_response.status_code, 404)

    def test_delete_missing_project(self):
        response = client.delete(
            "/api/projects/missing-project"
        )

        self.assertEqual(response.status_code, 404)

    def test_invalid_scene_plan_is_rejected(self):
        response = client.post(
            "/api/projects",
            json={
                "name": "Broken Project",
                "scene_plan": {
                    "title": "Broken",
                },
            },
        )

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()