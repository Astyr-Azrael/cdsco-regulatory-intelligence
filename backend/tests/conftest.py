"""Test-environment configuration that avoids locked Windows user-temp folders."""

from __future__ import annotations

import os
import uuid
from pathlib import Path


def pytest_configure(config) -> None:
    if config.option.basetemp is not None:
        return
    runs_root = Path(config.rootpath) / ".pytest-runs"
    runs_root.mkdir(parents=True, exist_ok=True)
    run_directory = (
        runs_root / f"run-{os.getpid()}-{uuid.uuid4().hex}"
    )
    config.option.basetemp = str(run_directory)
