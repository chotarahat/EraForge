from pathlib import Path

from app.renderer import RenderPlan
from app.scene_renderer import render_scene_to_svg


class RenderJobResult:
    def __init__(
        self,
        output_dir: str,
        scene_files: list[str],
    ):
        self.output_dir = output_dir
        self.scene_files = scene_files


def render_preview_bundle(
    render_plan: RenderPlan,
    output_root: str = "backend/outputs/render_preview",
) -> RenderJobResult:
    output_dir = Path(output_root)
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    scene_files: list[str] = []

    for index, scene in enumerate(
        render_plan.scenes,
        start=1,
    ):
        svg = render_scene_to_svg(
            scene,
            width=render_plan.width,
            height=render_plan.height,
        )

        filename = (
            f"scene_{index:03d}_{scene.scene_id}.svg"
        )

        path = output_dir / filename

        path.write_text(
            svg,
            encoding="utf-8",
        )

        scene_files.append(
            str(path)
        )

    return RenderJobResult(
        output_dir=str(output_dir),
        scene_files=scene_files,
    )