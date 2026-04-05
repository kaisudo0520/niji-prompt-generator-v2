流程：
1. 將以下模板做成一支程式方便輸出
```
{人物與鏡頭}, {服裝與配件}, {髮色與瞳色}, {表情與動作}, {主色調/光芒色彩}, {打光類型}, luminous brushwork, use of light and shadow, {場景與氛圍}, in the style of {繪師 A} and {繪師 B}, official art, anime aesthetic, {構圖修飾} --ar {比例} --niji 7 --s 750
```

2. 輸入描述 (簡單或清晰都可以)，並用LLM完善：{人物與鏡頭}, {服裝與配件}, {髮色與瞳色}, {表情與動作}, {主色調/光芒色彩}, {打光類型},{場景與氛圍} ,{構圖修飾}
a. {主色調/光芒色彩}：可做為選項INPUT或讓LLM自己選擇，例如：
```
- 夢幻/華麗： `pink and gold` (粉與金)、`rainbow-colored petals` (彩虹色花瓣)。
- 神祕/暗黑： `dark gray and light black` (深灰與淺黑)、`dark bronze and red` (深古銅與紅)、`stark black and white` (強烈的黑白)。
- 憂鬱/氣氛： `light bronze and blue` (淺古銅與藍)、`dark orange and white` (深橘與白)、`dark gray and red`(深灰與紅)。
```
b. {場景與氛圍}：讓LLM自己選擇，例如：
```
`picturesque garden as the background` (如畫般的風景花園背景)、`festive atmosphere` (節慶氛圍)、`grand amphitheater` (宏偉的圓形劇場)、`dark room` (幽暗的房間)

```
c. {打光類型}：讓LLM自己選擇，例如：`illuminated by soft, glowing lights`,`professional golden lighting`
d. {表情與動作}：讓LLM自己選擇，例如：
```
`striking a charming pose` (擺出迷人的姿勢)、`epic wind and earth bending shot` (史詩般的風與土之御氣鏡頭)、`dancing... playing with a graceful silver dolphin` (跳著舞...與優雅的銀色海豚玩耍)。
```
e. {構圖修飾}：讓LLM自己選擇，例如：`elegant composition`, `tilted frame`
f. {繪師 A} and {繪師 B}：讓使用者自己選擇1~2名繪師做為參考，選項如下：
`RURUDO`,`kousaki rui(光崎琉衣)`,`Anmi`,`Lake`,`Liduke`
並簡單在繪師選項旁邊標註其特色做為選擇參考。
g. {比例}：讓使用者自己選擇：16:9,1:1,4:3,3:4,9:16

3. 將翻譯成具體明確的英文及midjourney的語法，用逗號分隔，避免模糊氛圍詞等，並將{}去除後輸出，並有複製按鈕可複製提示詞