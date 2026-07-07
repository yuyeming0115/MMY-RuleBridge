from __future__ import annotations

from pathlib import Path

from rulebridge.adapters.base import TargetAdapter
from rulebridge.models import GeneratedFile, RenderContext


class ZCodeAdapter(TargetAdapter):
    name = "zcode"

    def render(self, context: RenderContext) -> list[GeneratedFile]:
        files = [
            GeneratedFile(path=Path(".zcode") / "skills" / skill.name / "SKILL.md", content=skill.content, managed=False)
            for skill in context.source.skills
        ]
        files.extend(
            GeneratedFile(path=Path(".zcode") / "commands" / f"{command.name}.md", content=command.content, managed=False)
            for command in context.source.commands
        )
        return files
