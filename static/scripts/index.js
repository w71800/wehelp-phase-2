const scrollBtns = document.querySelectorAll(".scroll_btn")
const scroller = document.querySelector(".scroll_scroller")
const scrollContainer = document.querySelector(".scroll_container")
const content = document.querySelector(".content")
const searchBtn = document.querySelector(".header_icon")
const showStatus = document.querySelector(".status")
let directionCounter = {}
let queryStatus = {
  nextPage: 0,
  keyword: null
}

scrollBtns.forEach( btn => {
  let direction = btn.dataset.direction
  btn.addEventListener("click", function(){
    scrolling(direction, this)
  })
  directionCounter[direction] = 0
})
searchBtn.addEventListener("click", function(){
  let input = document.querySelector(".header_bar input")
  queryStatus.keyword = input.value
  queryStatus.nextPage = 0

  getData()
})
window.addEventListener("scroll", e => {
  // 底部位置等於 scrollTop + window.innerHeight
  let nowPos = document.documentElement.scrollTop;
  let totalHeight = document.documentElement.scrollHeight;
  let windowHeight = window.innerHeight;

  if (nowPos + windowHeight >= totalHeight) {
    // 必要要處理 debounce
    getData()
  }
})


function scrolling(direction, el){
  // 按下 <（backward） ：正向位移、按下 >（forward） ：負向位移
  let scrollLength = parseInt(window.getComputedStyle(scrollContainer).getPropertyValue('width'))
  let scrollerLength = parseInt(window.getComputedStyle(scroller).getPropertyValue('width'))
  // 可以 forward 的臨界次數
  let maxTime = scrollerLength / scrollLength
  let operator = direction == "forward"? -1 : 1
  // 紀錄上去點擊後的次數
  directionCounter[direction] += operator
  // 淨次數
  let positionState = Object.values(directionCounter).reduce((accumulator, currentValue) => accumulator + currentValue, 0)
  // 大於零的話則不動，將狀態值全歸零
  if(positionState > 0){
    directionCounter["forward"] = 0
    directionCounter["backward"] = 0
    positionState = 0
  // 大於最大次數（-3 > 2.3）的話，移動到最大位置
  }else if(positionState < -maxTime){
    console.log(-maxTime);
    console.log(Math.ceil(-maxTime));
    directionCounter["forward"] = Math.ceil(-maxTime)
    directionCounter["backward"] = 0
    positionState = Math.ceil(-maxTime)
  }
  
  console.log(positionState);
  let delta = scrollLength * positionState
  scroller.style.setProperty("transform", `translateX(${delta}px)`)

}
function makeBlock(obj){
  let { name: title, mrt, category, images } = obj

  const block = document.createElement('div')
  block.classList.add('block')

  const blockImg = document.createElement('div')
  blockImg.classList.add('block_img')

  const img = document.createElement('img')
  img.src = `${images[0]}`

  blockImg.appendChild(img)

  const blockInfo = document.createElement('div')
  blockInfo.classList.add('block_info')

  const titleEl = document.createElement('div')
  titleEl.classList.add('title')
  titleEl.textContent = title

  const mrtEl = document.createElement('div')
  mrtEl.classList.add('mrt')
  mrtEl.textContent = mrt

  const categoryEl = document.createElement('div')
  categoryEl.classList.add('category')
  categoryEl.textContent = category

  blockInfo.appendChild(titleEl)
  blockInfo.appendChild(mrtEl)
  blockInfo.appendChild(categoryEl)

  block.appendChild(blockImg)
  block.appendChild(blockInfo)

return block 
}
// 抓到資料之後製作 block 並往後塞
function getData(){
  /* 
  ** 抓到 data 後將 nextPage 值要塞進去，之後的換頁請求就是由 nextPage 來決定
  ** 要搜尋 keyword 之前，要先把值加入全域的狀態變數，並把 nextPage 歸零 
  */

  let { nextPage: page, keyword } = queryStatus
  let queryStr = `page=${ page }`
  if(keyword){
    queryStr += `&keyword=${keyword}`
  }

  fetch(`api/attractions?${queryStr}`)
  .then( res => res.json() )
  .then( res => {
    let { data, nextPage } = res
    
    if(res.error){
      console.log("錯誤");
    }else{
  
      for(item of data){
        let block = makeBlock(item)
        content.appendChild(block)
      }
  
      queryStatus.nextPage = nextPage
      console.log(queryStatus);
    }
  })
  .catch( e => {
    console.log(e);
  })

}
function stringQueryer(str){
  queryStatus.keyword = str
  queryStatus.nextPage = 0
  while(content.firstChild){
    content.removeChild(content.firstChild)
  }

  getData()
}
function renderStatus(prosses){
  /**
   * 1. 剛載入時新抓資料時或關鍵字搜尋時：show 搜尋中、content 高度固定且資料清空 → 載入完畢 → 拔掉 show、回歸初始高度 → 交由 getData 來塞入
   * 2. 錯誤時： show 無此資料
   * 3. 繼續載入下一頁資料
   */
  if(prosses == "searching"){
    while(content.firstChild){
      content.removeChild(content.firstChild)
    }
    content.style.setProperty("height", "300px")
    showStatus.classList.add("show")
  }else if(prosses == "no data"){
    showStatus.textContent = "無此資料"
    content.style.setProperty("height", "300px")
    showStatus.classList.add("show")
  }else if(process == "next page"){
    content.style.setProperty("height", "300px")
    showStatus.classList.add("show")
  }
}
function init(){
  fetch("api/mrts")
  .then( res => res.json() )
  .then( res => {
    let { data } = res

    for(item of data){
      let elMrt = document.createElement("div")
      elMrt.classList.add("mrt")
      elMrt.textContent = item
      elMrt.addEventListener("click", function(){
        let input = document.querySelector(".header_bar input")
        
        input.value = this.textContent

        stringQueryer(this.textContent)
      })

      scroller.append(elMrt)
    }  
  })
  getData()

}

init()
