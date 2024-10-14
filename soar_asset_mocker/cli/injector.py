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
    poetry = Factory().create_poetry(cwd=repo_path())

    # Create a buffer for output
    out = BufferedOutput()
    io = IO(Input(), out, None)
    exporter = Exporter(poetry, io).with_credentials(False).with_hashes(False).with_urls(False)

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
    print("Updating requirements.txt")
    mocker_reqs = f"\n#Asset Mocker Dependencies\n{export_requirements_to_string()}"
    with open(requirements_path, "r") as f:
        reqs = f.read()
    if mocker_reqs in reqs:
        return
    with open(requirements_path, "a+") as f:
        f.write(mocker_reqs)


def modify_code(f):
    modified_code = ""
    import_added = False
    decorator_added = False

    import_line = "from soar_asset_mocker import AssetMocker, MockType\n"
    decorator_line = "@AssetMocker.use(MockType.HTTP)\n"

    for line in f.readlines():
        decorator_added = decorator_added or decorator_line in line
        import_added = import_added or import_line in line

        # search for import part of the code to append import_line
        # if it wasn't appended yet.
        if not import_added and (line.startswith("import ") or line.startswith("from ")):
            modified_code += import_line
            import_added = True

        # search for `handle_action` method in connector code
        # append decorator to this method if it's not already there
        if not decorator_added and "def handle_action(self" in line:
            modified_code += line.find("def") * " " + decorator_line

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
