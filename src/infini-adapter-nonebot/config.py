from typing import ClassVar
from pydantic import BaseModel


class Config(BaseModel, extra="allow"):
    """Plugin Config Here"""

    driver: ClassVar = "~fastapi+~httpx+~websockets"
