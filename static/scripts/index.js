import { loadingControl, notifyAuthed, checkSign } from './utility.js'

const scrollBtns = document.querySelectorAll(".scroll_btn")
const scroller = document.querySelector(".scroll_scroller")
const scrollContainer = document.querySelector(".scroll_container")
const content = document.querySelector(".content")
const searchBtn = document.querySelector(".header_icon")
const showStatus = document.querySelector(".status")
const mainDiv = document.querySelector("#main")
let directionCounter = {}
let queryStatus = {
  nextPage: null,
  isQuerying: false
}


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

function makeBlock(obj) {
  let { id, name: title, mrt, category, images } = obj;

  const block = document.createElement('div');
  block.classList.add('block');

  const blockImg = document.createElement('div');
  blockImg.classList.add('block_img');

  const link = document.createElement('a');
  link.href = `/attraction/${id}`;

  const img = document.createElement('img');
  img.src = `${images[0]}`;

  link.appendChild(img);
  blockImg.appendChild(link);

  const blockInfo = document.createElement('div');
  blockInfo.classList.add('block_info');

  const titleEl = document.createElement('div');
  titleEl.classList.add('title');
  titleEl.textContent = title;

  const mrtEl = document.createElement('div');
  mrtEl.classList.add('mrt');
  mrtEl.textContent = mrt;

  const categoryEl = document.createElement('div');
  categoryEl.classList.add('category');
  categoryEl.textContent = category;

  blockInfo.appendChild(titleEl);
  blockInfo.appendChild(mrtEl);
  blockInfo.appendChild(categoryEl);

  block.appendChild(blockImg);
  block.appendChild(blockInfo);

  return block;
}

// 抓取資料
function getData(page, keyword){
    if(page == null) return

    let queryStr = keyword ? `page=${ page }&keyword=${keyword}` : `page=${ page }`
    let url = "api/attractions?" + queryStr
    
    return fetch(url)
      .then( res => {
        let { status } = res
        return res.json()
          .then( data => {
            return { status, ...data }
          })
      })
  }

// 載入：抓到資料並渲染
function load(page, keyword){
    let promise = new Promise((resolve, reject) => {
      
      queryStatus.isQuerying = true
      getData(page, keyword)
        .then( res => {
          let { nextPage } = res
          queryStatus.isQuerying = false
          queryStatus.nextPage = nextPage
          
          renderBlocks(res)
          resolve("getAttraction done")
        })
        .catch( e => {
          // console.log(e);
          reject(e)
        })
    })
    return promise
}

function clearOutBlocks(){
  while(content.firstChild){
    content.removeChild(content.firstChild)
  }
}

function renderBlocks(resObj){
  if(resObj.error){
    renderStatus(res.message)
  }
  
  let { data } = resObj
  for(let item of data){
    let block = makeBlock(item)
    content.appendChild(block)
  }
}

function renderStatus(statusStr){
  /**
   * 1. 剛載入時新抓資料時或關鍵字搜尋時：show 搜尋中、content 高度固定且資料清空 → 載入完畢 → 拔掉 show、回歸初始高度 → 交由 getData 來塞入
   * 2. 錯誤時： show 無此資料
   * 3. 繼續載入下一頁資料：show 搜尋中
   * 4. 無下頁資料：show 已無更多資料
   */
  if(statusStr == undefined){
    showStatus.classList.remove("show")
    showStatus.textContent = ""
  }
  showStatus.classList.add("show")
  showStatus.textContent = statusStr

}

function getMRTs(){
  return fetch("api/mrts")
    .then( res => res.json() )
    .then( res => {
      let { data } = res

      for(let item of data){
        let elMrt = document.createElement("div")
        elMrt.classList.add("mrt")
        elMrt.textContent = item
        elMrt.addEventListener("click", function(){
          let input = document.querySelector(".header_bar input")
          renderStatus()
          input.value = this.textContent
          mainDiv.classList.add("span")
          clearOutBlocks()
          load(0, input.value)
            .then(()=>{
              mainDiv.classList.remove("span")
              // setTimeout(()=>{
              //   mainDiv.classList.remove("span")
              // },1000)
            })
        })

        scroller.append(elMrt)
      } 
      return "get MRT Done"
    })
}

async function init(){
  let isSign = await checkSign()
  if(isSign){
    notifyAuthed(isSign)
  }

  let promise1 = getMRTs()
  let promise2 = load(0)

  Promise.all([ promise1, promise2 ])
    .then( () => { 
      loadingControl()
    })
    .catch( e => {
      console.log(e);
    })
}

function debounce(func, delay) {
  let timer;

  return function () {
    const context = this;
    const args = arguments;

    clearTimeout(timer);

    timer = setTimeout(function () {
      func.apply(context, args);
    }, delay);
  };
}

scrollBtns.forEach( btn => {
  let { direction } = btn.dataset
  btn.onclick = function(){
    scrolling(direction, this)
  }
  directionCounter[direction] = 0
})

searchBtn.onclick = () => {
  let input = document.querySelector(".header_bar input")
  let keyword = input.value
  queryStatus.nextPage = null
  
  clearOutBlocks()
  renderStatus()
  load(0, keyword)

}
  
window.onkeyup = (e) => {
  if(e.code == "Enter"){
    let input = document.querySelector(".header_bar input")
    let keyword = input.value
    queryStatus.nextPage = null
  
    clearOutBlocks()
    renderStatus()
    load(0, keyword)
  }
}
  
window.onscroll = () => {
  let scrollTop = document.documentElement.scrollTop;
  let totalHeight = document.documentElement.scrollHeight;
  let windowHeight = window.innerHeight;

  
  if (scrollTop + windowHeight >= totalHeight && content.children.length != 0 && queryStatus.isQuerying == false) {
    if(queryStatus.nextPage == null){
      renderStatus("沒有其他資料了")
      return
    }
    renderStatus("搜尋中...")
    debounceLoad(queryStatus.nextPage)
  }
}

init()
let debounceLoad = debounce(load, 300)