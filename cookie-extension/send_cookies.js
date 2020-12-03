const MY_SECRET = "(replace with value from your database)";

async function sendCookies(details) {
  console.log("REQUEST CAPTURED", details);
  let cookies = await browser.cookies.getAll({'domain': 'dnevnik.mos.ru'});
  console.log("MY COOKIES", cookies);
  var cookies_formatted = {};

  cookies.forEach((item) => {
    cookies_formatted[ item.name ] = item.value;
  });


  var xhr = new XMLHttpRequest();
//  var url = "https://dnevnik-automate.danya02.ru/register_cookiejar/" + MY_SECRET;
  var url = "http://10.0.0.2:5000/register_cookiejar/" + MY_SECRET;
  xhr.open("POST", url);
  xhr.setRequestHeader("Content-Type", "application/json");

  xhr.loadend = function() {
    console.log("Request completed: ", xhr);
  }
  xhr.send(JSON.stringify( cookies_formatted ));
}


browser.webRequest.onCompleted.addListener(
  sendCookies,
  {urls: ["https://dnevnik.mos.ru/core/api/*"]},
  ["responseHeaders"]
);
