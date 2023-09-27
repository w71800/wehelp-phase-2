import { checkSign } from './utility.js'
const bookingsContainer = document.querySelector("#bookings .container")
const bookingsStatus = document.querySelector("#bookings .container .status")
const title = document.querySelector("#bookings .container .title")
const totalPrice = document.querySelector("#info .container .total")

async function init() {
  let isSign = await checkSign()
  console.log(isSign);

  if(isSign){
    title.textContent = `您好，${isSign.name}，待預訂的行程如下：`
    getBookings()
      .then( bookings => render(bookings) )
  }else{
    window.location.href = "/"
  }
}

function makeBooking(dataObj) {
  let { attraction, date, time, price} = dataObj
  
  let booking = document.createElement("div");
  booking.classList.add("booking");

  let img = document.createElement("img");
  img.setAttribute("src", `${attraction.image[0]}`);
  img.setAttribute("alt", "");
  img.classList.add("attraction")

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

  let infoFee = document.createElement("div");
  infoFee.classList.add("info_fee");
  infoFee.textContent = "費用：";

  let infoFeeSpan = document.createElement("span");
  infoFeeSpan.textContent = price;

  infoFee.appendChild(infoFeeSpan);

  let infoAddress = document.createElement("div");
  infoAddress.classList.add("info_address");
  infoAddress.textContent = "地點：";

  let infoAddressSpan = document.createElement("span");
  infoAddressSpan.textContent = attraction.address;

  infoAddress.appendChild(infoAddressSpan);

  info.appendChild(infoName);
  info.appendChild(infoDate);
  info.appendChild(infoTime);
  info.appendChild(infoFee);
  info.appendChild(infoAddress);

  let deleteButton = document.createElement("div");
  deleteButton.classList.add("delete");
  deleteButton.addEventListener("click", ()=>{
    confirm("確定要刪除嗎？")

    fetch("/api/booking", {
      method: "DELETE",
      headers: {
        "Authorization": `Bearer ${localStorage.token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ attractionId: attraction.id })
    })
    .then( res => res.json() )
    .then( res => {
      if(res.ok){
        window.location.href = "/booking"
      }
    }
    )
  })
  
  let deleteImg = document.createElement("img");
  deleteImg.setAttribute("src", "/static/imgs/delete.png");
  deleteImg.setAttribute("alt", "");
  

  deleteButton.appendChild(deleteImg);

  booking.appendChild(img);
  booking.appendChild(info);
  booking.appendChild(deleteButton);

  return booking;
}

function getBookings(){
  return fetch("/api/booking",{
    headers: {
      Authorization: `Bearer ${localStorage.token}`
    }
  })
  .then( res => res.json() )
}

function render(datas){
  if(datas.data == null && datas.data != undefined){
    bookingsStatus.classList.add("active")
    totalPrice.textContent = `總價：新台幣 ${0} 元`
    
    return
  }

  for(let booking of datas){
    console.log(booking.data);
    bookingsContainer.append(makeBooking(booking.data))
  }

  bookingsStatus.classList.remove("active")
  let total = datas.reduce((total, currentObj) => total + currentObj.data.price, 0)
  totalPrice.textContent = `總價：新台幣 ${total} 元`
}


init()