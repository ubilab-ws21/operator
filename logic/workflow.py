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
            self.on_finished(self.name, True)
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
        if self.state not in [WorkflowState.SKIPPED, WorkflowState.FINISHED]:
            if name.upper() == self.name.upper():
                if self.state is WorkflowState.ACTIVE:
                    self.on_finished(self.name, True)
                print(f"[{self.name}] Mark workflow as skipped...")
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

    def on_finished(self, name, skipped=False):
        if self._on_workflow_finished:
            self._on_workflow_finished(name)
        if not skipped:
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

        return [node], edges, [self.name]

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
                print(f"[{self.name}] State change to '{obj.state.name}'")
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
                        f"[{self.name}] State '{obj.state}' is not supported"
                    )
            elif obj.method == Method.TRIGGER:
                print(f"[{self.name}] Requested trigger '{obj.state.name}'")
                if obj.state == State.ON:
                    self._on_received_trigger_on(obj.data)
                elif obj.state == State.OFF:
                    self._on_received_trigger_off(obj.data)
                else:
                    self.on_error(
                        self.name,
                        f"[{self.name}] Trigger state '{obj.state}' is not supported"
                    )
            elif obj.method == Method.MESSAGE:
                print(f"[{self.name}] Received message with method 'MESSAGE'. "
                      "Nothing to do...")
            else:
                self.on_error(
                    self.name,
                    f"[{self.name}] Method '{obj.method}' is not supported"
                )
        except Exception as e:
            error_msg = f"[{self.name}] No valid JSON: {str(e)}"
            print(error_msg)
            self.on_error(self.name, error_msg)

        super().on_message(msg)

    def on_finished(self, name, skipped=False):
        self._publishTrigger(self.client, State.OFF, skipped)
        super().on_finished(name, skipped)

    def _publishTrigger(self, client, state, skipped=False):
        if self.topic is not None:
            if state is State.OFF and skipped:
                data = "skipped"
            else:
                data = self.get_settings()
            message = Message(Method.TRIGGER, state, data)
            client.publish(self.topic, message.toJSON(), 2)
            msg = f"[{self.name}] Trigger state '{state.name}'"
            if data:
                msg += f" with settings '{data}'"
            print(msg + "...")

    def _subscripeToTopic(self, client):
        if self.topic is not None:
            client.subscribe(self.topic)
            print(f"[{self.name}] Subscribed to topic '{self.topic}'...")

    def _unsubscripeFromTopic(self, client):
        if self.topic is not None:
            client.unsubscribe(self.topic)
            print(f"[{self.name}] Unsubscribed from topic '{self.topic}'...")

    def _on_received_status_inactive(self, data):
        print("  ==> Nothing to do")

    def _on_received_status_active(self, data):
        print("  ==> Nothing to do")

    def _on_received_status_finished(self, data):
        print("  ==> Puzzle solved successfully")
        self.on_finished(self.name)

    def _on_received_status_failed(self, data):
        print(f"  ==> An error occured: {data}")
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
        super()._execute(client)
        self.client = client
        self.__subscribe_current_workflow(self.client)

    def _dispose(self, client):
        """
        Disposes this workflow.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        self.current_workflow = 0
        if self.state is WorkflowState.ACTIVE:
            self.__unsubscribe_current_workflow(self.client)
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
        if self.current_workflow < len(self.workflows):
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

        return nodes, edges, last_final_state_ids

    def on_finished(self, name, skipped=False):
        if skipped and name == self.name:
            super().on_finished(self.name, True)
        else:
            self.__unsubscribe_current_workflow(self.client)
            self.current_workflow += 1
            if self.current_workflow >= len(self.workflows):
                print(f"  ==> Workflow sequence '{self.name}' finished...")
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
        print(f"[{', '.join(names)}] Starting in parallel...")
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
        if self.state is WorkflowState.ACTIVE:
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

        return nodes, edges, final_states

    def on_finished(self, name, skipped=False):
        if skipped and name == self.name:
            super().on_finished(self.name, True)
        else:
            self.workflow_finished[name] = True
            if all(list(self.workflow_finished.values())):
                print(f"  ==> Parallel workflow sequence '{self.name}' finished...")
                super().on_finished(self.name)


class SendTriggerWorkflow(BaseWorkflow):

    def __init__(self, name, topic, target_state):
        """
        Initializes a new instance of this class.

        Parameters
        ----------
        name : str
            Display name of the workflow.

        topic : str
            Name of the MQTT topic.

        target_state: State
            Target state of the workflow.
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
        """
        super()._execute(client)
        self._publishTrigger(client, self.target_state)
        self.on_finished(self.name)

    def _publishTrigger(self, client, state):
        if self.topic is not None:
            message = Message(Method.TRIGGER, state)
            client.publish(self.topic, message.toJSON(), 2)
            print(f"[{self.name}] Triggered '{state.name}'...")


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


class CombinedWorkflow(SequenceWorkflow):

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
        super().__init__(name, workflows, settings)

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
        return BaseWorkflow.get_graph(self, predecessors, parent)


class InitWorkflow(CombinedWorkflow):
    def __init__(self, workflows, settings=None):
        """
        Initializes a new instance of this class.

        Parameters
        ----------
        workflows : Workflow[]
            Collection of workflows should be executed in parallel.

        settings: keywords
            An dictionary of global settings.
        """
        super().__init__("Init", workflows, settings)


class ExitWorkflow(CombinedWorkflow):
    def __init__(self, workflows, settings=None):
        """
        Initializes a new instance of this class.

        Parameters
        ----------
        workflows : Workflow[]
            Collection of workflows should be executed in parallel.

        settings: keywords
            An dictionary of global settings.
        """
        super().__init__("Exit", workflows, settings)


class AudioControlWorkflow(BaseWorkflow):

    def __init__(self, name, payload, from_file=False):
        """
        Initializes a new instance of this class.

        Parameters
        ----------
        name : str
            Display name of the workflow.

        payload : str
            Either content or file location of the audio to play

        from_file : bool
            Whether a mp3 file should be played
        """
        self.payload = payload
        self.from_file = from_file
        self.topic = "2/textToSpeech"
        super().__init__(name)

    def _execute(self, client):
        """
        Executes this workflow.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        super()._execute(client)
        if self.from_file:
            message = {
                "method": "message",
                "play_from_file": True,
                "file_location": self.payload
            }
        else:
            message = {
                "method": "message",
                "data": self.payload
            }
        client.publish(self.topic, json.dumps(message), 2)
        self.on_finished(self.name)


class LightControlWorkflow(BaseWorkflow):

    def __init__(self, name, topic, target_state,
                 brightness=255, color=(255, 255, 255)):
        """
        Initializes a new instance of this class.

        Parameters
        ----------
        name : str
            Display name of the workflow.

        topic : str
            Name of the MQTT topic.

        target_state: State
            Target state of the light.

        brightness: int [0,255]
            Brightness of the light.

        color: Tuple (r, g, b)
            Color of the light decoded in hex.
        """
        self.target_state = target_state
        self.brightness = brightness
        self.color = color
        self.topic = topic
        super().__init__(name)

    def _execute(self, client):
        """
        Executes this workflow.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        super()._execute(client)

        col = f"{self.color[0]},{self.color[1]},{self.color[2]}"
        self._publishTrigger(client, 'rgb', col)
        self._publishTrigger(client, 'brightness', self.brightness)
        self._publishTrigger(client, 'power', self.target_state.name.lower())
        self.on_finished(self.name)

    def _publishTrigger(self, client, state, data):
        client.publish(
            self.topic,
            json.dumps({
                'method': 'trigger',
                'state': state,
                'data': data
            }),
            2
        )


class LabRoomLightControlWorkflow(CombinedWorkflow):
    def __init__(self, target_state, brightness=255, color=(255, 255, 255)):
        """
        Initializes a new instance of this class.

        Parameters
        ----------
        target_state: State
            Target state of the light.

        brightness: int [0,255]
            Brightness of the light.

        color: Tuple (r, g, b)
            Color of the light decoded in hex.
        """
        workflows = [
            LightControlWorkflow("Turn off light north",
                                 "2/ledstrip/labroom/north",
                                 target_state,
                                 brightness,
                                 color),
            LightControlWorkflow("Turn off light south",
                                 "2/ledstrip/labroom/south",
                                 target_state,
                                 brightness,
                                 color),
            LightControlWorkflow("Turn off light middle",
                                 "2/ledstrip/labroom/middle",
                                 target_state,
                                 brightness,
                                 color)
        ]
        name = f"Turn {target_state.name} lab room lights"
        super().__init__(name, workflows, None)


class ServerRoomLightControlWorkflow(CombinedWorkflow):
    def __init__(self, target_state, brightness=255, color=(255, 255, 255)):
        """
        Initializes a new instance of this class.

        Parameters
        ----------
        target_state: State
            Target state of the light.

        brightness: int [0,255]
            Brightness of the light.

        color: Tuple (r, g, b)
            Color of the light decoded in hex.
        """
        workflows = [
            LightControlWorkflow("Turn off light serverroom",
                                 "2/ledstrip/serverroom",
                                 target_state,
                                 brightness,
                                 color),
            LightControlWorkflow("Turn off light door server room",
                                 "2/ledstrip/doorserverroom",
                                 target_state,
                                 brightness,
                                 color)
        ]
        name = f"Turn {target_state.name} server room lights"
        super().__init__(name, workflows, None)
