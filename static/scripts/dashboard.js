import { checkSign, loadingControl, notifyAuthed } from './utility.js'
const spanToggle = document.querySelector("#toggle")
const ordersDiv = document.querySelector(".orders")
const signoutDiv = document.querySelector("#header .signout")
const welcomeTitleDiv = document.querySelector("#header .title")
const ordersHintDiv = document.querySelector(".orders .hint")
const footerDiv = document.querySelector("#footer")


async function init(){
  let user = await checkSign()
  if(!user){
    window.location.href = "/"
    return
  }
  notifyAuthed(user)

  welcomeTitleDiv.textContent = `歡迎！ ${user.name}！`

  let data = await getOrders()
  let orders = data.data
  console.log(orders);
  if(!orders){
    footerDiv.classList.add("fixed")
  }else{
    ordersHintDiv.classList.add("inactive")
    orders.sort((order1, order2) => order2.payment - order1.payment )
    for(let order of orders){
      let el = makeOrder(order)
      ordersDiv.append(el)
    }
  }

  
  let ordersHeight = window.getComputedStyle(ordersDiv).height
  ordersDiv.style.height = ordersHeight
  loadingControl()

}

function makeTrip(dataObj) {
  let { attraction, date, time } = dataObj;

  let trip = document.createElement("div");
  trip.classList.add("trip");

  let img = document.createElement("img");
  img.setAttribute("src", attraction.image[0]);
  img.setAttribute("alt", "");

  let info = document.createElement("div");
  info.classList.add("info");

  let infoName = document.createElement("div");
  infoName.classList.add("info_name");
  infoName.textContent = "台北一日遊：";

  let infoNameSpan = document.createElement("span");
  infoNameSpan.textContent = attraction.name;

  infoName.appendChild(infoNameSpan);

  let infoDate = document.createElement("div");
  infoDate.classList.add("info_date");
  infoDate.textContent = "日期：";

  let infoDateSpan = document.createElement("span");
  infoDateSpan.textContent = date;

  infoDate.appendChild(infoDateSpan);

  let infoTime = document.createElement("div");
  infoTime.classList.add("info_time");
  infoTime.textContent = "時間：";

  let infoTimeSpan = document.createElement("span");
  infoTimeSpan.textContent = time;

  infoTime.appendChild(infoTimeSpan);

  let infoAddress = document.createElement("div");
  infoAddress.classList.add("info_address");
  infoAddress.textContent = "地點：";

  let infoAddressSpan = document.createElement("span");
  infoAddressSpan.textContent = attraction.address;

  infoAddress.appendChild(infoAddressSpan);

  info.appendChild(infoName);
  info.appendChild(infoDate);
  info.appendChild(infoTime);
  info.appendChild(infoAddress);

  trip.appendChild(img);
  trip.appendChild(info);

  return trip;
}

function getOrders(){
  return fetch(`/api/orders`, {
    headers: {
      Authorization: `Bearer ${localStorage.token}`
    }
  })
  .then( res => res.json() )
}

function makeOrder(orderData) {
  let { number, price, trips, payment } = orderData
  let orderDiv = document.createElement("div");
  orderDiv.classList.add("order");

  let orderNumberDiv = document.createElement("div");
  orderNumberDiv.classList.add("order_number");
  orderNumberDiv.textContent = `訂單編號：${number}`;

  let orderStatusSpan = document.createElement("span");
  orderStatusSpan.classList.add("order_status");
  orderStatusSpan.textContent = payment == 0? `(已付款)` : `(未付款)`
  let statusClass = payment == 0? "paid" : "unpaid"
  orderStatusSpan.classList.add(statusClass)

  orderNumberDiv.appendChild(orderStatusSpan);

  let tripsDiv = document.createElement("div");
  tripsDiv.classList.add("trips");
  for(let trip of trips){
    tripsDiv.append(makeTrip(trip))
  }

  let totalPriceDiv = document.createElement("div");
  totalPriceDiv.classList.add("total_price");
  totalPriceDiv.textContent = `總價：新台幣 ${price} 元`;

  orderDiv.appendChild(orderNumberDiv);
  orderDiv.appendChild(tripsDiv);
  orderDiv.appendChild(totalPriceDiv);

  return orderDiv;
}

init()

signoutDiv.onclick = () => {
  let yes = confirm("確定要登出了嗎？")
  if(!yes) return
  
  localStorage.token = null
  window.location.href = "/"
}

spanToggle.onclick = function(){
  let img = this.querySelector("img")
  let span = this.querySelector("span")
  let orders = this.nextElementSibling
  img.classList.toggle("fold")
  orders.classList.toggle("fold")
  if(orders.classList.contains("fold")){
    span.textContent = "展開"
  }else{
    span.textContent = "收合"
  }
}

