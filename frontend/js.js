
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

  request.send(JSON.stringify({ long_url: url }));
}
