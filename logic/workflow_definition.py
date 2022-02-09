from workflow import *
from workflow_extras import *
from message import State
from util import Location


class WorkflowDefinition:
    """
    This class serves as factory for the defined workflow.
    """

    def create(self, settings):
        participants = 4
        skip_to = None
        if settings:
            participants = settings.get('participants')
            skip_to = settings.get('skipTo')

        workflow = [
            # Init
            InitWorkflow([
                # legacy init
                SendTriggerWorkflow("Reset safe", "5/safe/control", State.OFF),
                SendTriggerWorkflow("Close lab room door", "4/door/entrance", State.OFF),
                SendTriggerWorkflow("Close server room door", "4/door/server", State.OFF),
                LightControlWorkflow(Location.LOBBYROOM, State.ON, 255, (255, 255, 255)),
                LightControlWorkflow(Location.MAINROOM, State.ON, 255, (255, 255, 255)),
                LightControlWorkflow(Location.SERVERROOM, State.ON, 255, (255, 255, 255)),

                # Puzzle 5 init
                SendMessageWorkflow("Set Battery Level", "5/battery/1/level", 0),
                #SendMessageWorkflow("Set Battery UID", "5/battery/1/uid", 0),
                #SendTriggerWorkflow("Open Safe", "5/safe/control", State.ON),
            ]),


            SequenceWorkflow("Lobby Room", [
                Workflow("Power Failure Trigger", "env/powerfail"),
                CombinedWorkflow("Power Failure Env", [
                    LightControlWorkflow(Location.LOBBYROOM, State.ON, 255, (0, 0, 0)),
                    LightControlWorkflow(Location.MAINROOM, State.ON, 255, (0, 0, 0)),
                    LightControlWorkflow(Location.SERVERROOM, State.ON, 255, (0, 0, 0)),
                    TTSAudioWorkflow("TTS1", "Warning, power failure! Warning, power failure!"),
                    LightControlWorkflow(Location.LOBBYROOM, State.ON, 255, (255, 0, 0)),
                    #SendTriggerWorkflow("Play Video", "env/video", State.ON),
                ]),
                SequenceWorkflow("Puzzle 1 - Cube", [
                    Workflow("Panels Released", "1/cube/state"),
                    Workflow("Panels Placed", "1/panel/state"),
                ]),
                Workflow("Input Keypad Code", "4/puzzle"),
                SendTriggerWorkflow("Open Control Room Door", "4/door/entrance", State.ON),
                CombinedWorkflow("First Door Open Env", [
                    LightControlWorkflow(Location.MAINROOM, State.ON, 255, (255, 0, 0)),
                    TTSAudioWorkflow("TTS2", "Warning, emergency backup battery empty, please recharge!"),
                ]),
            ]),


            SequenceWorkflow("Control Room", [
                SequenceWorkflow("Puzzle 5 - Battery", [
                    Workflow("Battery Recharged", "5/control_room/power"),
                ]),
                CombinedWorkflow("Backup Power Restored Env", [
                    LightControlWorkflow(Location.LOBBYROOM, State.ON, 255, (255, 255, 255)),
                    LightControlWorkflow(Location.MAINROOM, State.ON, 255, (255, 255, 255)),
                    LightControlWorkflow(Location.SERVERROOM, State.ON, 255, (255, 0, 0)),
                    TTSAudioWorkflow("TTS3", "Emergency power restored! Generators offline! Restart server!"),
                ]),
                SequenceWorkflow("Puzzle 3 - Radio", [
                    Workflow("Antenna Aligned", "3/gamecontrol/antenna"),
                    Workflow("Radio Tuned", "3/gamecontrol/map"),
                    Workflow("Touch Game Solved", "3/gamecontrol/touchgame"),
                ]),
                SequenceWorkflow("Puzzle 2 - Switchboard", [
                    Workflow("Switchboard Solved", "2/esp"),
                ]),
                SendTriggerWorkflow("Open Server Room Door", "4/door/server", State.ON),
                CombinedWorkflow("Second Door Open Env", [
                    LightControlWorkflow(Location.SERVERROOM, State.ON, 255, (255, 255, 255)),
                ]),
            ]),


            SequenceWorkflow("Server Room", [
                SequenceWorkflow("Puzzle 4 - Server", [
                    Workflow("Server Access Unlocked", "4/gamecontrol"),
                ]),
            ]),


            ExitWorkflow([
                SendTriggerWorkflow("Radio Success", "3/audiocontrol/roomsolved", State.ON),
                #SendTriggerWorkflow("Play Video", "env/video", State.ON),
                LightControlWorkflow(Location.LOBBYROOM, State.ON, 255, (0, 255, 0)),
                LightControlWorkflow(Location.MAINROOM, State.ON, 255, (0, 255, 0)),
                LightControlWorkflow(Location.SERVERROOM, State.ON, 255, (0, 255, 0)),
                #TTSAudioWorkflow("Play success", "success.mp3", True),
            ])
        ]

        self.apply_initial_settings(workflow, skip_to)

        return workflow

    def apply_initial_settings(self, workflow, skip_to):
        skip_node_reached = False
        for w in workflow:
            name = w.name.upper()
            # Highlight room nodes
            w.highlight = True
            # Skip until the "skip_to" node reached
            if skip_to and name != skip_to.upper() and not skip_node_reached:
                w.skip(name)
            else:
                skip_node_reached = True
