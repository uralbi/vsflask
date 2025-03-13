document.getElementById("pass_form").addEventListener("submit", async function(event) {
    event.preventDefault();  // Prevent page reload

    let password = document.getElementById("floatingPassword").value;
    
    let response = await fetch("/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ password: password })
    });

    let result = await response.json();
    console.log(result)
    let p_elem = document.getElementById("result_query")
    if (result.type === 1) {
      p_elem.innerHTML=`<a href="${result.data}" class="info_link" target="_blank">INFO LINK ➣ ${result.query}</a>`
    } else if (result.type === 2) {
      p_elem.innerHTML = "";
      let ul = document.createElement("ul");
      result.res_list.forEach(item => {
          let li = document.createElement("li");
          li.textContent = item;
          ul.appendChild(li);
      });
  
      // Append the list to `p_elem`
      p_elem.appendChild(ul);
    } else {
      p_elem.innerHTML="Error ... " // Show error message
    }
});