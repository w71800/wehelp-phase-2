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

export { checkSign, showSign, inputIsEmpty }