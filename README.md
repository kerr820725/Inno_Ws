 

- **async 執行指令**>  python3 async_main.py run=chat totaluser=1000  vend=vd002  before_delay=60:120:180 semaphore=5  chat_iid=1492826  chat_sport=football  chat_delay=10 chat_send=false bet_sport_iid=1559332 bet_sport_sid=0 bet_inplay=false  deposit_open=true  before_api=bet

- config 參數說明: 
    - **run** : rain(紅包雨)  , chat(聊天室) , sport(推送體育相關)  , **帶多個(run=rain,chat,sport)** 
    - **totaluser** : 用戶數量
    - **vend**: 業主
    - **before_delay** : 60:120:180 , api 在程式分配 range比例 , 數值越大 delay越久
    - **semaphore** : 同時登入量 
    - **chat_iid** : 聊天室 / 體育訂閱  都會拿來用此iid
    - **chat_sport** : 聊天室 連線
    - **chat_delay** : 聊天室 發話delay
    - **chat_send** : 聊天室是否要發話 (**true/false**)
    - **bet_sport_iid** : 體育投注指定 iid
    - **bet_sport_sid** : 體育投注指定sid , 如果帶 0 會程式自己找 ,並根據 **bet_inplay**滾球與否
    - **bet_inplay** : 體育投注指定inplay (**true/false**)
    - **before_api**  : api要打的項目 sport(體育) , bet(只有投注) ,  **帶其他會做 sport和platform**
    - **deposit_open**: 是否要做後台充值(true/false)


"# Inno_Ws" 
