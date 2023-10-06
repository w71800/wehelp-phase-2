const nowLoading = document.querySelector("#loading")

function checkSign(){
  return fetch("/api/auth", {
    headers: {
      Authorization: `Bearer ${localStorage.token}`
    }
  })
  .then( res => res.json() )
  .then( res => {
    let { data } = res
    return data
  } )
}

function showSign(){
  let filter = document.querySelector(".filter")
  filter.classList.toggle("active")
  setTimeout(()=>{
    let boxContainer = document.querySelector(".box_container")
    boxContainer.classList.toggle("active")
  },100)
}

function inputIsEmpty(str){
  return str.trim() === '' ? true : false
}

function loadingControl(){
  setTimeout(() => {
    nowLoading.style.opacity = 0
    nowLoading.addEventListener("transitionend", function(){
      this.classList.remove("active")
      document.querySelector("body").classList.remove("disable-scroll")
    })
  }, 1000)
}

export { checkSign, showSign, inputIsEmpty, loadingControl }