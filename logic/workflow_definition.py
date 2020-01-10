from workflow import Workflow
from workflow import ParallelWorkflow
from workflow import DoorWorkflow
from workflow import SequenceWorkflow
from workflow import DoorTargetState as ds


class WorkflowDefinition:

    def get(self):
        return [
            # First puzzle
            Workflow("Keypad_code_entrance_door", "4/door/entrance/puzzle"),
            # Open door after successfully solved previous puzzle
            DoorWorkflow("Entrance_door_opening",
                         "4/door/entrance", ds.OPENED),
            # Second puzzle for closing lab door
            Workflow("Closing_entrance_door_globes",
                     "4/puzzle", {'participants': 4}),
            # Allow multiple riddles in lab room
            ParallelWorkflow("Lab room", [
                SequenceWorkflow("Solve safe", [
                    Workflow("Activate_safe_lab_room", "5/safe/activate"),
                    Workflow("Open_safe_lab_room", "5/safe/control")
                ]),
                SequenceWorkflow("Solve fusebox", [
                    Workflow("Laser_lab_room", "7/laser"),
                    Workflow("Fusebox_lab_room", "7/fusebox"),
                    Workflow("Robot_lab_room", "7/robot")
                ])
                # Workflow("Button_lab_room", "7/buttonServer"),
                # Workflow("Catflap_lab_room", "7/catflap")
            ]),
            # Allow multiple riddles in server room
            ParallelWorkflow("Server room", [
                Workflow("Floppy_disk_server_room", "6/puzzle/floppy"),
                # Workflow("Terminal_server_room", "6/puzzle/terminal"),
                Workflow("Maze_server_room", "8/puzzle/maze"),
                Workflow("Simon_server_room", "8/puzzle/simon")
            ])
        ]
