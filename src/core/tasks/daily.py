from typing import Dict, Tuple

from ..signer import Signer
from .base import BaseTask


class DailyTask(BaseTask):
    def __init__(self, session, logger, config):
        super().__init__(session, logger, config)
        self.api = {
            "task_data": "https://interface.music.163.com/api/music/partner/daily/task/get"
        }

    def execute(self) -> bool:
        try:
            complete, task_data = self._get_daily_tasks()
            if not complete:
                self._process_tasks(task_data)
            return True
        except Exception as e:
            self.logger.error(f"执行每日任务失败: {str(e)}")
            return False

    def _get_daily_tasks(self) -> Tuple[bool, Dict]:
        """获取每日任务"""
        response = self.session.get(url=self.api["task_data"]).json()
        task_data = response.get("data", {})
        
        count = task_data.get("count", 0)
        completed_count = task_data.get("completedCount", 0)
        today_task = f"[{completed_count}/{count}]"
        complete = count == completed_count
        
        self.logger.info(f'今日任务：{"已完成" if complete else "未完成"}{today_task}')
        return complete, task_data

    def _process_tasks(self, task_data: Dict) -> None:
        """处理未完成的任务"""
        self.logger.info("开始评分...")
        signer = Signer(self.session, task_data["id"], self.logger, self.config)
        
        for task in task_data.get("works", []):
            work = task["work"]
            if task["completed"]:
                self.logger.info(f'{work["name"]}「{work["authorName"]}」已有评分：{int(task["score"])}分')
            else:
                signer.sign(work) 