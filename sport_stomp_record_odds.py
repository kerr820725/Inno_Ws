import stomper
import datetime,threading,time
import websocket
import json
import csv

env_setting = {
    "vd002" : {
        'platform_url' : "https://93a.me",
        'sport_url' :  "https://en-vd002-inno-sport.innouat.site",
        'ws_url' : "wss://sports-api.innouat.site"
    },
    'vd003' : {
        'platform_url' : "https://en-vd003-tiger-portal.innouat.site",
        'sport_url' : "https://en-vd003-inno-sport.innouat.site",
        'ws_url' : "wss://sports-api.innouat.site"
    }
}

iid = 1547112

filename = 'stomp_log_'+datetime.datetime.now().strftime("%Y%m%d%H%M%S")

def write_csv(filename, content):
    with open(filename+'.csv', 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['user', 'send_type', 'record_time', 'market', 'k', 'ov', 'ud', 'a', 'h']

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()
       
        writer.writerow(content)
        csvfile.close()

def run(num, env, csv_name):
    def on_msg(ws, msg):
        
        print(f"{num} msg: {msg}")
        if 'destination:/topic/odds-diff' in msg:
            new_msg =  msg[ msg.index('\n\n'):msg.index('\x00')]
            new_msg = new_msg.replace('\n\n','')
            temp_str = json.loads(new_msg)
            send_type = temp_str['sendType']
            odds = ""
            market = ""
            msg_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            if 'ou' in temp_str['market']:
                odds = temp_str['market']['ou']
                market = 'ou'
                for cnt in range(len(odds)) : 
                    k = odds[cnt]['k']
                    odds_ov = 'none'
                    odds_ud = 'none'
                    if 'ov' in odds[cnt]:
                        odds_ov = odds[cnt]['ov']
                    if 'ud' in odds[cnt]:
                        odds_ud = odds[cnt]['ud']
                    write_content = {
                        "user":num,
                        "send_type": send_type,
                        "record_time": msg_time,
                        "market":market,
                        "k": k,
                        "ov": odds_ov,
                        "ud": odds_ud,                  
                    } 
                    write_csv(csv_name, write_content)
            if 'ah' in temp_str['market']:
                odds = temp_str['market']['ah']
                market = 'ah'
                for cnt in range(len(odds)) : 
                    k = odds[cnt]['k']
                    odds_a = 'none'
                    odds_h = 'none'
                    if 'a' in odds[cnt]:
                        odds_a = odds[cnt]['a']
                    if 'h' in odds[cnt]:
                        odds_h = odds[cnt]['h']

                    write_content = {
                        "user":num,
                        "send_type": send_type,
                        "record_time": msg_time,
                        "market":market,
                        "k": k,
                        "a": odds_a,
                        "h": odds_h,                  
                    } 
                    write_csv(csv_name, write_content)
            
        elif 'destination:/topic/match/event' in msg:
            # print(f"{num} msg: event change!")  
            new_msg =  msg[ msg.index('\n\n'):msg.index('\x00')]
            new_msg = new_msg.replace('\n\n','')
            temp_str = json.loads(new_msg)
            msg_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            print("*******", msg_time, " ",temp_str)
            for event_count in range(len(temp_str)):
                event_status = temp_str[event_count]['status']
                if event_status == 3 :
                    event_iid = temp_str[event_count]['iid']
                    if event_iid == iid:
                        print(f"{num} msg: new match!! iid: {event_iid}")
                        write_content = {
                            "user":num,
                            "send_type": 'kickoff',
                            "record_time": msg_time
                        } 
                        write_csv(csv_name, write_content)

    def on_error(ws, err):
        try :
            print(f"==== No.{num} Error info: {err}")
        except Exception as e :
            print(e.with_traceback)

    def on_closed(ws, status_code, close_msg):
        print(f"==== No.{num} Closed : ", datetime.datetime.now().strftime('%m/%d %H:%M:%S'), " status:",status_code, " , msg:",close_msg)
        # writeLog(f"==== No.{num} Closed : status:",status_code, " , msg:",close_msg,"\n")
        

    def on_open(ws):
        ws.send("CONNECT\naccept-version:1.0,1.1,2.0")
        v = 1
        sub = stomper.subscribe(f"/topic/odds-diff/match/111111", v, ack="auto")
        ws.send(sub)
        v =v+ 1
        sub = stomper.subscribe(f"/topic/odds-diff/match/{iid}", v, ack="auto")
        ws.send(sub)
        
        sub = stomper.subscribe(f"/topic/match/event", v, ack="auto")
        ws.send(sub)    
   
    ws = websocket.WebSocketApp(f"{env['ws_url']}/product/websocket/ws?referer={env['platform_url']}", on_message=on_msg, on_error=on_error, on_close=on_closed)
    ws.on_open = on_open    
    ws.run_forever(ping_interval=30,ping_timeout=10)
    # ws.run_forever()


threads = []
vend_list = ['vd002', 'vd003']
for run_cnt in range(len(vend_list)):
    vd = vend_list[run_cnt]
    
    csv_name = 'stomp_'+vd+'_'+datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    env = env_setting[vd]
    threads.append(threading.Thread(target = run, args = (vd, env, csv_name)))
    threads[run_cnt].start()
    print(f"start : " + vd)
    time.sleep(0.5)
