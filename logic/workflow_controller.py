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
        self.client = mqtt.Client()
        self.client.on_connect = self.__on_connect
        self.client.on_message = self.__on_message
        self.mqtt_url = mqtt_url
        self.workflows = workflows
        self.current_workflow = 0

    def start(self):
        """
        Starts the main workflow.
        """
        self.client.connect(self.mqtt_url)
        self.client.loop_start()
        print("Workflow started...")

    def stop(self):
        """
        Stops the main workflow.
        """
        self.client.disconnect()
        self.client.loop_stop()
        print("Workflow stopped...")

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
        workflow.subscribe(client)
        workflow.register_on_failed(self.__on_workflow_failed)
        workflow.register_on_solved(self.__on_workflow_solved)

    def __unsubscribeCurrentWorkflow(self, client):
        workflow = self.workflows[self.current_workflow]
        workflow.unsubscribe(client)

    def __on_workflow_failed(self, error):
        self.stop()
        print("An error occured. The workflow exited. Error: %s" % (error))

    def __on_workflow_solved(self):
        print("Puzzle solved...")
        self.__unsubscribeCurrentWorkflow(self.client)
        self.current_workflow += 1
        if self.current_workflow >= len(self.workflows):
            self.stop()
            print("Workflow finished successfully!")
        else:
            self.__subscribeCurrentWorkflow(self.client)
