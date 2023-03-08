import stomper
import random,datetime,threading,time
import websocket, requests
import json
import os
import socket

from Function import platform_function as platform
from Function import general_function as general

vend = "vd002"
env = platform.get_env(vend)
pc_name = socket.gethostname()
# pc_name = "qa6"
pw = "test1234"
adminacc = "autoqa01"
adminpw = "test1234"

ws_threads = []
action_threads = []
totaluser = 1600
user_dict = {}

if '-' in pc_name:
    prefix = 'qa'+pc_name.split('-')[-1]
else:
    prefix = 'qa'+pc_name

platform_url = "https://93a.me"
platform_api_url = "https://tiger-api.innouat.site/platform"
ws_url = "wss://tiger-api.innouat.site/platform"

headers = {
            'accept': '*/*',
            'Content-Type': 'application/json',
            'Referer': env["platform_URL"],
            'Time-Zone': 'GMT+8',
            'accept-language': 'zh-cn',
            "currency": "CNY"
        }

filename = prefix+'_ws_'+datetime.datetime.now().strftime("%Y%m%d%H%M%S")
csv_name = prefix+'_csv_'+datetime.datetime.now().strftime("%Y%m%d%H%M%S")
def run(env, num, acc, platform_url, ptoken):
    def on_msg(ws, msg):        
        # print(f"==== Msg({num}) : ", datetime.datetime.now().strftime('%m/%d %H:%M:%S'), " ",msg)
        json_msg = msg.replace("'", "\"")
        if 'brPartyTime' in msg:            
            rain_dict = json.loads(json_msg)
            local_receive_time = time.time()*1000
            if 'brListId' in rain_dict['data']:
                promotion_id = rain_dict['data']['brListId']
            else:
                promotion_id = rain_dict['data']['masterId']
            
            rain_begin = rain_dict['data']['begin']
            promotion_title = rain_dict['data']['title']
            promotion_type = rain_dict['data']['promotionType']
            diff_sec = (local_receive_time-rain_begin)/1000
            countdownTime = rain_dict['data']['countdownTime']

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


            print(f"==== Msg({num}):", datetime.datetime.now().strftime('%m/%d %H:%M:%S'), " local_receive_time:",local_receive_time, " ,begin:",rain_begin, " ,diff:", diff_sec)
            if(diff_sec<0):
                time.sleep(int(abs(diff_sec)))

            apply_status_code, apply_response_sec, apply_amount, apply_start_time, apply_end_time, apply_response,  = platform.rain_apply(env, num, ptoken, promotion_type, promotion_id)
            
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

            status_code, response_sec, amount, start_time, end_time, response,  = platform.get_wallet_list(env, acc, ptoken)
            write_content = {
                "user":acc,
                "action": "/payment/wallets/list",
                "start_time": start_time,
                "end_time": end_time,
                "status_code":status_code,
                "diff": response_sec,
                "response":response
            } 
            general.write_csv(csv_name, write_content)
        else:
            write_content = {
                "user":acc,
                "action": "OtherWSMsg",
                "start_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "end_time":"",
                "status_code":0,
                "diff": -1,
                "response":json_msg
            } 
            print(f"==== Msg({num}) : ", datetime.datetime.now().strftime('%H:%M:%S'), " ",msg)
            general.write_csv(csv_name, write_content)
            
        

    def on_error(ws, err):
        try :
            # general.writeLog(filename, f"==== No.{num} Error info: {err}")
            print(f"==== No.{num} Error info: {err}")
            write_content = {
                "user":acc,
                "action": "WS_Error",
                "start_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "end_time":"",
                "status_code":"",
                "diff": "",
                "response":str(err)
            } 
            general.write_csv(csv_name, write_content)

        except Exception as e :
            print(e.with_traceback)

    def on_closed(ws, status_code, close_msg):
        print(f"==== No.{num} Closed : ", datetime.datetime.now().strftime('%m/%d %H:%M:%S'), " status:",status_code, " , msg:",close_msg)
        # general.writeLog(filename, f"==== No.{num} Closed : status:"+str(status_code)+ " , msg:"+close_msg+"\n")
        write_content = {
                "user":acc,
                "action": "WS_Closed",
                "start_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "end_time":"",
                "status_code":str(status_code),
                "diff": "",
                "response":str(close_msg)
            } 
        general.write_csv(csv_name, write_content)

    def on_open(ws):
        ws.send("CONNECT\naccept-version:1.0,1.1,2.0")
        v = 1
    ws = websocket.WebSocketApp(f"{ws_url}/websocket/channel/private?token={ptoken}&appType=2&referer={platform_url}&device=mobile&language=zh_CN", on_message=on_msg, on_error=on_error, on_close=on_closed)
    ws.on_open = on_open    
    ws.run_forever(ping_interval=20,ping_timeout=15)

def run_action(env, acc, ptoken, logname):
    
    try:
        # ===========
        status_code, response_sec, start_time, end_time, response = platform.get_userinfo(env,  acc, ptoken)
        write_content = {
                    "user":acc,
                    "action": "/user/userinfo",
                    "start_time": start_time,
                    "end_time":end_time,
                    "status_code":status_code,
                    "diff": response_sec,
                    "response":response
                } 
        general.write_csv(csv_name, write_content)

        # ===========
        status_code, response_sec, start_time, end_time, response = platform.get_announcement_list(env,  acc, ptoken)
        write_content = {
                    "user":acc,
                    "action": "/user/announcement/list",
                    "start_time": start_time,
                    "end_time":end_time,
                    "status_code":status_code,
                    "diff": response_sec,
                    "response":response
                } 
        general.write_csv(csv_name, write_content)
    except Exception as ex:
            print("run_action ex", ex)
    
    try:
        # ==============
        while True:
            status_code, response_sec, start_time, end_time, response = platform.extension(env,  acc, ptoken)
            if status_code != 200:
                write_content = {
                    "user":acc,
                    "action": "/user/token/extension",
                    "start_time": start_time,
                    "end_time":end_time,
                    "status_code":status_code,
                    "diff": response_sec,
                    "response":response
                } 
                general.write_csv(csv_name, write_content)

            time.sleep(120)

    except Exception as ex:
        print("run_action ex", ex)

for i in range(totaluser):
    acc = prefix+"{:03d}".format(i+1)
    isExist = platform.checkAccount(env, acc)

    if not isExist :
        isExist = platform.createAccount(env, acc, pw)

    if isExist :
        ptoken, status_code, response_sec, start_time, end_time, response = platform.loginPlatfomuser(env,  acc, pw)
        
        write_content = {
                "user":acc,
                "action": "/user/token",
                "start_time": start_time,
                "end_time":end_time,
                "status_code":status_code,
                "diff": response_sec,
                "response":response
            } 
        general.write_csv(csv_name, write_content)
        

        # ============
        ws_threads.append(threading.Thread(target = run, args = (env, i, acc, env["platform_URL"], ptoken , )))
        ws_threads[i].start()
        
        action_log = prefix+'_platform_'+acc+'_'+datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        action_threads.append(threading.Thread(target = run_action, args = (env, acc, ptoken ,action_log,)))
        action_threads[i].start()

        user_dict[i] = { "account" : acc , "ptoken":ptoken}
        print(f"===== No.{i} acc: {acc} , start : "+datetime.datetime.now().strftime('%m/%d %H:%M:%S'))
        general.writeLog(filename, f"===== No.{i} acc: {acc} , start \n")
        time.sleep(0.1)

