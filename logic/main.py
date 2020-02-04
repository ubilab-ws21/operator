#!/usr/bin/env python3
import sys
import signal
import argparse
from workflow_controller import WorkflowController


def load_workflow(module_name, class_name):
    """
    Loads the dynamically on runtime.
    Can be interpreted as:
    from <module_name> import <class_name>

    Parameters
    ----------
    module_name : str
        The module name is the name of the .py file to be loaded from.

    class_name : str
        The class which should be imported from the module

    Returns
    -------
    The instantiated workflow definition.
    """
    module = __import__(module_name)
    main_morkflow = getattr(module, class_name)
    return main_morkflow()


def parse_args():
    """
    Parses the command line arguments.
    """
    parser = argparse.ArgumentParser()

    help_text = """
    definition of the workflow.
    Format: module:class
    with get method returning an array of Workflows.
    """
    parser.add_argument("--workflow_def", "-d", help=help_text)
    parser.add_argument(
        "--mqtt_host",
        "-m",
        default="127.0.0.1",
        help="IP of the MQTT server.")
    return parser.parse_args()


def shutdown(controller):
    """
    Shutdown the programm.
    """
    controller.disconnect()
    sys.exit(0)


if __name__ == "__main__":
    # parse command line arguments
    args = parse_args()
    mqtt_url = args.mqtt_host

    # get parameter to load workflow definition
    workflow_module = "workflow_definition"
    workflow_class = "WorkflowDefinition"
    if args.workflow_def:
        definition = args.workflow_def.split(":")
        workflow_module = definition[0]
        workflow_class = definition[1]

    # load workflow to be executed
    workflow_factory = load_workflow(workflow_module, workflow_class)

    # create workflow controller with defined workflow
    controller = WorkflowController(mqtt_url, workflow_factory)
    controller.connect()

    # listen to SIGINT and wait until exit request received 
    signal.signal(signal.SIGINT, lambda sig, frame: shutdown(controller))
    print('Press Ctrl+C to exit...')
    signal.pause()
