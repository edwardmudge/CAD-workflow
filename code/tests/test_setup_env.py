"""scripts/setup_env.py reads the env name it will create from environment.yml,
so a renamed copy of the template sets up its own env, not this one."""
from __future__ import annotations

import importlib.util

from project_tools import ROOT

spec = importlib.util.spec_from_file_location("setup_env", ROOT / "scripts" / "setup_env.py")
setup_env = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup_env)


def test_env_name_read_from_environment_yml():
    assert setup_env.env_name((ROOT / "environment.yml").read_text(encoding="utf-8"))


def test_env_name_ignores_comments_and_trailing_text():
    text = "# name: wrong\nname: my-project  # renamed\nchannels:\n  - conda-forge\n"
    assert setup_env.env_name(text) == "my-project"
