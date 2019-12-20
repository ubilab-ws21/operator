#!/usr/bin/env python3
from workflow_controller import WorkflowController
from workflow import Workflow

if __name__ == "__main__":
    simpleController = [
        Workflow("Puzzle 1", "QUEUE_Puzzle_1"),
        Workflow("Puzzle 2", "QUEUE_Puzzle_2"),
        Workflow("Puzzle 3", "QUEUE_Puzzle_3")
    ]
    controller = WorkflowController("127.0.0.1", simpleController)
    controller.start()
    input("Press Enter to continue...\n")
    controller.stop()
