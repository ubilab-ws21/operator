from workflow import Workflow
from workflow import ParallelWorkflow
from workflow import SequenceWorkflow
from workflow import SendTriggerWorkflow
from workflow import ScaleWorkflow
from workflow import InitWorkflow
from message import State


class WorkflowDefinition:

    def create(self, settings):
        participants = 4
        if settings:
            participants = settings['participants']

        return [
            # Init
            InitWorkflow([
                SendTriggerWorkflow("Close lab room door",
                                    "4/door/entrance", State.OFF),
                SendTriggerWorkflow("Close server room door",
                                    "4/door/server", State.OFF)
            ]),
            # First puzzle
            Workflow("Input keypad code", "4/puzzle"),
            # Open door after successfully solved previous puzzle
            SendTriggerWorkflow("Open lab room door",
                                "4/door/entrance", State.ON),
            # Second puzzle for closing lab door
            Workflow("Globes riddle", "4/globes", {'data': participants}),
            # Allow multiple riddles in lab room
            ParallelWorkflow("Lab room", [
                SequenceWorkflow("Solve safe", [
                    Workflow("Activate safe", "5/safe/activate"),
                    Workflow("Open safe", "5/safe/control"),
                    ScaleWorkflow("Scale riddle", "6/puzzle/scale")
                ]),
                SequenceWorkflow("Solve door riddle", [
                    SendTriggerWorkflow("Activate laser", "7/laser", State.ON),
                    ParallelWorkflow("Solve fuse box", [
                        Workflow("Redirect laser in fusebox",
                                 "7/fusebox/laserDetection"),
                        Workflow("First rewiring of fusebox",
                                 "7/fusebox/rewiring0"),
                        Workflow("Second rewiring of fusebox",
                                 "7/fusebox/rewiring1"),
                        Workflow("Set potentiometer of fusebox",
                                 "7/fusebox/potentiometer")
                    ]),
                    Workflow("Control robot", "7/robot"),
                    SendTriggerWorkflow("Open server room door",
                                        "4/door/server", State.ON)
                ])
            ]),
            # Allow multiple riddles in server room
            ParallelWorkflow("Server room", [
                Workflow("Terminal riddle", "6/puzzle/terminal"),
                Workflow("Maze riddle", "8/puzzle/maze"),
                Workflow("Simon riddle", "8/puzzle/simon")
            ]),
            SendTriggerWorkflow("Open escape room door",
                                "4/door/entrance", State.ON)
        ]
