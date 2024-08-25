document.getElementById("shorten-button").addEventListener("click", shortenURL);

var input = document.getElementById("url");

// Options zone management
const optionsContent = document.getElementById("options-content");
document.getElementById("options-toggle").addEventListener('click', () => {
  optionsContent.style.display = (optionsContent.style.display === 'block') ? 'none' : 'block';
  displayOptionsText()
});

input.addEventListener("keypress", function (event) {
  if (event.key === "Enter") {
    event.preventDefault();
    document.getElementById("shorten-button").click();
  }
});

function shortenURL() {
  const url = document.getElementById("url").value;
  const endpoint = "https://__PLACEHOLDER__/create";
  const request = new XMLHttpRequest();
  request.open("POST", endpoint, true);

  request.onload = function () {
    const data = JSON.parse(request.responseText);
    const shortenedURL = data.short_url;
    if (request.status >= 200 && request.status < 400) {
      document.getElementById(
        "shortened-url"
      ).innerHTML = `<p>Shortened URL: <a href="${shortenedURL}" target="_blank">${shortenedURL}</a></p>`;
    } else {
      document.getElementById(
        "shortened-url"
      ).innerHTML = `<p>Error: ${request.responseText}</a></p>`;
    }
  };

  // Preparing the boyd
  var body = { long_url: url }

  // Get expiration delay
  var expiry = document.getElementById("option-expiry").value;
  if (parseInt(expiry)) body.ttl_in_days=parseInt(expiry)

  // Get humand readability  
  var humanReadable = document.getElementById("human-readable")
  body.human_readable=humanReadable.checked;

  request.send(JSON.stringify(body));
  document.getElementById("url").value = "";
}

// Let's display the correct text for the options label, based on content visibility
function displayOptionsText() {
  const optionTxt_expanded = "<span style='font-size: xx-large'>⚒️</span> Options &#9660;"
  const optionTxt_collapsed = "<span style='font-size: xx-large'>⚒️</span> Options &#9658;"
  if (optionsContent.style.display === 'block') {
    document.getElementById("options-toggle").innerHTML = optionTxt_expanded
  } else {
    document.getElementById("options-toggle").innerHTML = optionTxt_collapsed
  }
}

displayOptionsText()
