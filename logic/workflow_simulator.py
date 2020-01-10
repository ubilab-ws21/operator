import time
import paho.mqtt.publish as publish


messages = {
    # Entry room
    '4/door/entrance/puzzle': '{"method": "STATUS", "state": "SOLVED"}',
    '4/door/entrance': '{"method": "STATUS", "state": "SOLVED"}',
    '4/puzzle': '{"method": "STATUS", "state": "SOLVED"}',
    # Lab room
    '5/safe/activate': '{"method": "STATUS", "state": "SOLVED"}',
    '7/laser': '{"method": "STATUS", "state": "SOLVED"}',
    '5/safe/control': '{"method": "STATUS", "state": "SOLVED"}',
    '7/fusebox': '{"method": "STATUS", "state": "SOLVED"}',
    '7/robot': '{"method": "STATUS", "state": "SOLVED"}',
    # Server room
    '6/puzzle/floppy': '{"method": "STATUS", "state": "SOLVED"}',
    '8/puzzle/maze': '{"method": "STATUS", "state": "SOLVED"}',
    '8/puzzle/simon': '{"method": "STATUS", "state": "SOLVED"}'
}


if __name__ == "__main__":
    mqtt_url = "127.0.0.1"
    for topic in messages:
        publish.single(topic, messages[topic])
        time.sleep(2)