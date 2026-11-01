"""SkillOpt environment adapter for the verification benchmark.

Implements :class:`skillopt.envs.base.EnvAdapter` as the installed package requires:
``setup``, ``get_dataloader``, ``build_train_env``, ``build_eval_env``, ``rollout``,
``get_task_types``. Reflection is left to the base class (``run_minibatch_reflect``), which
reads the ``predictions/<id>/conversation.json`` files this package writes.

Register it with the trainer through ``bootstrap.py`` (SkillOpt keeps environments in a
module-level registry inside ``scripts.train``).
"""

from __future__ import annotations

import os

from skillopt.datasets.base import BatchSpec
from skillopt.envs.base import EnvAdapter

from .dataloader import VerificationDataLoader
from .rollout import AGENT_ENV, DEFAULT_AGENT_CMD, run_batch


class VerificationAdapter(EnvAdapter):
    """Environment adapter: agent under test + deterministic contract judge."""

    def __init__(
        self,
        split_dir: str = "",
        data_dir: str = "",
        split_mode: str = "split_dir",
        split_ratio: str = "7:2:1",
        split_seed: int = 42,
        split_output_dir: str = "",
        workers: int = 2,
        analyst_workers: int = 2,
        failure_only: bool = False,
        minibatch_size: int = 2,
        edit_budget: int = 2,
        seed: int = 42,
        limit: int = 0,
        max_completion_tokens: int = 8192,
        agent_cmd: str = "",
        agent_timeout: int = 900,
    ) -> None:
        self.workers = int(workers)
        self.analyst_workers = int(analyst_workers)
        self.failure_only = bool(failure_only)
        self.minibatch_size = int(minibatch_size)
        self.edit_budget = int(edit_budget)
        self.max_completion_tokens = int(max_completion_tokens)
        self.agent_cmd = agent_cmd or os.environ.get(AGENT_ENV) or DEFAULT_AGENT_CMD
        self.agent_timeout = int(agent_timeout)
        self.dataloader = VerificationDataLoader(
            split_dir=split_dir,
            data_path=data_dir,
            split_mode=split_mode,
            split_ratio=split_ratio,
            split_seed=split_seed,
            split_output_dir=split_output_dir,
            seed=seed,
            limit=limit,
        )

    # ── lifecycle ────────────────────────────────────────────────────────────

    def setup(self, cfg: dict) -> None:
        super().setup(cfg)
        self.dataloader.setup(cfg)

    def get_dataloader(self):
        return self.dataloader

    # ── batches ──────────────────────────────────────────────────────────────

    def build_env_from_batch(self, batch: BatchSpec, **kwargs):
        return list(batch.payload or [])

    def build_train_env(self, batch_size: int, seed: int, **kwargs):
        batch = self.dataloader.build_train_batch(batch_size=batch_size, seed=seed, **kwargs)
        return self.build_env_from_batch(batch, **kwargs)

    def build_eval_env(self, env_num: int, split: str, seed: int, **kwargs):
        batch = self.dataloader.build_eval_batch(env_num=env_num, split=split, seed=seed, **kwargs)
        return self.build_env_from_batch(batch, **kwargs)

    # ── rollout ──────────────────────────────────────────────────────────────

    def rollout(self, env_manager, skill_content: str, out_dir: str, **kwargs) -> list[dict]:
        return run_batch(
            items=list(env_manager),
            out_root=out_dir,
            skill_content=skill_content,
            workers=self.workers,
            cmd=self.agent_cmd,
            timeout=self.agent_timeout,
        )

    def get_task_types(self) -> list[str]:
        try:
            return sorted({str(row.get("task_type") or "verification")
                           for row in self.dataloader._splits.get("train", [])}) or ["verification"]
        except Exception:
            return ["verification"]
