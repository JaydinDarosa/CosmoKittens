import"./Layout.astro_astro_type_script_index_0_lang.CXkCNBTi.js";document.getElementById("login_buttton").addEventListener("click",function(n){const o=document.getElementById("username_form"),t=document.getElementById("password");fetch("/api/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({username:o.value,password:t.value})}).then(e=>{if(e.ok)return e.json();throw new Error("Network response was not ok.")}).then(e=>{console.log(e),window.location.href="/"}).catch(e=>{console.error("There has been a problem with your fetch operation:",e)})});document.getElementById("register_button").addEventListener("click",function(n){const o=document.getElementById("username_form"),t=document.getElementById("password");fetch("/api/users",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({username:o.value,password:t.value})}).then(e=>{if(e.ok)return e.json();throw new Error("Network response was not ok.")}).then(e=>{console.log(e),window.location.href="/"}).catch(e=>{console.error("There has been a problem with your fetch operation:",e)})});