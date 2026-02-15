/*=========================================================================
【DOM tree主要架構&定位記號查詢】@?

  說明：Ctrl+F輸入對應的定位用記號可快速跳至該段落。輸入 @? 可快速跳回本段落。

  定位記號             DOM tree主要架構
--------------------------------------------------
| @html       | html                             |
| @head       |   |-head                         |
| @body       |   |-body                         |
| @B#1        |   |-div(class:top-container)     |
| @header     |     |-header                     |
| @nav        |     |-nav                        |
| @B#2        |   |-div(class:container)         |
| @B2L        |     |-div(id:left_panel)         |
| @B2M        |     |-div(id:main_frame)         |
| @B2R        |     |-div(id:right_panel)        |
| @footer     |   |-footer                       |
--------------------------------------------------

===========================================================================*/
//【常數宣告賦值】
const toggleBtnLeft = document.getElementById('toggle_btn_left');
const toggleBtnRight = document.getElementById('toggle_btn_right');

const leftPanel = document.getElementById('left_panel');
const leftMenuItems = document.querySelectorAll('.left_panel_list');

const rightPanel = document.getElementById('right_panel');
const rightMenuItems = document.querySelectorAll('.right_panel_list');
//=========================================================================
//【導覽列左側漢堡包功能】@nav
  toggleBtnLeft.addEventListener('click', function(e) {

    //阻止預設的跳轉行為(雖然已經是 javascript:void(0))
    e.preventDefault();

    //切換collapsed類別(如果沒該類別就加上，有的話就移除)
    leftPanel.classList.toggle('collapsed');

  });
/*--------------------------------------------------------------------------*/
//【導覽列右側漢堡包功能】@nav
  toggleBtnRight.addEventListener('click', function(e) {

    //阻止預設的跳轉行為(雖然已經是 javascript:void(0))
    e.preventDefault();
    
    //切換collapsed類別(如果沒該類別就加上，有的話就移除)
    rightPanel.classList.toggle('collapsed');

  });
//=========================================================================
//【將左側面板選中的項目進行標記】@B2L
  leftMenuItems.forEach(item => {
    item.addEventListener('click', function() {

      //移除所有項目的active類別
      leftMenuItems.forEach(i => i.classList.remove('active'));
      
      //幫當前點擊的項目加上active類別
      this.classList.add('active');

    });
  });
//=========================================================================
//【將右側面板選中的項目進行標記】@B2L
  rightMenuItems.forEach(item => {
    item.addEventListener('click', function() {

      //移除所有項目的active類別
      rightMenuItems.forEach(i => i.classList.remove('active'));
      
      //幫當前點擊的項目加上active類別
      this.classList.add('active');

    });
  });
//--------------------------------------------------------------------------
//【點擊右側面板的項目後，觸發遮罩】@B2L
  function zoomImage(imgSrc) {
    const overlay = document.getElementById('image_overlay');
    const overlayImg = document.getElementById('overlay_img');
    const rightPanel = document.getElementById('right_panel');

    //設定圖片並顯示遮罩
    overlayImg.src = imgSrc;
    overlay.style.display = 'flex';

    //同時把右側面板處理掉
    if (rightPanel) {
      rightPanel.classList.add('collapsed');
    }

  }

  // 點擊遮罩任何地方就關閉
  document.getElementById('image_overlay').addEventListener('click', function() {
    this.style.display = 'none';
  });
//=========================================================================