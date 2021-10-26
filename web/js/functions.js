let checkPasted = false;
let checkStarted = false;
let globalListOfLinks = [];
window.onload = function () {
  const numbers = [45, 4, 9, 16, 25];

  let txt = "";
  for (let x in numbers) {
    txt += numbers[x] + "<br>";
  }

  document.getElementById("demo1").innerHTML = txt;
};

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
      '")>';
    for (let j in listOfLinks[i].formats) {
      new_items +=
        '<option value="' +
        listOfLinks[i].id +
        "-" +
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

    new_items +=
      '</select><p id="' +
      listOfLinks[i].id +
      '-status"></p></p></div></div></div>';
  }

  document.getElementById("list-links").innerHTML = new_items;
  checkPasted = false;
}
eel.expose(update_);
function ChangeFormat(item_id) {
  var x = document.getElementById(item_id).value;
  var temp_id = x.split("-")[0];
  var temp_select_format = x.split("-")[1];
  for (let i in globalListOfLinks) {
    if (globalListOfLinks[i].id === temp_id) {
      globalListOfLinks[i].select_format = temp_select_format;
      break;
    }
  }
  eel.update_listOfLinks_py(globalListOfLinks);
}
say_hello_js("Javascript World!");
eel.say_hello_py("Javascript World!"); // Call a Python function

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
    checkStarted = true;
    checkPasted = true;
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
    checkStarted = false;
    checkPasted = false;
    eel.stop_download_py();
    document.getElementById("pasteLinkBtnIcon").style.opacity = "1";
    document.getElementById("playBtnIcon").style.opacity = "1";

    for (let i in globalListOfLinks) {
      document.getElementById(globalListOfLinks[i].id).disabled = false;
    }
  }
}
