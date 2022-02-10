from threading import Timer
import subprocess
from enum import Enum
from paho.mqtt import publish


class Location(Enum):
    LOBBYROOM = 0
    MAINROOM = 1
    SERVERROOM = 2

class LEDPattern(Enum):
    RGB = "solidColor"
    WAVES = "colorwaves" 
    PALETTE_TEST = "palettetest"
    PRIDE =  "pride"
    RAINBOW = "rainbow"
    RAINBOW_GLITTER = "rainbowWithGlitter"
    CONFETTI = "confetti"
    SINELON = "sinelon"
    JUGGLE = "juggle"
    BPM = "bpm"
    FIRE = "fire"
    TIMERPRINT = "timerprint"
    GLOBES = "globes"
    STROBOSKOP = "stroboskop"

class ProcessList(list):
    """
    List to manage created processes
    """

    def append(self, cmd, cwd=None, stdout=None, stderr=None):
        """
        Creates a new process and adds it to the list

        :param cmd: The command to execute
        :param cwd: An optional working directory
        :param stderr: An optional stderr redirection
        :param stdout: An optional stdout redirection
        :return: None
        """
        if isinstance(cmd, str) or isinstance(cmd, list):
            process = subprocess.Popen(cmd, shell=isinstance(cmd, str),
                                       cwd=cwd, stdout=stdout, stderr=stderr)
        else:
            raise TypeError("Expecting a string or a list as cmd")
        # process.check_returncode()
        super().append(process)

    def wait(self):
        """
        Waits for all processes in list to finish -> locks process

        :return:
        """
        try:
            for process in self:
                process.wait()
        except subprocess.CalledProcessError as e:
            print(str(e))
            self.wait()


class RepeatTimer(Timer):
    """
    This class is derived from the Timer class to provide a repeating timer
    """
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


def publish_tts(text):
    """
    This method publishes a message to the TTS topic to have it played
    :param text: The text to play
    :return:
    """
    msg = f'{{"method":"message","data":"{text}"}}'
    publish.single("2/textToSpeech", msg, hostname="10.0.0.2")
