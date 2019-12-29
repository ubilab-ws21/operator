import paho.mqtt.client as mqtt


class WorkflowController:
    """
    The workflow controller manages the MQTT connection and organizes
    the transitions between the registered workflows.
    """

    def __init__(self, mqtt_url, workflows):
        """
        Initializes a new instance of this class.

        Parameters
        ----------
        mqtt_url : str
            The url of the MQTT server.

        workflows : Workflow[]
            An array of workflows defining the sequence of their execution.
        """
        self.client = None
        self.mqtt_url = mqtt_url
        self.workflows = workflows
        self.current_workflow = 0

    def start(self):
        """
        Starts the main workflow.
        """
        self.client = mqtt.Client()
        self.client.on_connect = self.__on_connect
        self.client.on_message = self.__on_message
        self.client.connect(self.mqtt_url)
        self.client.loop_start()
        print("Main workflow started...")

    def stop(self):
        """
        Stops the main workflow.
        """
        self.client.disconnect()
        self.client.loop_stop()
        print("Main workflow stopped...")

    def reset(self):
        """
        Resets the main workflow.
        """
        self.stop()
        self.current_workflow = 0
        self.start()

    def __on_connect(self, client, userdata, flags, rc):
        """
        Subscribing in on_connect() means that if we lose the connection and
        reconnect then subscriptions will be renewed.
        """
        self.__subscribeCurrentWorkflow(client)

    def __on_message(self, client, userdata, msg):
        workflow = self.workflows[self.current_workflow]
        workflow.on_message(msg)

    def __subscribeCurrentWorkflow(self, client):
        workflow = self.workflows[self.current_workflow]
        workflow.register_on_failed(self.__on_workflow_failed)
        workflow.register_on_solved(self.__on_workflow_solved)
        workflow.execute(client)

    def __unsubscribeCurrentWorkflow(self, client):
        workflow = self.workflows[self.current_workflow]
        workflow.register_on_failed(None)
        workflow.register_on_solved(None)
        workflow.dispose(client)

    def __on_workflow_failed(self, name, error):
        pass

    def __on_workflow_solved(self, name):
        self.__unsubscribeCurrentWorkflow(self.client)
        self.current_workflow += 1
        if self.current_workflow >= len(self.workflows):
            print("===============================")
            print("Workflow finished successfully!")
            print("===============================")
            self.reset()
            print("Main workflow resetted...")
        else:
            self.__subscribeCurrentWorkflow(self.client)
