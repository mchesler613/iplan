// iplan.tabs.js
function initTabs(initialTab) {
    let id='';
    if (typeof(Storage) !== "undefined") {
        // when switching from task to meeting, need to clear the sessionStorage
        const initialType = initialTab.split('_');
        if (sessionStorage.currentTab) {
            const currentType = sessionStorage.currentTab.split('_');
            console.log("Initial Type: " + initialType + "Current Type: " + currentType); 
            if (initialType[0] !== currentType[0]) {
                // clear session storage
                sessionStorage.clear();
                sessionStorage.currentTab = initialTab;
            }
        } else {
            sessionStorage.currentTab = initialTab; 
        }

        clearTabs();

        document.getElementById(sessionStorage.currentTab).style.display = "block";
        id = sessionStorage.currentTab + 'Title'
        document.getElementById(id).className += " w3-border-red";

        if (document.getElementById("debug")) {
            document.getElementById("debug").innerHTML += "Initial Current Tab:" + sessionStorage.currentTab
                + 'Tab Title: ' + id;
        }
    }
}

function clearTabs() {
    var i, x, tablinks;
    x = document.getElementsByClassName("tab");
    for (i = 0; i < x.length; i++) {
      x[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablink");
    for (i = 0; i < x.length; i++) {
      tablinks[i].className = tablinks[i].className.replace(" w3-border-red", "");
    }    
  }

function openTab(event, tabName) {
    clearTabs();

    sessionStorage.currentTab = tabName
    sessionStorage.event = event
    document.getElementById(tabName).style.display = "block";
    event.currentTarget.firstElementChild.className += " w3-border-red";

    if (document.getElementById("debug")) {
        document.getElementById("debug").innerHTML = "Current Tab:" + sessionStorage.currentTab;
    }
}
