from concurrent.futures import ThreadPoolExecutor
from typing import Callable
from .utils import adapter_update, hmr, file_upload, install, sync

pool = ThreadPoolExecutor(20)
workflows = {
    "echo.hmr": hmr,
    "echo.upload": file_upload,
    "ipm.sync": sync,
    "ipm.install": install,
    "ipm.adapter.update": adapter_update,
}


def put(func: Callable):
    pool.submit(func)
