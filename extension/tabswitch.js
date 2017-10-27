function save(url, move) {
	console.log(url)
	var xhr = new XMLHttpRequest();
	xhr.open("POST", "http://localhost:8888", true);
	xhr.setRequestHeader('Content-Type', 'application/json');
	xhr.send(JSON.stringify({
		active: url,
		move: move
	}));
}

function save_tabbed(tab) {
	save(tab.url, "tab")
}

function tab_callback(info) {
	chrome.tabs.get(info.tabId, save_tabbed)
}

function commit_callback(details) {
	transition = details.transitionType;
	if (transition == "link" && details.transitionQualifiers[0] != "forward_back"){
		save(details.url, "link")
		
	}
	else if (transition == "typed" || transition == "generated" || details.transitionQualifiers[0] == "forward_back"){
		save(details.url, "tab")
	}
}

chrome.tabs.onActivated.addListener(tab_callback)
chrome.webNavigation.onCommitted.addListener(commit_callback)