# SPDX-FileCopyrightText: 2025 The meson-python developers
#
# SPDX-License-Identifier: MIT
import os
import subprocess
import sys

from pathlib import Path

from pyproject_external import External

import mesonpy

from .conftest import in_git_repo_context


def _install_external(env_dir: Path, directory: Path, ecosystem: str = "conda-forge") -> subprocess.CompletedProcess:
    external = External.from_pyproject_path(directory / "pyproject.toml")
    cmd = external.install_command(ecosystem=ecosystem, package_manager="micromamba")
    cmd.append(f"--prefix={env_dir}")
    return subprocess.run(cmd, check=True)


def test_limited_api_pep725(tmp_path, conda_env, package_limited_api_pep725):
    _install_external(conda_env, package_limited_api_pep725)
    if sys.platform.startswith("linux"):
        assert Path(conda_env, "bin/gcc").is_file()
    elif sys.platform == "darwin":
        assert Path(conda_env, "bin/clang").is_file()
    elif sys.platform == "win32":
        pass  # compiler must be present in system separately

    with in_git_repo_context():
        wheel_path = tmp_path / mesonpy.build_wheel(tmp_path)
    conda_env.pip("install", wheel_path)

    output = conda_env.python("-c", "import module; print(module.add(1, 2))")
    assert int(output) == 3


# def test_link_against_local_lib_pep725(tmp_path, venv, package_link_against_local_lib_pep725):
#     _install_external(package_link_against_local_lib_pep725)
#     assert Path(CONDA_PREFIX, "bin/clang").is_file()

#     with in_git_repo_context():
#         wheel_path = tmp_path / mesonpy.build_wheel(tmp_path)
#     venv.pip("install", wheel_path, "-vvv")

#     output = venv.python("-c", "import example; print(example.example_sum(1, 2))")
#     assert int(output) == 3
