from __future__ import annotations

from pathlib import Path

from rulebridge.adapters.base import TargetAdapter
from rulebridge.models import GeneratedFile, RenderContext


class TraeAdapter(TargetAdapter):
    name = "trae"

    def render(self, context: RenderContext) -> list[GeneratedFile]:
        return [
            GeneratedFile(path=Path(".trae") / "skills" / skill.name / "SKILL.md", content=skill.content, managed=False)
            for skill in context.source.skills
        ]
