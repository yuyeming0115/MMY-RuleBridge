from __future__ import annotations

from .adapters import ADAPTERS
from .models import GeneratedFile, RenderContext, SourceContext


def resolve_targets(source: SourceContext, target: str | None = None) -> list[str]:
    targets = [target] if target else list(source.config.targets)
    return targets


def render_files(source: SourceContext, target: str | None = None) -> list[GeneratedFile]:
    targets = resolve_targets(source, target)
    context = RenderContext(source=source, targets=targets)
    files: list[GeneratedFile] = []
    for name in targets:
        adapter = ADAPTERS[name]
        files.extend(adapter.render(context))
    return files
