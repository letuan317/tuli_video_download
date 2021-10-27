let checkPasted = false;
let checkStarted = false;
let globalListOfLinks = [];

function show_unused_button() {
  checkPasted = false;
  checkStarted = false;
}
function hide_unused_button() {
  checkPasted = true;
  checkStarted = true;
}
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

eel.expose(error_message_js);
function error_message_js(message) {
  console.log("error_message_js: " + message);
  document.getElementById("footer").innerText = message;
  document.getElementById("footer").style.color = "red";
  checkPasted = false;
}

eel.expose(download_process_js);
function download_process_js(status) {
  document.getElementById("footer").innerText = status;
  document.getElementById("footer").style.color = "white";
  if (status === "Finished") {
    show_unused_button();
  }
}

eel.expose(update_listOfLinks_js);
function update_listOfLinks_js(listOfLinks) {
  globalListOfLinks = listOfLinks;
  let new_items = "";
  for (let i in listOfLinks) {
    new_items +=
      '<div class="item"><div class="left"><img src="' +
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
      checkStarted === true
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
  checkPasted = false;
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
  if (checkPasted === false) {
    navigator.clipboard.readText().then(
      (cliptext) => {
        eel.get_info_py(cliptext);
        checkPasted = true;
      },
      (err) => console.log(err)
    );
  }
}

function playBtnAction() {
  // send download action to Python
  // check skip downloaded, start download with default folder
  if (checkStarted == false) {
    hide_unused_button();
    eel.start_download_py();
    document.getElementById("pasteLinkBtnIcon").style.opacity = "0.3";
    document.getElementById("playBtnIcon").style.opacity = "0.3";

    for (let i in globalListOfLinks) {
      document.getElementById(globalListOfLinks[i].id).disabled = true;
    }
  }
}
function stopBtnAction() {
  if (checkStarted == true) {
    show_unused_button();
    eel.stop_download_py();
    document.getElementById("pasteLinkBtnIcon").style.opacity = "1";
    document.getElementById("playBtnIcon").style.opacity = "1";

    for (let i in globalListOfLinks) {
      document.getElementById(globalListOfLinks[i].id).disabled = false;
    }
  }
}
