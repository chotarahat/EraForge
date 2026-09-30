import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

from app.video_export import export_mp4


class TestVideoExportIntegration(unittest.TestCase):
    def test_real_ffmpeg_export(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            for index in range(1, 5):
                image = Image.new(
                    "RGB",
                    (320, 480),
                    "#0a0d11",
                )

                draw = ImageDraw.Draw(image)

                draw.text(
                    (100, 220),
                    f"Frame {index}",
                    fill="#ffffff",
                )

                image.save(
                    root / f"frame_{index:06d}.png"
                )

            output = (
                root / "test_export.mp4"
            )

            result = export_mp4(
                image_sequence=str(
                    root / "frame_%06d.png"
                ),
                output_file=str(output),
                width=320,
                height=480,
                fps=2,
            )

            self.assertTrue(
                output.exists()
            )

            self.assertGreater(
                output.stat().st_size,
                0,
            )

            self.assertEqual(
                result.width,
                320,
            )

            self.assertEqual(
                result.height,
                480,
            )


if __name__ == "__main__":
    unittest.main()