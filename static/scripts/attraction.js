const url = window.location.href;
const id = url.match(/attraction\/(\d+)/)[1]
const carouselBtns = document.querySelectorAll(".carousel-btn")
const prevBtn = document.querySelector(".prev")
const nextBtn = document.querySelector(".next")
const carouselImgs = document.querySelector(".carousel-imgs").children
const carouselIndicators = document.querySelector(".carousel-indicators").children
const timeIpnuts = document.querySelectorAll(".input-time input")
const fee = document.querySelector(".fee")
const signout = document.querySelector(".signout")
let carouselStatus = {
  now: 0,
  previousIsActive: false,
  nextIsActive: true
}
carouselBtns.forEach( btn => {
  btn.addEventListener("click", function(){
    let direction = btn.dataset.direction
    carouselRun(direction)
  })
})
timeIpnuts.forEach( input => {
  input.addEventListener("click", function(){
    let value = input.value
    fee.textContent = `新台幣 ${value} 元`
  })

  
})


function getData(){
  return fetch(`/api/attraction/${id}`)
  .then( res => res.json() )
  .then( data => data.data )
}

// 將資料塞入頁面
function render(data){
  let { name, category, mrt, images, description, address, transport } = data

  let title = document.querySelector(".title")
  title.textContent = name
  
  let subtitle = document.querySelector(".subtitle")
  subtitle.textContent = `${ category } at ${ mrt }`
  
  let imgs = document.querySelector(".carousel-imgs")
  let indicators = document.querySelector(".carousel-indicators")
  images.forEach( (url, i) => {
    let img = document.createElement("img")
    img.setAttribute("src", url)
    let indicator = document.createElement("div")
    indicator.classList.add("indicator")

    if(i == 0){
      img.classList.add("active")
      indicator.classList.add("active")
    }

    imgs.append(img)
    indicators.append(indicator)
  })

  let descripDiv = document.querySelector(".description .content")
  descripDiv.textContent = description

  let addressDiv = document.querySelector(".address .content")
  addressDiv.textContent = address

  let transportDiv = document.querySelector(".transport .content")
  transportDiv.textContent = transport

}

async function init(){
  let data = await getData()
  render(data)
}

function carouselRun(direction){
  let { now } = carouselStatus
  if(direction == "next"){
    if(now == carouselImgs.length - 1){
      return
    }
    carouselStatus.now += 1

    carouselImgs[carouselStatus.now - 1].classList.remove("active")
    carouselIndicators[carouselStatus.now - 1].classList.remove("active")
    carouselImgs[carouselStatus.now].classList.add("active")
    carouselIndicators[carouselStatus.now].classList.add("active")
    // if(carouselStatus.now == carouselImgs.length - 1) {
    //   nextBtn.classList.add("hide")
    // }else{
    //   nextBtn.classList.remove("hide")
    // }
  }else if(direction == "previous"){
    if(now == 0){
      return
    }
    carouselStatus.now -= 1

    carouselImgs[carouselStatus.now + 1].classList.remove("active")
    carouselIndicators[carouselStatus.now + 1].classList.remove("active")
    carouselImgs[carouselStatus.now].classList.add("active")
    carouselIndicators[carouselStatus.now].classList.add("active")
  }

  


  // carouselStatus.now += 1
  // console.log(carouselStatus.now);
}

init()






