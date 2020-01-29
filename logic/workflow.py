import json
from message import Message, Method, State, fromJSON
from enum import Enum


class WorkflowState(Enum):
    INACTIVE = 0
    ACTIVE = 1
    FINISHED = 2
    SKIPPED = 3


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
        if self.state is WorkflowState.SKIPPED:
            self.on_finished(self.name)
        else:
            self._execute(client)

    def _execute(self, client):
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
        if self.state is not WorkflowState.SKIPPED:
            self._dispose(client)

    def _dispose(self, client):
        """
        Disposes this workflow.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        if self.state is WorkflowState.ACTIVE:
            self.state = WorkflowState.INACTIVE

    def skip(self, name):
        if self.state is not WorkflowState.SKIPPED:
            if name.upper() == self.name.upper():
                if self.state is WorkflowState.ACTIVE:
                    self.on_finished(self.name)
                self.state = WorkflowState.SKIPPED

    def on_message(self, msg):
        """
        Processes the message sended by the MQTT server.

        Parameters
        ----------
        msg : Message
            Message from the MQTT topic.
        """
        pass

    def on_error(self, name, error):
        if self._on_workflow_failed:
            self._on_workflow_failed(name, error)

    def on_finished(self, name):
        if self._on_workflow_finished:
            self._on_workflow_finished(name)
        if self.state is not WorkflowState.SKIPPED:
            self.state = WorkflowState.FINISHED

    def get_settings(self):
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

        edges = self._create_edges(self.name, predecessors)

        return ([node], edges, [self.name])

    def _create_edges(self, target, predecessors):
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

    def _execute(self, client):
        """
        Executes this workflow.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        self.client = client
        self._publishTrigger(client, State.ON)
        self._subscripeToTopic(client)
        super()._execute(client)

    def _dispose(self, client):
        """
        Disposes this workflow.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        self._unsubscripeFromTopic(client)
        super()._dispose(client)

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
                    self.on_error(
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
                    self.on_error(
                        self.name,
                        "[%s] Trigger state '%s' is not supported"
                        % (self.name, obj.state))
            elif obj.method == Method.MESSAGE:
                print("[%s] Received message with method 'MESSAGE'. "
                      "Nothing to do..." % (self.name))
            else:
                self.on_error(
                    self.name,
                    "[%s] Method '%s' is not supported"
                    % (self.name, obj.method))
        except Exception as e:
            error_msg = "[%s] No valid JSON: %s" % (self.name, str(e))
            print(error_msg)
            self.on_error(self.name, error_msg)

        super().on_message(msg)

    def on_finished(self, name):
        self._publishTrigger(self.client, State.OFF)
        super().on_finished(name)

    def _publishTrigger(self, client, state):
        if self.topic is not None:
            data = self.get_settings()
            message = Message(Method.TRIGGER, state, data)
            client.publish(self.topic, message.toJSON(), 2)
            print("[%s] Trigger state '%s'..." % (self.name, state.name))

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
        self.on_finished(self.name)

    def _on_received_status_failed(self, data):
        print("  ==> An error occured: %s" % (data))
        self.on_error(self.name, data)

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

    def _execute(self, client):
        """
        Executes this workflow.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        self.client = client
        self.__subscribe_current_workflow(self.client)
        super()._execute(client)

    def _dispose(self, client):
        """
        Disposes this workflow.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        self.current_workflow = 0
        super()._dispose(client)

    def skip(self, name):
        super().skip(name)
        for workflow in self.workflows:
            if self.state == WorkflowState.SKIPPED:
                workflow.skip(workflow.name)
            else:
                workflow.skip(name)

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

        last_final_state_ids = predecessors
        for workflow in self.workflows:
            graph = workflow.get_graph(last_final_state_ids, self.name)
            nodes.extend(graph[0])
            edges.extend(graph[1])
            last_final_state_ids = graph[2]

        return (nodes, edges, last_final_state_ids)

    def on_finished(self, name):
        if name == self.name:
            super().on_finished(self.name)

        self.__unsubscribe_current_workflow(self.client)
        self.current_workflow += 1
        if self.current_workflow >= len(self.workflows):
            print("  ==> Workflow sequence '%s' finished..." % (self.name))
            super().on_finished(self.name)
        else:
            self.__subscribe_current_workflow(self.client)

    def __subscribe_current_workflow(self, client):
        workflow = self.workflows[self.current_workflow]
        workflow.register_on_failed(self.on_error)
        workflow.register_on_finished(self.on_finished)
        workflow.execute(client)

    def __unsubscribe_current_workflow(self, client):
        workflow = self.workflows[self.current_workflow]
        workflow.dispose(client)


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
            workflow.register_on_failed(self.on_error)
            workflow.register_on_finished(self.on_finished)

    def _execute(self, client):
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
        super()._execute(client)

    def _dispose(self, client):
        """
        Disposes this workflow.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        for workflow in self.workflows:
            workflow.dispose(client)
        super()._dispose(client)

    def skip(self, name):
        super().skip(name)
        for workflow in self.workflows:
            if self.state is WorkflowState.SKIPPED:
                workflow.skip(workflow.name)
            else:
                workflow.skip(name)

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

    def on_finished(self, name):
        if name == self.name:
            super().on_finished(self.name)

        self.workflow_finished[name] = True
        if all(list(self.workflow_finished.values())):
            print("  ==> Parallel workflow sequence '%s' finished..."
                  % (self.name))
            super().on_finished(self.name)


class DoorWorkflow(BaseWorkflow):

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
            Target state of the door (opened/closed)
        """
        self.target_state = target_state
        self.topic = topic
        super().__init__(name)

    def _execute(self, client):
        """
        Executes this workflow.

        Parameters
        ----------
        client : Client
            MQTT client

        Returns
        -------
        is_started : boolean
            Information if the workflow started.
        """
        super()._execute(client)
        self._publishTrigger(client, self.target_state)
        self.on_finished(self.name)

    def _publishTrigger(self, client, state):
        if self.topic is not None:
            message = Message(Method.TRIGGER, state)
            client.publish(self.topic, message.toJSON(), 2)
            door_state = ""
            if state is State.ON:
                door_state = "opens"
            elif state is State.OFF:
                door_state = "closes"
            print("[%s] Door %s..." % (self.name, door_state))


class ActivateLaserWorkflow(BaseWorkflow):

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
        super().__init__(name)

    def _execute(self, client):
        """
        Executes this workflow.

        Parameters
        ----------
        client : Client
            MQTT client

        Returns
        -------
        is_started : boolean
            Information if the workflow started.
        """
        super()._execute(client)
        self._publishTrigger(client)
        self.on_finished(self.name)

    def _publishTrigger(self, client):
        if self.topic is not None:
            message = Message(Method.TRIGGER, State.ON)
            client.publish(self.topic, message.toJSON(), 2)
            print("[%s] Laser activated..." % (self.name))


class ScaleWorkflow(Workflow):

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
        super().__init__(name, topic, settings)
        self.scale_status = State.INACTIVE

    def _on_received_status_inactive(self, data):
        if self.scale_status == State.ACTIVE:
            self.on_finished(self.name)
        else:
            self.scale_status = State.INACTIVE

    def _on_received_status_active(self, data):
        self.scale_status = State.ACTIVE
