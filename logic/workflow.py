import json
from message import Message, Method, State, fromJSON
from enum import Enum


class Workflow:
    """
    This class represents the default workflow implementation of a puzzle,
    defined in following UML sequence diagram:
    https://github.com/ubilab-escape/operator/blob/master/doc/design/general_%CE%BCC_workflow.svg
    """

    def __init__(self, name, topic, settings=None):
        """
        Initializes a new instance of this class.

        Parameters
        ----------
        name : str
            Display name of the workflow.

        topic : str
            Name of the MQTT topic.

        settings: keywords
            An dictionary of global settings.
        """
        self.topic = topic
        self.name = name
        self.settings = settings
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
        data = self.getData(self.settings)
        message = Message(Method.TRIGGER, State.ON, data)
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

    def getData(self, settings):
        data = None

        if settings:
            if len(settings) == 1:
                data = next(iter(settings.values()))
            else:
                data = json.dumps(settings)
        return data

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
                elif obj.state == State.FAILED:
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


class SequenceWorkflow(Workflow):
    """
    This class implements a wrapper to run multiple workflows in sequence.
    """

    def __init__(self, name, workflows):
        """
        Initializes a new instance of this class.

        Parameters
        ----------
        name : str
            Display name of the workflow.
        topic : str
            Name of the MQTT topic.
        workflows : Workflow[]
            Collection of workflows should be executed in parallel.
        """
        super().__init__(name, None)
        self.workflows = workflows
        self.client = None
        self.current_workflow = 0

    def execute(self, client):
        """
        Executes this workflow.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        self.client = client
        self.__subscribeCurrentWorkflow(self.client)

    def dispose(self, client):
        """
        Disposes this workflow.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        pass

    def on_message(self, msg):
        """
        Processes the message sended by the MQTT server.

        Parameters
        ----------
        msg : Message
            Message from the MQTT topic.
        """
        if (self.current_workflow < len(self.workflows)):
            workflow = self.workflows[self.current_workflow]
            workflow.on_message(msg)

    def on_received_status_solved(self, data):
        # A workflow sequence is solved iff the last workflow is solved
        pass

    def __on_workflow_failed(self, name, error):
        self._on_workflow_failed(error)

    def __on_workflow_solved(self, name):
        self.__unsubscribeCurrentWorkflow(self.client)
        self.current_workflow += 1
        if self.current_workflow >= len(self.workflows):
            print("  ==> Workflow sequence '%s' finished..." % (self.name))
            self._on_workflow_solved(self.name)
        else:
            self.__subscribeCurrentWorkflow(self.client)

    def __subscribeCurrentWorkflow(self, client):
        workflow = self.workflows[self.current_workflow]
        workflow.register_on_failed(self.__on_workflow_failed)
        workflow.register_on_solved(self.__on_workflow_solved)
        workflow.execute(client)

    def __unsubscribeCurrentWorkflow(self, client):
        workflow = self.workflows[self.current_workflow]
        # workflow.register_on_failed(None)
        # workflow.register_on_solved(None)
        workflow.dispose(client)


class ParallelWorkflow(Workflow):
    """
    This class implements a wrapper to run multiple workflows in parallel.
    The parallel workflow is a composition organising the flow of one or
    more arbitary workflows.
    """

    def __init__(self, name, workflows):
        """
        Initializes a new instance of this class.

        Parameters
        ----------
        name : str
            Display name of the workflow.
        topic : str
            Name of the MQTT topic.
        workflows : Workflow[]
            Collection of workflows should be executed in parallel.
        """
        super().__init__(name, None)
        self.workflows = workflows
        self.workflow_solved = {}
        for workflow in self.workflows:
            self.workflow_solved[workflow.name] = False
            workflow.register_on_failed(self.__on_workflow_failed)
            workflow.register_on_solved(self.__on_workflow_solved)

    def execute(self, client):
        """
        Executes this workflow.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        names = [w.name for w in self.workflows]
        print("[%s] Starting in parallel..." % (", ".join(names)))
        for workflow in self.workflows:
            workflow.execute(client)

    def dispose(self, client):
        """
        Disposes this workflow.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        for workflow in self.workflows:
            workflow.dispose(client)

    def on_message(self, msg):
        """
        Processes the message sended by the MQTT server.

        Parameters
        ----------
        msg : Message
            Message from the MQTT topic.
        """
        for workflow in self.workflows:
            workflow.on_message(msg)

    def on_received_status_solved(self, data):
        # A parallel workflow is solved iff all wrapped workflows are solved
        pass

    def __on_workflow_failed(self, name, error):
        self._on_workflow_failed(error)

    def __on_workflow_solved(self, name):
        self.workflow_solved[name] = True
        if all(list(self.workflow_solved.values())):
            self._on_workflow_solved(name)


class DoorTargetState(Enum):
    OPENED = 0
    CLOSED = 1


class DoorWorkflow(Workflow):

    def __init__(self, name, topic, target_state):
        """
        Initializes a new instance of this class.

        Parameters
        ----------
        name : str
            Display name of the workflow.
        topic : str
            Name of the MQTT topic.
        target_state: DoorState
            Target state of the doot (opened/closed)
        """
        self.target_state = target_state
        super().__init__(name, topic)

    def on_received_status_inactive(self, data):
        """
        OVERRIDDEN: Door doesn't confirm the state solved.
        """
        if data.lower() == self.target_state.name.lower():
            print("  ==> Door %s" % data.lower())
            self._on_workflow_solved(self.name)
        else:
            super.on_received_status_inactive(data)
