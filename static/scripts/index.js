const scrollBtns = document.querySelectorAll(".scroll_btn")
const scroller = document.querySelector(".scroll_scroller")
const scrollContainer = document.querySelector(".scroll_container")
let directionCounter = {}


scrollBtns.forEach( btn => {
  let direction = btn.dataset.direction
  btn.addEventListener("click", function(){
    scrolling(direction, this)
  })
  directionCounter[direction] = 0
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
  let positionState = Object.values(directionCounter).reduce((accumulator, currentValue) => accumulator + currentValue, 0);
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