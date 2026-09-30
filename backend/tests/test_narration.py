import unittest

from app.narration import (
    NarrationSettings,
    build_narration_plan,
)


def make_plan():
    from app.models import Scene, ScenePlan

    return ScenePlan(
        title="Test History",
        summary="A short historical test story.",
        total_duration=8,
        aspect_ratio="9:16",
        style="documentary",
        scenes=[
            Scene(
                id="scene_1",
                title="Opening",
                start=0,
                end=4,
                narration="The story begins in ancient Bangladesh.",
                caption="The story begins.",
                visual="Historical landscape",
                animation="Fade in",
                camera="Static",
                location="Bangladesh",
                asset_hints=[],
            ),
            Scene(
                id="scene_2",
                title="Second Scene",
                start=4,
                end=8,
                narration="",
                caption="A second scene.",
                visual="Map",
                animation="Zoom",
                camera="Zoom",
                location="India",
                asset_hints=["map"],
            ),
        ],
    )


class TestNarration(unittest.TestCase):
    def test_build_narration_plan(self):
        plan = build_narration_plan(make_plan())

        self.assertEqual(len(plan.segments), 1)
        self.assertEqual(plan.segments[0].scene_id, "scene_1")
        self.assertEqual(
            plan.segments[0].text,
            "The story begins in ancient Bangladesh.",
        )

    def test_empty_narration_is_skipped(self):
        plan = build_narration_plan(make_plan())

        scene_ids = [segment.scene_id for segment in plan.segments]

        self.assertNotIn("scene_2", scene_ids)

    def test_default_narration_settings(self):
        settings = NarrationSettings()

        self.assertEqual(settings.rate, 170)
        self.assertEqual(settings.volume, 1.0)

    def test_custom_narration_settings(self):
        settings = NarrationSettings(
            voice="test-voice",
            rate=190,
            volume=0.8,
        )

        self.assertEqual(settings.voice, "test-voice")
        self.assertEqual(settings.rate, 190)
        self.assertEqual(settings.volume, 0.8)


if __name__ == "__main__":
    unittest.main()