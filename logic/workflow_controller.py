import paho.mqtt.client as mqtt
import subprocess
import json
from workflow import SequenceWorkflow
from workflow_extras import LightControlWorkflow, TTSAudioWorkflow
from message import State
from util import Location
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

    def __init__(self, mqtt_url, workflow_factory):
        """
        Initializes a new instance of this class.

        Parameters
        ----------
        mqtt_url : str
            The url of the MQTT server.

        workflow_factory : WorkflowFactory
            A factory which creates the workflow structure defining
            the sequence of their execution.
        """
        self.client = None
        self.mqtt_url = mqtt_url
        self.game_control_topic = "op/gameControl"
        self.game_timer_topic = "op/gameTime"
        self.game_state_topic = "op/gameState"
        self.game_option_topic = "op/gameOptions"
        self.options = None
        self.workflow_factory = workflow_factory
        self.last_graph_config = None
        self.game_timer = GameTimer(mqtt_url, self.game_timer_topic)
        self.game_timer.register_on_expired(self.__on_game_time_expired)
        self.game_state = GameState.STOPPED
        self.main_sequence = None

    def connect(self):
        """
        Connects the game to the MQTT server
        and subscripes to the game control topic.
        """
        self.client = mqtt.Client("EscapeRoomGameLogic", False)
        self.client.on_connect = self.__on_connect
        self.client.on_message = self.__on_message
        self.client.connect(self.mqtt_url)
        self.client.loop_start()
        print("Waiting for game control commands...")

    def disconnect(self):
        self.client.disconnect()
        self.client.loop_stop()
        print("Main workflow disconnected...")

    def start(self):
        """
        Starts the main workflow.
        """
        if self.game_state != GameState.STARTED:
            self.__purge_all_topics()
            if self.game_state == GameState.STOPPED:
                workflow = self.workflow_factory.create(self.options)
                self.main_sequence = SequenceWorkflow(
                    "Main workflow", workflow)
                self.main_sequence.highlight = True
                self.main_sequence.register_on_finished(
                    self.__on_workflow_solved)
                self.main_sequence.execute(self.client)
            self.game_timer.set_duration(self.options["duration"])
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
            self.__purge_all_topics()
            print("Main workflow stopped...")

    def reset(self):
        """
        Resets the main workflow
        """
        self.stop()
        self.start()

    def pause(self):
        """
        Pauses the main workflow.
        """
        if self.game_state != GameState.PAUSED:
            self.game_timer.pause()
            self.game_state = GameState.PAUSED
            print("Main workflow paused...")

    def skip(self, workflow_name):
        """
        Skip the workflow with a given name.
        """
        self.main_sequence.skip(workflow_name)

    def __on_connect(self, client, userdata, flags, rc):
        """
        Subscribing in on_connect() means that if we lose the connection and
        reconnect then subscriptions will be renewed.
        """
        client.subscribe(self.game_control_topic)
        client.subscribe(self.game_option_topic)
        print("Main workflow (re)connected...")

    def __on_message(self, client, userdata, msg):
        if msg.topic == self.game_control_topic:
            self.__handle_command(msg)
        elif msg.topic == self.game_option_topic:
            self.__save_options(msg)
        else:
            if self.main_sequence:
                self.main_sequence.on_message(msg)
        self.publish_game_state()

    def publish_game_state(self):
        if self.main_sequence:
            config = self.main_sequence.get_graph_config()
            if config != self.last_graph_config:
                self.client.publish(self.game_state_topic, config, 0, True)
                self.last_graph_config = config

    def __handle_command(self, msg):
        message = msg.payload.decode("utf-8").upper()
        if message == "START":
            self.start()
        elif message == "STOP":
            self.stop()
        elif message == "PAUSE":
            self.pause()
        elif message.startswith("SKIP "):
            workflow_name = message[5:].strip()
            self.skip(workflow_name)
        elif message == '':
            pass
        else:
            print(f"The game command '{str(message)}' is not supported.")

    def __save_options(self, msg):
        message = msg.payload.decode("utf-8")
        self.options = json.loads(message)

    def __on_game_time_expired(self):
        print("==================")
        print("Game time expired!")
        print("==================")
        # for led in ["labroom/north", "labroom/south", "labroom/middle",
        #             "serverroom", "doorserverroom"]:
        #     lwf = LightControlWorkflow("Turn red " + led, "2/ledstrip/" + led,
        #                                State.ON, 255, "255,0,0")
        #     lwf.execute(self.client)
        lwf = LightControlWorkflow(Location.SERVERROOM, State.ON, 255, (255, 0, 0))
        lwf.execute(self.client)
        lwf = LightControlWorkflow(Location.MAINROOM, State.ON, 255, (255, 0, 0))
        lwf.execute(self.client)
        awf = TTSAudioWorkflow(
            "Play gameover",
            "/opt/ue-operator/sounds/gameover.mp3",
            True
        )
        awf.execute(self.client)
        self.client.publish(self.game_control_topic, None, 2, True)
        self.stop()

    def __on_workflow_solved(self, name):
        print("==================================")
        print("Escape room finished successfully!")
        print("==================================")
        self.client.publish(self.game_control_topic, None, 2, True)
        self.stop()

    def __purge_all_topics(self):
        print("=== Purges all topics ===")
        try:
            subprocess.Popen([
                "/opt/ue-operator/mosquitto_sub",
                "-h", self.mqtt_url,
                "-t", "#",
                "-T", "op/gameControl",
                "-T", "op/gameOptions",
                "--remove-retained",
                "--retained-only"], stdout=subprocess.PIPE)
        except subprocess.CalledProcessError:
            pass
