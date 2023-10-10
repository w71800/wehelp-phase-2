const initNowLoading = (function(){
  let loading = document.querySelector("#loading")
  let lastSpan = document.querySelectorAll("span")[13]

  return function(){
    lastSpan.addEventListener("animationend", ()=>{
      console.log("end")
      loading.classList.remove("bounce")
      setTimeout(()=>{
        loading.classList.add("bounce")  
      }, 200)
    })
  }
})();

initNowLoading()





