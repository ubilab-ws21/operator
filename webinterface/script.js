let mqtt;
let reconnectTimeout = 2000;
let host = "10.0.0.2";
let port = 9001;
let topics = new Set();
let states_on = new Set();
let states_off = new Set();

/**
 * Short version of getElementById
 * @param id
 * @returns {HTMLElement}
 */
function getID(id) {
    return document.getElementById(id);
}

/**
 * Is called when the connection fails for the mqtt client
 * Tries to restart the client connection
 * @param message
 */
function onFailure(message) {
    console.log("Connection attempt failed");
    console.log(message);
    setTimeout(mqttConnect, reconnectTimeout);
}

/**
 * Is called when the client connected
 */
function onConnect() {
    console.log("Connected debug");
    for (let i = 1; i < 9; i++) {
        mqtt.subscribe(i.toString() + "/#");
    }
}

/**
 * Is called when the client gets a message
 * Performs different actions
 * @param msg
 */
function onMessageArrived(msg) {
    if (topics.has(msg.destinationName.substr(0, 1))) {
        let op = getID("output");
        op.value += "Topic " + msg.destinationName + "; time ";
        if (!msg.payloadString.match(/\d{10}: .*/i)) op.value += ~~(Date.now() / 1000) + " ";
        op.value += msg.payloadString + "\n";
        op.scrollTop = op.scrollHeight;
    }

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
                    <input type="text" id="${dst_b64}_state" readonly=""><br>
                    <input type="text" id="${dst_b64}_data" readonly=""><br><div>
                    <button type="button" id="${dst_b64}_on" onclick="changeState('${dst_b64}', 'on');">On</button>
                    <button type="button" id="${dst_b64}_off"  onclick="changeState('${dst_b64}', 'off');">Off</button>
                    </div></form></div>`;
            }

            // Change the state of the status box
            getID(dst_b64 + "_state").value = obj.state.toLowerCase();
            getID(dst_b64 + "_data").value = obj.data || "";
            if(states_on.has(obj.state.toLowerCase())) {
                getID(dst_b64 + "_on").disabled = true;
            }
            if(states_off.has(obj.state.toLowerCase())) {
                getID(dst_b64 + "_off").disabled = true;
            }
        }
    } catch {
    }
}

/**
 * Creates and connects the mqtt client
 * @constructor
 */
function mqttConnect() {
    console.log("Connecting debug to " + host + ":" + port + "...");
    mqtt = new Paho.Client(host, port, "", "ws-client-d" + ~~(Date.now() / 1000));
    mqtt.onMessageArrived = onMessageArrived;
    mqtt.connect({timeout: 3, onSuccess: onConnect, onFailure: onFailure});
}

/**
 * Toggles the subscription button for a specific topic
 * @param topic
 * @param button
 */
function toggle(topic, button) {
    if (button.parentElement.id === "soff") {
        if (topic.startsWith("$")) {
            mqtt.subscribe(topic + "/#");
        }
        topics.add(topic.substr(0, 1));
    } else {
        if (topic.startsWith("$")) {
            mqtt.unsubscribe(topic + "/#");
        }
        topics.delete(topic.substr(0, 1));
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
    mqtt.publish(getID("send_topic").value, getID("send_message").value, getID("send_qos").value, getID("send_retain").checked);
    getID("send_topic").value = "";
    getID("send_message").value = "";
    getID("send_qos").value = 0
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
    getID("cameras-fallback").firstChild.src = "http://10.0.0.2:8080/stream?random="+new Date().getTime().toString();
}

/**
 * Changes the state of a puzzle displayed in the control section
 * @param dst_b64
 */
function changeState(dst_b64, state) {
    mqtt.send(atob(dst_b64), JSON.stringify({method: "trigger", state: state}), 2);
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
    mqtt.send("1/gameControl", content, 2, true);
}

/**
 * Sends a environment control command
 */
function envSet() {
    mqtt.send(getID("env-target").value, getID("env-command").value + getID("env-number1").value);
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
                if (child.value === "power:") {
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
async function onLoad() {
    new mqttConnect();

    // Read topics into textarea
    let client = new XMLHttpRequest();
    client.open('GET', 'MQTTTopics.md');
    client.onload = function () {
        if (client.status === 200) {
            getID("topics").innerText = client.responseText;
        } else {
            console.log("Error " + client.status.toString() + " reading MQTTTopics.md");
        }
    };
    client.send();
    // TODO: Move to onMessageArrived when real data comes in
    displayGraph(json);
    // TODO: redraw after resize
    window.addEventListener("resize", function(event) { let i=1 });
}

function displayGraph(jsonData) {
    let data = JSON.parse(jsonData);
    let cy = window.cy = cytoscape({
        container: document.getElementById('cy'),
        style: [
            {
                selector: 'node',
                css: {
                    'content': 'data(name)',
                    "color": "#000000",
                    "font-family": "Verdana, Geneva, sans-serif",
                    'text-valign': 'center',
                    'text-halign': 'center',
                    "background-color": "#93a1a1"
                }
            },
            {
                selector: 'node[status="ACTIVE"]',
                css: {
                    'background-color': '#859900'
                }
            },
            {
                selector: 'node[status="INACTIVE"]',
                css: {
                    'background-color': '#cb4b16'
                }
            },
            {
                selector: ':parent',
                css: {
                    'text-valign': 'top',
                    'text-halign': 'center',
                    "background-color": "#002b36"
                }
            },
            {
                selector: 'edge',
                css: {
                    'curve-style': 'bezier',
                    'target-arrow-shape': 'triangle'
                }
            },
            {
                selector: "core",
                css: {
                    "active-bg-size": 0
                }
            }
        ],
        elements: {
            nodes: data.nodes,
            edges: data.edges
        },
        layout: {
            name: 'fcose',
            randomize: false,
            animate: false,
            nodeDimensionsIncludeLabels: true,
            /*klay: {
                direction: "DOWN"
            }*/
        },
        // interaction options:
        zoom: 0.8,
        zoomingEnabled: false,
        userZoomingEnabled: false,
        panningEnabled: false,
        userPanningEnabled: false,
        boxSelectionEnabled: false,
        selectionType: 'single',
        autolock: false,
        autoungrabify: false,
        autounselectify: false,
    });
}