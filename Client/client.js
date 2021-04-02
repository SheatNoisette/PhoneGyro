
// Proto very proto hmmm

/*
Protocol:
    absolute;alpha;beta;gamma

*/

var connected_to_server = false;
var server_ip = null;
var socket = null;
var command_sent = 0;
// This request the server a calibration
// 0 => None; 1 => Top left; 2 => Bottom Right
var request_calibration = 0;

const abs_class = document.getElementsByClassName("absolute")[0];
const alpha_class = document.getElementsByClassName("alpha")[0];
const beta_class = document.getElementsByClassName("beta")[0];
const gamma_class = document.getElementsByClassName("gamma")[0];
const sent_command_element = document.getElementsByClassName("command_sent")[0];
const cb = document.getElementById('print_vals');

var command_queue = [];

function build_command_gyro(absolute, alpha, beta, gamma, calibration) {
    var out = ""

    if (absolute)
        out += "1;";
    else
        out += "0;"

    out += alpha + ";";
    out += beta + ";";
    out += gamma + ";";
    out += calibration;

    return out;
}

function request_calibration_top() {
    request_calibration = 1;
}

function request_calibration_bottom() {
    request_calibration = 2;
}

/*
    Return true is success
*/
function check_connection(server_ip) {
    console.log("Checking websocket connection - Server: " + server_ip + "...");

    try {
        socket = new WebSocket("ws://" + server_ip);

        socket.onopen = function (openEvent) {
            console.log("WebSocket success: " + JSON.stringify(openEvent, null, 4));
            connected_to_server = true;
        }

        socket.onerror = function () {
            console.log("Error while opening websocket");
            connected_to_server = false;
        }

    } catch (exception) {
        console.error(exception);
        connected_to_server = false;
    }

    return connected_to_server;
}

function get_server() {
    var text_box_server = document.getElementsByName("ip_svr")[0].value
    var result_connection = document.getElementsByClassName("server_result")[0];

    console.log("ServerIP: " + text_box_server);

    // Set IP
    server_ip = text_box_server;

    if (check_connection(server_ip)) {
        result_connection.innerText = "Success";
        connected_to_server = true;
        console.log("Connected to server: " + server_ip);
    }
    else {
        result_connection.innerText = "ERROR";
        connected_to_server = false;
    }
}

function handleOrientation(event) {
    var absolute = event.absolute;
    var alpha = event.alpha;
    var beta = event.beta;
    var gamma = event.gamma;

    if (cb.checked) {
        abs_class.innerText = "ABS: " + absolute;
        alpha_class.innerText = "Alpha:" + alpha;
        beta_class.innerText = "Beta: " + beta;
        gamma_class.innerText = "Gamma: " + gamma;
    }

    if (connected_to_server) {
        command_sent += 1;
        sent_command_element.innerText = command_queue.length;
        command_queue.push(build_command_gyro(absolute, alpha, beta, gamma, request_calibration));
        socket.send(command_queue.pop());
        // Reset calibration
        request_calibration = 0;
    }
}

window.addEventListener("deviceorientation", handleOrientation, true);
