from __future__ import annotations

from pathlib import Path

from rulebridge.adapters.base import TargetAdapter
from rulebridge.models import GeneratedFile, RenderContext
from rulebridge.render import cursor_frontmatter


class CursorAdapter(TargetAdapter):
    name = "cursor"

    def render(self, context: RenderContext) -> list[GeneratedFile]:
        files: list[GeneratedFile] = []
        for rule in context.source.rules:
            content = cursor_frontmatter(rule) + rule.content.strip() + "\n"
            files.append(GeneratedFile(path=Path(".cursor") / "rules" / f"{rule.name}.mdc", content=content, managed=False))
        return files
