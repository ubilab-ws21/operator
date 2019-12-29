from workflow import Workflow


class ParallelWorkflow(Workflow):
    """
    This class implements a wrapper to run multiple workflows in parallel.
    The parallel workflow is a composition organising the flow of one or
    more arbitary workflows.
    """

    def __init__(self, name, topic, workflows):
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
        super().__init__(name, topic)
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
