import subprocess
import sys
from pathlib import Path

from setuptools import Command
from setuptools import find_packages, setup as setuptools_setup


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
VERSION = "0.1.0"


def read_requirements() -> list[str]:
    requirements = []
    for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("pytest"):
            continue
        requirements.append(line)
    return requirements


def read_readme() -> str:
    return (ROOT / "README.md").read_text(encoding="utf-8")


class BDistExe(Command):
    description = "build a self-contained Windows executable with PyInstaller"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if sys.platform != "win32":
            raise SystemExit("bdist_exe must be run on Windows with Python 3.12.")

        icon_ico = SRC / "gui_files" / "icon.ico"
        icon_png = SRC / "gui_files" / "icon.png"
        hidden_imports = [
            "kraken",
            "kraken.containers",
            "kraken.lib.models",
            "kraken.lib.xml",
            "kraken.rpred",
            "lxml.etree",
            "PIL.Image",
            "PySide6.QtCore",
            "PySide6.QtGui",
            "PySide6.QtWidgets",
            "saxonche",
            "shiboken6",
            "torch",
            "torch.distributed",
            "torch.nn",
            "torch.nn.functional",
        ]
        collected_submodules = [
            "torch.distributed",
        ]
        excluded_modules = [
            "coremltools",
            "pytest",
            "skimage",
            "sklearn",
            "tensorflow",
            "tests",
            "tkinter",
            "torch.distributions",
            "torch.testing",
            "torch.utils.tensorboard",
            "torchaudio",
            "torchvision",
            "unittest",
        ]
        command = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--clean",
            "--onefile",
            "--windowed",
            "--name",
            "GlossToolsXML",
            "--icon",
            str(icon_ico),
            "--paths",
            str(SRC),
            "--add-data",
            f"{icon_png};gui_files",
            "--add-data",
            f"{icon_ico};gui_files",
        ]
        for module in hidden_imports:
            command.extend(["--hidden-import", module])
        for module in collected_submodules:
            command.extend(["--collect-submodules", module])
        for module in excluded_modules:
            command.extend(["--exclude-module", module])
        command.append(str(SRC / "connect_gui.py"))
        subprocess.check_call(command)


setup_function = setuptools_setup
setup_kwargs = {
    "name": "glosstools-xml",
    "version": VERSION,
    "description": "GlossIT XML tools and gloss connector GUI.",
    "long_description": read_readme(),
    "long_description_content_type": "text/markdown",
    "license": "GPL-3.0-only",
    "license_files": ["LICENSE"],
    "python_requires": ">=3.12,<3.13",
    "package_dir": {"": "src"},
    "packages": find_packages(where="src", exclude=["tests", "tests.*"]),
    "py_modules": [
        "connect_gui",
        "coordinate_manipulation",
        "glossit_connect_glosses",
        "glossit_dataclasses",
        "glossit_sanity_checks",
        "main",
        "xml_extraction",
    ],
    "include_package_data": True,
    "package_data": {
        "gui_files": ["*.ico", "*.png", "*.ui"],
    },
    "install_requires": read_requirements(),
    "extras_require": {
        "publish": ["build>=1.2", "twine>=5.0", "wheel>=0.43"],
        "windows": ["cx_Freeze>=8.6", "pyinstaller>=6.0"],
    },
    "cmdclass": {
        "bdist_exe": BDistExe,
    },
    "entry_points": {
        "console_scripts": [
            "glosstools-xml=main:main",
        ],
        "gui_scripts": [
            "glossit-gloss-connector=connect_gui:start_gui",
        ],
    },
    "classifiers": [
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Topic :: Text Processing :: Markup :: XML",
    ],
}


if {"build_exe", "bdist_msi"}.intersection(sys.argv[1:]):
    try:
        from cx_Freeze import Executable, setup as cx_freeze_setup
    except ImportError as exc:
        raise SystemExit(
            "cx_Freeze is required for Windows exe/msi builds. "
            "Install it with: python -m pip install -e .[windows]"
        ) from exc

    setup_function = cx_freeze_setup
    icon_ico = SRC / "gui_files" / "icon.ico"
    icon_png = SRC / "gui_files" / "icon.png"
    gui_base = "gui" if sys.platform == "win32" else None
    build_exe_dir = "build/exe.win-amd64-3.12"
    directory_table = [
        ("ProgramMenuFolder", "TARGETDIR", "."),
        ("GlossToolsXMLMenu", "ProgramMenuFolder", "GLOSS~1|GlossTools XML"),
    ]
    cx_freeze_includes = [
        "kraken",
        "kraken.containers",
        "kraken.lib.models",
        "kraken.lib.xml",
        "kraken.rpred",
        "lxml.etree",
        "PIL.Image",
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "saxonche",
        "shiboken6",
        "torch",
        "torch.distributed",
        "torch.nn",
        "torch.nn.functional",
    ]
    cx_freeze_packages = [
        "bs4",
        "colorama",
        "gui_files",
        "matplotlib",
        "networkx",
        "numpy",
        "pyqttoast",
        "rtree",
        "shapely",
        "tqdm",
        "torch.distributed",
        "umsgpack",
        "xmlschema",
    ]
    cx_freeze_excludes = [
        "coremltools",
        "pytest",
        "skimage",
        "sklearn",
        "tensorflow",
        "tests",
        "tkinter",
        "torch.distributions",
        "torch.testing",
        "torch.utils.tensorboard",
        "torchaudio",
        "torchvision",
        "unittest",
    ]

    setup_kwargs["options"] = {
        "build_exe": {
            "build_exe": build_exe_dir,
            "includes": cx_freeze_includes,
            "packages": cx_freeze_packages,
            "include_files": [
                (str(icon_png), "gui_files/icon.png"),
                (str(icon_ico), "gui_files/icon.ico"),
            ],
            "excludes": cx_freeze_excludes,
            "include_msvcr": True,
        },
        "bdist_msi": {
            "add_to_path": False,
            "data": {
                "Directory": directory_table,
            },
            "initial_target_dir": r"[ProgramFiles64Folder]GlossIT\GlossTools XML",
            "install_icon": str(icon_ico),
            "output_name": f"GlossToolsXML-{VERSION}-win64.msi",
            "product_name": "GlossTools XML",
            "summary_data": {
                "author": "GlossIT",
                "comments": "GlossIT XML tools and gloss connector GUI.",
            },
            "upgrade_code": "{8F0CF2D6-8F75-4E7E-87E9-6791D29F0B80}",
        },
    }
    setup_kwargs["executables"] = [
        Executable(
            script=str(SRC / "connect_gui.py"),
            base=gui_base,
            target_name="GlossToolsXML.exe",
            icon=str(icon_ico),
            shortcut_name="GlossIT Gloss Connector",
            shortcut_dir="GlossToolsXMLMenu",
        ),
        Executable(
            script=str(SRC / "main.py"),
            base=None,
            target_name="glosstools-xml-cli.exe",
            icon=str(icon_ico),
        ),
    ]


setup_function(**setup_kwargs)
