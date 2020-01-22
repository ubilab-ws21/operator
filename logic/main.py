#!/usr/bin/env python3
import argparse
from workflow_controller import WorkflowController


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

    workflow_factory = loadWorkflow(workflow_module, workflow_class)
    controller = WorkflowController(mqtt_url, workflow_factory)
    controller.connect()
    input("Press Enter to continue...\n")
    controller.disconnect()
