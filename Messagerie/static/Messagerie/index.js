const csrf_token = document.querySelector("#csrf_token").innerHTML;
const addrIP = "http://"+ location.host+"/Messagerie/";
let ws = new WebSocket("ws://" + location.host +"/ws/");

let replyTo = null;
let msgToEdit = null;
let userProfile = false;

ws.onopen = function (e){
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
     let fd = new FormData();
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
         }
     })
}

function fetchConvList(){
    let fd = new FormData();
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

function fetchMsg(first= 0) {
    let fd = new FormData();
    fd.append("type", 'fetchMsg');
    fd.append("nbFetch", "10");
    fd.append("first", first);
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
                let oldLatest = document.getElementById("msgUl").children[0]
                for(let i = 0; i < response['msgList'].length; i++){
                    JsonToMsg(response['msgList'][i]);
                }
                if (first !== 0) {
                    oldLatest.scrollIntoView();
                }else{
                    chatbox.scrollTop = chatbox.scrollHeight;
                }
            }
            catch(e){}
        }
    })
}

function JsonToMsg(msg, toAppend= false) {
    let userid = msg.userid;
    let username = msg.username;
    let convid = msg.convid;
    let msgid = msg.msgid;
    let text = msg.text;
    let files = msg.files;
    let date = msg.date;
    let reply = msg.reply;
    let edited = msg.Edited;
    genMsg(userid, username, convid, msgid, text, files, date, reply, edited, toAppend);
}

function JsonToConv(conv){
    let convid = conv.convid;
    let convname = conv.convname;
    genConv(convid, convname);
}

function genMsg(userid, username, convid, msgid, message, files, timestamp, reply, edited, toAppend){
    if (reply !== -1){
        askMsgByIdReply(reply, msgid);
    }
    let bottom = false
    if (chatbox.scrollHeight-chatbox.scrollTop < 700){
        bottom = true
    }
    let msgUl = document.getElementById("msgUl")
    let messageContainer ;
    if (!toAppend) {
        messageContainer = msgUl.insertBefore(document.createElement("li"), msgUl.children[0]);
    }else {
        messageContainer = msgUl.appendChild(document.createElement("li"));
    }
    messageContainer.id = "msgId"+msgid;
    messageContainer.className = "message-container";

    let messageHeader  = document.createElement("div");
    messageHeader.className = "message-header";
    messageContainer.appendChild(messageHeader);

    let messageInfo = document.createElement('span');
    messageHeader.appendChild(messageInfo);

    let usernameElement = document.createElement('span');
    usernameElement.classList.add('username');
    usernameElement.textContent = username;
    messageInfo.appendChild(usernameElement);

    const timestampElement = document.createElement('span');
    timestampElement.classList.add('timestamp');
    timestampElement.textContent = timestamp;
    messageInfo.appendChild(timestampElement);

    const messageButton = document.createElement("span");
    messageButton.classList.add('message-button');
    messageHeader.appendChild(messageButton);

    const messageBody = document.createElement('div');
    messageBody.classList.add('message-body');
    messageBody.textContent = message;
    messageContainer.appendChild(messageBody);

    const messageFiles = document.createElement('div');
    messageFiles.classList.add('message-files');
    messageContainer.appendChild(messageFiles);

    for (const file of files) {
        // Crée chaque fichier dans la liste
        const fileContainer = document.createElement('div');
        fileContainer.classList.add('file');
        messageFiles.appendChild(fileContainer);

        const fileImg = document.createElement('img');
        fileImg.src = file;
        fileImg.alt = file;
        fileContainer.appendChild(fileImg);
    }

    let messageFooter = document.createElement('div');
    messageFooter.classList.add('message-footer');
    let messageEdited = document.createElement('div');
    messageEdited.classList.add("message-edited");
    let messageReplied = document.createElement('div');
    messageReplied.classList.add("message-replied");
    if (edited){
        messageEdited.textContent = "(edited)";
    }
    messageFooter.appendChild(messageReplied);
    messageFooter.appendChild(messageEdited);
    messageContainer.appendChild(messageFooter);

    let btnDelete = messageButton.appendChild(document.createElement("button"));
    btnDelete.type = "submit";
    btnDelete.className = "btnMsgDelete";
    btnDelete.id = "btnMsgDelete" + msgid;
    btnDelete.value = msgid;
    btnDelete.textContent = "Delete";
    btnDelete.onclick = onClickMsgButton("deleteMsg", msgid);

    let btnEdit = messageButton.appendChild(document.createElement("button"));
    btnEdit.type = "submit";
    btnEdit.className = "btnMsgEdit";
    btnEdit.id = "btnMsgEdit" + msgid;
    btnEdit.value = msgid;
    btnEdit.textContent = "Edit";
    btnEdit.onclick = onClickMsgEdit(msgid);

    let btnReply = messageButton.appendChild(document.createElement("button"));
    btnReply.type = "submit";
    btnReply.className = "btnMsgReply";
    btnReply.id = "btnMsgReply" + msgid;
    btnReply.value = msgid;
    btnReply.textContent = "Reply";
    btnReply.onclick = onClickReplyButton(msgid);
    if (toAppend){
        chatbox.scrollTop = chatbox.scrollHeight;
    }
}
function onClickMsgEdit(msgid){
    return function() {
        let toSend = document.getElementById("toSend");
        let childList = document.getElementById("msgId"+msgid).children
        for(let i = 0 ; i < childList.length; i++){
            if (childList[i].className === "message-body"){
                toSend.textContent = childList[i].textContent;
                toSend.focus();
                let editMode = document.createElement("button");
                editMode.textContent = "Editing....";
                editMode.id = "msgEditMode";
                let msgSenderContainer = document.getElementById("msgSender-container");
                msgSenderContainer.appendChild(editMode);
                editMode.onclick = cancelEdit;
                msgToEdit = msgid;
                break;
            }
        }
    }
}

function cancelEdit(){
    document.getElementById("msgEditMode").remove();
    msgToEdit = null;
}

function onClickReplyButton(msgid){
    return function() {
        replyTo = msgid;
        document.getElementById("toSend").focus();
    }
}

convList = document.getElementById("convList");

function genConv(convid, convname){
    let btnS = "btnConvSelect"+convid;
    let btnD = "btnConvDelete"+convid;
    let li = convList.appendChild(document.createElement('li'));
    li.className = 'convLi';
    li.id = "idConv"+convid;
    li.appendChild(document.createElement('label')).textContent = convname + " ";
    let buttonSelect = li.appendChild(document.createElement('button'));
    buttonSelect.id = btnS;
    buttonSelect.className = 'btnConvSelect';
    buttonSelect.type = 'submit';
    buttonSelect.value = convid;
    buttonSelect.textContent = 'Select';
    buttonSelect.onclick = onClickConvButton("selectConv", convid);

    let buttonDelete = li.appendChild(document.createElement('button'));
    buttonDelete.id = btnD;
    buttonDelete.className = 'btnConvDelete';
    buttonDelete.type = 'submit';
    buttonDelete.value = convid;
    buttonDelete.textContent = 'Leave';
    buttonDelete.onclick = onClickConvButton("deleteConv", convid);

    li.appendChild(document.createElement('br'));
}

function onClickConvButton(type, convid, userid = "-1"){
    return function (){
        let fd = new FormData();
        fd.append("type", type);
        fd.append("convid", convid);
        fd.append("userid", userid);
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
                //ws.send(JSON.stringify(response));
            }
        })
    }
}

function onClickMsgButton(type, msgid){
    return function () {
        let fd = new FormData();
        fd.append("type", type);
        fd.append("msgid", msgid);
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
                //ws.send(JSON.stringify(response));
            }
        })
    }
}

document.getElementById("createConvButton").onclick = function (){
    let createConvInput = document.getElementById("createConvInput").textContent;
    let fd = new FormData();
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
            //ws.send(JSON.stringify(response));
        }
    })
}

document.getElementById("toSend").focus();
document.getElementById("messageSubmit").onclick = function (e){
    let messageTxt = document.querySelector("#toSend").textContent;
    let messageFiles = document.querySelector("#id_file").files;
    let fd = new FormData();
    fd.append("type", "sendMessage")
    fd.append("text", messageTxt);
    fd.append("Reply", replyTo);
    fd.append("Edited", msgToEdit);
    replyTo = null;
    if (msgToEdit !== null) {
        document.getElementById("msgEditMode").remove();
        let childList = document.getElementById("msgId"+msgToEdit).children;
        let element = null;
        for(let i = 0; i < childList.length; i++){
            if (childList[i].classList.contains("message-body")){
                element = childList[i].textContent;
                break;
            }
        }
        try {
            if (element === document.getElementById("toSend").textContent) {
                msgToEdit = null;
                return;
            }
        }
        catch{}
        msgToEdit = null;
    }
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
            //ws.send(JSON.stringify(response));
        }
    })
}

document.getElementById("addToConv").onclick = function (){
    let addToConvInput = document.getElementById("userToAdd").textContent;
    let fd = new FormData();
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
            if (response.response) {
                //ws.send(JSON.stringify(response));
            }
        }
    })
}

function genUser(username, userid) {
    let userList = document.getElementById("userList");
    let li = userList.appendChild(document.createElement('li'));
    li.className = "liUser";
    li.id = "userid"+userid;
    let label = li.appendChild(document.createElement('label'));
    label.innerHTML = username;
    let btnKick = li.appendChild(document.createElement('button'));
    btnKick.type = "submit";
    btnKick.value = userid;
    btnKick.innerHTML = "Kick";
    btnKick.onclick = onClickConvButton("deleteConv", -1, userid);
    let btnban = li.appendChild(document.createElement('button'));
    btnban.type = "submit";
    btnban.value = userid;
    btnban.innerHTML = "Ban";
    let btnWhisp = li.appendChild(document.createElement('button'));
    btnWhisp.type = "submit";
    btnWhisp.value = userid;
    btnWhisp.textContent = "Whisper";
}

function JsonToUser(msg){
    let username = msg.username;
    let userid = msg.userid;
    let email = msg.email;
    let PP = msg.PP;
    genUser(username, userid);
}

function askUser(convId){
    let fd = new FormData();
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
    let fd = new FormData();
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
    let fd = new FormData();
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

chatbox.onscroll = function (){
    if (chatbox.scrollTop === 0){
        fetchMsg(document.getElementById("msgUl").children.length);
    }
}

function askMsgById(msgid){
    let fd = new FormData();
    fd.append("type", "askMsgById");
    fd.append("msgid", msgid);
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
            JsonToMsg(response, true);
        }
    })
}

function askMsgByIdReply(reply, msgid){
    let fd = new FormData();
    fd.append("type", "askMsgById");
    fd.append("msgid", reply);
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
            let childList = document.getElementById("msgId"+msgid).children;
            for(let i = 0; i < childList.length; i++){
                if (childList[i].classList.contains("message-footer")) {
                    for (let j = 0; j < childList[i].children.length; j++) {
                        if (childList[i].children[j].classList.contains("message-replied")) {
                            if (response.text.length > 50){
                                response.text = response.text.substring(0, 50)+ "...";
                            }else{
                                response.text = response.text.substring(0, 50);
                            }
                            childList[i].children[j].textContent = "(@" + response.username + " : " + response.text + ")";
                        }
                    }
                }
            }
        }
    })
}

function askMsgByIdEdit(msgid){
    let fd = new FormData();
    fd.append("type", "askMsgById");
    fd.append("msgid", msgid);
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
            editMsgById(response.msgid, response.text)
        }
    })
}

function editMsgById(msgid, newText){
    let childList = document.getElementById("msgId"+msgid).children
    for(let i = 0; i < childList.length; i++){
        if (childList[i].className === "message-body"){
            childList[i].textContent = newText;
            let messageFooterChildren = childList[childList.length-1].children;
            for(let j = 0; j < messageFooterChildren.length; j++){
                if(messageFooterChildren[j].classList.contains("message-edited")){
                    messageFooterChildren[j].textContent = "(edited)";
                    break;
                }
            }
            break;
        }
    }
}

buildUserProfile();

function getUser(){
    let fd = new FormData();
    fd.append("type", "getUser");
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
            let img = document.getElementById("user-img");
            let imgEdit = document.getElementById("user-img-edit")
            let username = document.getElementById("user-username");
            img.src = response.PP;
            imgEdit.src = response.PP;
            username.textContent = response.username;
        }
    })
}

function userOnClick(){
    let hiddenDiv = document.getElementById("user-hidden-div");
    if (!userProfile) {
        hiddenDiv.style.display = 'inline-block';
        userProfile = true;
    }else{
        hiddenDiv.style.display = 'none';
        userProfile = false;
    }
}
function buildUserProfile(){
    let background = document.getElementById("sub-container-left-arr");
    let block = document.createElement("div");
    block.id = "user-profile-container";
    let info = document.createElement("div");
    info.id = "user-profile-button";
    let img = document.createElement("img");
    img.id = "user-img";
    let username = document.createElement("p");
    username.id = "user-username";
    block.style.position = "fixed";
    block.style.bottom = "1em";
    block.style.left = "1em";

    info.appendChild(img);
    info.appendChild(username);
    block.appendChild(info);
    background.appendChild(block);

    let hiddenDiv = document.createElement("div");
    hiddenDiv.id = "user-hidden-div";
    hiddenDiv.style.display = 'none';
    hiddenDiv.style.height = "50vh";
    hiddenDiv.style.width = "30vw";
    hiddenDiv.style.background = "#292b2f";
    hiddenDiv.style.position = "fixed";
    hiddenDiv.style.bottom = "2em";
    hiddenDiv.style.left = "2em";
    hiddenDiv.style.borderRadius = "1em";
    hiddenDiv.style.boxShadow = "0em 0em 1em 1em rgba(0,0,0,0.05)";

    let topDiv = document.createElement("div");
    topDiv.style.height = "20%";
    topDiv.style.borderTopLeftRadius = "1em";
    topDiv.style.borderTopRightRadius = "1em";
    topDiv.style.background = "rgba(0,38,70,0.64)";

    let img2 = document.createElement("img");
    img2.id = "user-img-edit";
    img2.style.borderRadius = "50%";
    img2.style.width = "5em";
    img2.style.height = "5em";
    img2.style.margin = "1em";
    img2.style.maxWidth = "5em";
    img2.style.maxHeight = "5em";

    let form = document.createElement("div");

    let pseudo = document.createElement("div");
    pseudo.contentEditable = "true";
    pseudo.classList.add("user-input");
    pseudo.ariaLabel = "Username";
    /*
    let email = document.createElement("div");
    email.contentEditable = "true";
    email.classList.add("user-input");
    email.textContent = "email";
    email.ariaLabel = "Email";
    */

    let password = document.createElement("div");
    password.contentEditable = "true";
    password.classList.add("user-input");
    password.ariaLabel = "Password";

    let apply = document.createElement("button");
    apply.textContent = "Apply";

    apply.onclick = function (){
        for (let i = 0; i < form.children.length; i++) {
            if (form.children[i].textContent !== "") {
                let fd = new FormData();
                fd.append("type", "set" + form.children[i].ariaLabel);
                fd.append(form.children[i].ariaLabel, form.children[i].textContent);
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
                    }
                })
                form.children[i].textContent = "";
                hiddenDiv.style.display = "none";
            }
        }
    }
    form.appendChild(pseudo);
    form.appendChild(password);



    hiddenDiv.appendChild(topDiv);
    hiddenDiv.appendChild(img2);
    hiddenDiv.appendChild(form);
    hiddenDiv.appendChild(apply);

    block.appendChild(hiddenDiv);

    getUser();
    info.onclick = userOnClick;
}

ws.onmessage = function (msg){
    msg = JSON.parse(msg.data);
    if (msg.type === "sendMessage"){
        askMsgById(msg.msgid);
    }else if (msg.type === "selectConv"){
        document.getElementById("msgUl").innerHTML = "";
        document.getElementById("userList").innerHTML = "";
        document.getElementById("convName").textContent = msg.convname;
        askUser(msg.convid);
        fetchMsg(0);
    }
    else if (msg.type === "userToKick"){
        document.getElementById("userList").removeChild(document.getElementById("userid"+msg.userid));
    }else if (msg.type === "kickFromConv"){
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
    }else if (msg.type === "msgToDelete"){
        document.getElementById("msgUl").removeChild(document.getElementById("msgId"+msg.msgid));
    }else if (msg.type === "editMsg"){
        askMsgByIdEdit(msg.msgid);
    }
}


