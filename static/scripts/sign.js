const initSign = (function (){
  const signinForm = document.querySelector("#box.signin form")
  const signupForm = document.querySelector("#box.signup form")
  const changeSpan = document.querySelectorAll("span")
  const cross = document.querySelectorAll(".box_cross")
  const boxContainer = document.querySelector(".box_container")
  const signinStatus = document.querySelector("#box.signin .sign_status")
  const signupStatus = document.querySelector("#box.signup .sign_status")
   
  return function(){
    function sendToSign(behavior = "SIGNIN"){
      let formData
      if(behavior == "SIGNUP"){
        formData = new FormData(signupForm);

        return fetch("/api/user", {
          method: "POST",
          body: formData
        })
        .then( res => res.json() )
      }

      if(behavior == "SIGNIN"){
        formData = new FormData(signinForm);
        
        return fetch("/api/auth", {
          method: "PUT",
          body: formData
        })
        .then( res => res.json() )
      }
      
    }


    signinForm.addEventListener("submit", async(e) => {
      e.preventDefault()
    
      let result = await sendToSign()
      if(result?.error){
        signinStatus.classList.toggle("error")
        signinStatus.textContent = "電子信箱或密碼錯誤"

        setTimeout(()=>{
          signinStatus.classList.remove("success")
          signinStatus.classList.remove("error")
          signinStatus.textContent = ""
        }, 1000)
      }else{
        signinStatus.classList.toggle("success")
        signinStatus.textContent = "登入成功"
        localStorage.setItem("token", result.token)
        
        setTimeout(()=>{
          if(boxContainer.classList.contains("fromBooking")){
            window.location.href = "/booking"  
            return
          }
          let currentURL = window.location.href;
          window.location.href = currentURL
        }, 1000)
      }

      Array.from(signinForm.elements).forEach( input => {
        if(input.type != "submit"){
          input.value = ""
        }
      })
    })

    signupForm.addEventListener("submit", async(e) => {
      e.preventDefault()
    
      let result = await sendToSign("SIGNUP")
      if(result?.error){
        signupStatus.classList.toggle("error")
        signupStatus.textContent = "此信箱已被註冊！"
      }else{
        signupStatus.classList.toggle("success")
        signupStatus.textContent = "註冊成功"

        Array.from(signupForm.elements).forEach( input => {
          if(input.type != "submit"){
            input.value = ""
          }
        })

        // const signBox = document.querySelectorAll("#box")
        // signBox.forEach( box => {
        //   box.classList.toggle("inactive")
        // })
      }
      setTimeout(()=>{
        signupStatus.classList.remove("success")
        signupStatus.classList.remove("error")
        signupStatus.textContent = ""

      }, 1000)

      
    })
    
    
    
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
        boxContainer.classList.remove("fromBooking")
        boxContainer.classList.toggle("active")
        setTimeout(()=>{
          let filter = document.querySelector(".filter")
          filter.classList.toggle("active")
        }, 700)
      })
    
    })
  }
})();

initSign()


