let mqtt;
let mqttControl;
let reconnectTimeout = 2000;
let host = "10.0.0.2";
let port = 9001;


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
    let op = document.getElementById("output");
    op.value += "Topic " + msg.destinationName + "; time ";
    if (!msg.payloadString.match(/\d{10}: .*/i)) op.value += ~~(Date.now() / 1000) + " ";
    op.value += msg.payloadString + "\n";
    op.scrollTop = op.scrollHeight;
}

function onMessageArrivedControl(msg) {
    try {
        let obj = JSON.parse(msg.payloadString);
        if (obj.method.toLowerCase() === "status") {
            let dst = msg.destinationName;
            let dst_b64 = btoa(dst);

            // Create the status box if it doesn't exist yet
            if (document.getElementById(dst_b64) == null) {
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
                let cont = document.getElementById("c" + dst.charAt(0));
                cont.appendChild(ele);
            }

            // Change the state of the status box
            document.getElementById(dst_b64 + "_state").value = obj.state.toLowerCase;
            document.getElementById(dst_b64 + "_data").value = obj.data || "";
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
    document.getElementById(button.parentElement.id === "soff" ? "son" : "soff").appendChild(button);
}

function toggleAll(from) {
    while (document.getElementById(from).firstElementChild !== null) {
        document.getElementById(from).firstElementChild.click();
    }
}

function send() {
    if (document.getElementById("send_topic").value === "") {
        alert("Topic is required");
        return;
    }
    mqtt.publish(document.getElementById("send_topic").value, document.getElementById("send_message").value, 0, document.getElementById("send_retain").checked);
    document.getElementById("send_topic").value = "";
    document.getElementById("send_message").value = "";
    document.getElementById("send_retain").checked = false;
}

function toggleHelp() {
    if(document.getElementById("help").style.display === "none") {
        document.getElementById("help").style.display = "inline-block";
    } else {
        document.getElementById("help").style.display = "none";
    }
}

function changeCamera() {
    let xhr = new XMLHttpRequest();
    let number = document.getElementById("camera-selection").value;

    xhr.onload = function () {
        console.log(this.statusText.concat(" (", this.status.toString(), ")"));
    };

    xhr.open("GET", "http://localhost:9000/".concat(number));
    xhr.send();
}

function changeState(dst_b64) {
    let dst = atob(dst_b64);
    let state = document.getElementById(dst_b64 + "_state").value;
    let json_obj = JSON.stringify({method: "trigger", state: "on", data: state});
    mqttControl.send(dst, json_obj, 2);
}

function changeTab(target) {
    for (name of ["control", "cameras", "cameras-fallback", "mosquitto"]) {
        if (name !== target) {
            document.getElementById(name).style.display = "none";
            document.getElementById("b-" + name).parentElement.className = "navitem";
        } else {
            document.getElementById(name).style.display = "block";
            document.getElementById("b-" + name).parentElement.className = "navitem selected";
        }
    }
}