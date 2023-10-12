import { showSign, checkSign, loadingControl } from "./utility.js";

const url = window.location.href;
const id = url.match(/attraction\/(\d+)/)[1]
const carouselBtns = document.querySelectorAll(".carousel-btn")
const carouselImgs = document.querySelector(".carousel-imgs").children
const carouselIndicators = document.querySelector(".carousel-indicators").children
const timeIpnuts = document.querySelectorAll(".input-time input")
const fee = document.querySelector(".fee")
const submit = document.querySelector("input.panel-button[type='submit']")
const attractionForm = document.querySelector("#page-attraction .area form")

timeIpnuts.forEach( input => {
  input.addEventListener("click", function(){
    let price = input.dataset.price
    fee.textContent = `新台幣 ${price} 元`
    
    let feeInput = document.querySelector(".input-fee input")
    feeInput.value = price
    console.log(feeInput.value);
  })

  
})

submit.addEventListener("click", e => {
  e.preventDefault()
  
  let formData = new FormData(attractionForm)
  for(let data of formData){
    if(data[1] == ""){
      alert("日期未填寫")
      return
    }
  }

  checkSign()
    .then( data => {
      if(data == null){
        showSign()
      }else{
        fetch('/api/booking',{
          method: "POST",
          headers: {
            Authorization: `Bearer ${localStorage.token}`,
          },
          body: formData,
        })
        .then( res => res.json() )
        .then( res => {
          if(res.ok){
            window.location.href = "/booking"
          }else{
            alert(res.message)
          }
        })
      }
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

function init(){
  getData()
    .then( data => {
      const setCarousel = (function(){
        let now = 0
        let last, max = data.images.length - 1 
        
        return function(mode, param){
          if(mode == "direction"){
            let direction = param

            if(direction == "next"){
              now += 1
              last = now - 1
              
              if(now > max){
                // 最多是 7 但現在 now 是 8 了
                now = 0
                last = data.images.length - 1
              }
            }
            if(direction == "previous"){
              now -= 1
              last = now + 1
              
              if(now < 0){
                // 最小是 0 但現在 now 是 -1 了
                now = data.images.length - 1
                last = 0
              }
            }
          }
          if(mode == "index"){
            let index = param

            last = now
            now = index
          }
          
          
          let nowImg = carouselImgs[now]
          let nowIndicator = carouselIndicators[now]
          let lastImg = carouselImgs[last]
          let lastIndicator = carouselIndicators[last]
          
          lastImg.classList.remove("active")
          lastIndicator.classList.remove("active")
          nowImg.classList.add("active")
          nowIndicator.classList.add("active")
        }
      })();

      render(data)
      loadingControl()
      carouselBtns.forEach( btn => {
        btn.addEventListener("click", function(){
          let direction = btn.dataset.direction
          setCarousel("direction", direction)
        })
      })
      Array.from(carouselIndicators).forEach( (indicator, index) => {
        indicator.onclick = () => {
          setCarousel("index", index)
        }
      })
      

    })
  
  document.querySelector("input[name='attractionId']").value = window.location.href.match(/\/(\d+)$/)[1]
}


init()






