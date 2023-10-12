// 取得登入的 token
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
  })
}

// 控制登入註冊的表格行為
function showSign(){
  let filter = document.querySelector(".filter")
  filter.classList.toggle("active")
  setTimeout(()=>{
    let boxContainer = document.querySelector(".box_container")
    boxContainer.classList.toggle("active")
  }, 100)
}

function inputIsEmpty(str){
  return str.trim() === '' ? true : false
}

function notifyAuthed(authData){
  const event = new CustomEvent('userAuthenticated', { detail: authData });
  window.dispatchEvent(event);
}

const loadingControl = (function (){
  let nowLoading = document.querySelector("#loading")

  return function(){
    setTimeout(() => {
      nowLoading.style.opacity = 0
      nowLoading.addEventListener("transitionend", function(){
        this.classList.remove("active")
        document.querySelector("body").classList.remove("disable-scroll")
      })
    }, 1000)
  }
})();


export { checkSign, showSign, inputIsEmpty, loadingControl, notifyAuthed }