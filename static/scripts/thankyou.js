import { checkSign } from './utility.js'
const thankyouName = document.querySelector("span.name")
const orderNumber = document.querySelector(".number span")

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

async function init(){
  if(localStorage.token){
    let user = await checkSign()
    let order = await getOrder()
    console.log(order);
    thankyouName.textContent = user.name
    orderNumber.textContent = order.data.number
  }else{
    window.location.href = "/"
  }

}

init()