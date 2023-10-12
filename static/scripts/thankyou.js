import { checkSign, loadingControl } from './utility.js'
const thankyouName = document.querySelector("span.name")
const orderNumber = document.querySelector(".number span")
const tripsDiv = document.querySelector(".trips")
const totalDiv = document.querySelector(".total_price")

function getNumber(){
  let url = window.location.href
  let urlObject = new URL(url);

  let number = urlObject.searchParams.get("number")

  console.log(number);
  return number
}

function getOrder(){
  return fetch(`/api/order/${getNumber()}`, {
    headers: {
      Authorization: `Bearer ${localStorage.token}`
    }
  })
  .then( res => res.json() )
}

function makeTrip(dataObj) {
  let { attraction, date, time } = dataObj;

  let order = document.createElement("div");
  order.classList.add("trip");

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

  order.appendChild(img);
  order.appendChild(info);

  return order;
}


async function init(){
  if(localStorage.token){
    let user = await checkSign()
    let order = await getOrder()
    let { data } = order
    
    for(let trip of data.trips){
      tripsDiv.append(makeTrip(trip))
    }
    totalDiv.textContent = `總價：新台幣 ${data.price} 元`
    thankyouName.textContent = user.name
    orderNumber.textContent = data.number
    loadingControl()
  }else{
    window.location.href = "/"
  }

}

init()