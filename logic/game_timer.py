import threading
import json
import paho.mqtt.client as mqtt
from datetime import timedelta


class GameTimer:
    """
    The game timer periodicaly updates the game time of a given topic.
    """

    def __init__(self, mqtt_url, topic, interval=5.0):
        """
        Initializes a new instance of this class.

        Parameters
        ----------
        mqtt_url : str
            The url of the MQTT server.

        topic : str
            The topic of MQTT server where the game time is published to.

        interval: float
            The intervall the game time is refreshed.
        """
        self.client = None
        self.mqtt_url = mqtt_url
        self.topic = topic
        self.game_time_sec = 0
        self.interval = interval
        self.timer = threading.Timer(self.interval, self.publish_game_time)

    def start(self):
        """
        Starts the game timer.
        """
        self.client = mqtt.Client()
        self.client.connect(self.mqtt_url)
        self.client.loop_start()
        self.publish_game_time()

    def cancel(self):
        """
        Cancels the game timer.
        """
        self.timer.cancel()
        self.client.loop_stop()

    def publish_game_time(self):
        """
        Publishes the game time to the specified MQTT topic.
        """
        self.game_time_sec += self.interval
        self.timer = threading.Timer(self.interval, self.publish_game_time)
        self.timer.start()
        result = json.dumps({
            "gameTimeInSec": self.game_time_sec,
            "formattedGameTime": str(timedelta(seconds=self.game_time_sec))
        })
        self.client.publish(self.topic, result)
