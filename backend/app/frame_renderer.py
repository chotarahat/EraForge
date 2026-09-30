from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.renderer import RenderPlan, SceneRenderPlan


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/calibri.ttf",
    ]

    for candidate in candidates:
        path = Path(candidate)

        if path.exists():
            return ImageFont.truetype(
                str(path),
                size,
            )

    return ImageFont.load_default()


def _draw_scene_frame(
    scene: SceneRenderPlan,
    width: int,
    height: int,
    frame_path: Path,
) -> None:
    image = Image.new(
        "RGB",
        (width, height),
        "#0a0d11",
    )

    draw = ImageDraw.Draw(image)

    text_font = _load_font(
        max(24, width // 24)
    )

    small_font = _load_font(
        max(16, width // 42)
    )

    for layer in scene.layers:
        if layer.type == "background":
            draw.rectangle(
                [0, 0, width, height],
                fill="#0a0d11",
            )
            continue

        if layer.type == "text":
            text = layer.text or ""

            bbox = draw.textbbox(
                (0, 0),
                text,
                font=text_font,
            )

            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            x = (width - text_width) // 2
            y = int(height * 0.82)

            draw.text(
                (x, y),
                text,
                fill="#f5f1e8",
                font=text_font,
            )

            continue

        if layer.type == "shape":
            radius = min(width, height) * 0.08

            cx = width // 2
            cy = height // 2

            draw.ellipse(
                [
                    cx - radius,
                    cy - radius,
                    cx + radius,
                    cy + radius,
                ],
                fill="#d8b365",
            )

            continue

        x = int(layer.position.x)
        y = int(layer.position.y)

        layer_width = int(
            layer.size.width
            or width * 0.8
        )

        layer_height = int(
            layer.size.height
            or height * 0.35
        )

        draw.rounded_rectangle(
            [
                x,
                y,
                x + layer_width,
                y + layer_height,
            ],
            radius=28,
            fill="#171c24",
            outline="#596273",
            width=2,
        )

        label = str(
            layer.metadata.get("asset_hint")
            or layer.asset_id
            or layer.type
        )

        bbox = draw.textbbox(
            (0, 0),
            label,
            font=small_font,
        )

        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        text_x = (
            x
            + (layer_width - text_width) // 2
        )

        text_y = (
            y
            + (layer_height - text_height) // 2
        )

        draw.text(
            (text_x, text_y),
            label,
            fill="#d7dce5",
            font=small_font,
        )

    image.save(
        frame_path,
        format="PNG",
    )


def render_plan_frames(
    render_plan: RenderPlan,
    output_root: str = "outputs/video_frames",
) -> list[str]:
    output_dir = Path(output_root)

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    frame_files: list[str] = []

    frame_index = 1

    for scene in render_plan.scenes:
        scene_duration = scene.end - scene.start

        frame_count = max(
            1,
            int(
                round(
                    scene_duration
                    * render_plan.fps
                )
            ),
        )

        for _ in range(frame_count):
            filename = (
                f"frame_{frame_index:06d}.png"
            )

            path = output_dir / filename

            _draw_scene_frame(
                scene,
                render_plan.width,
                render_plan.height,
                path,
            )

            frame_files.append(
                str(path)
            )

            frame_index += 1

    return frame_files