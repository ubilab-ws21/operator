import time
import paho.mqtt.publish as publish


messageSequence = [
    # Entry room
    ['1/gameOptions', '{"participants": 3, "duration": 5}'],
    ['1/gameControl', 'start'],
    ['4/puzzle', '{"method": "STATUS", "state": "Invalid}'],
    ['4/puzzle', '{"method": "STATUS", "state": "UNSOLVED"}'],
    ['4/puzzle', '{"method": "STATUS", "state": "SOLVED"}'],
    ['4/globes', '{"method": "status", "state": "solved"}'],
    # Lab room
    ['5/safe/activate', '{"method": "STATUS", "state": "SOLVED"}'],
    ['7/fusebox/laserDetection', '{"method": "STATUS", "state": "SOLVED"}'],
    ['7/fusebox/rewiring0', '{"method": "STATUS", "state": "SOLVED"}'],
    ['7/fusebox/rewiring1', '{"method": "STATUS", "state": "SOLVED"}'],
    ['7/fusebox/potentiometer', '{"method": "STATUS", "state": "SOLVED"}'],
    ['5/safe/control', '{"method": "STATUS", "state": "SOLVED"}'],
    ['6/puzzle/scale', '{"method": "STATUS", "state": "ACTIVE"}'],
    ['7/robot', '{"method": "STATUS", "state": "SOLVED"}'],
    ['6/puzzle/scale', '{"method": "STATUS", "state": "INACTIVE"}'],
    # Server room
    ['8/puzzle/maze', '{"method": "STATUS", "state": "SOLVED"}'],
    ['6/puzzle/terminal', '{"method": "STATUS", "state": "SOLVED"}'],
    ['8/puzzle/simon', '{"method": "STATUS", "state": "SOLVED"}']
]


if __name__ == "__main__":
    mqtt_url = "127.0.0.1"
    for message in messageSequence:
        publish.single(message[0], message[1], 2, False, mqtt_url)
        time.sleep(1)
