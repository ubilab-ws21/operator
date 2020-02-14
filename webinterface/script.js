let mqtt;
let reconnectTimeout = 2000;
let host = "10.0.0.2";
let port = 9001;
let topicsUser = new Set();
let topicsUI = new Set(["1/gameTime_formatted", "1/gameControl", "1/gameOptions", "1/gameState", "4/door/entrance", "4/door/serverRoom"]);
let tabs = new Set(["control", "cameras", "cameras-fallback", "mosquitto"]);
let printTime = false;
let controlleft = true;

/**
 * Short version of getElementById
 * @param id
 * @returns {HTMLElement}
 */
function getID(id) {
    return document.getElementById(id);
}

/**
 * This function toggles the spinner and sets the opacity of the tabs
 * @param activate Whether to activate or deactivate the spinner and opacity
 */
function setSpinner(activate) {
    getID("loader-control").style.display = activate ? "block" : "none";
    getID("loader-mosquitto").style.display = activate ? "block" : "none";
    getID("control").style.filter = activate ? "opacity(0.2)" : "";
    getID("mosquitto").style.filter = activate ? "opacity(0.2)" : "";
}

/**
 * Is called when the connection fails for the mqtt client
 * Tries to restart the client connection
 * @param message
 */
function onFailure(message) {
    setSpinner(true);
    console.log(message);
    setTimeout(mqttConnect, reconnectTimeout);
}

/**
 * Is called when the client connected
 */
function onConnect() {
    setSpinner(false);
    for (let topic of topicsUI) {
        mqtt.subscribe(topic);
    }
}

/**
 * Is called when the client gets a message
 * Performs different actions
 * @param msg
 */
function onMessageArrived(msg) {
    let topic = msg.destinationName;
    if (topicsUser.has(topic.substr(0, 1)) && (!topic.startsWith("1/gameTime") || printTime)) {
        let op = getID("output");
        op.value += "Topic " + topic + "; time ";
        if (!msg.payloadString.match(/\d{10}: .*/i)) op.value += ~~(Date.now() / 1000) + " ";
        op.value += msg.payloadString + "\n";
        op.scrollTop = op.scrollHeight;
    }

    // Displays game time
    if (topic === "1/gameTime_formatted") {
        getID("time").innerText = msg.payloadString;
    }
    // Dis-/enables game controls
    else if (topic === "1/gameControl") {
        switch (msg.payloadString) {
            case "start":
                getID("start").disabled = true;
                getID("pause").disabled = false;
                getID("stop").disabled = false;
                getID("time").className = "started";
                getID("playercount").disabled = true;
                getID("playtime").disabled = true;
                getID("skipto").disabled = true;
                break;
            case "pause":
                getID("start").disabled = false;
                getID("pause").disabled = true;
                getID("stop").disabled = false;
                getID("time").className = "paused";
                break;
            case "":
            case "stop":
                getID("start").disabled = false;
                getID("pause").disabled = true;
                getID("stop").disabled = true;
                getID("time").className = "stopped";
                getID("playercount").disabled = false;
                getID("playtime").disabled = false;
                getID("skipto").disabled = false;
                break;
        }
    }
    // Draw graph from gameState
    else if (topic === "1/gameState") {
        try {
            displayGraph(JSON.parse(msg.payloadString));
            getID("startnote").style.display = "none";
        } catch {
        }
    }
    // Show game options when game is running
    else if (topic === "1/gameOptions" && msg.payloadString) {
        try {
            let opts = JSON.parse(msg.payloadString);
            getID("playercount").value = opts.participants;
            getID("playtime").value = opts.duration;
            if(msg.skipTo) {
                getID("skipto").value = opts.skipTo;
            }
        } catch {
        }
    }
}

/**
 * Is called when the mqtt connection is lost
 * @param responseObject
 */
function onConnectionLost(responseObject) {
    setSpinner(true);
    console.log("Connection lost: " + JSON.stringify(responseObject));
    setTimeout(mqttConnect, reconnectTimeout);
}

/**
 * Creates and connects the mqtt client
 */
async function mqttConnect() {
    console.log("Connecting mqtt client to " + host + ":" + port + "...");
    setSpinner(true);
    mqtt = new Paho.Client(host, port, "", "ws-client-d" + ~~(Date.now() / 1000));
    mqtt.onMessageArrived = onMessageArrived;
    mqtt.onConnectionLost = onConnectionLost;
    mqtt.connect({timeout: 3, onSuccess: onConnect, onFailure: onFailure});
}

/**
 * Toggles the subscription button for a specific topic
 * @param topic
 * @param button
 */
function toggle(topic, button) {
    if (button.parentElement.id === "soff") {
        mqtt.subscribe(topic + "/#");
        topicsUser.add(topic.substr(0, 1));
    } else {
        mqtt.unsubscribe(topic + "/#");
        topicsUser.delete(topic.substr(0, 1));
        for (let tUI of topicsUI) {
            if (tUI.startsWith(topic)) {
                mqtt.subscribe(tUI);
            }
        }
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
    if (getID("send-topic").value === "") {
        alert("Topic is required");
        return;
    }
    mqtt.publish(getID("send-topic").value, getID("send-message").value, parseInt(getID("send-qos").value),
        getID("send-retain").checked);
    getID("send-topic").value = "";
    getID("send-message").value = "";
    getID("send-qos").value = 0;
    getID("send-retain").checked = false;
}

/**
 * Sends the message entered into the simplified form
 */
function simpleSend() {
    let message = {
        method: getID("simple-method").value,
        state: getID("simple-state").value,
        data: getID("simple-data").value
    };
    mqtt.publish(getID("simple-topic").value, JSON.stringify(message), parseInt(getID("simple-qos").value),
        getID("simple-retain").checked);
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
 * Toggles the left control bar
 */
function toggleControlLeft() {
    if(controlleft) {
        getID("toggle-left").style.left = "0.8em";
        getID("control-left").style.display = "none";
        getID("cytoscape-container").style.width = "100%";
        controlleft = false;
    } else {
        getID("toggle-left").style.left = "22em";
        getID("control-left").style.display = "block";
        getID("cytoscape-container").style.width = "calc(100% - 20em)";
        controlleft = true;
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
    getID("cameras-fallback").firstChild.src = "http://10.0.0.2:8080/stream?random=" + new Date().getTime().toString();
    // location.reload();
}

/**
 * Changes the state of a puzzle displayed in the control section
 * @param dst_b64
 * @param state
 */
function changeState(dst_b64, state) {
    mqtt.send(atob(dst_b64), JSON.stringify({
        method: "trigger",
        state: state
    }), 2);
}

/**
 * Sends the input message to the text-to-speech script
 */
function playMessage() {
    if (getID("tts").value === "") {
        alert("Message must be set");
    }
    mqtt.send("2/textToSpeech", JSON.stringify({
        method: "message",
        data: `<speak><prosody rate="${getID("tts-rate").value}" pitch="${getID("tts-pitch").value}" volume="${getID("tts-volume").value}">${getID("tts").value}</prosody></speak>`,
        kwargs: {
            TextType: "ssml",
            VoiceId: getID("tts-voice").value,
            LanguageCode: getLanguageByVoice(getID("tts-voice").value)
        }
    }), 2, false);
    getID("tts").value = "";
    getID("tts-rate").value = "default";
    getID("tts-pitch").value = "default";
    getID("tts-volume").value = "default";
    getID("tts-voice").value = "Joanna";
}

/**
 * Translates a voiceid to the corresponding language code
 */
function getLanguageByVoice(voice) {
    switch (voice) {
        case "Nicole":
        case "Russel":
            return "en-AU";
        case "Amy":
        case "Emma":
        case "Brian":
            return "en-GB";
        case "Aditi":
        case "Raveena":
            return "en-IN";
        case "Ivy":
        case "Joanna":
        case "Kendra":
        case "Kimberly":
        case "Sally":
        case "Joey":
        case "Justin":
        case "Matthew":
            return "en-US";
        case "Geraint":
            return "en-GB-WLS";
        case "Marlene":
        case "Vicki":
        case "Hans":
            return "de-DE";
    }
}

/**
 * Changes the currently active tab
 * @param target
 */
function changeTab(target) {
    let url = window.location.href.split("?")[0];
    if (tabs.has(target)) {
        for (name of tabs) {
            if (name !== target) {
                getID(name).style.display = "none";
                getID("b-" + name).className = "navlink";
            } else {
                getID(name).style.display = "block";
                getID("b-" + name).className = "navlink selected";
            }
        }
        url += "?" + target;
    }
    window.history.replaceState({}, document.title, url);
}

/**
 * Sends a game control command
 * @param content
 */
function command(content) {
    let options = {
        participants: parseInt(getID("playercount").value),
        duration: parseInt(getID("playtime").value)
    };
    if (getID("skipto").value !== "0") {
        options["skipTo"] = getID("skipto").value;
        getID("skipto").value = "0";
    }
    mqtt.send("1/gameOptions", JSON.stringify(options), 2, true);
    mqtt.send("1/gameControl", content, 2, true);
}

/**
 * Sends a environment control command
 */
function envSet() {
    let command = {
        method: "trigger",
        state: getID("env-command").value,
        data: null
    };
    switch (command.state) {
        case "0":
            return false;
        case "brightnessAdjust":
        case "patternAdjust":
            command.data = getID("env-adjust").value;
            break;
        case "rgb":
            let hex = getID("env-rgb").value;
            command.data = hex.match(/[A-Za-z0-9]{2}/g).map(function (v) {
                return parseInt(v, 16)
            }).join(",");
            break;
        case "blink":
            let hex1 = getID("env-rgb").value;
            hex1 = hex1.match(/[A-Za-z0-9]{2}/g).map(function (v) {
                return parseInt(v, 16)
            }).join(",");
            let hex2 = getID("env-rgb2").value;
            hex2 = hex2.match(/[A-Za-z0-9]{2}/g).map(function (v) {
                return parseInt(v, 16)
            }).join(",");
            command.data = getID("env-delay").value + "," + hex1 + "," + hex2;
            break;
        default:
            command.data = getID("env-" + command.state).value;
    }
    let target = getID("env-target").value;
    if (target.startsWith("powermeter")) {
        if (command.state === "power") {
            mqtt.send(target, command.data, 2, false);
        }
    } else if (target.includes(" lights")) {
        if (target === "lab room lights" || target === "all lights") {
            mqtt.send("2/ledstrip/labroom/north", JSON.stringify(command), 2, false);
            mqtt.send("2/ledstrip/labroom/south", JSON.stringify(command), 2, false);
            mqtt.send("2/ledstrip/labroom/middle", JSON.stringify(command), 2, false);
        }
        if (target === "server room lights" || target === "all lights") {
            mqtt.send("2/ledstrip/serverroom", JSON.stringify(command), 2, false);
            mqtt.send("2/ledstrip/doorserverroom", JSON.stringify(command), 2, false);
        }
    } else {
        mqtt.send(target, JSON.stringify(command), 2, false);
    }
}

/**
 * En-/disables valid environment commands upon selection of topic
 * @param target
 */
function validateCommands(target) {
    let cmd = getID("env-command");
    cmd.disabled = false;
    switch (target.value) {
        case "0":
            cmd.disabled = true;
            cmd.value = 0;
            validateValues(cmd);
            break;
        case "powermeter/gyrophare1/switch":
        case "powermeter/gyrophare2/switch":
        case "powermeter/switch":
            for (let child of cmd.children) {
                child.disabled = child.value !== "power";
                if (child.value === "power") {
                    child.selected = true;
                }
            }
            cmd.value = "power";
            validateValues(cmd);
            break;
        default:
            for (let child of cmd.children) {
                child.disabled = false;
            }
    }
}

/**
 * En-/disables valid environment command values upon selection of command
 * @param cmd
 */
function validateValues(cmd) {
    getID("env-power").disabled = true;
    getID("env-pattern").disabled = true;
    getID("env-brightness").disabled = true;
    getID("env-adjust").disabled = true;
    getID("env-rgb").disabled = true;
    getID("env-rgb2").disabled = true;
    getID("env-delay").disabled = true;
    getID("env-button").disabled = false;
    switch (cmd.value) {
        case "brightnessAdjust":
        case "patternAdjust":
            getID("env-adjust").disabled = false;
            break;
        case "blink":
            getID("env-rgb").disabled = false;
            getID("env-rgb2").disabled = false;
            getID("env-delay").disabled = false;
            break;
        case "0":
            getID("env-button").disabled = true;
            break;
        default:
            getID("env-" + cmd.value).disabled = false;
    }
}

/**
 * This function adds a listener for the enter key to an input or textarea which then triggers a button
 * @param target The target input or textarea
 * @param button The button to trigger
 */
function addEnterEvent(target, button) {
    target.addEventListener("keyup", function (event) {
        if (event.keyCode === 13) {
            event.preventDefault();
            button.click();
        }
    })
}

/**
 * Triggers all functions started on load in parallel
 */
async function onLoad() {
    if (window.location.href.includes("?")) {
        changeTab(window.location.href.split("?")[1])
    }
    let promises = [];
    promises.push(mqttConnect());
    promises.push(onLoadAddEnterEvents());
    promises.push(onLoadTopicHelp());
    promises.push(onLoadTopicsSelect());
    promises.push(onLoadBustAudioCache());
    await Promise.all(promises);
}

/**
 * Adds all enter events for buttons
 * @returns {Promise<void>}
 */
async function onLoadAddEnterEvents() {
    addEnterEvent(getID("tts"), getID("tts-button"));
    addEnterEvent(getID("send-topic"), getID("send-button"));
    addEnterEvent(getID("send-message"), getID("send-button"));
}

/**
 * Bust the HTTP cache for audio streaming
 * @returns {Promise<void>}
 */
async function onLoadBustAudioCache() {
    let aud = document.querySelector('audio source');
    aud.src = encodeURI(aud.src + '?nocache=' + Math.random().toString(36));
    aud.parentElement.load();
    aud.parentElement.play();
}

/**
 * Read topics into textarea (add timestamp to defy caching)
 * @returns {Promise<void>}
 */
async function onLoadTopicHelp() {
    let client = new XMLHttpRequest();
    client.open('GET', 'MQTTTopics.md?v=' + Date.now().toString());
    client.onload = function () {
        if (client.status === 200) {
            getID("topics").innerHTML = window.markdownit().render(client.responseText);
        } else {
            console.log("Error " + client.status.toString() + " reading MQTTTopics.md");
        }
    };
    client.send();
}

/**
 * Add topic options to simple send
 * @returns {Promise<void>}
 */
async function onLoadTopicsSelect() {
    let topicList2 = typeof topicList === 'undefined' ? ["0/dummy"] : topicList;
    let selectTopic = getID("simple-topic");
    for (let topic of topicList2) {
        let option = document.createElement("option");
        option.text = topic;
        selectTopic.add(option);
    }
}

function displayGraph(data) {
    let cy = window.cy = cytoscape({
        container: document.getElementById('cytoscape-container'),
        style: [
            {
                selector: 'node',
                css: {
                    'content': 'data(name)',
                    "color": "#ffffff",
                    "font-family": "Verdana, Geneva, sans-serif",
                    'text-valign': 'bottom',
                    'text-halign': 'center',
                    "background-color": "#93a1a1"
                }
            },
            {
                selector: 'node[?highlight]',
                css: {
                    'font-weight': 'bold',
                    'font-size': '1.2em'
                }
            },
            {
                selector: 'node[status="FINISHED"]',
                css: {
                    'background-color': '#859900'
                }
            },
            {
                selector: 'node[status="ACTIVE"]',
                css: {
                    'background-color': '#cb4b16'
                }
            },
            {
                selector: 'node[status="SKIPPED"]',
                css: {
                    'background-color': '#000000'
                }
            },
            {
                selector: 'node[message][messageState]',
                css: {
                    'border-width': '5px',
                    'border-color': "#5f5faf",
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
            name: 'dagre',
            randomize: false,
            animate: false,
            nodeDimensionsIncludeLabels: true,
            rankDir: "LR",
        },
        // interaction options:
        zoom: 0.5,
        zoomingEnabled: true,
        userZoomingEnabled: true,
        panningEnabled: true,
        userPanningEnabled: true,
        boxSelectionEnabled: false,
        selectionType: 'single',
        autolock: false,
        autoungrabify: true,
        autounselectify: true,
        wheelSensitivity: 0.05,
    });
    cy.cxtmenu({
        menuRadius: 70,
        atMouse: true,
        selector: "node[name!='main'][^topic]",
        commands: [
            {
                fillColor: 'rgba(0, 0, 255, 0.75)',
                content: 'Skip',
                select: function (ele) {
                    mqtt.send("1/gameControl", "SKIP " + ele.id(), 2, false);
                },
                enabled: true
            }
        ],

    });
    cy.cxtmenu({
        menuRadius: 70,
        atMouse: true,
        selector: "node[topic]",
        commands: [
            {
                fillColor: 'rgba(0, 0, 255, 0.75)',
                content: 'Skip',
                select: function (ele) {
                    mqtt.send("1/gameControl", "SKIP " + ele.id(), 2, false);
                },
                enabled: true
            },
            {
                fillColor: 'rgba(0, 255, 0, 0.75)',
                content: 'On',
                select: function (ele) {
                    mqtt.send(ele.data("topic"), JSON.stringify({
                        method: "trigger",
                        "state": "on"
                    }), 2, false);
                },
                enabled: true
            },
            {
                fillColor: 'rgba(255, 0, 0, 0.75)',
                content: 'Off',
                select: function (ele) {
                    mqtt.send(ele.data("topic"), JSON.stringify({
                        method: "trigger",
                        "state": "off"
                    }), 2, false);
                },
                enabled: true
            }
        ],

    });

    /**
     * This part displays a tooltip for those nodes who have a message set
     */
    for (let popper of document.getElementsByClassName("popper")) {
        popper.remove();
    }
    for (let el of cy.elements('node[message]')) {
        let div = document.createElement('div');
        div.innerHTML = el.data("message");
        div.className = "popper " + el.data("messageState");
        div.id = btoa(el.data("id"));
        document.body.appendChild(div);
    }
    cy.on("mouseover", 'node[message]', function (evt) {
        getID(btoa(evt.target.data("id"))).style.display = "block";
    });
    cy.on("mouseout", 'node[message]', function (evt) {
        getID(btoa(evt.target.data("id"))).style.display = "none";

    });
}