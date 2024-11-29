export function make_thumbnail(body, data, src){
  const div = document.createElement("div");
  div.className = "thumbnail";
  const image = new Image();
  image.src = src;

  let track_html = "";
  if (data.isTracked) {
    track_html = `<i id="${data.JAN_code}" class="fa fa-heart fa" aria-hidden="true"></i>`;
  } else {
    track_html = `<i id="${data.JAN_code}" class="fa fa-heart-o fa" aria-hidden="true"></i>`;
  }

  div.innerHTML = `
    <div id='detail_${data.JAN_code}' class='details details-collapse'>${data.title}</div>
    <!--  Heart Icon -->
    <a href="javascript:void(0);" id="a_${data.JAN_code}">
    <div class="iconwrapper left">
      ${track_html}  
    </div>
    </a>
    <!-- HLJ Link -->
    <a href="${data.page_url}" target="_blank">
      <div class="iconwrapper right" style="background-color: white;"> 
        <img src="/assets/hlj.ico">
      </div>
    </a>
  `;
  div.appendChild(image);
  body.appendChild(div);
}

export function set_active_nav(to_active){
  // Toggle Class for Navigation. Just change the UI of Navbar 
  const nav_bar = document.getElementById("nav_wrapper").children;
  for(var i = 0; i < nav_bar.length; i++){
      if(nav_bar[i].id == to_active) {
          nav_bar[i].classList.add("active");
      } else {
          nav_bar[i].classList.remove("active");
      }
  }
}

export async function read_file(file_path){
    const rsp = await fetch(file_path)
    return rsp.text()        
}

export function reload_hIcon(code) {
  const heart_icon = document.getElementById(code);
  // If heart_icon is hollow, need to update server that this item is going to be tracked.
  // else stop tracking

  var data = new FormData();
  data.append("code", code);

  // if (heart_icon.classList.contains("fa-heart-o")) {
  //     heart_icon.classList.remove("fa-heart-o");
  //     heart_icon.classList.add("fa-heart");
  //     fetch("http://localhost:8000/app/figure/update", {
  //         method: "POST",
  //         body: data,
  //     })
  //     .then((rsp) => rsp.json())
  //     .then((data) => {
  //         console.log(data);
  //     });
  // }
}

export function set_pagination(page_data){
  const pagination = document.getElementById("pagination");
  
  for(let i=1; i<=page_data["totalPages"]; i++){
    const a = document.createElement("a");
    a.innerHTML = i;
    a.href = `?page=${i}`
    pagination.appendChild(a);
  }
}
