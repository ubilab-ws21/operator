import json
from enum import Enum


class Method(Enum):
    MESSAGE = 0
    STATUS = 1
    TRIGGER = 2


class State(Enum):
    OFF = 0
    ON = 1
    INACTIVE = 2
    ACTIVE = 3
    SOLVED = 4
    FAILED = 5


def fromJSON(text):
    """
    Creates a message object from a JSON.

    >>> m = '{"method": "STATUS", "state": "ACTIVE", "data": null}'
    >>> message = fromJSON(m)
    >>> isinstance(message, Message)
    True
    >>> (message.method, message.state, message.data)
    (<Method.STATUS: 1>, <State.ACTIVE: 3>, None)
    >>> m = '{"method": "TRIGGER", "state": "ON", "data": "INACTIVE"}'
    >>> message = fromJSON(m)
    >>> isinstance(message, Message)
    True
    >>> (message.method, message.state, message.data)
    (<Method.TRIGGER: 2>, <State.ON: 1>, 'INACTIVE')
    """
    try:
        obj = json.loads(text)

        methodStr = obj.get("method")
        if not methodStr:
            raise Exception("JSON attribute 'method' is missing.")

        methodStr = methodStr.upper()
        if methodStr not in [k.name for k in Method]:
            raise Exception(f"Method '{methodStr}' is not valid.")

        stateStr = obj.get("state")
        if not stateStr:
            raise Exception("JSON attribute 'state' is missing.")

        stateStr = stateStr.upper()
        if stateStr not in [k.name for k in State]:
            raise Exception(f"State '{stateStr}' is not valid.")

        method = Method[methodStr]
        state = State[stateStr]
        data = obj.get("data")
    except ValueError as error:
        print(f"Message is no valid JSON: {error}")
        method = Method.MESSAGE
        state = None
        data = text

    return Message(method, state, data)


class Message:
    """
    Represents the specified data transfer object for the communication
    with other participants over MQTT.
    Definition:
    https://github.com/ubilab-ws21/operator#communication-format
    """

    def __init__(self, method, state, data=None):
        """
        Initializes a new instance of this class.

        Parameters
        ----------
        method : Method(Enum)
            Method of the message.

        state : State(Enum)
            State of the message.

        data : any
            Optional: Data of the message.
        """
        self.method = method
        self.state = state
        self.data = data

    def toJSON(self):
        """
        Creates a json from the message object.

        >>> m = Message(Method.STATUS, State.ACTIVE)
        >>> m.toJSON()
        '{"method": "status", "state": "active", "data": null}'
        >>> m = Message(Method.TRIGGER, State.ON)
        >>> m.toJSON()
        '{"method": "trigger", "state": "on", "data": null}'
        """
        result = json.dumps({
            "method": self.method.name.lower(),
            "state": self.state.name.lower(),
            "data": self.data
        })
        return result
