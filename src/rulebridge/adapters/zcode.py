from __future__ import annotations

from pathlib import Path

from rulebridge.adapters.base import TargetAdapter
from rulebridge.models import GeneratedFile, RenderContext


class ZCodeAdapter(TargetAdapter):
    name = "zcode"

    def render(self, context: RenderContext) -> list[GeneratedFile]:
        return [
            GeneratedFile(path=Path(".zcode") / "skills" / skill.name / "SKILL.md", content=skill.content, managed=False)
            for skill in context.source.skills
        ]
