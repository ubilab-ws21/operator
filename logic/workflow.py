import json
from message import Message, Method, State, fromJSON
from enum import Enum


class WorkflowState(Enum):
    INACTIVE = 0
    ACTIVE = 1
    FINISHED = 2


class BaseWorkflow:
    """
    This class provides the basic structure and functionality for workflows.
    """

    def __init__(self, name, settings=None):
        """
        Initializes a new instance of this class.

        Parameters
        ----------
        name : str
            Display name of the workflow.

        settings: keywords
            An dictionary of global settings.
        """
        self.name = name
        self.settings = settings
        self._on_workflow_failed = None
        self._on_workflow_finished = None
        self.state = WorkflowState.INACTIVE
        self.type = self.__class__.__name__

    def execute(self, client):
        """
        Executes this workflow.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        self.state = WorkflowState.ACTIVE

    def dispose(self, client):
        """
        Disposes this workflow.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        if self.state is not WorkflowState.FINISHED:
            self.state = WorkflowState.INACTIVE

    def on_message(self, msg):
        pass

    def getSettings(self):
        data = None
        if self.settings:
            if len(self.settings) == 1:
                data = next(iter(self.settings.values()))
            else:
                data = json.dumps(self.settings)
        return data

    def register_on_failed(self, func):
        """
        Register a new handler for handling errors.

        Parameters
        ----------
        func : Function
            Handler function: func(error)
        """
        self._on_workflow_failed = func

    def register_on_finished(self, func):
        """
        Register a new handler for handling the puzzle was solved.

        Parameters
        ----------
        func : Function
            Handler function: func()
        """
        self._on_workflow_finished = func

    def get_graph_config(self):
        """
        Generates a JSON configuration for a cyptoscape graph.
        """
        graph = self.get_graph()

        graphConfig = {
            'nodes': graph[0],
            'edges': graph[1]
        }

        return json.dumps(graphConfig)

    def get_graph(self, predecessors=None, parent=None):
        """
        Generates a graph from the workflow and returns a tuple:
        (nodes, edges, final_states)

        Parameters
        ----------
        predecessors : str[]
            The IDs of the predecessor states.

        parent : str
            The ID of the parent state (group).

        Return
        ------
        (nodes, edges, final_state_ids) : Tuple
            Graph as a tuple.
        """
        nodeData = {
            'id': self.name,
            'name': self.name,
            'status': self.state.name,
            'type': self.type
        }

        if parent is not None:
            nodeData['parent'] = parent

        node = {
            'data': nodeData
        }

        edges = self._createEdges(self.name, predecessors)

        return ([node], edges, [self.name])

    def _createEdges(self, target, predecessors):
        """
        Generates the edges from a target and it's predecessors.

        Parameters
        ----------
        target: str
            The ID of the target node.

        predecessors : str[]
            The IDs of the predecessor states.

        Return
        ------
        edges : Edge[]
            Created edges as array.
        """
        edges = []
        if predecessors:
            for predecessor in predecessors:
                edges.append({
                    'data': {
                        'id': predecessor + '->' + target,
                        'source': predecessor,
                        'target': target
                    }
                })
        return edges


class Workflow(BaseWorkflow):
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
        super().__init__(name, settings)
        self.topic = topic

    def execute(self, client):
        """
        Executes this workflow.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        self._publishTriggerOn(client)
        self._subscripeToTopic(client)
        super().execute(client)

    def dispose(self, client):
        """
        Disposes this workflow.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        self._unsubscripeFromTopic(client)
        super().dispose(client)

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
                    self._on_received_status_inactive(obj.data)
                elif obj.state == State.ACTIVE:
                    self._on_received_status_active(obj.data)
                elif obj.state == State.SOLVED:
                    self._on_received_status_finished(obj.data)
                elif obj.state == State.FAILED:
                    self._on_received_status_failed(obj.data)
                else:
                    if self._on_workflow_failed:
                        self._on_workflow_failed(
                            self.name,
                            "[%s] State '%s' is not supported"
                            % (self.name, obj.state))
            elif obj.method == Method.TRIGGER:
                print("[%s] Requested trigger '%s'"
                      % (self.name, obj.state.name))
                if obj.state == State.ON:
                    self._on_received_trigger_on(obj.data)
                elif obj.state == State.OFF:
                    self._on_received_trigger_off(obj.data)
                else:
                    if self._on_workflow_failed:
                        self._on_workflow_failed(
                            self.name,
                            "[%s] Trigger state '%s' is not supported"
                            % (self.name, obj.state))
            elif obj.method == Method.MESSAGE:
                print("[%s] Received message with method 'MESSAGE'. "
                      "Nothing to do..." % (self.name))
            else:
                if self._on_workflow_failed:
                    self._on_workflow_failed(
                        self.name,
                        "[%s] Method '%s' is not supported"
                        % (self.name, obj.method))
        except Exception as e:
            if self._on_workflow_failed:
                self._on_workflow_failed(
                    self.name,
                    "[%s] No valid JSON: %s" % (self.name, str(e)))

        super().on_message(msg)

    def _publishTriggerOn(self, client):
        if self.topic is not None:
            data = self.getSettings()
            message = Message(Method.TRIGGER, State.ON, data)
            client.publish(self.topic, message.toJSON(), 2)
            print("[%s] Started..." % (self.name))

    def _subscripeToTopic(self, client):
        if self.topic is not None:
            client.subscribe(self.topic)
            print("[%s] Subscribed to topic '%s'..." % (self.name, self.topic))

    def _unsubscripeFromTopic(self, client):
        if self.topic is not None:
            client.unsubscribe(self.topic)
            print("[%s] Unsubscribed from topic '%s'..."
                  % (self.name, self.topic))

    def _on_received_status_inactive(self, data):
        print("  ==> Nothing to do")

    def _on_received_status_active(self, data):
        print("  ==> Nothing to do")

    def _on_received_status_finished(self, data):
        print("  ==> Puzzle solved successfully")
        if self._on_workflow_finished:
            self._on_workflow_finished(self.name)
        self.state = WorkflowState.FINISHED

    def _on_received_status_failed(self, data):
        print("  ==> An error occured: %s" % (data))
        if self._on_workflow_failed:
            self._on_workflow_failed(self.name, data)

    def _on_received_trigger_on(self, data):
        print("  ==> Nothing to do")

    def _on_received_trigger_off(self, data):
        print("  ==> Nothing to do")


class SequenceWorkflow(BaseWorkflow):
    """
    This class implements a wrapper to run multiple workflows in sequence.
    """

    def __init__(self, name, workflows, settings=None):
        """
        Initializes a new instance of this class.

        Parameters
        ----------
        name : str
            Display name of the workflow.

        workflows : Workflow[]
            Collection of workflows should be executed in parallel.

        settings: keywords
            An dictionary of global settings.
        """
        super().__init__(name, settings)
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
        super().execute(client)

    def dispose(self, client):
        """
        Disposes this workflow.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        self.current_workflow = 0
        super().dispose(client)

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
        super().on_message(msg)

    def get_graph(self, predecessors=None, parent=None):
        """
        Generates a graph from the workflow and returns a tuple:
        (nodes, edges, final_states)

        Parameters
        ----------
        predecessors : str[]
            The IDs of the predecessor states.

        parent : str
            The ID of the parent state (group).

        Return
        ------
        (nodes, edges, final_state_ids) : Tuple
            Graph as a tuple.
        """
        graph = super().get_graph(None, parent)
        nodes = graph[0]
        edges = graph[1]
        print(nodes, edges)

        last_final_state_ids = predecessors
        for workflow in self.workflows:
            graph = workflow.get_graph(last_final_state_ids, self.name)
            nodes.extend(graph[0])
            edges.extend(graph[1])
            last_final_state_ids = graph[2]

        return (nodes, edges, last_final_state_ids)

    def __subscribeCurrentWorkflow(self, client):
        workflow = self.workflows[self.current_workflow]
        workflow.register_on_failed(self.__on_workflow_failed)
        workflow.register_on_finished(self.__on_workflow_finished)
        workflow.execute(client)

    def __unsubscribeCurrentWorkflow(self, client):
        workflow = self.workflows[self.current_workflow]
        workflow.dispose(client)

    def __on_workflow_failed(self, name, error):
        if self._on_workflow_failed:
            self._on_workflow_failed(name, error)

    def __on_workflow_finished(self, name):
        self.__unsubscribeCurrentWorkflow(self.client)
        self.current_workflow += 1
        if self.current_workflow >= len(self.workflows):
            print("  ==> Workflow sequence '%s' finished..." % (self.name))
            if self._on_workflow_finished:
                self._on_workflow_finished(self.name)
            self.state = WorkflowState.FINISHED
        else:
            self.__subscribeCurrentWorkflow(self.client)


class ParallelWorkflow(BaseWorkflow):
    """
    This class implements a wrapper to run multiple workflows in parallel.
    The parallel workflow is a composition organising the flow of one or
    more arbitary workflows.
    """

    def __init__(self, name, workflows, settings=None):
        """
        Initializes a new instance of this class.

        Parameters
        ----------
        name : str
            Display name of the workflow.

        workflows : Workflow[]
            Collection of workflows should be executed in parallel.

        settings: keywords
            An dictionary of global settings.
        """
        super().__init__(name, settings)
        self.workflows = workflows
        self.workflow_finished = {}
        for workflow in self.workflows:
            self.workflow_finished[workflow.name] = False
            workflow.register_on_failed(self.__on_workflow_failed)
            workflow.register_on_finished(self.__on_workflow_finished)

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
        super().execute(client)

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
        super().dispose(client)

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
        super().on_message(msg)

    def get_graph(self, predecessors=None, parent=None):
        """
        Generates a graph from the workflow and returns a tuple:
        (nodes, edges, final_states)

        Parameters
        ----------
        predecessors : str[]
            The IDs of the predecessor states.

        parent : str
            The ID of the parent state (group).

        Return
        ------
        (nodes, edges, final_state_ids) : Tuple
            Graph as a tuple.
        """
        graph = super().get_graph(predecessors, parent)
        nodes = graph[0]
        edges = graph[1]
        final_states = graph[2]

        final_state_ids = []
        for workflow in self.workflows:
            graph = workflow.get_graph(None, self.name)
            nodes.extend(graph[0])
            edges.extend(graph[1])
            final_state_ids.extend(graph[2])

        return (nodes, edges, final_states)

    def __on_workflow_failed(self, name, error):
        if self._on_workflow_failed:
            self._on_workflow_failed(name, error)

    def __on_workflow_finished(self, name):
        self.workflow_finished[name] = True
        if all(list(self.workflow_finished.values())):
            if self._on_workflow_finished:
                self._on_workflow_finished(name)
            self.state = WorkflowState.FINISHED


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
            if self._on_workflow_finished:
                self._on_workflow_finished(self.name)
            self.state = WorkflowState.FINISHED
        else:
            super.on_received_status_inactive(data)


class ActivateLaserWorkflow(Workflow):

    def execute(self, client):
        """
        Executes this workflow.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        super().execute(client)

        if self._on_workflow_finished:
            self._on_workflow_finished(self.name)
        self.state = WorkflowState.FINISHED
