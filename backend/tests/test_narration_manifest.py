import unittest

from app.narration import (
    NarrationManifest,
    NarrationPlan,
    NarrationSegment,
    build_narration_manifest,
)


def make_plan():
    from app.models import Scene, ScenePlan

    return ScenePlan(
        title="Narration Test",
        summary="Narration timeline test",
        total_duration=10,
        aspect_ratio="9:16",
        style="documentary",
        scenes=[
            Scene(
                id="scene_1",
                title="Opening",
                start=0,
                end=5,
                narration="Opening narration.",
                caption="Opening",
                visual="Historical scene",
                animation="Fade in",
                camera="Static",
                location="",
                asset_hints=[],
            ),
            Scene(
                id="scene_2",
                title="Second",
                start=5,
                end=10,
                narration="Second narration.",
                caption="Second",
                visual="Historical scene",
                animation="Fade in",
                camera="Static",
                location="",
                asset_hints=[],
            ),
        ],
    )


class TestNarrationManifest(unittest.TestCase):
    def test_manifest_matches_scene_timing(self):
        narration = NarrationPlan(
            segments=[
                NarrationSegment(
                    scene_id="scene_1",
                    text="Opening narration.",
                    audio_file="scene_1.wav",
                    duration_seconds=3.0,
                ),
                NarrationSegment(
                    scene_id="scene_2",
                    text="Second narration.",
                    audio_file="scene_2.wav",
                    duration_seconds=4.5,
                ),
            ]
        )

        manifest = build_narration_manifest(
            make_plan(),
            narration,
        )

        self.assertEqual(len(manifest.segments), 2)

        self.assertEqual(
            manifest.segments[0].start,
            0,
        )

        self.assertEqual(
            manifest.segments[0].end,
            5,
        )

    def test_audio_that_fits_scene_is_valid(self):
        narration = NarrationPlan(
            segments=[
                NarrationSegment(
                    scene_id="scene_1",
                    text="Opening narration.",
                    audio_file="scene_1.wav",
                    duration_seconds=3.0,
                )
            ]
        )

        manifest = build_narration_manifest(
            make_plan(),
            narration,
        )

        self.assertTrue(
            manifest.segments[0].fits_scene
        )

    def test_audio_longer_than_scene_is_flagged(self):
        narration = NarrationPlan(
            segments=[
                NarrationSegment(
                    scene_id="scene_1",
                    text="Opening narration.",
                    audio_file="scene_1.wav",
                    duration_seconds=7.0,
                )
            ]
        )

        manifest = build_narration_manifest(
            make_plan(),
            narration,
        )

        self.assertFalse(
            manifest.segments[0].fits_scene
        )

    def test_unknown_scene_is_ignored(self):
        narration = NarrationPlan(
            segments=[
                NarrationSegment(
                    scene_id="unknown",
                    text="Unknown narration.",
                    audio_file="unknown.wav",
                    duration_seconds=2.0,
                )
            ]
        )

        manifest = build_narration_manifest(
            make_plan(),
            narration,
        )

        self.assertEqual(
            len(manifest.segments),
            0,
        )


if __name__ == "__main__":
    unittest.main()