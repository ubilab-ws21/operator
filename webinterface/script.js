// Debug client
let mqtt;
// Control client
let mqttControl;
let reconnectTimeout = 2000;
let host = "10.0.0.2";
let port = 9001;

/**
 * Short version of getElementById
 * @param id
 * @returns {HTMLElement}
 */
function getID(id) {
    return document.getElementById(id);
}

/**
 * Is called when the connection fails for the debug client
 * Tries to restart the client connection
 * @param message
 */
function onFailure(message) {
    console.log("Connection attempt for debug failed");
    console.log(message);
    setTimeout(mqttConnect, reconnectTimeout);
}

/**
 * Is called when the connection fails for the control client
 * Tries to restart the client connection
 * @param message
 */
function onFailureControl(message) {
    console.log("Connection attempt for control failed");
    console.log(message);
    setTimeout(mqttConnectControl, reconnectTimeout);
}

/**
 * Is called when the debug client connected
 */
function onConnect() {
    console.log("Connected debug");
}

/**
 * Is called when the control client connected
 * Subscribes to the topic of all groups
 */
function onConnectControl() {
    console.log("Connected control");
    for (let i = 1; i < 9; i++) {
        mqttControl.subscribe(i.toString() + "/#");
    }
}

/**
 * Is called when the debug client gets a message
 * Prints the message to the textarea
 * @param msg
 */
function onMessageArrived(msg) {
    let op = getID("output");
    op.value += "Topic " + msg.destinationName + "; time ";
    if (!msg.payloadString.match(/\d{10}: .*/i)) op.value += ~~(Date.now() / 1000) + " ";
    op.value += msg.payloadString + "\n";
    op.scrollTop = op.scrollHeight;
}

/**
 * Is called when the control client gets a message
 * Performs different actions
 * @param msg
 */
function onMessageArrivedControl(msg) {
    // Displays game time
    if (msg.destinationName === "1/gameTime_formatted") {
        getID("time").innerText = msg.payloadString;
    }
    // Dis-/enables game controls
    else if (msg.destinationName === "1/gameControl") {
        switch (msg.payloadString) {
            case "start":
                getID("start").disabled = true;
                getID("pause").disabled = false;
                getID("stop").disabled = false;
                break;
            case "pause":
                getID("start").disabled = false;
                getID("pause").disabled = true;
                getID("stop").disabled = false;
                break;
            case "stop":
                getID("start").disabled = false;
                getID("pause").disabled = true;
                getID("stop").disabled = true;
                break;
        }
    }
    // Parse JSON and display puzzle status
    try {
        let obj = JSON.parse(msg.payloadString);
        if (obj.method.toLowerCase() === "status") {
            let dst = msg.destinationName;
            let dst_b64 = btoa(dst);

            // Create the status box if it doesn't exist yet
            if (getID(dst_b64) == null) {
                getID("c" + dst.charAt(0)).innerHTML += `<div id="${dst_b64}" class="control"><b>${dst}</b><form>
                    <select id="${dst_b64}_state">
                        <option value="inactive">inactive</option>
                        <option value="active">active</option>
                        <option value="solved">solved</option>
                        <option value="failed">failed</option>
                    </select><br><input type="text" id="${dst_b64}_data" readonly=""><br>
                    <button type="button" onclick="changeState('${dst_b64}');">Change</button></form></div>`;
            }

            // Change the state of the status box
            getID(dst_b64 + "_state").value = obj.state.toLowerCase();
            getID(dst_b64 + "_data").value = obj.data || "";
        }
    } catch(error){
        // Catch only JSON syntax error
        if(!(error instanceof SyntaxError)) {
            throw error;
        }
    }
}

/**
 * Creates and connects the debug client
 * @constructor
 */
function mqttConnect() {
    console.log("Connecting debug to " + host + ":" + port + "...");
    mqtt = new Paho.Client(host, port, "", "ws-client-d" + ~~(Date.now() / 1000));
    mqtt.onMessageArrived = onMessageArrived;
    mqtt.connect({timeout: 3, onSuccess: onConnect, onFailure: onFailure});
}

/**
 * Creates and connects the control client
 * @constructor
 */
function mqttConnectControl() {
    console.log("Connecting control to " + host + ":" + port + "...");
    mqttControl = new Paho.Client(host, port, "", "ws-client-c" + ~~(Date.now() / 1000));
    mqttControl.onMessageArrived = onMessageArrivedControl;
    mqttControl.connect({timeout: 3, onSuccess: onConnectControl, onFailure: onFailureControl});
}

/**
 * Toggles the subscription button for a specific topic
 * @param topic
 * @param button
 */
function toggle(topic, button) {
    if (button.parentElement.id === "soff") {
        mqtt.subscribe(topic + "/#");
    } else {
        mqtt.unsubscribe(topic + "/#");
    }
    getID(button.parentElement.id === "soff" ? "son" : "soff").appendChild(button);
}

/**
 * Toggles all un- or subscription buttons by calling their click event
 * @param from
 */
function toggleAll(from) {
    while (getID(from).firstElementChild !== null) {
        getID(from).firstElementChild.click();
    }
}

/**
 * Sends the message entered into the form
 */
function send() {
    if (getID("send_topic").value === "") {
        alert("Topic is required");
        return;
    }
    mqtt.publish(getID("send_topic").value, getID("send_message").value, 0, getID("send_retain").checked);
    getID("send_topic").value = "";
    getID("send_message").value = "";
    getID("send_retain").checked = false;
}

/**
 * Toggles a given help block
 * @param n
 */
function toggleHelp(n) {
    let id = n === 1 ? "help" : "help2";
    if (getID(id).style.display === "none") {
        getID(id).style.display = "inline-block";
    } else {
        getID(id).style.display = "none";
    }
}

/**
 * Switches the textarea between the debug output and the topic table
 */
function toggleTopics() {
    if (getID("topics").style.display === "none") {
        getID("topics").style.display = "inline-block";
        getID("output").style.display = "none";
    } else {
        getID("topics").style.display = "none";
        getID("output").style.display = "inline-block";
    }
}

/**
 * Sends a message to the camera control to change the active camera in fallback mode
 */
function changeCamera() {
    let xhr = new XMLHttpRequest();
    let number = getID("camera-selection").value;

    xhr.onload = function () {
        console.log(this.statusText + " (" + this.status.toString() + ")");
    };

    xhr.open("GET", "http://localhost:9000/".concat(number));
    xhr.send();
}

/**
 * Changes the state of a puzzle displayed in the control section
 * @param dst_b64
 */
function changeState(dst_b64) {
    let dst = atob(dst_b64);
    let state = getID(dst_b64 + "_state").value;
    let json_obj = JSON.stringify({method: "trigger", state: "on", data: state});
    mqttControl.send(dst, json_obj, 2);
}

/**
 * Changes the currently active tab
 * @param target
 */
function changeTab(target) {
    for (name of ["control", "cameras", "cameras-fallback", "mosquitto"]) {
        if (name !== target) {
            getID(name).style.display = "none";
            getID("b-" + name).parentElement.className = "navitem";
        } else {
            getID(name).style.display = "block";
            getID("b-" + name).parentElement.className = "navitem selected";
        }
    }
}

/**
 * Sends a game control command
 * @param content
 */
function command(content) {
    mqttControl.send("1/gameControl", content, 2, true);
}

/**
 * Sends a environment control command
 */
function envSet() {
    mqttControl.send(getID("env-target").value, getID("env-command").value + getID("env-number1").value);
}

/**
 * En-/disables valid environment commands upon selection of topic
 * @param select
 */
function validateCommands(select) {
    let cmd = getID("env-command");
    cmd.disabled = false;
    switch (select.value) {
        case "0":
            cmd.disabled = true;
            getID("env-number1").disabled = true;
            getID("env-button").disabled = true;
            break;
        case "2/gyrophare":
            for (let child of cmd.children) {
                child.disabled = child.value !== "power:";
                if(child.value === "power:") {
                    child.selected = true;
                    getID("env-number1").disabled = false;
                    getID("env-number1").max = 1;
                    getID("env-button").disabled = false;
                }
            }
            break;
        default:
            for (let child of cmd.children) {
                child.disabled = false;
            }
            break;
    }
}

/**
 * En-/disables valid environment command values upon selection of command
 * @param select
 */
function validateNumbers(select) {
    let num = getID("env-number1");
    num.disabled = false;
    getID("env-button").disabled = false;
    switch (select.value) {
        case "0":
            num.disabled = true;
            getID("env-button").disabled = true;
            break;
        case "pattern:":
            num.max = 11;
            break;
        case "brightness:":
            num.max = 255;
            break;
        default:
            num.max = 1;
            break;
    }
}

/**
 * Triggers all functions started on load
 */
function onLoad() {
    new mqttConnect();
    new mqttConnectControl();

    // Read topics into textarea
    let client = new XMLHttpRequest();
    client.open('GET', 'http://10.0.0.2/MQTTTopics.md');
    client.onload = function() {
        if(client.status === 200) {
            getID("topics").innerText = client.responseText;
        } else {
            console.log("Error " + client.status.toString() + " reading MQTTTopics.md");
        }
    };
    client.send();
}