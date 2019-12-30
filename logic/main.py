#!/usr/bin/env python3
import argparse
from workflow_controller import WorkflowController
from game_timer import GameTimer


def loadWorkflow(module_name, class_name):
    module = __import__(module_name)
    mainWorkflow = getattr(module, class_name)
    return mainWorkflow()


def parseArgs():
    # initiate the parser
    parser = argparse.ArgumentParser()

    help_text = """
    definition of the workflow.
    Format: module:class
    with get method returning an array of Workflows.
    """

    # add long and short argument
    parser.add_argument("--workflow_def", "-d", help=help_text)

    # read arguments from the command line
    return parser.parse_args()


if __name__ == "__main__":
    args = parseArgs()

    workflow_module = "workflow_definition"
    workflow_class = "WorkflowDefinition"
    if args.workflow_def:
        definition = args.workflow_def.split(":")
        workflow_module = definition[0]
        workflow_class = definition[1]

    mqtt_url = "127.0.0.1"

    game_timer = GameTimer(mqtt_url, "1/gameTime")
    workflowDefinition = loadWorkflow(workflow_module, workflow_class)
    controller = WorkflowController(mqtt_url, workflowDefinition.get())
    game_timer.start()
    controller.start()
    input("Press Enter to continue...\n")
    controller.stop()
    game_timer.cancel()

    # TODO: Design game workflow
    # TODO: Worklow simulation
