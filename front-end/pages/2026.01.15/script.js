//============================================================
//【範例：】
//------------------------------------------------------------
// const refs = document.getElementById("test01");
// console.log(refs);
// refs.textContent = 'World Peace!'
// refs.style.color = 'red';
// refs.innerHTML = `<marquee scrollAmount="10" direction="right">${refs.textContent}</marquee>`
//============================================================
//【範例：照片切換】
//------------------------------------------------------------
let image_urls = [
  'https://sp.yimg.com/ib/th/id/OIP.kPKeDT9S-__cusemFeqxaAHaLJ?pid=Api&w=148&h=148&c=7&rs=1', 
  'https://sp.yimg.com/ib/th/id/OIP.dl1a1oMcqGGejajw6eFWpAHaEn?pid=Api&w=148&h=148&c=7&rs=1',
  'https://sp.yimg.com/ib/th/id/OIP.-bJ9vjKFAixH748GH1BKhwHaFj?pid=Api&w=148&h=148&c=7&rs=1',
  'https://sp.yimg.com/ib/th/id/OIP.UjA5W6kup_wFjspeJu0uYAHaE8?pid=Api&w=148&h=148&c=7&rs=1',
  'https://sp.yimg.com/ib/th/id/OIP.UMsQng1Q70kE__jDGAZARgHaEp?pid=Api&w=148&h=148&c=7&rs=1',
]

let counter = 0;
let max_value = image_urls.length - 1
next_photo_btn.onclick = function(){
  if (counter > max_value)
    counter = 0;
  else
    now_image.src = image_urls[counter];
    counter++;
}
//============================================================
//【範例：顯示時間】
//------------------------------------------------------------
const btn = document.getElementById("myBtn");

// Add EventListener to btn
btn.addEventListener("click", function () {
  document.getElementById("demo").innerHTML = Date();
});
//============================================================
//【範例：滑鼠軌跡追踪】
//------------------------------------------------------------
// Let document listen for mousemove
document.addEventListener("mousemove", function (event) {
  document.getElementById("demo2").innerHTML =
  "X: " + event.clientX + " Y: " + event.clientY;
});
//============================================================
//【範例：mouseover、mouseout events】
//------------------------------------------------------------
const box = document.getElementById("box");

// Let box listen for mouseover
box.addEventListener("mouseover", function () {
  box.innerHTML = "Mouse is over me!";
});

// Let box listen for mouseout
box.addEventListener("mouseout", function () {
  box.innerHTML = "Mouse is out!";
});
//============================================================
//【範例：鍵盤偵測】
//------------------------------------------------------------
const k = document.getElementById("k");
// Let k listen for keydown
k.addEventListener("keydown", function (event) {
  document.getElementById("demo3").innerHTML = "You pressed: " + event.key;
});


const in01 = document.getElementById("in01");
// Let in01 listen for keydown
in01.addEventListener("keydown", function (event) {
// If key was "enter", then display text
  if (event.code === "Enter") {
    document.getElementById("demo4").innerHTML = "Enter was pressed!";
  }
});
//============================================================
//【範例：時鐘】
//------------------------------------------------------------
// Call showTime every 1000 millisec
setInterval(showTime, 1000);

// Function to display the time
function showTime() {
  const d = new Date();
  document.getElementById("clock").innerHTML =
  d.getHours() + ":" + d.getMinutes() + ":" + d.getSeconds();
}
//============================================================
//【範例：JS類別】
//------------------------------------------------------------
class Car{
  constructor(name,year){
    this.name = name;
    this.year = year;
  }

  //一般成員函式
  age(){
    const today = new Date();
    return today.getFullYear() - this.year;
  }

  //靜態成員函式(前面要加static，靜態函式不需要建實例就能用)
  static location(){
    return "Earth";
  }
}

const myCar1 = new Car('BMW', 2003);
document.getElementById("ex_car").innerHTML = myCar1.name
document.getElementById("ex_year").innerHTML = myCar1.year
document.getElementById("ex_age").innerHTML = myCar1.age()
document.getElementById("ex_location").innerHTML = Car.location()
//============================================================