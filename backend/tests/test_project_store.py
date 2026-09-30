import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.models import Scene, ScenePlan
from app.project_store import (
    create_project,
    delete_project,
    get_project,
    list_projects,
    update_project,
)


def make_scene_plan() -> ScenePlan:
    scene = Scene(
    id="scene-1",
    title="The Beginning",
    start=0,
    end=5,
    narration="A historical event begins.",
    caption="The Beginning",
    visual="Historical city",
    animation="fade_in",
    camera="static",
    )

    return ScenePlan(
        title="Test History",
        summary="A test project.",
        total_duration=5,
        aspect_ratio="9:16",
        style="documentary",
        scenes=[scene],
    )


class TestProjectStore(unittest.TestCase):
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
        project = create_project(
            name="My History Project",
            scene_plan=make_scene_plan(),
            script="This is my historical script.",
            duration=90,
        )

        self.assertEqual(project["name"], "My History Project")
        self.assertIsNotNone(project["scene_plan"])
        self.assertEqual(
            project["script"],
            "This is my historical script.",
        )
        self.assertEqual(project["duration"], 90)
        self.assertTrue(
            (self.projects_root / f"{project['id']}.json").exists()
        )

    def test_get_project(self):
        created = create_project("History", make_scene_plan())

        project = get_project(created["id"])

        self.assertIsNotNone(project)
        self.assertEqual(project["id"], created["id"])
        self.assertEqual(project["name"], "History")

    def test_get_missing_project(self):
        self.assertIsNone(get_project("missing-project"))

    def test_list_projects(self):
        create_project("Project A")
        create_project("Project B")

        projects = list_projects()

        self.assertEqual(len(projects), 2)
        self.assertEqual(
            {project["name"] for project in projects},
            {"Project A", "Project B"},
        )

        self.assertNotIn("scene_plan", projects[0])

    def test_update_project_name(self):
        created = create_project("Old Name")

        updated = update_project(
            created["id"],
            name="New Name",
        )

        self.assertIsNotNone(updated)
        self.assertEqual(updated["name"], "New Name")

        stored = get_project(created["id"])
        self.assertEqual(stored["name"], "New Name")

    def test_update_project_script_and_duration(self):
        created = create_project(
            name="History",
            script="Old script",
            duration=60,
        )

        updated = update_project(
            project_id=created["id"],
            script="Updated script",
            duration=120,
        )

        self.assertIsNotNone(updated)
        self.assertEqual(updated["script"], "Updated script")
        self.assertEqual(updated["duration"], 120)

    def test_update_project_scene_plan(self):
        created = create_project("History")

        updated = update_project(
            created["id"],
            scene_plan=make_scene_plan(),
        )

        self.assertIsNotNone(updated)
        self.assertIsNotNone(updated["scene_plan"])
        self.assertEqual(
            updated["scene_plan"]["title"],
            "Test History",
        )

    def test_update_missing_project(self):
        self.assertIsNone(
            update_project(
                "missing-project",
                name="New Name",
            )
        )

    def test_delete_project(self):
        created = create_project("Delete Me")

        deleted = delete_project(created["id"])

        self.assertTrue(deleted)
        self.assertIsNone(get_project(created["id"]))

    def test_delete_missing_project(self):
        self.assertFalse(delete_project("missing-project"))

    def test_empty_project_name_rejected(self):
        with self.assertRaises(ValueError):
            create_project("   ")

    def test_invalid_project_id_rejected(self):
        with self.assertRaises(ValueError):
            get_project("../bad-project")


if __name__ == "__main__":
    unittest.main()