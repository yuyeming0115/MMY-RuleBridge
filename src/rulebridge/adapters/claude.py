from __future__ import annotations

from pathlib import Path

from rulebridge.adapters.base import TargetAdapter
from rulebridge.models import GeneratedFile, RenderContext
from rulebridge.render import render_rule_bundle


class ClaudeAdapter(TargetAdapter):
    name = "claude"

    def render(self, context: RenderContext) -> list[GeneratedFile]:
        return [GeneratedFile(path=Path("CLAUDE.md"), content=render_rule_bundle(context.source, "Claude Code Rules"))]
