import paho.mqtt.client as mqtt
import subprocess
import json
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
        self.game_control_topic = "1/gameControl"
        self.game_timer_topic = "1/gameTime"
        self.game_state_topic = "1/gameState"
        self.game_option_topic = "1/gameOptions"
        self.options = None
        self.workflow_factory = workflow_factory
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
            self.__purge_all_topics()
            if self.game_state == GameState.STOPPED:
                workflow = self.workflow_factory.create(self.options)
                self.main_sequence = SequenceWorkflow("main", workflow)
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
        print("Main workflow connected...")
        print("Waiting for game control commands...")

    def __on_message(self, client, userdata, msg):
        if msg.topic == self.game_control_topic:
            self.__handle_command(msg)
        elif msg.topic == self.game_option_topic:
            self.__save_options(msg)
        else:
            self.main_sequence.on_message(msg)
            # Publish game state to MQTT
            config = self.main_sequence.get_graph_config()
            self.client.publish(self.game_state_topic, config, 0, True)

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
            print("The game command '%s' is not supported." % (str(message)))

    def __save_options(self, msg):
        message = msg.payload.decode("utf-8")
        self.options = json.loads(message)

    def __on_workflow_solved(self, name):
        print("===============================")
        print("Workflow finished successfully!")
        print("===============================")
        self.client.publish(self.game_control_topic, None, 2, True)
        self.stop()

    def __purge_all_topics(self):
        print("=== Purges all topics ===")
        try:
            subprocess.Popen([
                "/snap/bin/mosquitto_sub",
                "-t", "#",
                "-h", self.mqtt_url,
                "--remove-retained",
                "--retained-only"])
        except subprocess.CalledProcessError as error:
            pass
