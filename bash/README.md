## 關於B01.sh
此bash script檔的用途為輔助生成gaussian計算軟體的輸入檔。透過將已有的.gjf、.log格式，提取關鍵原子座標資訊，並透過使用者輸入所需的計算參數，以生成對應的.com檔供mksh檔(另一個事先寫好的script檔)進行job遞送。

## 功能展示
預設為4CPU、512MW的記憶體，計算用的hybrid functional是b3lyp，basis set是cc-pVTZ
1. 選項1：可讓使用者批量將gjf檔轉成com檔
2. 選項2：可讓使用者批量將log檔轉成com檔
3. 選項3：可讓使用者自行更改
4. 選項3a：可將目前的設定還原回default設定
5. 選項3b：可更改目前的設定為使用者自訂
6. 選項4：可讓使用者實現批量改名
7. 選項5：可讓使用者實現批量送job
