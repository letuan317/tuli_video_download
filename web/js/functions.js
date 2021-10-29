let IsPaste = true;
let IsAdd = true;
let IsDownload = true;
let IsPause = false;
let IsSort = true;
let IsClear = true;
let IsSetting = true;

let globalListOfLinks = [];

window.onload = function () {};

window.onresize = function () {
  if (window.outerWidth < 800 || window.outerHeight < 500) {
    window.resizeTo(800, 500);
  }
};
// Expose this function to Python
eel.expose(say_hello_js);
function say_hello_js(x) {
  console.log("Hello from " + x);
}
say_hello_js("Javascript World!");
eel.say_hello_py("Javascript World!"); // Call a Python function

eel.expose(setup_config_js);
function setup_config_js(data_config) {
  console.log(data_config);
  document.getElementById("default_path_storage").innerText =
    data_config.path_storage;
  document.getElementById("default_path_downloaded").innerText =
    data_config.path_downloaded;
}

function show_unused_button() {
  IsPaste = true;
  IsAdd = true;
  IsDownload = true;
  IsPause = false;
  IsSort = true;
  IsClear = true;
  document.getElementById("pasteLinkBtnIcon").style.opacity = "1";
  document.getElementById("addFileBtnIcon").style.opacity = "1";
  document.getElementById("downloadBtnIcon").style.opacity = "1";
  document.getElementById("pauseBtnIcon").style.opacity = "0.3";
  document.getElementById("sortBtnIcon").style.opacity = "1";
  document.getElementById("clearBtnIcon").style.opacity = "1";
}
function hide_unused_button() {
  IsPaste = false;
  IsAdd = false;
  IsDownload = false;
  IsPause = true;
  IsSort = false;
  IsClear = false;
  document.getElementById("pasteLinkBtnIcon").style.opacity = "0.3";
  document.getElementById("addFileBtnIcon").style.opacity = "0.3";
  document.getElementById("downloadBtnIcon").style.opacity = "0.3";
  document.getElementById("pauseBtnIcon").style.opacity = "0.3";
  document.getElementById("sortBtnIcon").style.opacity = "0.3";
  document.getElementById("clearBtnIcon").style.opacity = "0.3";
}

eel.expose(error_message_js);
function error_message_js(message) {
  console.log("error_message_js: " + message);
  document.getElementById("footer").innerText = message;
  document.getElementById("footer").style.color = "red";
  if (IsPaste == false) {
    IsPaste = true;
  }
}
eel.expose(notify_message_js);
function notify_message_js(message) {
  document.getElementById("footer").innerText = "[INFO] " + message;
  document.getElementById("footer").style.color = "green";
}

eel.expose(download_process_js);
function download_process_js(status) {
  document.getElementById("footer").innerText = status;
  document.getElementById("footer").style.color = "white";
  if (status.includes("ETA")) {
    document.getElementById("progress-bar").style.display = "block";
    let percent = status.split("of")[0];
    document.getElementById("download-progress-bar").style.width = percent;
  } else {
    document.getElementByC("progress-bar").style.display = "none";
  }

  if (status === "Done") {
    show_unused_button();
  }
}

eel.expose(update_listOfLinks_js);
function update_listOfLinks_js(listOfLinks) {
  globalListOfLinks = listOfLinks;
  let new_items = "";
  for (let i in listOfLinks) {
    new_items += '<div class="item" id="' + listOfLinks[i].id + '-item">';
    if (IsDownload == false) {
      new_items += '<div style="display: none;"';
    } else {
      new_items += "<div ";
    }

    new_items +=
      ' class="delete-bin" onclick="deleteItemAction(\'' +
      listOfLinks[i].id +
      '\')"><img src="img/icons8-delete-bin-48.png" alt="delete-bin"/></div><div class="open-link" onclick="openLinkAction(\'' +
      listOfLinks[i].webpage_url +
      '\')"><img src="img/icons8-link-48.png" alt="open-link"/></div><div class="left"><img src="' +
      listOfLinks[i].thumbnail +
      '"alt="youtube"/></div><div class="right"><div class="top"><h5>' +
      listOfLinks[i].title +
      '</h5></div><div class="bottom"><p class="channel">' +
      listOfLinks[i].channel +
      '</p><select id="' +
      listOfLinks[i].id +
      '" onchange=ChangeFormat("' +
      listOfLinks[i].id +
      '") ';
    if (
      ["Downloaded"].includes(listOfLinks[i].status) ||
      IsDownload === false
    ) {
      new_items += "disabled";
    }
    new_items += ">";
    for (let j in listOfLinks[i].formats) {
      new_items +=
        '<option value="' +
        listOfLinks[i].id +
        " " +
        listOfLinks[i].formats[j].format_id +
        '">' +
        listOfLinks[i].formats[j].format +
        ", " +
        listOfLinks[i].formats[j].ext +
        ", " +
        listOfLinks[i].formats[j].format_note +
        ", " +
        listOfLinks[i].formats[j].fps +
        "fps, ";
      if (listOfLinks[i].formats[j].filesize / 1024 / 1024 / 1024 < 1) {
        new_items +=
          (listOfLinks[i].formats[j].filesize / 1024 / 1024).toFixed(2) + "MB";
      } else {
        new_items +=
          (listOfLinks[i].formats[j].filesize / 1024 / 1024 / 1024).toFixed(2) +
          "GB";
      }
      new_items += "</option>";
    }

    if (listOfLinks[i].status === "Downloaded") {
      new_items +=
        '</select><p style="color:#e9c46a;font-weight:bold;">Downloaded</p></div></div></div>';
    } else if (listOfLinks[i].status === "Downloading") {
      new_items +=
        '</select><p style="color:#f4a261;font-weight:bold;">Downloading</p></div></div></div>';
    } else if (listOfLinks[i].status === "Paused") {
      new_items +=
        '</select><p style="color:#ede0d4;font-weight:bold;">Paused</p></div></div></div>';
    } else if (listOfLinks[i].status === "Error") {
      new_items +=
        '</select><p style="color:#e76f51;font-weight:bold;">Error</p></div></div></div>';
    } else {
      new_items += "</select><p></p></div></div></div>";
    }
  }

  document.getElementById("list-links").innerHTML = new_items;
  if (IsDownload == false) {
    IsPaste = true;
  }
}
function ChangeFormat(item_id) {
  var x = document.getElementById(item_id).value;
  var temp_id = x.split(" ")[0];
  var temp_select_format = x.split(" ")[1];
  for (let i in globalListOfLinks) {
    if (globalListOfLinks[i].id === temp_id) {
      globalListOfLinks[i].select_format = temp_select_format;
      for (let j in globalListOfLinks[i].formats) {
        if (globalListOfLinks[i].formats[j].format_id === temp_select_format) {
          let temp_format = globalListOfLinks[i].formats[j];
          const index = globalListOfLinks[i].formats.indexOf(temp_format);
          globalListOfLinks[i].formats.splice(index, 1);
          globalListOfLinks[i].formats.unshift(temp_format);
          break;
        }
      }
      break;
    }
  }
  eel.update_listOfLinks_py(globalListOfLinks);
}
// Paste the clipboard
document.addEventListener("DOMContentLoaded", function () {
  let pasteButton = document.getElementsByTagName("button")[0];
  pasteButton.addEventListener("click", function () {
    navigator.clipboard.readText().then(
      (cliptext) =>
        (document.getElementById("clipboard-paste").innerText = cliptext),
      (err) => console.log(err)
    );
  });
});
//end paste the clipboard

//paste-link-btn
function pasteLinkBtnAction() {
  if (IsPaste === true) {
    navigator.clipboard.readText().then(
      (cliptext) => {
        eel.paste_link_action_py(cliptext);
        IsPaste = false;
        IsAdd = false;
        IsDownload = false;
        IsPause = false;
        IsSort = false;
        IsClear = false;
        IsSetting = false;
        document.getElementById("pasteLinkBtnIcon").style.opacity = "0.3";
        document.getElementById("addFileBtnIcon").style.opacity = "0.3";
        document.getElementById("downloadBtnIcon").style.opacity = "0.3";
        document.getElementById("pauseBtnIcon").style.opacity = "0.3";
        document.getElementById("sortBtnIcon").style.opacity = "0.3";
        document.getElementById("clearBtnIcon").style.opacity = "0.3";
        document.getElementById("settingBtnIcon").style.opacity = "0.3";
      },
      (err) => console.log(err)
    );
  }
}

eel.expose(paste_link_response_js);
function paste_link_response_js() {
  IsPaste = true;
  IsAdd = true;
  IsDownload = true;
  IsPause = false;
  IsSort = true;
  IsClear = true;
  IsSetting = true;
  document.getElementById("pasteLinkBtnIcon").style.opacity = "1";
  document.getElementById("addFileBtnIcon").style.opacity = "1";
  document.getElementById("downloadBtnIcon").style.opacity = "1";
  document.getElementById("pauseBtnIcon").style.opacity = "0.3";
  document.getElementById("sortBtnIcon").style.opacity = "1";
  document.getElementById("clearBtnIcon").style.opacity = "1";
  document.getElementById("settingBtnIcon").style.opacity = "1";
  console.log("Paste Link Done", IsDownload);
}

function addFileBtnAction() {
  console.log("add file clicked");
  if (IsAdd === true) {
    IsPaste = false;
    IsAdd = false;
    IsDownload = false;
    IsPause = false;
    IsSort = false;
    IsClear = false;
    document.getElementById("pasteLinkBtnIcon").style.opacity = "0.3";
    document.getElementById("addFileBtnIcon").style.opacity = "0.3";
    document.getElementById("downloadBtnIcon").style.opacity = "0.3";
    document.getElementById("pauseBtnIcon").style.opacity = "0.3";
    document.getElementById("sortBtnIcon").style.opacity = "0.3";
    document.getElementById("clearBtnIcon").style.opacity = "0.3";
    eel.add_file_action_py();
  } else if (IsAdd === false && IsSetting === true) {
    IsPaste = true;
    IsAdd = true;
    IsDownload = true;
    IsPause = false;
    IsSort = true;
    IsClear = true;
    document.getElementById("pasteLinkBtnIcon").style.opacity = "1";
    document.getElementById("addFileBtnIcon").style.opacity = "1";
    document.getElementById("downloadBtnIcon").style.opacity = "1";
    document.getElementById("pauseBtnIcon").style.opacity = "0.3";
    document.getElementById("sortBtnIcon").style.opacity = "1";
    document.getElementById("clearBtnIcon").style.opacity = "1";
    update_listOfLinks_js(globalListOfLinks);
  }
}
eel.expose(add_file_response_js);
function add_file_response_js() {
  addFileBtnAction();
}

function downloadBtnAction() {
  // send download action to Python
  // check skip downloaded, start download with default folder
  if (IsDownload == true) {
    IsPaste = false;
    document.getElementById("pasteLinkBtnIcon").style.opacity = "0.3";
    IsAdd = false;
    document.getElementById("addFileBtnIcon").style.opacity = "0.3";
    IsDownload = false;
    document.getElementById("downloadBtnIcon").style.opacity = "0.3";
    IsPause = true;
    document.getElementById("pauseBtnIcon").style.opacity = "1";
    IsSort = false;
    document.getElementById("sortBtnIcon").style.opacity = "0.3";
    IsClear = false;
    document.getElementById("clearBtnIcon").style.opacity = "0.3";
    IsSetting = false;
    document.getElementById("settingBtnIcon").style.opacity = "0.3";
    eel.start_download_py();
    for (let i in globalListOfLinks) {
      document.getElementById(globalListOfLinks[i].id).disabled = true;
    }
  }
}
function pauseBtnAction() {
  if (IsPause == true) {
    document.getElementById("pasteLinkBtnIcon").style.opacity = "1";
    IsPaste = true;
    document.getElementById("addFileBtnIcon").style.opacity = "1";
    IsAdd = true;
    document.getElementById("downloadBtnIcon").style.opacity = "1";
    IsDownload = true;
    document.getElementById("pauseBtnIcon").style.opacity = "0.3";
    IsPause = false;
    document.getElementById("sortBtnIcon").style.opacity = "1";
    IsSort = true;
    document.getElementById("clearBtnIcon").style.opacity = "1";
    IsClear = true;
    document.getElementById("settingBtnIcon").style.opacity = "1";
    IsSetting = true;
    eel.pause_download_py();

    for (let i in globalListOfLinks) {
      document.getElementById(globalListOfLinks[i].id).disabled = false;
    }
  }
}
function settingBtnAction() {
  if (IsSetting == true) {
    IsPaste = false;
    IsAdd = false;
    IsDownload = false;
    IsPause = false;
    IsSort = false;
    IsClear = false;
    IsSetting = false;
    document.getElementById("pasteLinkBtnIcon").style.opacity = "0.3";
    document.getElementById("addFileBtnIcon").style.opacity = "0.3";
    document.getElementById("downloadBtnIcon").style.opacity = "0.3";
    document.getElementById("pauseBtnIcon").style.opacity = "0.3";
    document.getElementById("sortBtnIcon").style.opacity = "0.3";
    document.getElementById("clearBtnIcon").style.opacity = "0.3";
    document.getElementById("settingBtnIcon").style.opacity = "0.3";
    document.getElementById("setting-container").style.display = "block";
  }
}
function settingCloseBtnAction() {
  document.getElementById("setting-container").style.display = "none";
  IsPaste = true;
  IsAdd = true;
  IsDownload = true;
  IsPause = false;
  IsSort = true;
  IsClear = true;
  IsSetting = true;
  document.getElementById("pasteLinkBtnIcon").style.opacity = "1";
  document.getElementById("addFileBtnIcon").style.opacity = "1";
  document.getElementById("downloadBtnIcon").style.opacity = "1";
  document.getElementById("pauseBtnIcon").style.opacity = "0.3";
  document.getElementById("sortBtnIcon").style.opacity = "1";
  document.getElementById("clearBtnIcon").style.opacity = "1";
  document.getElementById("settingBtnIcon").style.opacity = "1";
}
function sortBtnAction() {
  if (IsSort === true) {
    eel.sort_action_py();
  }
}
function clearBtnAction() {
  if (IsClear === true) {
    eel.clear_action_py();
  }
}
function openFolderBtnAction() {
  console.log("clicked");
  eel.open_folder_storage_py();
}

function addFileInputCheckmarkBtnAction() {
  var path_file = document.getElementById("addFileInputPath").value;
  eel.add_file_action_py(path_file);
}
function addFileInputCancelBtnAction() {
  document.getElementById("addFileInputPath").value = "";
}

function deleteItemAction(item_id) {
  console.log(item_id + " delete");
  eel.delete_item_action_py(item_id);
}
function openLinkAction(web_url) {
  window.open(web_url);
}
function settingChangeDefaultPathStorage() {
  eel.setting_change_default_path_py("path_storage");
}
function settingChangeDefaultPathDownload() {
  eel.setting_change_default_path_py("path_downloaded");
}
