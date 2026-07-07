from __future__ import annotations

from pathlib import Path

from rulebridge.adapters.base import TargetAdapter
from rulebridge.models import GeneratedFile, RenderContext
from rulebridge.render import render_rule_bundle


class ClaudeAdapter(TargetAdapter):
    name = "claude"

    def render(self, context: RenderContext) -> list[GeneratedFile]:
        files = [GeneratedFile(path=Path("CLAUDE.md"), content=render_rule_bundle(context.source, "Claude Code Rules"))]
        files.extend(
            GeneratedFile(path=Path(".claude") / "commands" / f"{command.name}.md", content=command.content, managed=False)
            for command in context.source.commands
        )
        return files
