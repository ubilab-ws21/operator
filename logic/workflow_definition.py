from workflow import Workflow
from workflow import ParallelWorkflow
from workflow import DoorWorkflow
from workflow import SequenceWorkflow
from workflow import ActivateLaserWorkflow
from workflow import ScaleWorkflow
from workflow import DoorTargetState as ds


class WorkflowDefinition:

    def create(self):
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
                    Workflow("Open_safe_lab_room", "5/safe/control"),
                    ScaleWorkflow("Scale_puzzle_lab_room", "6/puzzle/scale")
                ]),
                SequenceWorkflow("Solve fusebox", [
                    ActivateLaserWorkflow("Laser_lab_room", "7/laser"),
                    ParallelWorkflow("Solve fuse box", [
                        Workflow("Fusebox_laser_detection_lab_room",
                                 "7/fusebox/laserDetection"),
                        Workflow("Fusebox_rewiring0_lab_room",
                                 "7/fusebox/rewiring0"),
                        Workflow("Fusebox_rewiring1_lab_room",
                                 "7/fusebox/rewiring1"),
                        Workflow("Fusebox_potentiometer_lab_room",
                                 "7/fusebox/potentiometer")
                    ]),
                    Workflow("Robot_lab_room", "7/robot")
                ])
            ]),
            # Allow multiple riddles in server room
            ParallelWorkflow("Server room", [
                Workflow("Floppy_disk_server_room", "6/puzzle/floppy"),
                Workflow("Terminal_server_room", "6/puzzle/terminal"),
                Workflow("Maze_server_room", "8/puzzle/maze"),
                Workflow("Simon_server_room", "8/puzzle/simon")
            ])
        ]
