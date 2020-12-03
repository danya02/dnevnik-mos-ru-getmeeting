async function sendCookies(details) {
  console.log("REQUEST CAPTURED", details);
  let cookies = await browser.cookies.getAll({'domain': 'dnevnik.mos.ru'});
  console.log("MY COOKIES", cookies);
}


browser.webRequest.onCompleted.addListener(
  sendCookies,
  {urls: ["https://dnevnik.mos.ru/core/api/*"]},
  ["responseHeaders"]
);

