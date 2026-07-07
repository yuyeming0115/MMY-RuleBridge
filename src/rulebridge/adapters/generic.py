from __future__ import annotations

from pathlib import Path

from rulebridge.adapters.base import TargetAdapter
from rulebridge.models import GeneratedFile, RenderContext
from rulebridge.render import render_rule_bundle


class GenericAdapter(TargetAdapter):
    name = "generic"

    def render(self, context: RenderContext) -> list[GeneratedFile]:
        return [GeneratedFile(path=Path("AI_RULES.md"), content=render_rule_bundle(context.source, "AI Rules"))]
