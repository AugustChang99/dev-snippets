//=================================================
//【求平方和】
// let form_str = `
// <style>
//   [type=number] {font-size:20px; width:100px;}
// </style>
// <form action="">
//   <p>
//     <span>平方和 = </span>
//     <span id="ans">...</span>
//   </p>
//   <input type="number" id="initial_value" placeholder="起始值">
//   <input type="number" id="end_value" placeholder="結束值">
//   <button type="button" id="calcbtn">計算</button>
// </form>
// `;

// document.body.insertAdjacentHTML('beforeend', form_str)

// calcbtn.addEventListener('click', function(){
//   calc(Number(initial_value.value), Number(end_value.value));
// });
// //------------------------------------------------------------
// let i;
// function  calc(start_value, end_value = 100){
//   sum_of_squares = 0;
//   // console.log(start_value, end_value);
//   // console.log(typeof start_value, typeof end_value);
//   for (i = start_value; i <= end_value; i++){
//     sum_of_squares += i ** 2;
//   }
//   ans.textContent = sum_of_squares;
// }

//================================================================
//【求和】
// function summation(...args){
//   console.log(args);
//   let sum = 0;
//   for (let arg of args) sum += arg;
//   return sum;
// }
// let result = summation(33, 5, 7);
// console.log(result);
// ============================================================
//【計算圓面積】
// let form_str = `
// <form action="">
//   <p id="answer">...</p>
//   <input type="text" id="radius" placeholder="半徑值...">
//   <button type="button" id="calcbtn">計算</button>
// </form>
// `;

// document.body.insertAdjacentHTML('beforeend', form_str)
//-------------------------------------------------------------
//正常寫法
// let circle_area;

// function calc(){
//   circle_area = Math.PI * (Number(radius.value) ** 2);
//   console.log(circle_area);
//   ex1.textContent = circle_area.toFixed(2); //取到小數點第二位
// }

// calcbtn.onclick = calc;
//--------------------------------------------------------------
//匿名函式
// calcbtn.onclick = function () {
//   circle_area = Math.PI * (Number(radius.value) ** 2);
//   console.log(circle_area);
//   ex1.textContent = circle_area.toFixed(2); //取到小數點第二位
// }
//--------------------------------------------------------------
//箭頭函式
// calcbtn.onclick = () => {
//   circle_area = Math.PI * (Number(radius.value) ** 2);
//   console.log(circle_area);
//   ex1.textContent = circle_area.toFixed(2); //取到小數點第二位
// }
// =============================================================
// 【JS的物件】
// const human01 = {};
// console.log(typeof human01);

// human01.first_name = "August";
// human01.last_name = "Chang";
// human01['gender'] = "male" //這樣寫是把gender:male加到human01的屬性裡面
// console.log(human01)


// const human02 = new Object();
// console.log(typeof human02);

// const humna03 = {
//   first_name: 'Francesco',
//   last_name: 'Ko',
//   age: 999,
//   city: 'Taoyuan City',
//   full_name:
//     function ()
//     {
//       return `${this.first_name} ${this.last_name}`;
//     },
// };
// console.log(humna03);
// console.log(humna03.full_name());

// function Person(first, last, age, eye)
// {
//   this.first_name = first;
//   this.last_name = last;
//   this.age = age;
//   this.eye_color = eye;
// }

// const my_father = new Person('John', 'Doe', 50, 'blue');
// console.log(my_father);
// const your_brother = new Person('Franceso', 'Ko', 999, 'brown');
// delete your_brother.age;
// console.log(your_brother);
//================================================================
