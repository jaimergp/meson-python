# SPDX-FileCopyrightText: 2025 The meson-python developers
#
# SPDX-License-Identifier: MIT
import platform
import shutil
import subprocess
import sys

from pathlib import Path

from pyproject_external import External

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


def _assert_package_installed(package: str, prefix: Path) -> Path:
    prefix = Path(str(prefix))
    if package == "<c-compiler>":
        if sys.platform.startswith("linux"):
            pkg = (prefix / "bin" / "gcc")
        elif sys.platform == "darwin":
            pkg = next((prefix / "bin").glob(f"{platform.machine()}-*-clang"))
    else:
        pkg = shutil.which(package)
    assert pkg is not None
    pkg = Path(pkg)
    assert pkg.is_file()
    assert str(prefix) in str(pkg)
    return pkg


def _get_meson_logs(build_dir: Path) -> str:
    return (build_dir / "meson-logs" / "meson-log.txt").read_text()


def test_limited_api_pep725(
    tmp_path: Path,
    conda_env: CondaEnv,
    package_limited_api_pep725,
):
    _install_external(conda_env, package_limited_api_pep725)
    pkg_config = _assert_package_installed("pkg-config", conda_env)
    compiler = _assert_package_installed("<c-compiler>", conda_env)
    resolved_compiler = compiler.resolve()

    with in_git_repo_context():
        wheel_path = tmp_path / mesonpy.build_wheel(
            tmp_path,
            config_settings={"build-dir": str(tmp_path / "_build")},
        )

    # Make sure the detected compiler comes from our prefix
    logs = _get_meson_logs(tmp_path / "_build")
    if sys.platform != "win32":  # pkg-config not used in Windows
        assert compiler.name in logs or resolved_compiler.name in logs
        assert str(pkg_config) in logs

    conda_env.pip("install", wheel_path)
    output = conda_env.python("-c", "import module; print(module.add(1, 2))")
    assert int(output) == 3


def test_link_against_local_lib_pep725(
    tmp_path: Path,
    conda_env: CondaEnv,
    package_link_against_local_lib_pep725,
):
    _install_external(conda_env, package_link_against_local_lib_pep725)
    pkg_config = _assert_package_installed("pkg-config", conda_env)
    compiler = _assert_package_installed("<c-compiler>", conda_env)
    resolved_compiler = compiler.resolve()

    with in_git_repo_context():
        wheel_path = tmp_path / mesonpy.build_wheel(
            tmp_path,
            config_settings={"build-dir": str(tmp_path / "_build")},
        )

    # Make sure the detected compiler comes from our prefix
    logs = _get_meson_logs(tmp_path / "_build")
    if sys.platform != "win32":  # pkg-config not used in Windows
        assert compiler.name in logs or resolved_compiler.name in logs
        assert str(pkg_config) in logs

    conda_env.pip("install", wheel_path, "-vvv")

    output = conda_env.python("-c", "import example; print(example.example_sum(1, 2))")
    assert int(output) == 3
