import json, time
from workflow import WorkflowState, Workflow, CombinedWorkflow, SingleCommandWorkflow
from message import Message, Method, State
from util import Location


class InitWorkflow(CombinedWorkflow):
    """
    This workflow is just a named ("Init") combined workflow to do some initial
    tasks.
    """

    def __init__(self, workflows, settings=None):
        """
        Initializes a new instance of this class.

        Parameters
        ----------
        workflows : Workflow[]
            Collection of workflows should be executed in parallel.

        settings: keywords
            An dictionary of global settings.
        """
        wrap_parent = 'wrap_parent'
        if settings and wrap_parent not in settings:
            settings[wrap_parent] = True
        else:
            settings = {wrap_parent: True}

        super().__init__("Init", workflows, settings)


class ExitWorkflow(CombinedWorkflow):
    """
    This workflow is just a named ("Exit") combined workflow to do some
    finalization tasks.
    """

    def __init__(self, workflows, settings=None):
        """
        Initializes a new instance of this class.

        Parameters
        ----------
        workflows : Workflow[]
            Collection of workflows should be executed in parallel.

        settings: keywords
            An dictionary of global settings.
        """
        wrap_parent = 'wrap_parent'
        if settings and wrap_parent not in settings:
            settings[wrap_parent] = True
        else:
            settings = {wrap_parent: True}

        super().__init__("Exit", workflows, settings)


class SendTriggerWorkflow(SingleCommandWorkflow):
    """
    This workflow sends trigger:on and trigger:off to a given topic. Can optionally send data as well.
    """

    def __init__(self, name, topic, target_state, data=None):
        """
        Initializes a new instance of this class.

        Parameters
        ----------
        name : str
            Display name of the workflow.

        topic : str
            Name of the MQTT topic.

        target_state: State
            Target state of the workflow.
        """
        self.target_state = target_state
        self.topic = topic
        self.data = data
        super().__init__(name)

    def _execute_single_command(self, client):
        """
        Executes an atomic command.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        self._publishTrigger(client, self.target_state, self.data)

    def _publishTrigger(self, client, state, data=None):
        if self.topic is not None:
            message = Message(Method.TRIGGER, state, data)
            client.publish(self.topic, message.toJSON(), 2)
            print(f"[{self.name}] Trigger '{state.name}' on topic '{self.topic}'...")


class SendMessageWorkflow(SingleCommandWorkflow):
    """
    This workflow sends a message to a given topic.
    """

    def __init__(self, name, topic, message_to_send):
        """
        Initializes a new instance of this class.

        Parameters
        ----------
        name : str
            Display name of the workflow.

        topic : str
            Name of the MQTT topic.

        message_to_send: str
            Message to send.
        """
        self.message = message_to_send
        self.topic = topic
        super().__init__(name)

    def _execute_single_command(self, client):
        """
        Executes an atomic command.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        self._publishTrigger(client, self.message)

    def _publishTrigger(self, client, message_str):
        if self.topic is not None:
            message_obj = Message(Method.MESSAGE, State.NONE, message_str)
            client.publish(self.topic, message_obj.toJSON(), 2)
            print(f"[{self.name}] Message '{message_str}' sent to '{self.topic}'...")


class TTSAudioWorkflow(SingleCommandWorkflow):
    """
    This workflow sends messages to text-to-speech or play defined
    audio files over the audio system.
    """

    def __init__(self, name, payload, from_file=False):
        """
        Initializes a new instance of this class.

        Parameters
        ----------
        name : str
            Display name of the workflow.

        payload : str
            Either content or file location of the audio to play

        from_file : bool
            Whether a mp3 file should be played
        """
        self.payload = payload
        self.from_file = from_file
        self.topic = "2/textToSpeech"
        super().__init__(name)

    def _execute_single_command(self, client):
        """
        Executes an atomic command.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        if self.from_file:
            message = {
                "method": "message",
                "play_from_file": True,
                "file_location": self.payload
            }
        else:
            message = {
                "method": "message",
                "data": self.payload
            }
        client.publish(self.topic, json.dumps(message), 2)


class SingleLightControlWorkflow(SingleCommandWorkflow):
    """
    This workflow allows to contol the light of the room.
    """

    def __init__(self, name, topic, target_state,
                 brightness=255, color=(255, 255, 255)):
        """
        Initializes a new instance of this class.

        Parameters
        ----------
        name : str
            Display name of the workflow.

        topic : str
            Name of the MQTT topic.

        target_state: State
            Target state of the light.

        brightness: int [0,255]
            Brightness of the light.

        color: Tuple (r, g, b)
            Color of the light decoded in hex.
        """
        self.target_state = target_state
        self.brightness = brightness
        self.color = color
        self.topic = topic
        super().__init__(name)

    def _execute_single_command(self, client):
        """
        Executes an atomic command.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        col = f"{self.color[0]},{self.color[1]},{self.color[2]}"
        self._publishTrigger(client, 'rgb', col)
        self._publishTrigger(client, 'brightness', self.brightness)
        self._publishTrigger(client, 'power', self.target_state.name.lower())

    def _publishTrigger(self, client, state, data):
        client.publish(
            self.topic,
            json.dumps({
                'method': 'trigger',
                'state': state,
                'data': data
            }),
            2
        )


class LightControlWorkflow(CombinedWorkflow):
    """
    This workflow controls the LED stripes at the specified location in one single workfow.
    """

    def __init__(self, target_location, target_state, brightness=255, color=(255, 255, 255)):
        """
        Initializes a new instance of this class.

        Parameters
        ----------
        target_location: Location
            Target location which light to control.

        target_state: State
            Target state of the light.

        brightness: int [0,255]
            Brightness of the light.

        color: Tuple (r, g, b)
            Color of the light decoded in hex.
        """
        if target_location == Location.LOBBYROOM:
            workflows = [
                SingleLightControlWorkflow("Control lobbyroom light", "2/ledstrip/lobby", target_state, brightness, color)
            ]
        elif target_location == Location.MAINROOM:  
            workflows = [
                SingleLightControlWorkflow("Control mainroom light north", "2/ledstrip/labroom/north", target_state, brightness, color),
                SingleLightControlWorkflow("Control mainroom light south", "2/ledstrip/labroom/south", target_state, brightness, color),
                SingleLightControlWorkflow("Control mainroom light middle", "2/ledstrip/labroom/middle", target_state, brightness, color)
            ]
        elif target_location == Location.SERVERROOM:
            workflows = [
                SingleLightControlWorkflow("Control serverroom light", "2/ledstrip/serverroom", target_state, brightness, color),
            ]
        else:
            workflows = []

        name = f"Turn {target_state.name} {target_location.name} lights {brightness}/255"
        super().__init__(name, workflows, None)


class DelayWorkflow(Workflow):
    """
    This workflow implements a blocking delay.
    """

    def __init__(self, name, delay_sec):
        """
        Initializes a new instance of this class.

        Parameters
        ----------
        name : str
            Display name of the workflow.

        delay_sec : int
            The number of seconds delay.
        """
        self.delay_sec = delay_sec
        self.start_time = 0
        super().__init__(name, "op/gameTime_in_sec")

    def _execute(self, client):
        """
        Executes this workflow.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        print(f"[{self.name}] DelayWorkflow started with delay of {self.delay_sec}s.")
        super()._subscripeToTopic(client)
        self.state = WorkflowState.ACTIVE

    def on_message(self, msg):
        """
        Processes the message sent by the MQTT server.

        Parameters
        ----------
        msg : Message
            Message from the MQTT topic.
        """
        try:
            # Check for relevant topic
            if msg.topic != self.topic:
                return

            try:
                current_sec = float(msg.payload.decode("utf-8"))
            except:
                return

            if self.start_time > 0 and current_sec - self.start_time >= self.delay_sec:
                print(f"[{self.name}] DelayWorkflow delay reached, done.")
                self.state = WorkflowState.FINISHED
                if self._on_workflow_finished:
                    self._on_workflow_finished(self.name)
            elif self.start_time <= 0:
                print(f"[{self.name}] DelayWorkflow start_time set to {current_sec} (was {self.start_time})")
                self.start_time = current_sec

        except Exception as e:
            error_msg = f"[{self.name}] Error: {str(e)}"
            print(error_msg)
            self.on_error(self.name, error_msg)
