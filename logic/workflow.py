import json
from message import Message, Method, State, fromJSON
from enum import Enum
from util import RepeatTimer, publish_tts


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
        self.highlight = False

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
                print(f"[{self.name}] Mark workflow as skipped...")
                old_state = self.state
                self.state = WorkflowState.SKIPPED
                if old_state is WorkflowState.ACTIVE:
                    self.on_finished(self.name, True)

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
        if not skipped:
            self.state = WorkflowState.FINISHED
        if self._on_workflow_finished:
            self._on_workflow_finished(name)

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

    def get_graph(self, predecessors=None, parent=None,
                  name=None, highlight=None):
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
        name_id = self.name
        if name:
            name_id = name

        hl = self.highlight
        if highlight is not None:
            hl = highlight

        nodeData = {
            'id': name_id,
            'name': name_id,
            'highlight': hl,
            'status': self.state.name,
            'type': self.type
        }

        if hasattr(self, "topic"):
            nodeData['topic'] = self.topic

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
        self.client = None

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
                        f"[{self.name}] Trigger state "
                        f"'{obj.state}' is not supported"
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
        if self.topic and client:
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
        skipped = False
        if self.state is not WorkflowState.FINISHED:
            if name.upper() == self.name.upper():
                print(f"[{self.name}] Set workflow sequence to skipped...")
                skipped = True

            for workflow in self.workflows:
                if skipped:
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
        graph = super().get_graph(predecessors, parent)
        nodes = graph[0]
        edges = graph[1]

        last_final_state_ids = None
        for workflow in self.workflows:
            graph = workflow.get_graph(last_final_state_ids, self.name)
            nodes.extend(graph[0])
            edges.extend(graph[1])
            last_final_state_ids = graph[2]

        return nodes, edges, [self.name]

    def on_finished(self, name, skipped=False):
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
        skipped = False
        if self.state is not WorkflowState.FINISHED:
            if name.upper() == self.name.upper():
                print(f"[{self.name}] Set parallel workflows to skipped...")
                skipped = True

            for workflow in self.workflows:
                if skipped:
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
        self.workflow_finished[name] = True
        if all(list(self.workflow_finished.values())):
            print(f"  ==> Parallel workflow sequence"
                  f" '{self.name}' finished...")
            super().on_finished(self.name)


class CombinedWorkflow(SequenceWorkflow):
    """
    This workflow is a special sequence workflows displaying all
    it's capsulate workflows as one node in the graph config.
    """

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
        node = BaseWorkflow.get_graph(self, predecessors, parent)
        nodes = []
        nodes.extend(node[0])
        edges = []
        edges.extend(node[1])

        if self.settings and self.settings.get('wrap_parent'):
            child = BaseWorkflow.get_graph(
                self, None, self.name,
                f"{self.name} routines", False)
            nodes.extend(child[0])
            edges.extend(child[1])

        return nodes, edges, [self.name]


class InitWorkflow(CombinedWorkflow):
    """
    This workflow is just a named ("Init") combined workflow to do some initial
    tasks.
    """

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
        wrap_parent = 'wrap_parent'
        if settings and wrap_parent not in settings:
            settings[wrap_parent] = True
        else:
            settings = {wrap_parent: True}

        super().__init__("Init", workflows, settings)


class ExitWorkflow(CombinedWorkflow):
    """
    This workflow is just a named ("Exit") combined workflow to do some
    finalization tasks.
    """

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
        wrap_parent = 'wrap_parent'
        if settings and wrap_parent not in settings:
            settings[wrap_parent] = True
        else:
            settings = {wrap_parent: True}

        super().__init__("Exit", workflows, settings)


class ScaleWorkflow(Workflow):
    """
    This workflow handles the special solved condition of the scale riddle.
    The riddle is solved if the scale is unbalanced and after that is
    balanced again.
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
        super().__init__(name, topic, settings)
        self.scale_status = State.INACTIVE

    def _on_received_status_inactive(self, data):
        if self.scale_status == State.ACTIVE:
            # call super().super() on_finished to avoid sending trigger:off
            BaseWorkflow.on_finished(self, self.name)
        else:
            self.scale_status = State.INACTIVE

    def _on_received_status_active(self, data):
        self.scale_status = State.ACTIVE


class GlobesWorkflow(Workflow):
    """
    Special workflow for the globes puzzle to play a hint via tts while
    the entrance door is still opened
    """
    running_timer = None

    def _on_received_status_active(self, data):
        """
        This method overrides the method in Workflow to start a
        timer if it is not already set
        :param data:
        :return:
        """
        if not self.running_timer:
            self.running_timer = RepeatTimer(20.0, publish_tts,
                                             args=("Please close the door",))
            self.running_timer.start()
            print("==> Hint timer started")
        else:
            print("==> Hint timer already running, nothing to do")

    def on_finished(self, name, skipped=False):
        """
        This method overrides the method in Workflow to stop the
        timer if it is already set (for normal finishing and skipping)
        :param name:
        :param skipped:
        :return:
        """
        if self.running_timer:
            self.running_timer.cancel()
            self.running_timer = None
            print("==> Hint timer stopped")
        else:
            print("==> Hint timer not running, nothing to do")
        super().on_finished(name, skipped)


class IPWorkflow(Workflow):
    """
    Special workflow for the IP puzzle avoiding a trigger:off
    if the puzzle is finished.
    """

    def on_finished(self, name, skipped=False):
        BaseWorkflow.on_finished(self, name, skipped)


class SingleCommandWorkflow(BaseWorkflow):
    """
    This workflow executes a single command without waiting for an answer.
    """

    def _execute(self, client):
        """
        Executes this workflow.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        super()._execute(client)
        self._execute_single_command(client)
        self.on_finished(self.name)

    def _execute_single_command(self, client):
        """
        Executes an atomic command.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        pass

    def skip(self, name):
        """
        Overridden: On skip there is nothing to do, because it's a
        single command (atomic).
        """
        pass


class SendTriggerWorkflow(SingleCommandWorkflow):
    """
    This workflow sends trigger:on and trigger:off to a given topic.
    """

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

    def _execute_single_command(self, client):
        """
        Executes an atomic command.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        self._publishTrigger(client, self.target_state)

    def _publishTrigger(self, client, state):
        if self.topic is not None:
            message = Message(Method.TRIGGER, state)
            client.publish(self.topic, message.toJSON(), 2)
            print(f"[{self.name}] Triggered '{state.name}'...")


class AudioControlWorkflow(SingleCommandWorkflow):
    """
    This workflow sends messages to text-to-speech or play defined
    audio files over the audio system.
    """

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

    def _execute_single_command(self, client):
        """
        Executes an atomic command.

        Parameters
        ----------
        client : Client
            MQTT client
        """
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


class LightControlWorkflow(SingleCommandWorkflow):
    """
    This workflow allows to contol the light of the room.
    """

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

    def _execute_single_command(self, client):
        """
        Executes an atomic command.

        Parameters
        ----------
        client : Client
            MQTT client
        """
        col = f"{self.color[0]},{self.color[1]},{self.color[2]}"
        self._publishTrigger(client, 'rgb', col)
        self._publishTrigger(client, 'brightness', self.brightness)
        self._publishTrigger(client, 'power', self.target_state.name.lower())

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
    """
    This workflow controls all LED stripes in the lab room in one
    single workfow.
    """

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
    """
    This workflow controls all LED stripes in the server room in one
    single workfow.
    """

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
        name = f"Turn {target_state.name} " \
               f"{'dimmed' if brightness < 255 else 'full'}" \
               f" server room lights"
        super().__init__(name, workflows, None)
