import threading
import paho.mqtt.client as mqtt
from datetime import timedelta
from enum import Enum


class TimerState(Enum):
    STOPPED = 0
    STARTED = 1
    PAUSED = 2


class GameTimer:
    """
    The game timer periodicaly updates the game time of a given topic.
    """

    def __init__(self, mqtt_url, topic, interval=1.0):
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
        self.timer_state = TimerState.STOPPED

    def set_duration(self, duration_in_minutes):
        """
        Sets the duration in minutes.

        Parameters
        ----------
        duration_in_minutes : number
            The game time in duration.
        """
        self.game_duration_in_sec = duration_in_minutes * 60

    def start(self):
        """
        Starts the game timer.
        """
        if self.timer_state != TimerState.STARTED:
            if self.timer_state == TimerState.STOPPED:
                self.client = mqtt.Client()
                self.client.connect(self.mqtt_url)
                self.client.loop_start()
            self.timer_state = TimerState.STARTED
            self.publish_game_time()

    def stop(self):
        """
        Stops the game timer.
        """
        if self.timer_state != TimerState.STOPPED:
            self.timer.cancel()
            self.client.loop_stop()
            self.game_time_sec = 0
            self.timer_state = TimerState.STOPPED

    def pause(self):
        """
        Pauses the game timer
        """
        if self.timer_state != TimerState.PAUSED:
            self.timer.cancel()
            self.timer_state = TimerState.PAUSED

    def register_on_expired(self, func):
        """
        Register a new handler for handling the game timer is expired.

        Parameters
        ----------
        func : Function
            Handler function: func()
        """
        self._on_time_expired = func

    def publish_game_time(self):
        """
        Publishes the game time to the specified MQTT topic.
        """
        self.game_time_sec += self.interval
        if self.game_time_sec >= self.game_duration_in_sec:
            self._on_time_expired()
        else:
            self.timer = threading.Timer(self.interval, self.publish_game_time)
            self.timer.start()
            formatted_game_time = str(timedelta(seconds=self.game_time_sec))
            formatted_game_time_remain = str(timedelta(seconds=( self.game_duration_in_sec - self.game_time_sec)))
            self.client.publish(self.topic + "_in_sec", self.game_time_sec)
            self.client.publish(self.topic + "_remain_in_sec", self.game_duration_in_sec - self.game_time_sec)
            self.client.publish(self.topic + "_formatted", formatted_game_time)
            self.client.publish(self.topic + "_remain_formatted", formatted_game_time_remain)
