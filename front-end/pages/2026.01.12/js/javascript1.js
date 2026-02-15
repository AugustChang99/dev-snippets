//================================================================
//【範例：更改特定id元素內的文字】
//----------------------------------------------------------------
  //寫法1
  //document.getElementById('demo').innerText = 'hellow world';

  //寫法2(有的瀏覽器可能不支援把id直接加在變數名稱的前面)
  //demo.innerText = 'hellow world';
//================================================================
//【範例：根據系統時間更改特定id元素內的文字】
  //Date()在此為Date類別的建構函式
//----------------------------------------------------------------
  //寫法1
    if (new Date().getHours() < 18){
      demo.innerText = "日安";
    }
  //寫法2
  
//================================================================
//【範例：數字判斷】
//----------------------------------------------------------------
//寫法1
//        function sub(){
//          const inputValue = document.getElementById("exercise1_1").value;
//          document.getElementById("exercise1_2").innerText = "";
//          if (Number(exercise1_1.value) > 5){
//            document.getElementById("exercise1_3").innerText = "數字" + inputValue + "是一個大於5的數字";
//          }
//          else if(Number(exercise1_1.value) < 5){
//            document.getElementById("exercise1_3").innerText = "數字" + inputValue + "是一個小於5的數字";                        
//          }
//          else if(Number(exercise1_1.value) == 5){
//            document.getElementById("exercise1_3").innerText = "數字" + inputValue + "是一個等於5的數字";                        
//          }
//          else{
//            document.getElementById("exercise1_3").innerText = "格式不正確，請輸入數字";                        
//          }
//        }

  //寫法2
        function sub(){
          const inputValue = document.getElementById("exercise1_1").value;
          document.getElementById("exercise1_2").innerText = "";
          switch (true){
          case Number(exercise1_1.value) > 5:
          document.getElementById("exercise1_3").innerText = "數字" + inputValue + "是一個大於5的數字";
            break;
          case Number(exercise1_1.value) < 5:
          document.getElementById("exercise1_3").innerText = "數字" + inputValue + "是一個小於5的數字";
            break;
          case Number(exercise1_1.value) == 5:
          document.getElementById("exercise1_3").innerText = "數字" + inputValue + "是一個等於5的數字";
            break;
          default:
          document.getElementById("exercise1_3").innerText = "格式不正確，請輸入數字";  
          }
        }
//================================================================
//【範例：輸出國籍】
//----------------------------------------------------------------
    function sub2(){
      const selectEl = document.getElementById("exercise2_1");
      const inputText = selectEl.options[selectEl.selectedIndex].text;
      document.getElementById("exercise2_2").innerText = inputText;

      if(inputText === "台灣"){
        document.getElementById("exercise2_3").innerText = "本國居民";
      }
      else if(inputText !== "台灣"){
        document.getElementById("exercise2_3").innerText = "外籍人士";
      }
    }
//====================================
//【範例：今天星期幾】
//-------------------------------------
  let date = new Date().getDay();
  let week = ['日','一','二','三','四','五','六']
  document.getElementById('exercise3').innerText = '今天星期' + week[date];
//====================================