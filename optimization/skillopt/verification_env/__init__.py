"""SkillOpt benchmark package for the agent-verification skill.

Registration happens in :mod:`bootstrap` (SkillOpt keeps its environment registry inside
``scripts.train``), because the installed package has no plugin entry point.
"""

from .adapter import VerificationAdapter
from .dataloader import VerificationDataLoader

__all__ = ["VerificationAdapter", "VerificationDataLoader"]
