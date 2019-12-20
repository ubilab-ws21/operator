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
        obj = json.loads(text)
        method = obj.get("method")
        if not method:
            raise Exception("JSON attribute 'method' is missing.")
        elif method not in [k.name for k in Method]:
            raise Exception("Method '%s' is not valid." % (method))
        
        state = obj.get("state")
        if not state:
            raise Exception("JSON attribute 'state' is missing.")
        elif state not in [k.name for k in State]:
            raise Exception("State '%s' is not valid." % (state))
        
        date = obj.get("data")

        return Message(Method[method], State[state], date)
        
class Message:
    """
    Represents the specified data transfer object for the communication
    with other participants over MQTT.
    Definition:
    https://github.com/ubilab-escape/operator#communication-format
    """

    def __init__(self, method, state, data = None):
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
        '{"method": "STATUS", "state": "ACTIVE", "data": null}'
        >>> m = Message(Method.TRIGGER, State.ON)
        >>> m.toJSON()
        '{"method": "TRIGGER", "state": "ON", "data": null}'
        """
        result = json.dumps({
            "method": self.method.name,
            "state": self.state.name,
            "data": self.data
        })
        return result