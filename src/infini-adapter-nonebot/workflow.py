from concurrent.futures import ThreadPoolExecutor
from typing import Callable
from .utils import adapter_update, hmr, file_upload, install, sync

pool = ThreadPoolExecutor(20)
workflows = {
    "echo.hmr": hmr,
    "echo.upload": file_upload,
    "sync": sync,
    "install": install,
    "adapter.update": adapter_update,
}


def put(func: Callable):
    pool.submit(func)
