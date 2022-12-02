const user_id = JSON.parse(document.getElementById('user_id').textContent);
const csrf_token = document.querySelector("#csrf_token").innerHTML;
const addrIP = "http://127.0.0.1:8000/Messagerie/";

const ws = new WebSocket("ws://127.0.0.1:8000/ws/");
ws.onclose = function (e){
    console.log("disconnected");
}
document.querySelector("#toSend").focus();
document.querySelector("#messageSubmit").onclick = function (e){
    let messageTxt = document.querySelector("#toSend").innerHTML;
    let messageFiles = document.querySelector("#id_file").files;
    let xhr = new XMLHttpRequest();
    xhr.open("POST", addrIP, true);
    xhr.setRequestHeader('X-CSRFToken', csrf_token, );
    xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    xhr.setRequestHeader("Content-Disposition", 'attachment')
    let formdata = new FormData();
    formdata.append("csrfmiddlewaretoken", csrf_token);
    formdata.append("text", messageTxt);
    formdata.append("file", messageFiles);
    xhr.send(formdata);
    //ws.send(JSON.stringify({msg: messageTxt, user_id: user_id}));
}


