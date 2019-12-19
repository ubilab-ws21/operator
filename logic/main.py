#!/usr/bin/env python3
from workflow_controller import WorkflowController
from workflow import Workflow

if __name__ == "__main__":
    simpleController = Workflow("Test1", "Test")
    controller = WorkflowController("127.0.0.1", [simpleController])
    controller.start()
    input("Press Enter to continue...\n")
    controller.stop()
