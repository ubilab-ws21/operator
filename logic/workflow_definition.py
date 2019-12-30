from workflow import Workflow
from workflow import ParallelWorkflow
from workflow import DoorWorkflow
from workflow import DoorTargetState as ds


class WorkflowDefinition:

    def get(self):
        return [
            Workflow("Keypad_code_entrance_door", "4/door/entrance/puzzle"),
            DoorWorkflow("Door_opening", "4/door/entrance", ds.OPENED),
            Workflow("Globes_server_room", "4/puzzle", {'participants': 4}),
            ParallelWorkflow("Lab room", [
                Workflow("Puzzle 4", "QUEUE_Puzzle_4"),
                Workflow("Puzzle 5", "QUEUE_Puzzle_5")
            ])
        ]
