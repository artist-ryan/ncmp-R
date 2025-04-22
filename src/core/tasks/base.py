from abc import ABC, abstractmethod
from typing import Dict

import requests

from ...utils.logger import Logger


class BaseTask(ABC):
    def __init__(self, session: requests.Session, logger: Logger, config: Dict):
        self.session = session
        self.logger = logger
        self.config = config

    @abstractmethod
    def execute(self) -> bool:
        """执行任务的抽象方法"""
        pass 