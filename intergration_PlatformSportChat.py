import stomper
import random,datetime,threading,time
import websocket
import json , configparser
import sys  , asyncio
from Function import platform_function as platform
from Function import general_function as general
import nest_asyncio , pytz

from Logger import create_logger

log = create_logger()

sys.setrecursionlimit(20000)
#nest_asyncio.apply()
tw = pytz.timezone('Asia/Taipei')

if sys.platform != 'win32': # docker
    csv_mess_name = 'docker_csv_chat'
else:
    csv_mess_name =  'on_message'+'_csv_'+datetime.datetime.now().astimezone(tw).strftime("%Y%m%d%H%M") # 監聽msg 的 csv 另外存一個
def writeLog(content ,filename  ):
    try:
        with open(filename+'.txt', 'a', newline='', encoding='utf-8') as csvfile:
                csvfile.writelines(str(datetime.datetime.now().astimezone(tw).strftime("%Y-%m-%d %H:%M:%S.%f"))+ " " +content) 
    except Exception as e :
        print(e.with_traceback)


def retrun_write_content(acc , action , start_time , end_time= '' , status_code = '' , diff = '' , response = ''    ):
    write_content = {
            "user":acc,
            "action": action ,
            "start_time": start_time ,
            "end_time":  end_time ,
            "diff": diff  ,
            "status_code":  status_code ,
            "response": response
        } 
    return write_content


def chat_send_msg(ws  , acc , csv_name ): # 聊天室  發送訊息

    #send_msg = "autoTest%s"%random.randint(1000, 9999)
    try:
        now_time =  datetime.datetime.now().astimezone(tw).strftime('%H:%M:%S') # 會拿來當作發送訊息 . 把年 月 拿掉 , 後端 吐回訊息 會被 ****



        str_msg = json.dumps(  {"type":"message","target":"","data":{"self":True ,"message":  now_time }}   )
        #print('acc : %s send_chat_msg: %s'%(acc , str_msg ))l


        
        sub = stomper.send(dest =  f"/app/chat.{chat_iid}" , content_type =  "application/json" , msg = str_msg )
        
        ws.send( sub )    

       

        write_content = retrun_write_content(acc = acc  , action = 'send_msg'   , start_time = now_time , 
            end_time= '' , status_code = '' , diff = '' , response =  '{"self":True ,"message":  %s }'%now_time    )


        general.write_csv(csv_name, write_content)
        
       


    except Exception as e:
        #print('chat_send msg error: %s'%e)
        return False


def return_order_info(order_info , now_time ):
    bet_data = {"type":"betOrder","data":{"uuid":  order_info['orderno'] ,"ante":100,"totalAnte":"100","payout":0,"mayWinAmount":"47","netWin":-100,
    "parlayBet":False,"parlay":1,"option":1,"canceled":False,
    "details":[{"sid": order_info['sid']     ,"tournamentName": order_info['tournamentName']  ,"iid":chat_iid ,"homeName": order_info['homeName'] ,"awayName":order_info['awayName'] ,
    "kickOffTime": order_info['kickOffTime'] ,"odds": order_info['odds'] ,"market": order_info['market'] ,"betOn":"h","conditions":"","settle":0,
    "outright":False,"inplay":True,"period":"q2","stage":"","cashoutPeriod":"","cashoutStage":"","orderPhase":1,"homeScore":"28",
    "awayScore":"25","probability":"0.609900","vendor":"b","tid":order_info['tid'] ,"homeId": order_info['homeId']  , 
    "awayId":order_info['awayId'],"scoreType":"NORMAL","matchScore":{}}],
    "marketType":"EU","status":2,"cashOut":False,"safeFlag":True,"currency":"CNY","betTime":now_time }}

    return bet_data


def chat_bet(ws , acc , bet_dict , csv_name ): # 曬單 #221025004928-716631
    
    #while True:
    now_time =  datetime.datetime.now().astimezone(tw).strftime("%Y-%m-%d %H:%M:%S")
    try:
        order_data = bet_dict[acc] 
        bet_data = return_order_info(order_info = order_data  , now_time = now_time   )
    except Exception as e:
        #print('chat_bet error: %s'%e)
        return False

    try:
        str_msg = json.dumps(bet_data)

        sub = stomper.send(dest =  f"/app/chat.{chat_iid}" , content_type =  "application/json" , msg = str_msg )

        ws.send( sub )

        excel_msg = 'uuid: %s ,betTime: %s '%(bet_data['data']['uuid'] , bet_data['data']['betTime']    ) # excel 寫入訊息太長  , excle 顯示 會被塞滿
        write_content = retrun_write_content(acc = acc , action = 'send_bet'   , start_time = now_time , 
                end_time= '' , status_code = '' , diff = '' , response = excel_msg    )


        general.write_csv(csv_name, write_content)


    
        
    except Exception as e :
        #print('chat_bet send msg error: %s'%e)
        return False

def chat_vote(ws , vote , acc , csv_name  ): # 聊天室 投票
    #while True:
    try:
        str_msg = json.dumps(  {"type":"vote","data":{"result": vote }}     )
        #print('acc : %s  send_vote_msg: %s'%(acc , str_msg ))
        sub = stomper.send(dest =  f"/app/chat.{chat_iid}" , content_type =  "application/json" , msg = str_msg )
        ws.send( sub )

        write_content = retrun_write_content(acc = acc , action = 'send_vote'   , start_time = datetime.datetime.now().astimezone(tw).strftime('%H:%M:%S') , 
            end_time= '' , status_code = '' , diff = '' , response = str_msg    )


        general.write_csv(csv_name, write_content)


    except Exception as e :
        #print('chat_vote send msg error: %s'%e)
        return False

#體育 socket
def run(num, platform_url  , acc , filename , csv_name  , sport_ws_url):
    def on_msg(ws, msg):        
        #print(f"Msg({num}) : ", datetime.datetime.now().astimezone(tw).strftime('%m/%d %H:%M:%S'), " ")
        writeLog(content = f"No.{num} "+msg+"\n"  , filename = filename)        
        

    def on_error(ws, err):
        try :
            #writeLog(f"==== No.{num} Error: {err} \n")
            #print(f"==== No.{num} sport ws Error info: {err}")

            write_content = {
                "user":acc,
                "action": "Sport_WS_Error",
                "start_time": datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S'),
                "end_time":"",
                "status_code":  "" ,
                "diff": "",
                "response": str(err)
            } 


            general.write_csv(csv_name, write_content)

        except Exception as e :
            print(e.with_traceback)

    def on_closed(ws, status_code, close_msg):
        #print(f"==== No.{num}  sport ws Closed : ", datetime.datetime.now().astimezone(tw).strftime('%m/%d %H:%M:%S'), " status:",status_code, " , msg:",close_msg)        
        #writeLog(f"==== Closed.{num} msg:" + close_msg + " status_code:"+str(status_code) + "\n")
        
        write_content = {
                "user":acc,
                "action": "Sport_WS_Closed",
                "start_time": datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S'),
                "end_time":"",
                "status_code":str(status_code),
                "diff": "",
                "response":str(close_msg)
            } 


        general.write_csv(csv_name, write_content)

        #sport_ws( num = num ,   run_type = 'retry' , acc = acc  , sport_ws_url = sport_ws_url , csv_name = csv_name  , filename= filename     ) # 從新連線 ws

    def on_open(ws):
        ws.send("CONNECT\naccept-version:1.0,1.1,2.0")
        v = 1
        sub = stomper.subscribe(f"/topic/odds-diff/match/111111", v, ack="auto")
        ws.send(sub)
        v =v+ 1
        time.sleep(1)
        sub = stomper.subscribe(f"/topic/odds-diff/match/{chat_iid}", v, ack="auto")
        ws.send(sub)
        v=v+1
        time.sleep(1)
        sub = stomper.subscribe(f"/topic/match/inplay/info/{chat_iid}", v, ack="auto")
        ws.send(sub)
        v=v+1
        time.sleep(1)
        sub = stomper.subscribe(f"/topic/match/event", v, ack="auto")
        ws.send(sub)  
        
    ws = websocket.WebSocketApp(f"{sport_ws_url}/product/websocket/ws?referer={platform_url}", on_message=on_msg, on_error=on_error, on_close=on_closed)    
    ws.on_open = on_open    
    ws.run_forever(ping_interval=0,ping_timeout=30)



def run_chat(env , num, platform_url, stoken   , acc   , csv_name  , sport_ws_url):

    
    def on_msg(ws, msg):        
        #print(f"Chat Msg({num}) ", datetime.datetime.now().astimezone(tw).strftime('%m/%d %H:%M:%S'), " ")
        
        #print(msg)

        end_time , diff  = '', ''  
        now_time =  datetime.datetime.now().astimezone(tw).strftime('%H:%M:%S')
        now_time_date = datetime.datetime.strptime(now_time , '%H:%M:%S') 
        try:
            if 'CONNECTED' in msg:
                action = 'CONNECTED'
                split_msg = 'CONNECTED'
            else:
                split_msg = msg.split('\n\n')[1]   
                if '"type":"message"'  in   msg:
                    action = 'message'
                    split_msg = split_msg.replace('\x00' , '')
                    split_msg_dict = json.loads( split_msg  )

                    end_time = split_msg_dict['data']['message'] 
                    source = split_msg_dict['source']

                    split_msg = 'type: message , source: %s  , message: %s'%(source , end_time  )


                    try: # 監聽到 不是 時間格式
                        end_time_date =  datetime.datetime.strptime(end_time , '%H:%M:%S')  

                        diff = (now_time_date - end_time_date).seconds

                    except:
                        end_time = ''
                        diff = 'N/A'


                elif '"type":"voteResult"'  in   msg:
                    action = 'voteResult'
                
                elif '"type":"betOrder"' in msg:
                    action = 'betOrder'


                else:
                    action = 'others'

        except Exception as e:
            action = 'error_action'
            #print('error_action error: %s , msg: %s'%(e , msg)  )
            split_msg = msg

        #on_open(ws)
        write_content = {
            "user":acc,
            "action":  'on_msg_%s'%action   ,
            "start_time": now_time ,
            "end_time":  end_time  ,
            "status_code":  "" ,
            "diff": diff ,
            "response": split_msg
    } 
        

        general.write_csv(csv_mess_name, write_content  )

  
    def on_error(ws, err):
        try :
            #print(f"==== Chat No.{num} Error info: {err}")
            '''
            先註解調  斷線頻繁
            print(f"==== Chat No.{num} Error info: {err}")

            write_content = {
                "user":acc,
                "action": "Chat_WS_Error",
                "start_time": datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S'),
                "end_time":"",
                "status_code":  "" ,
                "diff": "",
                "response": str(err)
            } 


            general.write_csv(csv_name, write_content)
            '''
            pass

        except Exception as e :
            log.error(e.with_traceback)

    def on_closed(ws, status_code, close_msg ):
        
        '''
        # 先註解
        print(f"==== Chat No.{num} Closed : ", datetime.datetime.now().astimezone(tw).strftime('%m/%d %H:%M:%S'), " status:",status_code, " , msg:",close_msg)        


        write_content = {
                "user":acc,
                "action": "Chat_WS_Closed",
                "start_time": datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S'),
                "end_time":"",
                "status_code":str(status_code),
                "diff": "",
                "response":str(close_msg)
            } 


        general.write_csv(csv_name, write_content)
        '''

        chat_ws( num = num ,   run_type = 'retry' , acc = acc  , sport_ws_url = sport_ws_url , csv_name = csv_name) # 從新連線 ws

    def on_open(ws ):


        ws.send("CONNECT\naccept-version:1.1,1.0")
        v = 1
        sub = stomper.subscribe(f"/topic/chat.1111111", v, ack="auto")
        ws.send(sub)
        time.sleep(1)
        
        
        v = v+1
        sub = stomper.subscribe(f"/topic/chat.{chat_iid}", v, ack="auto")
        ws.send(sub)
        time.sleep(1)

        
    
        v = v+1
        sub = stomper.subscribe(f"/user/topic/chat.{chat_iid}", v, ack="auto")
        ws.send(sub)
        time.sleep(1)

        
        '''
        for chat_event_ in chat_event:
            if chat_event_ == 'msg':

                # 聊天室寄送訊息 
                t = threading.Thread(target= chat_send_msg , args= ( ws  , acc , csv_name   ) )
                t.start()  

        
            elif chat_event_ == 'bet':
                
                # 體育投注
                sport_parlay = platform.Sport_Parlay_Bet(   env = env  , csv_name = csv_name  ) 
                sport_parlay.parlay_info(   token = stoken , sport = chat_sport , acc = acc , inplay_type = 'false' , assign_iid = 'true' , sinlge ='true' ) # 抓資訊 抓一次就可
                order_info = sport_parlay.sport_bet(sport = chat_sport , token=stoken , acc = acc  , bet_amount= 100 , parlay_type= '' , single='true' , 
                assign_iid = 'true'    )

                t = threading.Thread(target= chat_bet , args= ( ws , acc , order_info  , csv_name) )
                t.start() 

            else: # vote
                vote_list = ['h', 'a', 'd' ]
                random.shuffle( vote_list ) 
                vote = vote_list[0]


                t = threading.Thread(target= chat_vote , args= ( ws , vote , acc  , csv_name  ) )
                t.start()  
        '''


        t =  threading.Thread(target= chat_all , args= (size_list , ws , acc  , csv_name , env ,stoken    ) )
        t.start()

        '''
        random.shuffle(size_list )
        chat_event_ = chat_event[0]
        
        
        if chat_event_ == 'msg':

            # 聊天室寄送訊息 
            loop.run_until_complete(         chat_send_msg( ws  , acc , csv_name     ))
            time.sleep(bet_delay)

        
        elif chat_event_ == 'bet':
            
            # 體育投注
            sport_parlay = platform.Sport_Parlay_Bet(   env = env  , csv_name = csv_name  ) 
            sport_parlay.parlay_info(   token = stoken , sport = chat_sport , acc = acc , inplay_type = 'false' , assign_iid = 'true' , sinlge ='true' ) # 抓資訊 抓一次就可
            order_info = sport_parlay.sport_bet(sport = chat_sport , token=stoken , acc = acc  , bet_amount= 100 , parlay_type= '' , single='true' , 
                assign_iid = 'true'    )

            loop.run_until_complete(chat_bet(ws , acc , order_info  , csv_name    )) 

        elif chat_event_ == 'vote':

            #聊天室 發送 投票 result : h / a /d  -> 主 和 客   / 寄送訊息
            vote_list = ['h', 'a', 'd' ]
            random.shuffle( vote_list ) 
            vote = vote_list[0]
            #print('vote: %s'%vote)

            #t = threading.Thread(target= chat_send_msg , args= ( ws  , acc , csv_name   ) )
            #t.start()  
            loop.run_until_complete(chat_vote(ws , vote , acc  , csv_name    )) 

        else:
            print('chat_event輸入有誤: %s'%chat_event)

        else:
        

            #聊天室 發送 投票 result : h / a /d  -> 主 和 客   / 寄送訊息
            vote_list = ['h', 'a', 'd' ]
            random.shuffle( vote_list ) 
            vote = vote_list[0]
            #print('vote: %s'%vote)

            #t = threading.Thread(target= chat_send_msg , args= ( ws  , acc , csv_name   ) )
            #t.start()  
            loop.run_until_complete(         chat_send_msg( ws  , acc , csv_name     ))
            #chat_send_msg( ws  , acc , csv_name     )
            

            # 體育投注
            sport_parlay = platform.Sport_Parlay_Bet(   env = env  , csv_name = csv_name  ) 
            sport_parlay.parlay_info(   token = stoken , sport = chat_sport , acc = acc , inplay_type = 'false' , assign_iid = 'true' , sinlge ='true' ) # 抓資訊 抓一次就可
            order_info = sport_parlay.sport_bet(sport = chat_sport , token=stoken , acc = acc  , bet_amount= 100 , parlay_type= '' , single='true' , 
                assign_iid = 'true' )
            
            time.sleep(3)
            #t = threading.Thread(target= chat_bet , args= ( ws , acc , order_info  , csv_name) )
            #t.start() 
            loop.run_until_complete(chat_bet(ws , acc , order_info  , csv_name    )) 

            time.sleep(3)
            #t = threading.Thread(target= chat_vote , args= ( ws , vote , acc  , csv_name  ) )
            #t.start()  
            loop.run_until_complete(chat_vote(ws , vote , acc  , csv_name    )) 
        '''

        #time.sleep(chat_delay)




    run_chat_url = f"{sport_ws_url}/product/chat/ws-chat?channel={chat_iid}&sid={chat_sid}&token={stoken}&referer={platform_url}&language=zh-cn"
    #print('run_chat_url: %s'%run_chat_url)
    
    ws = websocket.WebSocketApp(f"{run_chat_url}", on_message=on_msg, on_error=on_error, on_close=on_closed  )
    

    ws.on_open = on_open
    

    ws.run_forever(ping_interval=0,ping_timeout=30)
    
    # ws.run_forever()
bet_dict = {}

def chat_all(chat_event , ws , acc  , csv_name , env ,stoken ,    ):

    while True:
        try:
            for index , _chat_event in enumerate(chat_event):
                chat_send_msg( ws  , acc , csv_name   )
                time.sleep(msg_delay) 
                
                if index % 25  == 0:
                    if acc not in bet_dict:
                        sport_parlay = platform.Sport_Parlay_Bet(   env = env  , csv_name = csv_name  ) 
                        sport_parlay.parlay_info(   token = stoken , sport = chat_sport , acc = acc , inplay_type = 'false' , assign_iid = 'true' , sinlge ='true' ) # 抓資訊 抓一次就可
                        order_info = sport_parlay.sport_bet(sport = chat_sport , token=stoken , acc = acc  , bet_amount= 100 , parlay_type= '' , single='true' , 
                            assign_iid = 'true'    )
                        bet_dict[acc] = order_info
                    
                    chat_bet(   ws , acc , bet_dict  ,  csv_name  ) 

                elif index % 40 == 0 :

                    vote_list = ['h', 'a', 'd' ]
                    random.shuffle( vote_list ) 
                    vote = vote_list[0]
                    chat_vote( ws , vote , acc  , csv_name  ) 

                else:
                    pass


                '''
                
                if _chat_event == 'vote':
                    vote_list = ['h', 'a', 'd' ]
                    random.shuffle( vote_list ) 
                    vote = vote_list[0]
                    chat_vote( ws , vote , acc  , csv_name  )

                elif    _chat_event == 'bet':
                    if acc not in bet_dict:
                        sport_parlay = platform.Sport_Parlay_Bet(   env = env  , csv_name = csv_name  ) 
                        sport_parlay.parlay_info(   token = stoken , sport = chat_sport , acc = acc , inplay_type = 'false' , assign_iid = 'true' , sinlge ='true' ) # 抓資訊 抓一次就可
                        order_info = sport_parlay.sport_bet(sport = chat_sport , token=stoken , acc = acc  , bet_amount= 100 , parlay_type= '' , single='true' , 
                            assign_iid = 'true'    )
                        bet_dict[acc] = order_info
                    
                    chat_bet(   ws , acc , bet_dict  ,  csv_name  )                 
                
                else:
                    chat_send_msg( ws  , acc , csv_name   )

                '''


        except Exception as e:
            log.error('chat_all error: %s'%e)
            return False




#threads_sport = [] # 體育 
#thread_chat = [] # 聊天室 

user_dict = {} #  # 存放 key 為 user , value ptoken  stoken


def sport_ws(env = '' , num = '' ,acc = '' , csv_name = '', filename = '' ,  run_type = 'init' , sport_ws_url = '' , first_sport_start= '' ):

    global platform_URL ,  chat_iid
    if run_type == 'retry': 
        '''
        try:
            threads_sport[num].join()

        except Exception as e:
            #print('num: %s , acc: %s - sport ws threads join 有誤: %s'%(num , acc , e)   )
            pass
        '''

        try:
            # 將 run / chat 的列表  從新更新
            '''
            t = threading.Thread(target = run, args = ( num , platform_URL ,    acc , filename , csv_name , sport_ws_url   ))
            t.start()
            '''
            run( num , platform_URL ,    acc , filename , csv_name , sport_ws_url    )
            #print('user :%s sport ws 從連成功'%acc)
        except Exception as e:
            log.error( '更新 sport ws  threads 有誤: %s'%e )

    else: # 初始
        if first_sport_start == 'true':
            config = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
            config.read('config.ini', encoding="utf-8")

            chat_iid = config['sport_chart']['chat_iid']



        platform_URL = env["platform_URL"]

        # 體育
        threads_sport = threading.Thread(target = run, args = (num, platform_URL  , acc   , filename   , csv_name , sport_ws_url )) 
        threads_sport.start()


# 聊天室 ws 執行 function
def chat_ws(env = '' , num = '' , ptoken = '' ,acc = '' , csv_name = '', filename = '' ,  run_type = 'init'  , sport_ws_url = '' , stoken = '' ,first_start = ''): # 聊天室 執行邏輯 
    
    global chat_iid , chat_event , msg_delay , vote_delay  , bet_delay , chat_sid , chat_sport ,  platform_URL  ,size_list


    
    if run_type == 'retry': 
        '''
        try:
            thread_chat[num].join()

        except Exception as e:
            print('num: %s , acc: %s - chat ws threads join 有誤: %s'%(num , acc , e)   )
            pass
        
    
        t1 = threading.Thread(target = run_chat, args = (env , num ,platform_URL , user_dict[acc ]['stoken']   , acc   , csv_name  , sport_ws_url  ) )
        t1.start()
        '''

        try:
            # 將 run / chat 的列表  從新更新
            #
            run_chat( env , num ,platform_URL , user_dict[acc ]['stoken']   , acc   , csv_name  , sport_ws_url    )
            #print('user :%s chat ws 從連成功'%acc)
        except Exception as e:
            log.error( '更新 chat ws  threads 有誤: %s'%e )

    else: # 初始走這
        if first_start == 'true': # 一次讀寫 相關 Config , 設global . 
            #loop = asyncio.get_event_loop()
            
            config = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
            config.read('config.ini', encoding="utf-8")
            
            chat_sport = config['sport_chart']['chat_sport']
            chat_iid = config['sport_chart']['chat_iid']
            chat_event = config['sport_chart']['chat_event'].split(',') # 控制聊天室 要做的事項 ,  all : 寄送訊息 / 投票  ,  msg : 寄送訊息 , vote : 投票
            chat_delay = config['sport_chart']['chat_delay'].split(':')
            
            size_list = [] # 根據 chat_delay 第一個值 ,ex: 100 , 分配 msg list [0~100]
            for a , b in zip(chat_delay ,chat_event ):
                for i in range(100 ):
                    size_list.append(b)
                break

            
            # 這邊目前先不會用到 , 改寫在  chat_all 裡 sleep固定10 s
            msg_delay = int(chat_delay[0])
            vote_delay = int(chat_delay[1] )
            bet_delay = int( chat_delay[2] )

            sport_sid_mapping = {'football' : 1 , 'basketball': 2  , 'tennis': 3   ,'baseball': 4}
            chat_sid = sport_sid_mapping[chat_sport]
            
            log.info('聊天室 -  msg_delay: %s , vote_delay : %s , bet_delay : %s , chat_sport : %s , chat_iid : %s   , chat_event : %s , chat_sid: %s '%(msg_delay , 
                vote_delay , bet_delay , chat_sport , chat_iid   , chat_event , chat_sid)   )


        user_dict[acc ] = {  "ptoken":ptoken , 'stoken': stoken  }
        platform_URL = env["platform_URL"]

        # 聊天室
        
        chat_sokcet= threading.Thread(target = run_chat, args = (env , num, platform_URL , user_dict[acc]['stoken']     , acc  , csv_name , 
                sport_ws_url   )) 
        chat_sokcet.start()


