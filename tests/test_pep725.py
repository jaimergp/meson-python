# SPDX-FileCopyrightText: 2025 The meson-python developers
#
# SPDX-License-Identifier: MIT
import shutil
import subprocess
import sys

from pathlib import Path

from pyproject_external import External
from pytest import CaptureFixture

import mesonpy
from tests.conftest import CondaEnv

from .conftest import in_git_repo_context


def _install_external(
    env_dir: Path,
    directory: Path,
    ecosystem: str = "conda-forge",
) -> subprocess.CompletedProcess:
    external = External.from_pyproject_path(directory / "pyproject.toml")
    cmd = external.install_command(ecosystem=ecosystem, package_manager="micromamba")
    cmd.append(f"--prefix={env_dir}")
    return subprocess.run(cmd, check=True)


def test_limited_api_pep725(
    tmp_path: Path,
    conda_env: CondaEnv,
    package_limited_api_pep725,
    capfd: CaptureFixture[str],
):
    _install_external(conda_env, package_limited_api_pep725)
    pkg_config = shutil.which("pkg-config")
    assert pkg_config
    assert str(conda_env) in pkg_config

    with in_git_repo_context():
        wheel_path = tmp_path / mesonpy.build_wheel(tmp_path)
    if sys.platform != "win32":  # pkg-config not used in Windows
        out, err = capfd.readouterr()
        assert pkg_config in out + err

    conda_env.pip("install", wheel_path)
    output = conda_env.python("-c", "import module; print(module.add(1, 2))")
    assert int(output) == 3


def test_link_against_local_lib_pep725(
    tmp_path: Path,
    conda_env: CondaEnv,
    package_link_against_local_lib_pep725,
    capfd: CaptureFixture[str],
):
    _install_external(conda_env, package_link_against_local_lib_pep725)
    pkg_config = shutil.which("pkg-config")
    assert pkg_config
    assert str(conda_env) in pkg_config

    with in_git_repo_context():
        wheel_path = tmp_path / mesonpy.build_wheel(tmp_path)
    if sys.platform != "win32":  # pkg-config not used in Windows
        out, err = capfd.readouterr()
        assert pkg_config in out + err

    conda_env.pip("install", wheel_path, "-vvv")

    output = conda_env.python("-c", "import example; print(example.example_sum(1, 2))")
    assert int(output) == 3
