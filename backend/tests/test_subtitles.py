import unittest

from app.subtitles import (
    SubtitleCue,
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


if __name__ == "__main__":
    unittest.main()