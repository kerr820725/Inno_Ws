import datetime,threading,time
import websocket
import json
import socket , asyncio
import configparser  , sys
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc
from Function import platform_function as platform
from Function import general_function as general
import nest_asyncio
import pytz

from Logger import create_logger

log = create_logger()

tw = pytz.timezone('Asia/Taipei')

nest_asyncio.apply()
sys.setrecursionlimit(20000)
pc_name = socket.gethostname()


action_threads = []
user_dict = {} # 存放 key 為 user , value ptoken
#scheduler = BackgroundScheduler(daemon=True, timezone="Asia/Taipei")

#scheduler.start()


async def apply(env, num, acc,  user_dict, promotion_type, promotion_id , csv_name , sleep_time):
    try:
        if sleep_time < 0:
            sleep_time = float(abs(sleep_time)   )
            await asyncio.sleep(sleep_time)
        print(f"==== Msg({num}):", datetime.datetime.now().astimezone(tw).strftime('%m/%d %H:%M:%S')," apply") 
        apply_status_code, apply_response_sec, apply_amount, apply_start_time, apply_end_time, apply_response  =  platform.rain_apply(env, acc, user_dict, promotion_type, str(promotion_id) )
        
        
        write_content = {
                    "user":acc,
                    "action": "/promotion/promotion/apply",
                    "start_time": apply_start_time,
                    "end_time":apply_end_time,
                    "status_code":apply_status_code,
                    "diff": apply_response_sec,
                    "response":apply_response
                } 
        general.write_csv(csv_name, write_content)

        status_code, response_sec, amount, start_time, end_time, response  =  platform.get_wallet_list(env, acc, user_dict[acc]['ptoken'] )

        
        write_content = {
                    "user":acc,
                    "action": "/platform/payment/wallets/list",
                    "start_time": start_time,
                    "end_time": end_time,
                    "status_code":status_code,
                    "diff": response_sec,
                    "response":response
                } 
        general.write_csv(csv_name, write_content)
        
        if apply_response['data']:
            if apply_response['data']['rewards'][0]['rewardType'] == 1:
                status_code, response_sec, availableSize, start_time, end_time, response =  platform.get_coupon_summary(env, acc, user_dict[acc]['ptoken'] )

                write_content = {
                            "user":acc,
                            "action": "/platform/payment/coupon/summary",
                            "start_time": start_time,
                            "end_time": end_time,
                            "status_code":status_code,
                            "diff": response_sec,
                            "response":response
                        } 
                general.write_csv(csv_name, write_content)

                status_code, response_sec, availableAmount, start_time, end_time, response = platform.get_coupon_list(env, acc, user_dict[acc]['ptoken'] )

                write_content = {
                            "user":acc,
                            "action": "/platform/payment/coupon/list",
                            "start_time": start_time,
                            "end_time": end_time,
                            "status_code":status_code,
                            "diff": response_sec,
                            "response":response
                        } 
                general.write_csv(csv_name, write_content)
    except Exception as e:
        log.error(' acc : %s apply error: %s '%(acc , e ))    
    #platform.Rain_Api(   env = env , csv_name = csv_name  , ptoken=ptoken    ).after_api(acc=acc   )  

def run(env, num, acc, platform_url, user_dict , csv_name  , ws_url ):
    def on_msg(ws, msg):     
        # print(f"==== Msg({num}) : ", datetime.datetime.now().astimezone(tw).strftime('%m/%d %H:%M:%S'), " ",msg)
        json_msg = msg.replace("'", "\"")
        if 'brPartyTime' in msg:            
            rain_dict = json.loads(json_msg)
            local_receive_time = time.time()*1000 # python 當下接收時間
            if 'brListId' in rain_dict['data']:
                promotion_id = rain_dict['data']['brListId']
            else:
                promotion_id = rain_dict['data']['masterId']
            
            rain_begin = rain_dict['data']['begin'] # 紅包雨開始時間
            #promotion_title = rain_dict['data']['title']
            promotion_type = rain_dict['data']['promotionType']
            diff_sec = (local_receive_time-rain_begin)/1000 
            #countdownTime = rain_dict['data']['countdownTime']

            write_content = {
                "user":acc,
                "action": "Rain",
                "start_time": rain_begin,
                "end_time":local_receive_time,
                "status_code":0,
                "diff": diff_sec,
                "response":json_msg
            } 
            general.write_csv(csv_name, write_content)
            log.info(f"==== Msg({num}):  local_receive_time: {local_receive_time }, begin: { rain_begin } , diff: {diff_sec}  ")

            '''
            原流程
            if diff_sec<0 :
                sleep_sec = float(abs(diff_sec))
                alarm_time = datetime.datetime.now() + datetime.timedelta(seconds=sleep_sec)
                print(f"==== Msg({num}): alarm_time:",alarm_time, ", sleep_sec:",sleep_sec)
            
                job_id = 'id'+str(num)+str(promotion_id)+str(alarm_time) 
                scheduler.add_job(apply, 'date', run_date = alarm_time, args=[env, num, acc, ptoken, promotion_type, promotion_id], id=job_id, misfire_grace_time=180, timezone="Asia/Taipei")
            '''
            
            # 改用 thread 來 apply 
            #sleep_time = float(abs(diff_sec)) + 1 # 故意加個 1秒 
            #t = threading.Thread( target = apply , args= (env, num, acc,  user_dict , promotion_type, promotion_id , csv_name , sleep_time )    ) 
            #time.sleep(sleep_time)    
            #t.start()
            loop.run_until_complete(apply(  env, num, acc,  user_dict , promotion_type, promotion_id , csv_name , diff_sec ) )
            
            
        else:
            write_content = {
                "user":acc,
                "action": "Rain_OtherWSMsg",
                "start_time": datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S'),
                "end_time":"",
                "status_code":0,
                "diff": -1,
                "response":json_msg
            } 
            if 'availableBalance' in msg: 
                log.info(f"==== Msg({num}) , msg: {msg} "  )
            general.write_csv(csv_name, write_content)   

    def on_error(ws, err):
        try :
            # general.writeLog(filename, f"==== No.{num} Error info: {err}")
            log.error(f"==== No.{num} rain ws Error info: {err}")
            write_content = {
                "user":acc,
                "action": "Rain_WS_Error",
                "start_time": datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S'),
                "end_time":"",
                "status_code":"",
                "diff": "",
                "response":str(err)
            } 
            general.write_csv(csv_name, write_content)

        except Exception as e :
            print(e.with_traceback)

    def on_closed(ws, status_code, close_msg):
        log.error(f"==== No.{num}, user: {acc} rain ws Closed  , status: {status_code } , msg: {close_msg } "  )
        # general.writeLog(filename, f"==== No.{num} Closed : status:"+str(status_code)+ " , msg:"+close_msg+"\n")
        write_content = {
                "user":acc,
                "action": "Rain_WS_Closed",
                "start_time": datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S'),
                "end_time":"",
                "status_code":str(status_code),
                "diff": "",
                "response":str(close_msg)
            } 
        general.write_csv(csv_name, write_content) 


        rain_ws( env= env , num = num , acc= acc ,  exe_type = 'retry'  , csv_name =csv_name , ws_url = ws_url  )# 指定 num 從新作 流程

    def on_open(ws):
        ws.send("CONNECT\naccept-version:1.0,1.1,2.0")
        v = 1  
    
    
    wss_url = f"{ws_url}/websocket/channel/private?token={user_dict[acc]['ptoken'] }&appType=2&referer={platform_url}&device=mobile&language=zh_CN"
    #print(wss_url)
    ws = websocket.WebSocketApp(f"{wss_url}", on_message=on_msg, on_error=on_error, on_close=on_closed)
    ws.on_open = on_open
    ws.run_forever(ping_interval=20,ping_timeout=15)
    


def run_action(env, acc, user_dict , csv_name     ):

    while True:
        
        try:
            status_code, response_sec, start_time, end_time, response = platform.extension(env, acc , user_dict[acc]['ptoken']  )
            write_content = {
                "user":acc,
                "action": "/platform/user/token/extension",
                "start_time": start_time,
                "end_time":end_time,
                "status_code":status_code,
                "diff": response_sec,
                "response":response
            } 
            general.write_csv(csv_name, write_content)
    
        except Exception as e:
            log.error('extension 有誤: %s '%e)



        if before_api == 'sport':
            platform.Sport_Api(   env , csv_name , before_delay   ).before_api(    acc ,  user_dict[acc]['ptoken']  , user_dict[acc]['stoken']  )    
        elif before_api == 'platform':
            platform.Platform_Api(   env , user_dict[acc]['ptoken']  , csv_name  , before_delay   ).before_api(   acc=acc   )  
        else: #兩個都做 
            platform.Sport_Api(   env , csv_name , before_delay    ).before_api(    acc ,  user_dict[acc]['ptoken'] , user_dict[acc]['stoken']    ) 


        time.sleep(60)
        


    

def rain_ws(env = '' ,num = ''  , ptoken = '' , acc= '' , exe_type ='init'    , csv_name = '' ,filename = '' , ws_url = '' , stoken= '' , first_start=''  ):#用 type 來判斷 是 一開始 range ,還是　close 制定 帶 要執行的num
    global platform_URL , loop
    try:
        if exe_type == 'retry': # ws 斷線 retry
            
            '''
            try:
                action_threads[num].join()
            except Exception as e:
                pass
            # socket 
            ws_threads = threading.Thread(target = run, args = (env, num, acc, platform_URL  , user_dict , csv_name  , ws_url ))
            ws_threads.start()
            
            '''

            

            try:
                #action_threads[num] = ws_threads
                #run ( env, num, acc, platform_URL , user_dict , csv_name  , ws_url   )
                ws_threads = threading.Thread(target = run, args = (env, num, acc, platform_URL , user_dict , csv_name  , ws_url ))
                ws_threads.start()
                log.info('user :%s rain ws 從連成功'%acc)
                '''
                ws_threads = threading.Thread(target = run, args = (env, num, acc, platform_URL , user_dict , csv_name  , ws_url ))
                ws_threads.start()
                print('user :%s rain ws 從連成功'%acc)
                '''

            except Exception as e:
                log.error( '更新 rain ws  threads 有誤: %s'%e )
                
        
        else: # 初始


            if first_start == 'true':
                global before_api , before_delay 

                config = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
                config.read('config.ini', encoding="utf-8")

                before_api = config['paltform_rain_ws']['before_api']
                before_delay = config['paltform_rain_ws']['before_delay']

                log.info('紅包雨 -  before_api: %s , before_delay: %s  '%( before_api , before_delay ))

                loop = asyncio.get_event_loop()
            
            user_dict[acc ] = {  "ptoken":ptoken , 'stoken': stoken  }

            status_code, response_sec, start_time, end_time, response = platform.get_announcement_list(env = env,  acc = acc , ptoken = ptoken )
            write_content = {
                    "user":acc,
                    "action": "/platform/user/announcement/list",
                    "start_time": start_time,
                    "end_time":end_time,
                    "status_code":status_code,
                    "diff": response_sec,
                    "response":response
                } 
            general.write_csv(csv_name, write_content)

            platform_URL = env["platform_URL"]

            # socket 
            ws_threads = threading.Thread(target = run, args = (env, num, acc, platform_URL , user_dict , csv_name  , ws_url ))
            ws_threads.start()
           

            # 一班api
            api_thread = threading.Thread(target = run_action, args = (env, acc, user_dict  , csv_name  ))
            api_thread.start()
            
           


    except Exception as e:
        log.error('rain_ws: error: %s'%e)

         
