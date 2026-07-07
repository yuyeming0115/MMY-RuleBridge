from __future__ import annotations

from rulebridge.adapters.base import TargetAdapter
from rulebridge.adapters.claude import ClaudeAdapter
from rulebridge.adapters.codebuddy import CodeBuddyAdapter
from rulebridge.adapters.codex import CodexAdapter
from rulebridge.adapters.cursor import CursorAdapter
from rulebridge.adapters.generic import GenericAdapter
from rulebridge.adapters.git import GitAdapter
from rulebridge.adapters.mcp import McpAdapter
from rulebridge.adapters.trae import TraeAdapter
from rulebridge.adapters.workbuddy import WorkBuddyAdapter
from rulebridge.adapters.zcode import ZCodeAdapter

ADAPTERS: dict[str, TargetAdapter] = {
    adapter.name: adapter
    for adapter in [
        CodexAdapter(),
        ClaudeAdapter(),
        CursorAdapter(),
        GenericAdapter(),
        GitAdapter(),
        McpAdapter(),
        ZCodeAdapter(),
        TraeAdapter(),
        CodeBuddyAdapter(),
        WorkBuddyAdapter(),
    ]
}


def get_adapter(name: str) -> TargetAdapter:
    return ADAPTERS[name]


def list_targets() -> list[str]:
    return sorted(ADAPTERS)
