const url = window.location.href;
const id = url.match(/attraction\/(\d+)/)[1]

function getData(){
  return fetch(`/api/attraction/${id}`)
  .then( res => res.json() )
  .then( data => data.data )
}

// 將資料塞入頁面
function render(){

}

async function init(){
  let data = await getData()
}




