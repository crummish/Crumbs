from dataclasses import dataclass
import json
import argparse
import os
import shutil
import requests
import concurrent.futures
import itertools
from pathlib import Path
from typing import Any, Sequence
from zipfile import ZipFile
from tempfile import TemporaryDirectory
from dotenv import load_dotenv
from functools import cached_property

script_dir = Path(os.path.realpath(__file__)).parent
SERVER_CONFIG = script_dir / "default.cfg"
SERVER_FILES = script_dir / "server_files"
CLIENT_OVERRIDES = ["config", "mods", "scripts"]
load_dotenv()
CURSEFORGE_API_KEY = os.getenv("CURSEFORGE_API_KEY")
if CURSEFORGE_API_KEY is None:
    raise IOError("Missing CurseForge API key.")


@dataclass
class Mod:
    json: Any

    @property
    def name(self) -> str:
        return self.json["__meta"]["name"]

    @property
    def project_id(self) -> str:
        return self.json["projectID"]

    @property
    def file_id(self) -> str:
        return self.json["fileID"]


@dataclass
class Manifest:
    json: Any

    @property
    def version(self) -> str:
        return self.json["version"]

    @property
    def name(self) -> str:
        return self.json["name"]

    @cached_property
    def mods(self) -> list[Mod]:
        return [Mod(f) for f in self.json["files"]]


def main():
    args = argument_parser().parse_args()
    with TemporaryDirectory() as server_modpack_dir, TemporaryDirectory() as client_modpack_dir:
        with ZipFile(args.client, "r") as client_modpack:
            client_modpack.extractall(client_modpack_dir)
        try:
            with open(Path(client_modpack_dir) / "manifest.json") as f_manifest:
                manifest = Manifest(json.load(f_manifest))
        except OSError:
            raise IOError("Client pack does not contain manifest.json file")
        for folder in CLIENT_OVERRIDES:
            try:
                shutil.copytree(
                    Path(client_modpack_dir) / "overrides" / folder,
                    Path(server_modpack_dir) / folder,
                )
            except FileNotFoundError:
                pass
        shutil.copytree(SERVER_FILES, server_modpack_dir, dirs_exist_ok=True)
        shutil.copyfile(SERVER_CONFIG, Path(server_modpack_dir) / "settings.cfg")
        with concurrent.futures.ThreadPoolExecutor() as exector:
            exector.map(download_mod, manifest.mods, itertools.repeat(Path(server_modpack_dir) / "mods"))
        shutil.make_archive(
            str(args.outfile).replace(".zip", ""), "zip", server_modpack_dir
        )


def download_mod(mod: Mod, target_dir: Path) -> Path:
    print(f"Downloading mod '{mod.name}'...")
    response = api_get_mod(mod)
    data = response["data"]
    if not data["isAvailable"] or data["downloadUrl"] is None:
        print(
            f"WARNING: Mod {data['displayName']} is unavailable from the CurseForge website."
        )
    with open(target_dir / data["fileName"], "wb") as f:
        response = requests.get(data["downloadUrl"])
        f.write(response.content)


def api_get_mod(mod: Mod) -> Any:
    headers = {"Accept": "application/json", "x-api-key": CURSEFORGE_API_KEY}
    r = requests.get(
        f"https://api.curseforge.com/v1/mods/{mod.project_id}/files/{mod.file_id}",
        headers=headers,
    )
    return r.json()


def with_extensions(path: Path, *extensions: str) -> str:
    if path.suffix not in extensions:
        raise argparse.ArgumentTypeError(
            f"File must have one of the following types: [{','.join(extensions)}]"
        )
    return path


def exists(path: Path) -> str:
    if not path.exists():
        raise argparse.ArgumentTypeError(f"File not found: {path}")
    return path


def valid_arg_client(param: str) -> str:
    return with_extensions(exists(Path(param)), ".zip")


def valid_arg_outfile(param: str) -> str:
    return with_extensions(Path(param), ".zip")


def argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a deployable Crumbs server pack."
    )
    parser.add_argument(
        "client",
        type=valid_arg_client,
        help="The client modpack (must be a zipfile in Curse modpack structure).",
    )
    parser.add_argument(
        "outfile",
        type=valid_arg_outfile,
        help="The zipfile to save the server pack to.",
    )
    return parser


if __name__ == "__main__":
    main()
