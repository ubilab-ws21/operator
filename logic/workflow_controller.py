import paho.mqtt.client as mqtt
from workflow import SequenceWorkflow
from game_timer import GameTimer
from enum import Enum


class GameState(Enum):
    STOPPED = 0
    STARTED = 1
    PAUSED = 2


class WorkflowController:
    """
    The workflow controller manages the MQTT connection and organizes
    the transitions between the registered workflows.
    """

    def __init__(self, mqtt_url, workflows):
        """
        Initializes a new instance of this class.

        Parameters
        ----------
        mqtt_url : str
            The url of the MQTT server.

        workflows : Workflow[]
            An array of workflows defining the sequence of their execution.
        """
        self.client = None
        self.mqtt_url = mqtt_url
        self.game_control_topic = "1/gameControl"
        self.game_timer_topic = "1/gameTime"
        self.game_state_topic = "1/gameState"
        self.main_sequence = SequenceWorkflow("main", workflows)
        self.game_timer = GameTimer(mqtt_url, self.game_timer_topic)
        self.game_state = GameState.STOPPED

    def connect(self):
        """
        Connects the game to the MQTT server
        and subscripes to the game control topic.
        """
        self.client = mqtt.Client()
        self.client.on_connect = self.__on_connect
        self.client.on_message = self.__on_message
        self.client.connect(self.mqtt_url)
        self.client.loop_start()

    def disconnect(self):
        self.client.disconnect()
        self.client.loop_stop()
        print("Main workflow disconnected...")

    def start(self):
        """
        Starts the main workflow.
        """
        if self.game_state != GameState.STARTED:
            if self.game_state == GameState.STOPPED:
                self.main_sequence.register_on_finished(
                    self.__on_workflow_solved)
                self.main_sequence.execute(self.client)
            self.game_timer.start()
            self.game_state = GameState.STARTED
            print("Main workflow started...")

    def stop(self):
        """
        Stops the main workflow.
        """
        if self.game_state != GameState.STOPPED:
            self.game_timer.stop()
            self.main_sequence.dispose(self.client)
            self.game_state = GameState.STOPPED
            print("Main workflow stopped...")

    def pause(self):
        """
        Pauses the main workflow.
        """
        if self.game_state != GameState.PAUSED:
            self.game_timer.pause()
            self.game_state = GameState.PAUSED
            print("Main workflow paused...")

    def __on_connect(self, client, userdata, flags, rc):
        """
        Subscribing in on_connect() means that if we lose the connection and
        reconnect then subscriptions will be renewed.
        """
        client.subscribe(self.game_control_topic)
        print("Main workflow connected...")
        print("Waiting for game control commands...")

    def __on_message(self, client, userdata, msg):
        if msg.topic == self.game_control_topic:
            message = msg.payload.decode("utf-8").upper()
            if message == "START":
                self.start()
            elif message == "STOP":
                self.stop()
            elif message == "PAUSE":
                self.pause()
            else:
                print("The game command '%s' is not supported."
                      % (str(message)))
        else:
            self.main_sequence.on_message(msg)
            # Publish game state to MQTT
            self.client.publish(
                self.game_state_topic,
                self.main_sequence.toJSON(),
                0,
                True
            )

    def __on_workflow_solved(self, name):
        print("===============================")
        print("Workflow finished successfully!")
        print("===============================")
        self.stop()
        print("Main workflow stopped...")
