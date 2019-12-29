from workflow import Workflow


class WorkflowDefinition:

    def get(self):
        return [
            Workflow("Puzzle 1", "QUEUE_Puzzle_1"),
            Workflow("Puzzle 2", "QUEUE_Puzzle_2"),
            Workflow("Puzzle 3", "QUEUE_Puzzle_3")
        ]
