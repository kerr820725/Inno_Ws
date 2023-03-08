import stomper
import random,datetime,threading,time
import websocket, requests
import json
import os
import socket

from Function import platform_function as platform


vend = "vd002"
env = platform.get_env(vend)
# acc = "newnicole002"
pc_name = socket.gethostname()
pw = "test1234"

print (pc_name)
if '-' in pc_name:
    prefix = 'qa'+pc_name.split('-')[-1]
else:
    prefix = 'qa'+pc_name

print (prefix)

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
            'accept-language': 'zh-cn'
        }

filename = prefix+'_platform_'+datetime.datetime.now().strftime("%Y%m%d%H%M%S")

def writeLog(content):
    try:
        with open(filename+'.txt', 'a', newline='', encoding='utf-8') as csvfile:
                csvfile.writelines(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))+ " " +content) 
    except Exception as e :
        print(e.with_traceback)

def run(num, platform_url, ptoken):
    def on_msg(ws, msg):        
        print(f"==== Msg({num}) : ", datetime.datetime.now().strftime('%m/%d %H:%M:%S'), " ",msg)
        writeLog(f"No.{num} "+msg+"\n")
        
        # if '\n\n' in msg and 'dynamic' in msg : 
        #     new_msg =  msg[ msg.index('\n\n'):msg.index('\x00')]
        #     new_msg = new_msg.replace('\n\n','')
        #     temp_str = json.loads(new_msg)
        #     print("*******", " ",temp_str)

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

threads = []
totaluser = 1000
user_dict = {}

def run_extension(num):    
    while True:
        time.sleep(120)
        for tmp in range(0, len(user_dict)):
            extension_rs = platform.extension(env, user_dict[tmp]['account'], user_dict[tmp]['ptoken'])
            # print(user_dict[tmp]['account'] + " extension " + datetime.datetime.now().strftime('%m/%d %H:%M:%S'))

t_extension = threading.Thread(target=run_extension, args=( totaluser, ))
t_extension.start()


for i in range(totaluser):
    acc = prefix+"{:03d}".format(i+1)
    isExist = platform.checkAccount(env, acc)

    if not isExist :
        isExist = platform.createAccount(env, acc, pw)

    if isExist :
        ptoken = platform.loginPlatfomuser(env,  acc, pw)
        threads.append(threading.Thread(target = run, args = (i, env["platform_URL"], ptoken , )))
        threads[i].start()
        user_dict[i] = { "account" : acc , "ptoken":ptoken}
        print(f"===== No.{i} acc: {acc} , start : "+datetime.datetime.now().strftime('%m/%d %H:%M:%S'))
        writeLog(f"===== No.{i} acc: {acc} , start \n")
        time.sleep(0.1)



# while True:
#     time.sleep(120)
#     for tmp in range(0, len(user_dict)):
#         extension_rs = platform.extension(env, user_dict[tmp]['account'], user_dict[tmp]['ptoken'])
#         print(user_dict[tmp]['account'] + " extension " + datetime.datetime.now().strftime('%m/%d %H:%M:%S'))
    
        
