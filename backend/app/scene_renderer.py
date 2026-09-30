from html import escape

from app.renderer import (
    AnimationInstruction,
    RenderLayer,
    SceneRenderPlan,
)


def _render_layer_content(layer: RenderLayer, width: int, height: int) -> str:
    x = layer.position.x
    y = layer.position.y
    layer_width = layer.size.width or width * 0.8
    layer_height = layer.size.height or height * 0.35
    opacity = layer.opacity

    if layer.type == "background":
        return (
            f'<rect x="0" y="0" width="{width}" height="{height}" '
            f'fill="#0a0d11" opacity="{opacity}" />'
        )

    if layer.type == "text":
        text = escape(layer.text or "")
        return (
            f'<text x="{width / 2}" y="{height * 0.85}" '
            f'text-anchor="middle" '
            f'fill="#f5f1e8" '
            f'font-family="Arial, sans-serif" '
            f'font-size="48" '
            f'font-weight="700" '
            f'opacity="{opacity}">{text}</text>'
        )

    if layer.type == "shape":
        cx = width / 2
        cy = height / 2
        radius = min(width, height) * 0.08
        return (
            f'<circle cx="{cx}" cy="{cy}" r="{radius}" '
            f'fill="#d8b365" opacity="{opacity}" />'
        )

    label = escape(
        str(
            layer.metadata.get("asset_hint")
            or layer.asset_id
            or layer.type
        )
    )

    return (
        f'<rect x="{x}" y="{y}" '
        f'width="{layer_width}" height="{layer_height}" '
        f'rx="28" '
        f'fill="#171c24" '
        f'stroke="#596273" '
        f'stroke-width="2" '
        f'opacity="{opacity}" />'
        f'<text x="{x + layer_width / 2}" '
        f'y="{y + layer_height / 2}" '
        f'text-anchor="middle" '
        f'dominant-baseline="middle" '
        f'fill="#d7dce5" '
        f'font-family="Arial, sans-serif" '
        f'font-size="32">{label}</text>'
    )


def _render_animation(
    animation: AnimationInstruction,
    layer_id: str,
) -> str:
    begin = animation.start
    duration = animation.end - animation.start

    if animation.type == "fade_in":
        return (
            f'<animate attributeName="opacity" '
            f'begin="{begin}s" '
            f'dur="{duration}s" '
            f'from="0" to="1" fill="freeze" />'
        )

    if animation.type == "fade_out":
        return (
            f'<animate attributeName="opacity" '
            f'begin="{begin}s" '
            f'dur="{duration}s" '
            f'from="1" to="0" fill="freeze" />'
        )

    if animation.type == "slide":
        direction = animation.direction or "left"

        if direction == "right":
            x_from, x_to = "-120", "0"
        elif direction == "up":
            x_from, x_to = "0", "120"
        elif direction == "down":
            x_from, x_to = "0", "-120"
        else:
            x_from, x_to = "120", "0"

        if direction in {"up", "down"}:
            return (
                f'<animateTransform attributeName="transform" '
                f'type="translate" '
                f'begin="{begin}s" '
                f'dur="{duration}s" '
                f'from="0 {x_from}" '
                f'to="0 {x_to}" '
                f'fill="freeze" />'
            )

        return (
            f'<animateTransform attributeName="transform" '
            f'type="translate" '
            f'begin="{begin}s" '
            f'dur="{duration}s" '
            f'from="{x_from} 0" '
            f'to="{x_to} 0" '
            f'fill="freeze" />'
        )

    if animation.type == "scale":
        from_value = animation.from_value or "0.8"
        to_value = animation.to_value or "1"

        return (
            f'<animateTransform attributeName="transform" '
            f'type="scale" '
            f'begin="{begin}s" '
            f'dur="{duration}s" '
            f'from="{from_value}" '
            f'to="{to_value}" '
            f'fill="freeze" />'
        )

    if animation.type == "highlight":
        return (
            f'<animate attributeName="opacity" '
            f'begin="{begin}s" '
            f'dur="{duration}s" '
            f'values="1;0.45;1" '
            f'repeatCount="2" '
            f'fill="freeze" />'
        )

    if animation.type == "reveal":
        return (
            f'<animate attributeName="opacity" '
            f'begin="{begin}s" '
            f'dur="{duration}s" '
            f'from="0" to="1" '
            f'fill="freeze" />'
        )

    return ""


def _render_camera_animation(
    scene: SceneRenderPlan,
) -> str:
    camera = scene.camera

    if camera.type == "zoom":
        zoom_from = camera.zoom_from or 1.0
        zoom_to = camera.zoom_to or 1.2

        cx = camera.x if camera.x is not None else 0
        cy = camera.y if camera.y is not None else 0

        return (
            f'<animateTransform attributeName="transform" '
            f'type="scale" '
            f'origin="{cx} {cy}" '
            f'begin="{camera.start}s" '
            f'dur="{camera.end - camera.start}s" '
            f'from="{zoom_from}" '
            f'to="{zoom_to}" '
            f'fill="freeze" />'
        )

    if camera.type == "pan":
        x = camera.x or 0
        y = camera.y or 0

        return (
            f'<animateTransform attributeName="transform" '
            f'type="translate" '
            f'begin="{camera.start}s" '
            f'dur="{camera.end - camera.start}s" '
            f'from="0 0" '
            f'to="{x} {y}" '
            f'fill="freeze" />'
        )

    return ""


def render_layer_to_svg(
    layer: RenderLayer,
    width: int,
    height: int,
    animations: list[AnimationInstruction] | None = None,
) -> str:
    animations = animations or []

    content = _render_layer_content(layer, width, height)

    relevant_animations = [
        animation
        for animation in animations
        if animation.metadata.get("layer_id") == layer.id
        or (
            not animation.metadata.get("layer_id")
            and layer.type not in {"background", "text"}
        )
    ]

    animation_markup = "".join(
        _render_animation(animation, layer.id)
        for animation in relevant_animations
    )

    camera_wrapper = f"<g>{content}{animation_markup}</g>"

    return camera_wrapper


def render_scene_to_svg(
    scene: SceneRenderPlan,
    width: int = 1080,
    height: int = 1920,
) -> str:
    layers: list[str] = []

    visual_animation = False

    for layer in scene.layers:
        content = _render_layer_content(layer, width, height)

        if (
            scene.animations
            and not visual_animation
            and layer.type not in {"background", "text"}
        ):
            animation_markup = "".join(
                _render_animation(animation, layer.id)
                for animation in scene.animations
            )
            content = f"<g>{content}{animation_markup}</g>"
            visual_animation = True

        layers.append(content)

    layer_markup = "".join(layers)

    camera_animation = _render_camera_animation(scene)

    if camera_animation:
        layer_markup = (
            f'<g>'
            f'{layer_markup}'
            f'{camera_animation}'
            f'</g>'
        )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
        f'{layer_markup}'
        f'</svg>'
    )