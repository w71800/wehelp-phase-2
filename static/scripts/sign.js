const signinForm = document.querySelector("#box.signin form")
const changeSpan = document.querySelectorAll("span")
const cross = document.querySelectorAll(".box_cross")
const boxContainer = document.querySelector(".box_container")
signinForm.addEventListener("submit", async(e) => {
  e.preventDefault()

  let result = await sendToSignin()
  if(result?.error){
  }else{
    localStorage.setItem("token", result.token)

    let currentURL = window.location.href;
    window.location.href = currentURL
  }
})

function sendToSignin(){
    const formData = new FormData(signinForm);
    console.log(signinForm);
    return fetch("/api/auth", {
      method: "PUT",
      body: formData
    })
    .then( res => res.json() )
}

changeSpan.forEach( item => {
  item.addEventListener("click", ()=>{
    let signinBox = document.querySelector("#box.signin")
    let signupBox = document.querySelector("#box.signup")
  
    signinBox.classList.toggle("inactive")
    signupBox.classList.toggle("inactive")
  })  
})

cross.forEach( item => {
  item.addEventListener("click", () => {  
    boxContainer.classList.toggle("active")
    setTimeout(()=>{
      let filter = document.querySelector(".filter")
      filter.classList.toggle("inactive")
    }, 700)
  })

})