import { make_thumbnail, read_file, set_active_nav, reload_hIcon } from "./utils/library.js";

window.onload = (e) => {
  read_file("nav.html")
  .then(html_data => {
    document.getElementById("navigation").innerHTML = html_data;
    set_active_nav("nav_home");
  });
  displayRecent();
  // fetch("http://localhost:8000/app/figure/price?" + new URLSearchParams({code: "FIGURE-175747"}), {
  //     method: "GET"
  // }).then(rsp => rsp.json())
  // .then(data => console.log(data));
};

// submit_btn.addEventListener("click", () => {
//     /* Only server side need to enable cors. Client side if use cors, it will use pre-flight request which will fuck up the request. */
//     fetch("http://localhost:8000/tracker/get", {
//         method: "GET",
//         headers: {
//             "Accept": "application/json",
//             "Content-Type": "application/json"
//         },
//     }).then((rsp) => rsp.json())
//     .then((data) => {console.log(data)})
//     .catch(rsp => {
//         console.log(rsp);
//     })
// })

function displayRecent() {
  const content = document.getElementById("displayContent");
  get_recent().then((data) => {
    data["results"].forEach((d) => {
      make_thumbnail(content, d, "http://localhost:8000" + d.image_url);
      document.getElementById(`a_${d.code}`).onclick = () => reload_hIcon(d.code);
    });
  });
}

async function get_recent() {
  const rsp = await fetch("http://localhost:8000/app/amiami/recent", {
    method: "GET",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
  });
  return rsp.json();
}