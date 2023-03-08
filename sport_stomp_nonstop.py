import stomper
import random,datetime,threading,time
import websocket, requests
import json

platform_url = "https://93a.me"
sport_url =  "https://en-vd002-inno-sport.innouat.site"
platform_api_url = "https://tiger-api.innouat.site/platform"
sport_api_url = "https://sports-api.innouat.site/product"
ws_url = "wss://sports-api.innouat.site"

headers = {
            'accept': '*/*',
            'Content-Type': 'application/json',
            'Referer': platform_url,
            'Time-Zone': 'GMT+8',
            'accept-language': 'zh-cn'
        }

filename = 'stomp_log_'+datetime.datetime.now().strftime("%Y%m%d%H%M%S")
# totalThread = int(10)
currentThreadId = "0"
ttId=1


def writeLog(content):
    try:
        with open(filename+'.txt', 'a', newline='', encoding='utf-8') as csvfile:
                csvfile.writelines(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))+ " " +content) 
    except Exception as e :
        print(e.with_traceback)

def createNewThread(count):
    try:
        print("===== createNewThread",ttId)
        threads = []
        for i in range(count):
            threadId = ttId + i
            threads.append(threading.Thread(target = run, args = (threadId,)))
            threads[i].start()
            print(f"==== No.{threadId} Start : "+datetime.datetime.now().strftime('%m/%d %H:%M:%S'))
            time.sleep(0.1)
            writeLog(f"New Thread {threadId}\n")
    except Exception as e :
        print(e.with_traceback)
    
    return threadId+1

def getMatchesList():
    iids = []
    for sid in range(1,5) :
        response = requests.request("GET", f"{sport_api_url}/business/sport/tournament/info?sid={sid}&inplay=true&sort=tournament", headers=headers).json()
    
        if response['data']['tournaments'] :
            for tournament in response['data']['tournaments'] :
                for game in tournament['matches'] :
                    iids.append(game['iid'])
        
    print(iids)
    return iids

iid_list = []
iid_list = getMatchesList()

def run(num):
    def on_msg(ws, msg):
        
        # writeLog(f"No.{num} receive msg"+"\n")
        # print(f"{num} msg")  
        print(f"{num} msg: {msg}")  
        if 'destination:/topic/match/event' in msg:
            # print(f"{num} msg: event change!")  
            new_msg =  msg[ msg.index('\n\n'):msg.index('\x00')]
            new_msg = new_msg.replace('\n\n','')
            temp_str = json.loads(new_msg)
            # print("*******", " ",temp_str)
            for event_count in range(len(temp_str)):
                event_status = temp_str[event_count]['status']
                if event_status == 3:
                    event_iid = temp_str[event_count]['iid']
                    print(f"{num} msg: new match!! iid: {event_iid}")
                    writeLog(f"{num} msg: new match!! iid: {event_iid} \n")
                    sub = stomper.subscribe(f"/topic/odds-diff/match/{event_iid}", 1, ack="auto")
                    ws.send(sub)

    def on_error(ws, err):
        try :
            writeLog(f"==== No.{num} Error\n")
            print(f"==== No.{num} Error info: {err}")
            createNewThread(1)
        except Exception as e :
            print(e.with_traceback)

    def on_closed(ws, status_code, close_msg):
        print(f"==== No.{num} Closed : ", datetime.datetime.now().strftime('%m/%d %H:%M:%S'), " status:",status_code, " , msg:",close_msg)
        writeLog(f"==== No.{num} Closed : status:",status_code, " , msg:",close_msg,"\n")
        


    def on_open(ws):
        ws.send("CONNECT\naccept-version:1.0,1.1,2.0")
        v = 1
        # sub = stomper.subscribe(f"/topic/odds-diff/match/111111", v, ack="auto")
        # ws.send(sub)
        # v =v+ 1
        # for iid in iid_list :
        #     sub = stomper.subscribe(f"/topic/odds-diff/match/{iid}", v, ack="auto")
        #     ws.send(sub)
        #     v=v+1
        #     sub = stomper.subscribe(f"/topic/match/inplay/info/{iid}", v, ack="auto")
        #     ws.send(sub)
        #     v=v+1
        
        sub = stomper.subscribe(f"/topic/match/event", v, ack="auto")
        ws.send(sub)    
   
    ws = websocket.WebSocketApp(f"{ws_url}/product/websocket/ws?referer=https://93a.me", on_message=on_msg, on_error=on_error, on_close=on_closed)
    ws.on_open = on_open    
    ws.run_forever(ping_interval=30,ping_timeout=10)
    # ws.run_forever()






ttId = createNewThread(1)
print("============= create done.", ttId)
# ttId = createNewThread(1)
# print("============= create done.", ttId)
# while True:
#     time.sleep(120)
#     for tmp in range(0, len(user_dict)):
#         extension_rs = platform.extension(env, user_dict[tmp]['account'], user_dict[tmp]['ptoken'])
        