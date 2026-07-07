from __future__ import annotations

from pathlib import Path

from rulebridge.adapters.base import TargetAdapter
from rulebridge.models import GeneratedFile, RenderContext
from rulebridge.render import codebuddy_frontmatter


class CodeBuddyAdapter(TargetAdapter):
    name = "codebuddy"

    def render(self, context: RenderContext) -> list[GeneratedFile]:
        files: list[GeneratedFile] = []
        for rule in context.source.rules:
            content = codebuddy_frontmatter(rule, "rulebridge") + "<system_reminder>\n" + rule.content.strip() + "\n</system_reminder>\n"
            files.append(GeneratedFile(path=Path(".codebuddy-plugin") / "rules" / f"{rule.name}.md", content=content, managed=False))
        for skill in context.source.skills:
            files.append(GeneratedFile(path=Path(".codebuddy-plugin") / "skills" / skill.name / "SKILL.md", content=skill.content, managed=False))
        return files
