const loading = document.querySelector("#loading")
const lastSpan = document.querySelectorAll("span")[13]

console.log(lastSpan)

lastSpan.addEventListener("animationend", ()=>{
  console.log("end")
  loading.classList.remove("bounce")
  setTimeout(()=>{
    loading.classList.add("bounce")  
  }, 200)
})

