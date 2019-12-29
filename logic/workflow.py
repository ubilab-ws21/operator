from message import Message, Method, State, fromJSON


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
        name : str
            Display name of the workflow.
        topic : str
            Name of the MQTT topic.
        """
        self.topic = topic
        self.name = name
        self._on_workflow_failed = None
        self._on_workflow_solved = None

    def execute(self, client):
        """
        Executes this workflow.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        message = Message(Method.TRIGGER, State.ON)
        client.publish(self.topic, message.toJSON())
        print("[%s] Started..." % (self.name))
        client.subscribe(self.topic)
        print("[%s] Subscribed to topic '%s'..." % (self.name, self.topic))

    def dispose(self, client):
        """
        Disposes this workflow.

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
        try:
            # Check for relevant topic
            if msg.topic != self.topic:
                return

            message = msg.payload.decode("utf-8")
            obj = fromJSON(message)
            if obj.method == Method.STATUS:
                print("[%s] State change to '%s'"
                      % (self.name, obj.state.name))
                if obj.state == State.INACTIVE:
                    self.on_received_status_inactive(obj.data)
                elif obj.state == State.ACTIVE:
                    self.on_received_status_active(obj.data)
                elif obj.state == State.SOLVED:
                    self.on_received_status_solved(obj.data)
                if obj.state == State.FAILED:
                    self.on_received_status_failed(obj.data)
                else:
                    self._on_workflow_failed(
                        self.name,
                        "[%s] State '%s' is not supported"
                        % (self.name, obj.state))
            elif obj.method == Method.TRIGGER:
                print("[%s] Requested trigger '%s'"
                      % (self.name, obj.state.name))
                if obj.state == State.ON:
                    self.on_received_trigger_on(obj.data)
                elif obj.state == State.OFF:
                    self.on_received_trigger_off(obj.data)
                else:
                    self._on_workflow_failed(
                        self.name,
                        "[%s] Trigger state '%s' is not supported"
                        % (self.name, obj.state))
            elif obj.method == Method.MESSAGE:
                print("[%s] Received message with method 'MESSAGE'. "
                      "Nothing to do..." % (self.name))
            else:
                self._on_workflow_failed(
                    self.name,
                    "[%s] Method '%s' is not supported"
                    % (self.name, obj.method))
        except Exception as e:
            self._on_workflow_failed(
                self.name,
                "[%s] No valid JSON: %s" % (self.name, str(e)))

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

    def on_received_status_inactive(self, data):
        print("  ==> Nothing to do")

    def on_received_status_active(self, data):
        print("  ==> Nothing to do")

    def on_received_status_solved(self, data):
        print("  ==> Puzzle solved successfully")
        self._on_workflow_solved(self.name)

    def on_received_status_failed(self, data):
        print("  ==> An error occured: %s" % (data))
        self._on_workflow_failed(self.name, data)

    def on_received_trigger_on(self, data):
        print("  ==> Nothing to do")

    def on_received_trigger_off(self, data):
        print("  ==> Nothing to do")
