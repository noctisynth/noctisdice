from concurrent.futures import ThreadPoolExecutor
from typing import Callable
from .utils import hmr, file_upload, install, sync

pool = ThreadPoolExecutor(20)
workflows = {
    "echo.hmr": hmr,
    "echo.upload": file_upload,
    "sync": sync,
    "install": install,
}


def put(func: Callable):
    pool.submit(func)
