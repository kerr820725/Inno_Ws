import stomper
import random,datetime,threading,time
import websocket, requests
import json
import os
import socket

from Function import platform_function as platform


vend = "vd002"
env = platform.get_env(vend)
pc_name = socket.gethostname()
# pc_name = "qa9"
pw = "test1234"
adminacc = "autoqa01"
adminpw = "test1234"

ws_threads = []
action_threads = []
totaluser = 50
user_dict = {}

if '-' in pc_name:
    prefix = 'qa'+pc_name.split('-')[-1]
else:
    prefix = 'qa'+pc_name

print (prefix)

adminToken=""
platform_url = "https://93a.me"
sport_url =  "https://en-vd002-inno-sport.innouat.site"
platform_api_url = "https://tiger-api.innouat.site/platform"
sport_api_url = "https://sports-api.innouat.site/product"
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

def writeLog(content):
    try:
        with open(filename+'.txt', 'a', newline='', encoding='utf-8') as csvfile:
                csvfile.writelines(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))+ " " +content) 
    except Exception as e :
        print(e.with_traceback)

def writeAction(logname, content):
    print(content)
    try:
        with open(logname+'.txt', 'a', newline='', encoding='utf-8') as csvfile:
                csvfile.writelines(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))+ " " +content+'\n') 
    except Exception as e :
        print(e.with_traceback)

def run(num, platform_url, ptoken):
    def on_msg(ws, msg):        
        # print(f"==== Msg({num}) : ", datetime.datetime.now().strftime('%m/%d %H:%M:%S'), " ",msg)
        writeLog(f"No.{num} "+msg+"\n")

    def on_error(ws, err):
        try :
            writeLog(f"==== No.{num} Error info: {err}")
            print(f"==== No.{num} Error info: {err}")

        except Exception as e :
            print(e.with_traceback)

    def on_closed(ws, status_code, close_msg):
        print(f"==== No.{num} Closed : ", datetime.datetime.now().strftime('%m/%d %H:%M:%S'), " status:",status_code, " , msg:",close_msg)
        writeLog(f"==== No.{num} Closed : status:"+str(status_code)+ " , msg:"+close_msg+"\n")
    def on_open(ws):
        ws.send("CONNECT\naccept-version:1.0,1.1,2.0")
        v = 1
    ws = websocket.WebSocketApp(f"{ws_url}/websocket/channel/private?token={ptoken}&appType=2&referer={platform_url}&device=mobile&language=zh_CN", on_message=on_msg, on_error=on_error, on_close=on_closed)
    ws.on_open = on_open    
    ws.run_forever(ping_interval=20,ping_timeout=15)

def run_action(env, acc, ptoken, adminToken, logname):
    while True:
        extension_rs = platform.extension(env, acc, ptoken)
        wallet_before = platform.get_wallet(env, acc, ptoken)
        bankcard = platform.get_bankcard(env, acc, ptoken)
        orderNo = platform.deposit(env, acc, ptoken, bankcard)
        res = platform.approve_deposit(env, adminToken, orderNo)
        wallet_after = platform.get_wallet(env, acc, ptoken)
        result=""
        if float(wallet_after)-float(wallet_before)==1000:
            result="PASS!"
        else:
            result="FAIL!"
            content = orderNo
            writeAction(logname,content)  
            
        content = acc+' : before:'+wallet_before+", after:"+wallet_after+ " [result]:" +result
        writeAction(logname,content)        
        time.sleep(5)





adminToken = platform.loginAdmin(env, adminacc, adminpw)
for i in range(totaluser):
    acc = prefix+"{:03d}".format(i+1)
    isExist = platform.checkAccount(env, acc)

    if not isExist :
        isExist = platform.createAccount(env, acc, pw)

    if isExist :
        ptoken = platform.loginPlatfomuser(env,  acc, pw)
        

        ws_threads.append(threading.Thread(target = run, args = (i, env["platform_URL"], ptoken , )))
        ws_threads[i].start()

        action_log = prefix+'_platform_'+acc+'_'+datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        action_threads.append(threading.Thread(target = run_action, args = (env, acc, ptoken , adminToken,action_log,)))
        action_threads[i].start()

        user_dict[i] = { "account" : acc , "ptoken":ptoken}
        print(f"===== No.{i} acc: {acc} , start : "+datetime.datetime.now().strftime('%m/%d %H:%M:%S'))
        writeLog(f"===== No.{i} acc: {acc} , start \n")
        time.sleep(0.1)



# while True:
#     time.sleep(120)
#     for tmp in range(0, len(user_dict)):
#         extension_rs = platform.extension(env, user_dict[tmp]['account'], user_dict[tmp]['ptoken'])
#         print(user_dict[tmp]['account'] + " extension " + datetime.datetime.now().strftime('%m/%d %H:%M:%S'))
    
        
