import { 
    make_thumbnail, read_file, set_active_nav, reload_hIcon, set_pagination
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
    const content = document.getElementById("displayContent");

    // get favourites from API
    getData().then( data => {
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

        set_pagination(data["metadata"]);
    })
}

async function getData(){
    // Get List of Favs
    const rsp = await fetch(`http://localhost:8000/favs`, {
        method: "GET",    
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    })

    return rsp.json();
}