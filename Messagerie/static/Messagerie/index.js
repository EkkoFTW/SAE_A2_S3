const user_id = JSON.parse(document.getElementById('user_id').textContent);
const csrf_token = document.querySelector("#csrf_token").innerHTML;
const addrIP = "http://127.0.0.1:8000/Messagerie/";
let ws = new WebSocket("ws://127.0.0.1:8000/ws/");

let messageMode = true;
let shift_pressed = false;

ws.onopen = function (e){
    fetchConvList();
    selectConv("Begin");
    let toFiles = document.getElementById("FileMessage");
    toFiles.onclick = OnClickLoadFiles();
}

ws.onclose = function (e) {
    console.log("disconnected");
}

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
             ws.send(JSON.stringify(response));
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
                    JsonToMsg(response['msgList'][i])
                }
                if (first !== 0) {
                    oldLatest.scrollIntoView();
                }else{
                    let chatbox = document.getElementById("msgList");
                    chatbox.scrollTop = chatbox.scrollHeight;
                }
            }
            catch(e){}
        }
    })
}

function JsonToMsg(msg, toAppend= false){
    let userid = msg.userid;
    let username = msg.username
    let convid = msg.convid;
    let msgid = msg.msgid;
    let text = msg.text;
    let files = msg.files;
    let date = msg.date;
    genMsg(userid, username, convid, msgid,text, files, date, toAppend);
}

function JsonToConv(conv){
    let convid = conv.convid;
    let convname = conv.convname;
    genConv(convid, convname);
}


function genMsg(userid, username, convid, msgid,text, files, date, toAppend){
    let bottom = false
    let chatbox = document.getElementById("msgList");
    if (chatbox.scrollHeight-chatbox.scrollTop < 700){
        bottom = true
    }
    let msgUl = document.getElementById("msgUl")
    let li;
    if (!toAppend) {
        li = msgUl.insertBefore(document.createElement("li"), msgUl.children[0]);
    }else {
        li = msgUl.appendChild(document.createElement("li"));
    }
    li.id = "msgId"+msgid
    li.appendChild(document.createElement("p")).innerHTML = date;
    let user = li.appendChild(document.createElement("a"));
    user.innerHTML = username;
    li.appendChild(document.createElement("p")).innerHTML = text;
    let file;
    for (let i = 0; i < files.length; i++) {
        file = li.appendChild(document.createElement("img"));
        file.className = "aImg";
        file.src = files[i];
        file.alt = files[i];
    }
    let btnDelete = li.appendChild(document.createElement("button"));
    btnDelete.type = "submit";
    btnDelete.className = "btnMsgDelete";
    btnDelete.id = "btnMsgDelete" + msgid;
    btnDelete.value = msgid;
    btnDelete.innerHTML = "Delete";
    let btnEdit = li.appendChild(document.createElement("button"));
    btnEdit.type = "submit";
    btnEdit.className = "btnMsgEdit";
    btnEdit.id = "btnMsgEdit" + msgid;
    btnEdit.value = msgid;
    btnEdit.innerHTML = "Edit";
    let btnReply = li.appendChild(document.createElement("button"));
    btnReply.type = "submit";
    btnReply.className = "btnMsgReply";
    btnReply.id = "btnMsgReply" + msgid;
    btnReply.value = msgid;
    btnReply.innerHTML = "Reply";
    if (toAppend){
        let chatbox = document.getElementById("msgList");
        chatbox.scrollTop = chatbox.scrollHeight;
    }
}

convList = document.getElementById("convList");

function genConv(convid, convname){
    let btnS = "btnConvSelect"+convid;
    let btnD = "btnConvDelete"+convid;
    let li = convList.appendChild(document.createElement('li'));
    li.className = 'convLi';
    li.id = "idConv"+convid;
    li.appendChild(document.createElement('label')).innerHTML = convname;
    let buttonSelect = li.appendChild(document.createElement('button'));
    buttonSelect.id = btnS;
    buttonSelect.className = 'btnConvSelect';
    buttonSelect.type = 'submit';
    buttonSelect.value = convid;
    buttonSelect.innerHTML = 'Select';
    buttonSelect.onclick = onClickConvButton("selectConv", convid);

    let buttonDelete = li.appendChild(document.createElement('button'));
    buttonDelete.id = btnD;
    buttonDelete.className = 'btnConvDelete';
    buttonDelete.type = 'submit';
    buttonDelete.value = convid;
    buttonDelete.innerHTML = 'Leave';
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
                ws.send(JSON.stringify(response));
                document.getElementById("convName").innerHTML = response["convname"]
            }
        })
    }
}

document.getElementById("createConvButton").onclick = function (){
    let createConvInput = document.getElementById("createConvInput").innerHTML;
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
            ws.send(JSON.stringify(response));
        }
    })
}

function prepareSendButton() {
    document.getElementById("toSend").focus();
    let sendButton = document.getElementById("messageSubmit");
    sendButton.onclick = sendMessageListener(true);
    document.onkeydown = keyDownListener;
    document.onkeyup = keyUpListener;
}

function keyDownListener(e){
    console.log("I'm here ! e value:");
    console.log(e);
    if(e.key === "Enter" && !(shift_pressed)){
        console.log("Aaaaand message should be sent");
        sendMessage(false);
    }
    else{
        if(e.key === "Shift"){
            shift_pressed = true;
        }
    }
}

function keyUpListener(e){
    if(e.key === "Shift"){
        shift_pressed = false;
    }
}

function sendMessageListener(buttonClicked){
    return function(){
        sendMessage(buttonClicked);
    }
}
function sendMessage(buttonClicked){
    console.log("inside sendMessage");
    console.log(document.activeElement);
    if(document.activeElement === document.getElementById("toSend") || buttonClicked) {
        let messageTxt = document.querySelector("#toSend").innerHTML;
        document.querySelector("#toSend").innerHTML = "";
        let messageFiles = document.querySelector("#id_file").files;
        let fd = new FormData();
        fd.append("type", "sendMessage")
        fd.append("text", messageTxt);
        addFiles(fd, messageFiles);
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

document.getElementById("addToConv").onclick = function (){
    let addToConvInput = document.getElementById("userToAdd").innerHTML;
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
                ws.send(JSON.stringify(response));
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
    btnWhisp.innerHTML = "Whisper";
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

function prepareChatBox() {
    let chatbox = document.getElementById("msgList");
    chatbox.onscroll = function () {
        if (chatbox.scrollTop === 0) {
            fetchMsg(document.getElementById("msgUl").children.length);
        }
    }
}

ws.onmessage = function (msg){
    msg = JSON.parse(msg.data);
    if (msg.type === "sendMessage"){
        JsonToMsg(msg, true);

    }else if (msg.type === "selectConv"){
        if (!messageMode){
            loadFiles();
        }
        else {
            console.log(messageMode);
            document.getElementById("msgUl").innerHTML = "";
            document.getElementById("convName").innerHTML = msg.convname;
            document.getElementById("userList").innerHTML = "";
            askUser(msg.convid);
            fetchMsg(0);
        }
    }
    else if (msg.type === "userToKick"){
        document.getElementById("userList").removeChild(document.getElementById("userid"+msg.userid));
    }else if (msg.type === "kickFromConv"){
        ws.send(JSON.stringify({"type": "hasBeenKicked", "convid": msg.convid}))
        document.getElementById("convList").removeChild(document.getElementById("idConv"+msg.convid));
        selectConv("Begin");
    }
    else if (msg.type === "createConv"){
        selectConv(msg.convid);
        JsonToConv(msg);
    }else if (msg.type === "add_usertoconv"){
        askUserById(msg.userid);
    }else if (msg.type === "got_addedtoconv") {
        askConvById(msg.convid);
    }
}

function loadMessages(){
    let displayMod = document.getElementById("displayMod");
    console.log("Inside loadMessages")
    let toFiles = document.getElementById("FileMessage");
    toFiles.onclick = OnClickLoadFiles();
    if(messageMode === false){
        messageMode = true;
        displayMod.innerHTML = "";
        document.getElementById("addDir").remove();
        createMessageListEnvironment(displayMod);
        createMessageInput(displayMod);
        prepareSendButton();
    }

    selectConv("Begin");
}
function createMessageListEnvironment(parent){
    let msgList = createDiv("msgList",null,parent);
    let ulList = document.createElement("ul");
    ulList.id = "msgUl";
    msgList.appendChild(ulList);
    prepareChatBox();
}
function createMessageInput(parent){
        let sub_container_main_bottom = document.createElement("div");
        sub_container_main_bottom.id = "sub-container-main-bottom";
        let msgSender_container = document.createElement("div");
        msgSender_container.id = "msgSender-container";
        let msgSender_left = createDiv("msgSender-left",null, msgSender_container);
        let msgSender_main = createDiv("msgSender-main",null, msgSender_container);
        let msgSender_right = createDiv("msgSender-right",null, msgSender_container);
        let fileform_label = document.createElement("label");
        fileform_label.htmlFor = "id_file";
        fileform_label.innerHTML = "File:";
        let fileform_file = document.createElement("input");
        fileform_file.id = "id_file";
        fileform_file.type = "file";
        fileform_file.name = "file";
        fileform_file.multiple = "";
        let fileform_text = createDiv("toSend");
        fileform_text.name = "text";
        fileform_text.contentEditable = "true";
        let sendButton = createButton("submit", "sendMessage", null,"Send", "messageSubmit");
        parent.appendChild(sub_container_main_bottom);
        sub_container_main_bottom.appendChild(msgSender_container);
        sub_container_main_bottom.appendChild(sendButton);
        msgSender_left.appendChild(fileform_label);
        msgSender_left.appendChild(fileform_file);
        msgSender_main.appendChild(fileform_text);
}

function createDiv(id = null, classe = null, parent = null){
    let div = document.createElement("div");
    if(id != null){
        div.id = id;
    }
    if(classe != null){
        div.className = classe;
    }
    if(parent != null) {
        parent.appendChild(div);
    }
    return div;
}

function OnClickLoadFiles(){
    return function() {
        loadFiles();
    }
}

function loadFiles(reload_page = true){
    if(messageMode){
        messageMode = false;
        let container = document.getElementsByClassName("sub-container-right")[0];
        console.log(container.children);
        let containerAddDir = createDiv("addDir");
        container.insertBefore(containerAddDir, container.children[3]);
        let addDirField = createDiv("addDirField", null, containerAddDir);
        addDirField.contentEditable = "true";
        let addDirButton = createButton("submit", "addDirButton", null, "Ajouter", "addDirButton")
        addDirButton.onclick = OnClickAddDir;
        containerAddDir.appendChild(addDirButton);

    }
    let toMessages = document.getElementById("FileMessage");
    toMessages.onclick = OnClickLoadMessages();
    fetchFiles();
    console.log("end loadFiles")
}

function OnClickAddDir(){
    let field = document.getElementById("addDirField");
    let text = field.innerHTML;
    let fd = new FormData();
    fd.append("type", "addDir");
    fd.append("name", text);
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
            field.innerHTML = "";
            loadFiles();
        }
    })
}

function OnClickEnterDir(dirId){
    return function(){
        console.log("Inside OnClickEnterDir")
        enterDir(dirId);
    }
}

function enterDir(dirId){
    console.log("Inside enterDir")
    let displayMod = document.getElementById("displayMod");
    displayMod.innerHTML = "";

    let displayUl = document.createElement("ul");
    displayUl.id = "ulDocuments";

    let fd = new FormData();
    fd.append("type", 'enterDir');
    fd.append("dirId", dirId);
    console.log("Send request...")
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
            loadFiles(false);
        }
    })
}

function OnClickBackDir(){
    return function(){
        backDir();
    }
}

function backDir(){
    let fd = new FormData();
    console.log("Inside BackDir");
    fd.append("type", 'backDir');
    console.log("Send request...")
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
            if(response["isTopFile"]){
                loadFiles(true);
            }
            else{
                loadFiles(false);
            }
        }
    })
}

function OnClickLoadMessages(){
    return function(){
        loadMessages()
    }
}

function genFile(title, id){
    console.log("Inside genFile");                        //To secure later with less datas
    let parent = document.getElementById("ulDocuments");
    let listIl = parent.appendChild(document.createElement("li"));
    listIl.draggable = true;
    listIl.ondragstart = dragStartListener;
    listIl.ondragenter = dragEnterDirListener;
    listIl.ondragover = dragOverListener;
    listIl.setAttribute("data-type", "File");
    listIl.setAttribute("data-id", id);
    let label = listIl.appendChild(document.createElement("label"));
    label.innerText = title;
    listIl.appendChild(createButton("submit", "selectFile", id, "Select"));
    listIl.appendChild(createButton("submit", "deleteFile", id, "Delete"));
    listIl.appendChild(createButton("submit", "downloadFile", id, "Download"));
}

function genDir(title, id, parent_id, conv_id){
    let parent = document.getElementById("ulDocuments");
    console.log("Generating directory " + title + " " + id);
    if(parent == null){
        console.log("Generating ulDocuments because is null");
        let displayMod = document.getElementById("displayMod");
        parent = document.createElement("ul");
        parent.id = "ulDocuments";
        displayMod.appendChild(parent);
    }
    let listIl = parent.appendChild(document.createElement("li"));
    listIl.setAttribute("data-type", "Dir");
    listIl.setAttribute("data-id", id);
    listIl.draggable = true;
    listIl.ondragstart = dragStartListener;
    listIl.ondragenter = dragEnterDirListener;
    listIl.ondragover = dragOverListener;
    listIl.ondrop = dropDirListener;
    let label = listIl.appendChild(document.createElement("label"));
    label.innerText = title;
    listIl.appendChild(createButton("submit", "selectDir", id, "Select"));
    listIl.appendChild(createButton("submit", "deleteDir", id, "Delete"));
    let dirEnterButton = createButton("submit", "enterDir", id, "Enter");
    dirEnterButton.onclick= OnClickEnterDir(id);
    listIl.appendChild(dirEnterButton);
}

function dragStartListener(e){
    e.dataTransfer.effectAllowed="move";
    console.log("dragStartListener");
    let data = e.target.dataset.valueOf();
    data = JSON.stringify(data);
    e.dataTransfer.setData("text/plain", data);
}

function dragOverListener(e){
    e.preventDefault();
}

function dragEnterDirListener(e){
    e.preventDefault();
}

function dropDirListener(e){
    console.log('----------------------');
    console.log(e);
    e.preventDefault();
    let fd = new FormData();
    let target = null;
    if(e.target.closest("li") != null){
       target = e.target.closest("li");
    }
    else{
        target = e.target;
    }
    console.log(target);
    let receiverDir = target.dataset.valueOf()["id"];
    console.log("receiverDir = " + receiverDir);
    let value = JSON.parse(e.dataTransfer.getData("text/plain"));
    console.log(value);
    let type = value["type"];
    console.log(type)
    let id = value["id"];
    console.log(id);
    console.log("Inside dropDirListener");
    fd.append("type", 'dropInDir');
    fd.append("mvItemId", id);
    fd.append("receiverDir", receiverDir)
    fd.append("itemType", type)
    console.log("Send request...")
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
            if(response["success"]){
                loadFiles();
            }
            else{
                alert("Error.");
            }
        }
    })
}

function createButton(type, name, value, innerText=null, id=null, classe=null){
    let button = document.createElement("button");
    button.type = type;
    button.name = name;
    button.value = value;
    button.innerText = innerText;
    button.id = id;
    button.class = classe;
    return button
}


function fetchFiles(){
    console.log("Inside fetchfiles")
    let fd = new FormData();
    fd.append("type", 'fetchFiles');
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
                console.log("Inside try of fetchFiles");
                console.log("Number of subdirs:");
                console.log(response["all_subdirs"].length)
                console.log(response["all_subdirs"])

                let displayMod = document.getElementById("displayMod");
                displayMod.innerHTML = "";
                if(response["parent"] === 0){
                    let displayUl = document.createElement("ul");
                    displayUl.id = "ulDocuments";
                    displayMod.appendChild(displayUl);
                }
                else {
                    let displayMod = document.getElementById("displayMod");
                    let backButton = createButton("submit", "back", "", "Back", "backButton");
                    backButton.setAttribute("data-id", response["parent"]);
                    backButton.setAttribute("data-type", "Dir");
                    backButton.ondragenter = dragEnterDirListener;
                    backButton.ondragover = dragOverListener;
                    backButton.ondrop = dropDirListener;
                    backButton.onclick = OnClickBackDir();
                    displayMod.appendChild(backButton);
                    let displayUl = document.createElement("ul");
                    displayUl.id = "ulDocuments";
                    displayMod.appendChild(displayUl);
                }
                for(let i = 0; i < response["all_subdirs"].length; i++){
                    console.log("Subdir id : " + i)
                    JsonToDir(response['all_subdirs'][i]);
                }
                console.log("Number of file:");
                console.log(response["all_files"].length);
                for(let i = 0; i < response["all_files"].length; i++){
                    console.log("In for");
                    JsonToFile(response["all_files"][i]);
                }
            }
            catch(e){}
        }
    })
}

function JsonToFile(file){
    console.log("Inside JsonToFile");
    let path = file.path;
    let id = file.id;
    let title = file.title;
    let author_id = file.author_id;
    let date = file.dateAdded;
    let directory_id = file.directory_id;
    let message_id = file.Message_id;
    console.log(title);
    genFile(title, id);
}

function JsonToDir(dir) {
    let path = dir.path;
    let id = dir.id;
    let title = dir.title;
    let parent_id = dir.parent_id;
    let conv_id = dir.conv_User_id;
    genDir(title, id, parent_id, conv_id, path);
}

createMessageListEnvironment(document.getElementById("displayMod"));
createMessageInput(document.getElementById("displayMod"));
prepareSendButton();