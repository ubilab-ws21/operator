let mqtt;
let mqttControl;
let reconnectTimeout = 2000;
let host = "10.0.0.2";
let port = 9001;

function getID(id) {
    return document.getElementById(id);
}

function onFailure(message) {
    console.log("Connection attempt for debug failed");
    console.log(message);
    setTimeout(MQTTconnect, reconnectTimeout);
}

function onFailureControl(message) {
    console.log("Connection attempt for control failed");
    console.log(message);
    setTimeout(MQTTconnectControl, reconnectTimeout);
}

function onConnect() {
    console.log("Connected debug");
}

function onConnectControl() {
    console.log("Connected control");
    for (let i = 1; i < 9; i++) {
        mqttControl.subscribe(i.toString() + "/#");
    }
}

function onMessageArrived(msg) {
    let op = getID("output");
    op.value += "Topic " + msg.destinationName + "; time ";
    if (!msg.payloadString.match(/\d{10}: .*/i)) op.value += ~~(Date.now() / 1000) + " ";
    op.value += msg.payloadString + "\n";
    op.scrollTop = op.scrollHeight;
}

function onMessageArrivedControl(msg) {
    if (msg.destinationName === "1/gameTime") {
        getID("time").innerText = msg.payloadString;
    } else if (msg.destinationName === "1/gameControl") {
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
    try {
        let obj = JSON.parse(msg.payloadString);
        if (obj.method.toLowerCase() === "status") {
            let dst = msg.destinationName;
            let dst_b64 = btoa(dst);

            // Create the status box if it doesn't exist yet
            if (getID(dst_b64) == null) {
                // Create dropdown options
                let opt1 = document.createElement("option");
                opt1.innerText = "inactive";
                opt1.value = "inactive";
                let opt2 = document.createElement("option");
                opt2.innerText = "active";
                opt2.value = "active";
                let opt3 = document.createElement("option");
                opt3.innerText = "solved";
                opt3.value = "solved";
                let opt4 = document.createElement("option");
                opt4.innerText = "failed";
                opt4.value = "failed";
                // Create dropdown field and append options
                let select = document.createElement("select");
                select.id = dst_b64 + "_state";
                select.appendChild(opt1);
                select.appendChild(opt2);
                select.appendChild(opt3);
                select.appendChild(opt4);
                // Create data field
                let data = document.createElement("input");
                data.type = "text";
                data.id = dst_b64 + "_data";
                data.readOnly = true;
                // Create button
                let button = document.createElement("button");
                button.innerText = "Change";
                button.type = "button";
                button.setAttribute("onclick", "changeState('" + dst_b64 + "');");
                // Create form and append fields
                let form = document.createElement("form");
                form.appendChild(select);
                form.appendChild(document.createElement("br"));
                form.appendChild(data);
                form.appendChild(document.createElement("br"));
                form.appendChild(button);
                // Create title/topic name
                let header = document.createElement("b");
                header.innerText = dst;
                // Create container and append elements
                let ele = document.createElement("div");
                ele.id = dst_b64;
                ele.className = "control";
                ele.appendChild(header);
                ele.appendChild(form);
                // Select group container and append single container
                let cont = getID("c" + dst.charAt(0));
                cont.appendChild(ele);
            }

            // Change the state of the status box
            getID(dst_b64 + "_state").value = obj.state.toLowerCase;
            getID(dst_b64 + "_data").value = obj.data || "";
        }
    } catch {
    }
}

function MQTTconnect() {
    console.log("Connecting debug to " + host + ":" + port + "...");
    mqtt = new Paho.Client(host, port, "", "ws-client-d" + ~~(Date.now() / 1000));
    mqtt.onMessageArrived = onMessageArrived;
    mqtt.connect({timeout: 3, onSuccess: onConnect, onFailure: onFailure});
}

function MQTTconnectControl() {
    console.log("Connecting control to " + host + ":" + port + "...");
    mqttControl = new Paho.Client(host, port, "", "ws-client-c" + ~~(Date.now() / 1000));
    mqttControl.onMessageArrived = onMessageArrivedControl;
    mqttControl.connect({timeout: 3, onSuccess: onConnectControl, onFailure: onFailureControl});
}

function toggle(topic, button) {
    if (button.parentElement.id === "soff") {
        mqtt.subscribe(topic + "/#");
    } else {
        mqtt.unsubscribe(topic + "/#");
    }
    getID(button.parentElement.id === "soff" ? "son" : "soff").appendChild(button);
}

function toggleAll(from) {
    while (getID(from).firstElementChild !== null) {
        getID(from).firstElementChild.click();
    }
}

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

function toggleHelp(n) {
    let id = n === 1 ? "help" : "help2";
    if (getID(id).style.display === "none") {
        getID(id).style.display = "inline-block";
    } else {
        getID(id).style.display = "none";
    }
}

function changeCamera() {
    let xhr = new XMLHttpRequest();
    let number = getID("camera-selection").value;

    xhr.onload = function () {
        console.log(this.statusText.concat(" (", this.status.toString(), ")"));
    };

    xhr.open("GET", "http://localhost:9000/".concat(number));
    xhr.send();
}

function changeState(dst_b64) {
    let dst = atob(dst_b64);
    let state = getID(dst_b64 + "_state").value;
    let json_obj = JSON.stringify({method: "trigger", state: "on", data: state});
    mqttControl.send(dst, json_obj, 2);
}

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

function command(content) {
    mqttControl.send("1/gameControl", content, 2, true);
}

function envSet() {
    mqttControl.send(getID("env-target").value, getID("env-command").value + getID("env-number1").value);
}

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