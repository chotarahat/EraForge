import unittest

from app.narration import (
    NarrationManifest,
    NarrationManifestSegment,
)
from app.subtitles import (
    SubtitleCue,
    SubtitleTrack,
    build_subtitle_track,
    format_srt_timestamp,
    split_sentences,
    subtitle_track_to_srt,
)


def make_plan():
    from app.models import Scene, ScenePlan

    return ScenePlan(
        title="Subtitle Test",
        summary="Subtitle synchronization test",
        total_duration=10,
        aspect_ratio="9:16",
        style="documentary",
        scenes=[
            Scene(
                id="scene_1",
                title="Opening",
                start=0,
                end=5,
                narration="History begins here. The story continues.",
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
                narration="",
                caption="Second",
                visual="Historical scene",
                animation="Fade in",
                camera="Static",
                location="",
                asset_hints=[],
            ),
        ],
    )


class TestSubtitles(unittest.TestCase):
    def test_split_sentences(self):
        result = split_sentences(
            "First sentence. Second sentence!"
        )

        self.assertEqual(
            result,
            [
                "First sentence.",
                "Second sentence!",
            ],
        )

    def test_empty_text_returns_no_sentences(self):
        self.assertEqual(
            split_sentences("   "),
            [],
        )

    def test_build_subtitle_track(self):
        track = build_subtitle_track(
            make_plan()
        )

        self.assertEqual(
            len(track.cues),
            2,
        )

        self.assertEqual(
            track.cues[0].start,
            0,
        )

        self.assertEqual(
            track.cues[-1].end,
            5,
        )

    def test_cues_are_sequential(self):
        track = build_subtitle_track(
            make_plan()
        )

        for previous, current in zip(
            track.cues,
            track.cues[1:],
        ):
            self.assertAlmostEqual(
                previous.end,
                current.start,
                places=3,
            )

    def test_cues_are_inside_scene(self):
        track = build_subtitle_track(
            make_plan()
        )

        for cue in track.cues:
            self.assertGreaterEqual(
                cue.start,
                0,
            )
            self.assertLessEqual(
                cue.end,
                5,
            )

    def test_srt_timestamp(self):
        self.assertEqual(
            format_srt_timestamp(1.25),
            "00:00:01,250",
        )

        self.assertEqual(
            format_srt_timestamp(65.5),
            "00:01:05,500",
        )

    def test_srt_generation(self):
        track = build_subtitle_track(
            make_plan()
        )

        srt = subtitle_track_to_srt(track)

        self.assertIn(
            "00:00:00,000 -->",
            srt,
        )

        self.assertIn(
            "History begins here.",
            srt,
        )

        self.assertTrue(
            srt.endswith("\n")
        )

    def test_empty_track_srt(self):
        from app.subtitles import SubtitleTrack

        self.assertEqual(
            subtitle_track_to_srt(
                SubtitleTrack()
            ),
            "",
        )

    def test_invalid_cue_timing(self):
        with self.assertRaises(ValueError):
            SubtitleCue(
                index=1,
                start=5,
                end=5,
                text="Invalid",
            )

    def test_narration_duration_controls_subtitles(self):
        manifest = NarrationManifest(
            segments=[
                NarrationManifestSegment(
                    scene_id="scene_1",
                    start=0,
                    end=5,
                    text=(
                        "History begins here. "
                        "The story continues."
                    ),
                    audio_file="scene_1.wav",
                    audio_duration=3.0,
                )
            ]
        )

        track = build_subtitle_track(
            make_plan(),
            manifest,
        )

        self.assertAlmostEqual(
            track.cues[-1].end,
            3.0,
            places=3,
        )

    def test_audio_duration_cannot_exceed_scene(self):
        manifest = NarrationManifest(
            segments=[
                NarrationManifestSegment(
                    scene_id="scene_1",
                    start=0,
                    end=5,
                    text="Long audio.",
                    audio_file="scene_1.wav",
                    audio_duration=9.0,
                )
            ]
        )

        track = build_subtitle_track(
            make_plan(),
            manifest,
        )

        self.assertLessEqual(
            track.cues[-1].end,
            5.0,
        )

    def test_valid_subtitle_sync(self):
        from app.subtitles import validate_subtitle_track

        track = build_subtitle_track(
            make_plan()
        )

        report = validate_subtitle_track(
            make_plan(),
            track,
        )

        self.assertTrue(report.valid)
        self.assertEqual(
            len(report.issues),
            0,
        )

    def test_invalid_subtitle_overlap(self):
        from app.subtitles import validate_subtitle_track

        track = SubtitleTrack(
            cues=[
                SubtitleCue(
                    index=1,
                    start=0,
                    end=3,
                    text="First.",
                ),
                SubtitleCue(
                    index=2,
                    start=2,
                    end=4,
                    text="Second.",
                ),
            ]
        )

        report = validate_subtitle_track(
            make_plan(),
            track,
        )

        self.assertFalse(report.valid)

        issue_types = [
            issue.type
            for issue in report.issues
        ]

        self.assertIn(
            "overlap",
            issue_types,
        )

    def test_subtitle_outside_scene_is_invalid(self):
        from app.subtitles import validate_subtitle_track

        track = SubtitleTrack(
            cues=[
                SubtitleCue(
                    index=1,
                    start=11,
                    end=12,
                    text="Invalid timing.",
                )
            ]
        )

        report = validate_subtitle_track(
            make_plan(),
            track,
        )

        self.assertFalse(report.valid)

        issue_types = [
            issue.type
            for issue in report.issues
        ]

        self.assertIn(
            "outside_scene",
            issue_types,
        )


if __name__ == "__main__":
    unittest.main()