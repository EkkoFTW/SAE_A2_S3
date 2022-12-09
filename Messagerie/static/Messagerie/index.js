const user_id = JSON.parse(document.getElementById('user_id').textContent);
const csrf_token = document.querySelector("#csrf_token").innerHTML;
const addrIP = "http://127.0.0.1:8000/Messagerie/";
let ws = new WebSocket("ws://127.0.0.1:8000/ws/");

let actualConv = null;

ws.onopen = function (e){
    fetchMsg(true);
    fetchConvList();
    selectConv("Begin");
}

ws.onclose = function (e) {
    console.log("disconnected");
}

let chatbox = document.getElementById("msgList");

function addFiles(fd, messageFiles){
    for (let i = 0; i < messageFiles.length; i++){
        fd.append('files', messageFiles[i]);
    }
}

function selectConv(convid){
     fd = new FormData();
     fd.append("type", "selectConv");
     fd.append("convid", convid);
     $.ajax({
         type: "POST",
         url: addrIP + "handler",
         processData: false,
         contentType: false,
         data: fd,
         cache: false,
         async: true,
         headers: {
             'X-CSRFToken': csrf_token,
         },
         success: function (response) {
             ws.send(JSON.stringify(response));
         }
     })
}

function fetchConvList(){
    fd = new FormData();
    fd.append("type", 'fetchConv');
    $.ajax({
        type: "POST",
        url: addrIP+"handler",
        processData: false,
        contentType: false,
        data: fd,
        cache: false,
        async: true,
        headers : {
            'X-CSRFToken' : csrf_token,
        },
        success: function (response){
            try {
                for(let i = 0; i < response['convList'].length; i++){
                    JsonToConv(response['convList'][i])
                }
            }
            catch(e){}
        }
    })
}

function fetchMsg(first=false) {
    fd = new FormData();
    fd.append("type", 'fetchMsg');
    fd.append("nbFetch", "10");
    $.ajax({
        type: "POST",
        url: addrIP+"handler",
        processData: false,
        contentType: false,
        data: fd,
        cache: false,
        async: true,
        headers : {
            'X-CSRFToken' : csrf_token,
        },
        success: function (response){
            try {
                for(let i = 0; i < response['msgList'].length; i++){
                    JsonToMsg(response['msgList'][i])
                }
                if (true){
                    chatbox.scrollTop = chatbox.scrollHeight;
                }
            }
            catch(e){}
        }
    })
}

function JsonToMsg(msg){
    let userid = msg.userid;
    let username = msg.username
    let convid = msg.convid;
    let msgid = msg.msgid;
    let text = msg.text;
    let files = msg.files;
    let date = msg.date;
    genMsg(userid, username, convid, msgid,text, files, date);
}

function JsonToConv(conv){
    let convid = conv.convid;
    let convname = conv.convname;
    genConv(convid, convname);
}


function genMsg(userid, username, convid, msgid,text, files, date){
    let listFile = "";
    for (let i = 0; i < files.length; i++){
        listFile += "<img class='aImg' src="+files[i]+" alt="+files[i]+">";
    }
    let bottom = false
    if (chatbox.scrollHeight-chatbox.scrollTop < 700){
        bottom = true
    }
    document.querySelector("#msgUl").innerHTML +=
        "<li id='msgId'><p>"+date+"</p>"+
            "<a href="+username+">username</a>"+
            "<p> "+text+" </p>"+
            listFile +
            "<button type='submit' name='deleteMessage' value="+msgid+"> Delete</button>"+
            "<button type='submit' name='editMessage' value="+msgid+"> Edit</button>"+
            "<button type='submit' name='replyMessage' value="+msgid+"> Reply</button>"+
        "</li>"+
        "<br>";
    if (bottom === true){
        chatbox.scrollTop = chatbox.scrollHeight;
    }
}

convList = document.getElementById("convList");

function genConv(convid, convname){
    btnS = "btnConvSelect"+convid;
    btnD = "btnConvDelete"+convid;
    li = convList.appendChild(document.createElement('li'));
    li.className = 'convLi';
    li.id = "idConv"+convid;
    li.appendChild(document.createElement('label')).innerHTML = convname;
    buttonSelect = li.appendChild(document.createElement('button'));
    buttonSelect.id = btnS;
    buttonSelect.className = 'btnConvSelect';
    buttonSelect.type = 'submit';
    buttonSelect.value = convid;
    buttonSelect.innerHTML = 'Select';
    buttonSelect.onclick = onClickConvButton("selectConv", convid);

    buttonDelete = li.appendChild(document.createElement('button'));
    buttonDelete.id = btnD;
    buttonDelete.className = 'btnConvDelete';
    buttonDelete.type = 'submit';
    buttonDelete.value = convid;
    buttonDelete.innerHTML = 'Leave';
    buttonDelete.onclick = onClickConvButton("deleteConv", convid);

    li.appendChild(document.createElement('br'));
}

function onClickConvButton(type, convid){
    return function (){
        fd = new FormData();
        fd.append("type", type);
        fd.append("convid", convid);
        $.ajax({
            type: "POST",
            url: addrIP + "handler",
            processData: false,
            contentType: false,
            data: fd,
            cache: false,
            async: true,
            headers: {
                'X-CSRFToken': csrf_token,
            },
            success: function (response) {
                ws.send(JSON.stringify(response));
            }
        })
    }
}

document.getElementById("createConvButton").onclick = function (){
    let createConvInput = document.getElementById("createConvInput").innerHTML;
    fd = new FormData();
    fd.append("type", "createConv")
    fd.append("convname", createConvInput);
    $.ajax({
        type: "POST",
        url: addrIP+"handler",
        processData: false,
        contentType: false,
        data: fd,
        cache: false,
        async: true,
        headers : {
            'X-CSRFToken' : csrf_token,
        },
        success: function (response){
            ws.send(JSON.stringify(response));
        }
    })
}

document.getElementById("toSend").focus();
document.getElementById("messageSubmit").onclick = function (e){
    let messageTxt = document.querySelector("#toSend").innerHTML;
    let messageFiles = document.querySelector("#id_file").files;
    fd = new FormData();
    fd.append("type", "sendMessage")
    fd.append("text", messageTxt);
    addFiles(fd, messageFiles);
    $.ajax({
        type: "POST",
        url: addrIP+"handler",
        processData: false,
        contentType: false,
        data: fd,
        cache: false,
        async: true,
        headers : {
            'X-CSRFToken' : csrf_token,
        },
        success: function (response){
            ws.send(JSON.stringify(response));
        }
    })
}

document.getElementById("addToConv").onclick = function (){
    let addToConvInput = document.getElementById("userToAdd").innerHTML;
    fd = new FormData();
    fd.append("type", "addUserToConv");
    fd.append("email", addToConvInput);
    $.ajax({
        type: "POST",
        url: addrIP+"handler",
        processData: false,
        contentType: false,
        data: fd,
        cache: false,
        async: true,
        headers : {
            'X-CSRFToken' : csrf_token,
        },
        success: function (response){
            ws.send(JSON.stringify(response));
        }
    })
}

function genUser(username, userid) {
    let userList = document.getElementById("userList");
    let li = userList.appendChild(document.createElement('li'));
    li.className = "liUser";
    let label = userList.appendChild(document.createElement('label'));
    label.innerHTML = username;
    let btnKick = userList.appendChild(document.createElement('button'));
    btnKick.type = "submit";
    btnKick.value = userid;
    btnKick.innerHTML = "Kick";
    let btnban = userList.appendChild(document.createElement('button'));
    btnban.type = "submit";
    btnban.value = userid;
    btnban.innerHTML = "Ban";
    let btnWhisp = userList.appendChild(document.createElement('button'));
    btnWhisp.type = "submit";
    btnWhisp.value = userid;
    btnWhisp.innerHTML = "Whisper";
}

function JsonToUser(msg){
    username = msg.username;
    userid = msg.userid;
    email = msg.email;
    PP = msg.PP;
    genUser(username, userid);
}

function askUser(convId){
    fd = new FormData();
    fd.append("type", "askUser");
    fd.append("convid", convId);
    $.ajax({
        type: "POST",
        url: addrIP+"handler",
        processData: false,
        contentType: false,
        data: fd,
        cache: false,
        async: true,
        headers : {
            'X-CSRFToken' : csrf_token,
        },
        success: function (response) {
            for(let i = 0 ; i < response['userList'].length; i++){
                JsonToUser(response['userList'][i]);
            }
        }
    })
}

function askUserById(userid){
    fd = new FormData();
    fd.append("type", "askUserById");
    fd.append("userid", userid);
    $.ajax({
        type: "POST",
        url: addrIP+"handler",
        processData: false,
        contentType: false,
        data: fd,
        cache: false,
        async: true,
        headers : {
            'X-CSRFToken' : csrf_token,
        },
        success: function (response) {
            JsonToUser(response);
        }
    })
}

function askConvById(convid){
    fd = new FormData();
    fd.append("type", "askConvById");
    fd.append("convid", convid);
    $.ajax({
        type: "POST",
        url: addrIP+"handler",
        processData: false,
        contentType: false,
        data: fd,
        cache: false,
        async: true,
        headers : {
            'X-CSRFToken' : csrf_token,
        },
        success: function (response) {
            JsonToConv(response);
        }
    })
}

ws.onmessage = function (msg){
    msg = JSON.parse(msg.data);
    if (msg.type === "sendMessage"){
        JsonToMsg(msg);
    }else if (msg.type === "selectConv"){
        document.getElementById("msgUl").innerHTML = "";
        document.getElementById("convName").innerHTML = msg.convname;
        document.getElementById("userList").innerHTML = "";
        askUser(msg.convid);
        fetchMsg(true);
    }
    else if (msg.type === "deleteConv"){
        document.getElementById("convList").removeChild(document.getElementById("idConv"+msg.convid));
        selectConv("Begin");
    }
    else if (msg.type === "createConv"){
        selectConv(msg.convid);
        JsonToConv(msg);
    }else if (msg.type === "add_usertoconv"){
        askUserById(msg.userid);
    }else if (msg.type === "got_addedtoconv"){
        askConvById(msg.convid);
    }
}
