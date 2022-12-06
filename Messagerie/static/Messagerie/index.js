const user_id = JSON.parse(document.getElementById('user_id').textContent);
const csrf_token = document.querySelector("#csrf_token").innerHTML;
const addrIP = "http://127.0.0.1:8000/Messagerie/";
const ws = new WebSocket("ws://127.0.0.1:8000/ws/");

ws.onopen = function (e){
    //fetchMsg();
}

ws.onclose = function (e){
    console.log("disconnected");
}

document.querySelector("#msgList").innerHTML = "<ul id='msgUl'></ul>";


function addFiles(fd, messageFiles){
    for (let i = 0; i < messageFiles.length; i++){
        fd.append('files', messageFiles[i]);
    }
}

function fetchMsg() {
    fd = new FormData();
    fd.append("type", 'fetch');
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
                    JsonToMsg(JSON.stringify(response['msgList'][i]))
                }

            }
            catch(e){}
        }
    })
}

function JsonToMsg(msg){
    obj = JSON.parse(msg);
    let userid = obj.userid;
    let username = obj.username
    let convid = obj.convid;
    let msgid = obj.msgid;
    let text = obj.text;
    let files = obj.files;
    let date = obj.date;
    genMsg(userid, username, convid, msgid,text, files, date);
}


function genMsg(userid, username, convid, msgid,text, files, date){
    let listFile = "";
    for (let i = 0; i < files.length; i++){
        listFile += "<img class='aImg' src="+files[i]+" alt="+files[i]+">";
    }
    document.querySelector("#msgUl").innerHTML +=
        "<li><p>"+date+"</p>"+
        "<form method='post'>"+
            "<a href="+username+">username</a>"+
            "<p> "+text+" </p>"+
            listFile +
                    "<button type='submit' name='deleteMessage' value="+msgid+"> Delete</button>"+
                "<button type='submit' name='editMessage' value="+msgid+"> Edit</button>"+
                "<button type='submit' name='replyMessage' value="+msgid+"> Reply</button>"+
        "</form>"+
        "<br>";
}

document.querySelector("#toSend").focus();
document.querySelector("#messageSubmit").onclick = function (e){
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
            //JsonToMsg(JSON.stringify(response));
        }
    })

    ws.onmessage = function (msg){
        console.log(msg.data);
        JsonToMsg(msg.data);
    }

}


