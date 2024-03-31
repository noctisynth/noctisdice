from typing import Optional
from nonebot.adapters import Bot
from nonebot.log import logger
from pathlib import Path
from ipm.models.ipk import InfiniProject
from infini.core import Core
from infini.loader import Loader
from infini.output import Output

import importlib
import sys
import asyncio

core: Core


def get_core():
    return core


def get_packages():
    project = InfiniProject()
    packages = [requirement.name for requirement in project.requirements]
    return packages


def hmr(output: Optional[Output] = None):
    global core
    importlib.invalidate_caches()

    packages = get_packages()
    logger.info("挂载规则包: " + ", ".join(packages))

    loader = Loader()
    for package in packages:
        for name in [name for name in sys.modules.keys() if name.startswith(package)]:
            sys.modules[name] = (
                importlib.reload(sys.modules[name])
                if name in sys.modules
                else importlib.import_module(name)
            )
        sys.modules[package] = (
            importlib.reload(sys.modules[package])
            if package in sys.modules
            else importlib.import_module(package)
        )

        loader.load(package)
    core = loader.into_core()
    loader.close()

    if output:
        output.status = 0


def file_upload(bot: Bot, filepath: Path, output: Output):
    asyncio.run(
        bot.call_api(
            "upload_group_file",
            **{
                "group_id": output.variables["group_id"],
                "file": str(filepath),
                "name": filepath.name,
            },
        )
    )
    output.status = 0
