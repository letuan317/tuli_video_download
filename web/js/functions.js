let checkPasted = false;

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
}

eel.expose(update_listOfLinks_js);
function update_listOfLinks_js(listOfLinks) {
  let new_items = "";
  for (let i in listOfLinks) {
    console.log(listOfLinks[i]);
    new_items +=
      '<div class="list-links"><div class="item"><div class="left"><img src="' +
      listOfLinks[i].thumbnail +
      '"alt="youtube"/></div><div class="right"><div class="top"><h5>' +
      listOfLinks[i].title.substring(0, 50) +
      '</h5></div><div class="bottom"><p class="channel">' +
      listOfLinks[i].channel +
      '</p><select name="formats">';
    for (let j in listOfLinks[i].formats) {
      new_items +=
        '<option value="' +
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

    new_items += "</select></div></div></div></div>";
  }

  console.log(listOfLinks[0].id);
  document.getElementById("list-links").innerHTML = new_items;
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
        eel.getInfo(cliptext);
        checkPasted = true;
      },
      (err) => console.log(err)
    );
  }
}

function playBtnAction() {
  eel.server_log("Play button clicked");
  console.log("Play button clicked");
  const numbers = [45, 4, 9, 16, 25];

  let txt = "";
  for (let x in numbers) {
    txt += numbers[x] + "<br>";
  }

  document.getElementById("demo1").innerHTML = txt;
}
