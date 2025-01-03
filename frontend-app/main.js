import { 
  read_file, set_active_nav
 } from "./utils/library.js";

window.onload = (e) => {
  read_file("components/nav.html")
  .then(html_data => {
    document.getElementById("navigation").innerHTML = html_data;
    set_active_nav("nav_home");
  });
};
