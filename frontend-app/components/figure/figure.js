import { 
    make_thumbnail, read_file, set_active_nav, reload_hIcon, set_pagination, get_figure_details
   } from "/utils/library.js";

window.onload = (e) => {
  read_file("/components/nav.html")
  .then(html_data => {
    document.getElementById("navigation").innerHTML = html_data;
    set_active_nav("nav_figure");
  });

  displayFavs();
};

function displayFavs(){
    // Get page Number
    const urlParams = new URLSearchParams(window.location.search);
    let pageNum = urlParams.get("page");
    if(pageNum == null){
        pageNum = 1;
    }
    const content = document.getElementById("displayContent");

    // get favourites from API
    get_figure_details(`http://localhost:8000/favs?page=${pageNum}`)
    .then( data => {
        data["results"].forEach(d => {
            make_thumbnail(content, d, d.img_url);
            document.getElementById(`a_${d.JAN_code}`).onclick = () => reload_hIcon(d.JAN_code);
            // Add event listener on hover
            const detail = document.getElementById(`detail_${d.JAN_code}`);
            detail.addEventListener('mouseenter', (e) => { 
                e.target.classList.add("details-expand"); 
                e.target.classList.remove("details-collapse");
            });
            detail.addEventListener('mouseleave', (e) => { 
                e.target.classList.add("details-collapse"); 
                e.target.classList.remove("details-expand");
            });
            // TODO: when un-favourite item, how do I remove the 
            //  item without reloading the whole page.
            //  How to make just the item disappear.
        });

        // TODO: fix pagination css style when there are less then 3 pages
        set_pagination(data["metadata"]);
    })
}