
from datetime import datetime


class TaskPlanner:

    def __init__(self):

        self.tasks = []
        self.next_task_id = 1

    def create_plan(self, goal, steps=None):

        if not isinstance(goal, str) or not goal.strip():
            return None

        if steps is None:
            steps = []

        if not isinstance(steps, list):
            return None

        plan = {
            "task_id": self.next_task_id,
            "goal": goal.strip(),
            "steps": [
                {
                    "step_number": index + 1,
                    "description": str(step).strip(),
                    "status": "pending"
                }
                for index, step in enumerate(steps)
                if str(step).strip()
            ],
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }

        self.tasks.append(plan)
        self.next_task_id += 1

        return plan

    def get_plan(self, task_id):

        for task in self.tasks:
            if task["task_id"] == task_id:
                return task

        return None

    def update_step(self, task_id, step_number, status):

        if status not in ("pending", "in_progress", "completed", "failed"):
            return False

        plan = self.get_plan(task_id)

        if not plan:
            return False

        for step in plan["steps"]:
            if step["step_number"] == step_number:
                step["status"] = status
                self._update_plan_status(plan)
                return True

        return False

    def _update_plan_status(self, plan):

        steps = plan["steps"]

        if not steps:
            return

        if all(step["status"] == "completed" for step in steps):
            plan["status"] = "completed"

        elif any(step["status"] == "failed" for step in steps):
            plan["status"] = "failed"

        elif any(step["status"] == "in_progress" for step in steps):
            plan["status"] = "in_progress"

        else:
            plan["status"] = "pending"

    def get_all_tasks(self):

        return self.tasks.copy()

    def clear_completed_tasks(self):

        self.tasks = [
            task for task in self.tasks
            if task["status"] != "completed"
        ]
