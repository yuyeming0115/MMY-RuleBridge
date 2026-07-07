from __future__ import annotations

from abc import ABC, abstractmethod

from rulebridge.models import GeneratedFile, RenderContext


class TargetAdapter(ABC):
    name: str

    @abstractmethod
    def render(self, context: RenderContext) -> list[GeneratedFile]:
        raise NotImplementedError
