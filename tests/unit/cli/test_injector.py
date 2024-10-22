import shutil
from pathlib import Path

from soar_asset_mocker.cli import injector


def test_add_am_lib(tmp_path):
    injector.add_am_lib(tmp_path)
    assert Path(tmp_path / "soar_asset_mocker").exists()


def test_update_dependencies(tmp_path):
    app_requirements = ["six==1.16.0\n", "selenium==4.9.1\n"]
    requirements_path = tmp_path / "requirements.txt"
    with open(requirements_path, "w") as f:
        f.writelines(app_requirements)
    injector.update_dependencies(requirements_path)
    with open(requirements_path, "r") as f:
        requirements_lines = f.readlines()

    print([line for line in requirements_lines if "pack" in line])
    for line in [
        *app_requirements,
        "#Asset Mocker Dependencies\n",
        'msgpack==1.1.0 ; python_version >= "3.9" and python_version < "4.0"\n',
    ]:
        assert line in requirements_lines


def test_inject_decorator(tmp_path):
    app_path = tmp_path / "app.py"
    path = Path(__file__).parent.parent.parent  # tests folder
    example_path = Path(path, "./files/example_connector.py")
    wanted_path = Path(path, "./files/example_connector_w_mocker.py")
    shutil.copy(example_path, app_path)

    injector.inject_am_decorator(app_path)

    with open(app_path) as f:
        actual_content = f.read()

    with open(wanted_path) as f:
        wanted_content = f.read()

    assert actual_content == wanted_content
