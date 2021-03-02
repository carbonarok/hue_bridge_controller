"""Replacement for Makefile."""
import os
import sys
from distutils.util import strtobool
from invoke import task

try:
    import toml
except ImportError:
    sys.exit(
        "Please make sure to `pip install toml` or enable the Poetry shell and run `poetry install`."
    )


def project_ver():
    """Find version from pyproject.toml to use for docker image tagging."""
    with open("pyproject.toml") as file:
        return toml.load(file)["tool"]["poetry"].get("version", "latest")


def project_name():
    """Find name from pyproject.toml to use for docker image tagging."""
    with open("pyproject.toml") as file:
        return toml.load(file)["tool"]["poetry"]["name"]


def is_truthy(arg):
    """Convert "truthy" strings into Booleans.

    Examples:
        >>> is_truthy('yes')
        True
    Args:
        arg (str): Truthy string (True values are y, yes, t, true, on and 1; false values are n, no,
        f, false, off and 0. Raises ValueError if val is anything else.
    """
    if isinstance(arg, bool):
        return arg
    return bool(strtobool(arg))


# Can be set to a separate Python version to be used for launching or building container
PYTHON_VER = os.getenv("PYTHON_VER", "3.7")
# Valid Python Versions
VALID_PYTHON_VERS = ["3.7", "3.8"]
# Name of the project
PROJECT_NAME = project_name()
# Version of the project
PROJECT_VER = project_ver()
# By default docker images will be built and tagged: {PROJECT_NAME}:{PROJECT_VER}-py{PYTHON_VER}
# Name of the docker image/container
IMAGE_NAME = os.getenv("IMAGE_NAME", PROJECT_NAME)
# Tag for the image
IMAGE_VER = os.getenv("IMAGE_VER", f"{PROJECT_VER}-py{PYTHON_VER}")
# Gather current working directory for Docker commands
PWD = os.getcwd()
# Local or Docker execution provide "local" to run locally without docker execution
INVOKE_LOCAL = is_truthy(os.getenv("INVOKE_LOCAL", False))  # pylint: disable=W1508
# Name of Jenkins Buildnode Image
JENKINS_BUILDNODE_IMAGE_NAME = (
    f"registry.rcluster.io/rdirect/autonet-core-system-builder:{PROJECT_VER}"
)


def run_cmd(context, exec_cmd, local=INVOKE_LOCAL):
    """Wrapper to run the invoke task commands.

    Args:
        context ([invoke.task]): Invoke task object.
        exec_cmd ([str]): Command to run.
        local (bool): Define as `True` to execute locally

    Returns:
        result (obj): Contains Invoke result from running task.
    """
    if local:
        print(f"LOCAL - Running command {exec_cmd}")
        result = context.run(exec_cmd, pty=True)
    else:
        print(
            f"DOCKER - Running command: {exec_cmd} container: {IMAGE_NAME}:{IMAGE_VER}"
        )
        result = context.run(
            f"docker run -it -v {PWD}:/local {IMAGE_NAME}:{IMAGE_VER} sh -c '{exec_cmd}'",
            pty=True,
        )

    return result


@task
def build(context):
    """This will build a container with the provided name and python version.

    Args:
        context (obj): Used to run specific commands
    """
    print(f"Building container {IMAGE_NAME}:{IMAGE_VER}")
    result = context.run(
        f"docker build --tag {IMAGE_NAME}:{IMAGE_VER} --build-arg PYTHON_VER={PYTHON_VER} -f Dockerfile .",
        hide=True,
    )
    if result.exited != 0:
        print(
            f"Failed to build container {IMAGE_NAME}:{IMAGE_VER}\nError: {result.stderr}"
        )


@task
def clean(context):
    """This stops and removes the specified image.

    Args:
        context (obj): Used to run specific commands
    """
    print(f"Attempting to forcefully remove image {IMAGE_NAME}:{IMAGE_VER}")
    context.run(f"docker rmi {IMAGE_NAME}:{IMAGE_VER} --force")
    print(f"Successfully removed image {IMAGE_NAME}:{IMAGE_VER}")


@task
def rebuild(context):
    """This will clean the image and then rebuild image without using cache.

    Args:
        context (obj): Used to run specific commands
    """
    clean(context)
    build(context)


@task
def pytest(context):
    """This will run pytest for the specified name and Python version.

    Args:
        context (obj): Used to run specific commands
    """
    # pty is set to true to properly run the docker commands due to the invocation process of docker
    # https://docs.pyinvoke.org/en/latest/api/runners.html - Search for pty for more information
    # Install python module
    exec_cmd = "pytest -vv"
    run_cmd(context, exec_cmd)


@task
def black(context):
    """This will run black to check that Python files adherence to black standards.

    Args:
        context (obj): Used to run specific commands
    """
    # pty is set to true to properly run the docker commands due to the invocation process of docker
    # https://docs.pyinvoke.org/en/latest/api/runners.html - Search for pty for more information
    exec_cmd = "black --check --diff ."
    run_cmd(context, exec_cmd)


@task
def flake8(context):
    """This will run flake8 for the specified name and Python version.

    Args:
        context (obj): Used to run specific commands
    """
    # pty is set to true to properly run the docker commands due to the invocation process of docker
    # https://docs.pyinvoke.org/en/latest/api/runners.html - Search for pty for more information
    exec_cmd = "flake8 ."
    run_cmd(context, exec_cmd)


@task
def pylint(context):
    """This will run pylint for the specified name and Python version.

    Args:
        context (obj): Used to run specific commands
    """
    # pty is set to true to properly run the docker commands due to the invocation process of docker
    # https://docs.pyinvoke.org/en/latest/api/runners.html - Search for pty for more information
    exec_cmd = 'find . -name "*.py" | xargs pylint'
    run_cmd(context, exec_cmd)


@task
def pydocstyle(context):
    """This will run pydocstyle to validate docstring formatting adheres to NTC defined standards.

    Args:
        context (obj): Used to run specific commands
    """
    # pty is set to true to properly run the docker commands due to the invocation process of docker
    # https://docs.pyinvoke.org/en/latest/api/runners.html - Search for pty for more information
    exec_cmd = "pydocstyle ."
    run_cmd(context, exec_cmd)


@task
def bandit(context):
    """This will run bandit to validate basic static code security analysis.

    Args:
        context (obj): Used to run specific commands
    """
    # pty is set to true to properly run the docker commands due to the invocation process of docker
    # https://docs.pyinvoke.org/en/latest/api/runners.html - Search for pty for more information
    exec_cmd = "bandit --recursive ./ --configfile .bandit.yml"
    run_cmd(context, exec_cmd)


@task
def cli(context):
    """This will enter the image to perform troubleshooting or dev work.

    Args:
        context (obj): Used to run specific commands
    """
    exec_cmd = "/bin/bash"
    run_cmd(context, exec_cmd, local=False)


@task
def tests(context):
    """This will run all tests for the specified name and Python version.

    Args:
        context (obj): Used to run specific commands
    """
    print("Running black...")
    black(context)
    print("Running flake8...")
    flake8(context)
    # print("Running pylint...")
    # pylint(context)
    # print("Running pydocstyle...")
    # pydocstyle(context)
    print("Running bandit...")
    bandit(context)
    print("Running pytest...")
    pytest(context)

    print("All tests have passed!")
