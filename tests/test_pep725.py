# SPDX-FileCopyrightText: 2025 The meson-python developers
#
# SPDX-License-Identifier: MIT
import subprocess
import sys

from pathlib import Path

from pyproject_external import External

import mesonpy

from .conftest import in_git_repo_context


def _install_external(directory: Path, ecosystem: str = "conda-forge") -> subprocess.CompletedProcess:
    external = External.from_pyproject_path(directory / "pyproject.toml")
    cmd = external.install_command(ecosystem=ecosystem, package_manager="conda")
    return subprocess.run(cmd, check=True)


def test_limited_api_pep725(tmp_path, venv, package_limited_api_pep725):
    _install_external(package_limited_api_pep725)
    assert Path(sys.prefix, "bin/clang").is_file()

    with in_git_repo_context():
        wheel_path = tmp_path / mesonpy.build_wheel(tmp_path)
    venv.pip("install", wheel_path)

    output = venv.python("-c", "import module; print(module.add(1, 2))")
    assert int(output) == 3


# def test_link_against_local_lib_pep725(tmp_path, venv, package_link_against_local_lib_pep725):
#     _install_external(package_link_against_local_lib_pep725)
#     assert Path(sys.prefix, "bin/clang").is_file()

#     with in_git_repo_context():
#         wheel_path = tmp_path / mesonpy.build_wheel(tmp_path)
#     venv.pip("install", wheel_path, "-vvv")

#     output = venv.python("-c", "import example; print(example.example_sum(1, 2))")
#     assert int(output) == 3
