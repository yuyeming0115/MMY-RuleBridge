from __future__ import annotations

from pathlib import Path

from rulebridge.adapters.base import TargetAdapter
from rulebridge.models import GeneratedFile, RenderContext
from rulebridge.render import mcp_servers_for_target, render_mcp_json


class McpAdapter(TargetAdapter):
    name = "mcp"

    def render(self, context: RenderContext) -> list[GeneratedFile]:
        if not mcp_servers_for_target(context.source.mcp_servers, self.name):
            return []
        return [GeneratedFile(path=Path(".mcp.json"), content=render_mcp_json(context.source.mcp_servers, self.name), managed=False)]
