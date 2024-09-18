import json
import shutil
from pathlib import Path

import isort
from cleo.io.inputs.input import Input
from cleo.io.io import IO
from cleo.io.outputs.buffered_output import BufferedOutput
from poetry.factory import Factory
from poetry_plugin_export.exporter import Exporter


def repo_path():
    return Path(__file__).parent.parent


def export_requirements_to_string():
    # TODO change to simpler requirements.txt modification after pypi release

    # Load the Poetry instance from the current project
    poetry = Factory().create_poetry()

    # Create a buffer for output
    out = BufferedOutput()
    io = IO(Input(), out, None)
    exporter = (
        Exporter(poetry, io)
        .with_credentials(False)
        .with_hashes(False)
        .with_urls(False)
    )

    exporter.export("requirements.txt", Path.cwd(), io)
    requirements = ""
    for line in out.fetch().splitlines():
        requirements += line[: line.find(";")] + "\n"
    return requirements


def add_am_lib(app_dir: Path):
    # TODO change to requirements.txt modification after pypi release
    print(f"Copying {repo_path()} to {app_dir}")
    shutil.rmtree(app_dir / "soar_asset_mocker", ignore_errors=True)
    shutil.copytree(repo_path(), app_dir / "soar_asset_mocker")


def update_dependencies(requirements_path: Path):
    with open(requirements_path, "a+") as f:
        f.write("\n#Asset Mocker Dependencies\n")
        f.write(export_requirements_to_string())


def modify_code(f):
    modified_code = ""
    imports_added = False
    for line in f.readlines():
        if not imports_added and (
            line.startswith("import ") or line.startswith("from ")
        ):
            modified_code += (
                "from soar_asset_mocker import AssetMocker, MockType\n"
            )
            imports_added = True
        if "def handle_action(self" in line:
            modified_code += (
                line.find("def") * " " + "@AssetMocker.use(MockType.HTTP)\n"
            )
        modified_code += line
    return modified_code


def inject_am_decorator(app_py_path: Path):
    print(f"Adding decorator to {app_py_path}")
    "from soar_asset_mocker import AssetMocker"
    "AssetMocker.use(MockType.HTTP)"
    with open(app_py_path) as f:
        modified_code = modify_code(f)
    with open(app_py_path, "w") as f:
        f.write(isort.code(modified_code))


def inject_app(app_json_path: Path):
    with open(app_json_path) as f:
        app_json = json.load(f)
    app_py_path = app_json_path.parent / app_json["main_module"]

    add_am_lib(app_json_path.parent)
    inject_am_decorator(app_py_path)
    update_dependencies(app_json_path.parent / "requirements.txt")
