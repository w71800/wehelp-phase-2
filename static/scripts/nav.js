const initNav = (function (){
  const signout = document.querySelector(".signout")
  const sign = document.querySelector(".sign")
  const book = document.querySelector(".navbar_option.booking")
  
  return function(){
    signout.addEventListener("click", ()=>{
      localStorage.clear()
      let currentURL = window.location.href
      window.location.href = currentURL
    })

    window.addEventListener('userAuthenticated', e => {
      let { detail } = e
      if(detail != null){ 
        let navOptions = document.querySelector(".navbar_options")
        let sign = document.querySelector(".sign")
        let signout = document.querySelector(".signout")
        
        let el = document.createElement("div")
        el.textContent = `哈囉，${detail.name}！`
        el.classList.add("navbar_hello")
        navOptions.prepend(el)
        
        signout.classList.remove("inactive")
        sign.classList.add("inactive")
      }
    });
    
    sign.addEventListener("click", ()=>{
      let filter = document.querySelector(".filter")
      filter.classList.toggle("active")
      setTimeout(()=>{
        let boxContainer = document.querySelector(".box_container")
        boxContainer.classList.toggle("active")
      },100)
    })

    book.addEventListener("click", ()=>{
      if(localStorage.token){
        window.location.href = "/booking"
      }else{
        let filter = document.querySelector(".filter")
        filter.classList.toggle("active")
        setTimeout(()=>{
          let boxContainer = document.querySelector(".box_container")
          boxContainer.classList.toggle("active")
        },100)
      }
    })
  }
})();

initNav()