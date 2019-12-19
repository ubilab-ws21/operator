class Workflow:
    """
    This class represents the default workflow implementation of a puzzle,
    defined in following UML sequence diagram:
    https://github.com/ubilab-escape/operator/blob/master/doc/design/general_%CE%BCC_workflow.svg
    """

    def __init__(self, name, topic):
        """
        Initializes a new instance of this class.

        Parameters
        ----------
        topic : str
            Name of the MQTT topic.
        """
        self.topic = topic
        self.name = name
        self._on_workflow_failed = None
        self._on_workflow_solved = None

    def subscribe(self, client):
        """
        Subscribes the given client to the topic of this workflow.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        client.subscribe(self.topic)
        print("[%s] Subscribed to topic '%s'..." % (self.name, self.topic))

    def unsubscribe(self, client):
        """
        Unsubscribes the given client from the topic of this workflow.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        client.unsubscribe(self.topic)
        print("[%s] Unsubscribed from topic '%s'..." % (self.name, self.topic))

    def on_message(self, msg):
        """
        Processes the message sended by the MQTT server.

        Parameters
        ----------
        msg : Message
            Message from the MQTT topic.
        """
        print("%s | %s" % (msg.topic, msg.payload))

        if self._on_workflow_solved:
            self._on_workflow_solved()

    def register_on_failed(self, func):
        """
        Register a new handler for handling errors.

        Parameters
        ----------
        func : Function
            Handler function: func(error)
        """
        self._on_workflow_failed = func

    def register_on_solved(self, func):
        """
        Register a new handler for handling the puzzle was solved.

        Parameters
        ----------
        func : Function
            Handler function: func()
        """
        self._on_workflow_solved = func
