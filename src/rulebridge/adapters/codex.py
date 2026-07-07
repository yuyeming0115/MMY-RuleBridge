from __future__ import annotations

from pathlib import Path

from rulebridge.adapters.base import TargetAdapter
from rulebridge.models import GeneratedFile, RenderContext
from rulebridge.render import render_rule_bundle


class CodexAdapter(TargetAdapter):
    name = "codex"

    def render(self, context: RenderContext) -> list[GeneratedFile]:
        return [GeneratedFile(path=Path("AGENTS.md"), content=render_rule_bundle(context.source, "Agent Rules"))]
