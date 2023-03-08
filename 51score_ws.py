import stomper
import random,datetime,threading,time
import websocket, requests
import json
import os
import socket
from Function import general_function as general

ws_url = "ws://139.95.0.158"
ws_threads = []
totaluser = 2000
pc_name = socket.gethostname()
if '-' in pc_name:
    prefix = 'qa'+pc_name.split('-')[-1]
else:
    prefix = 'qa'+pc_name

filename = "51score_"+prefix+'_ws_'+datetime.datetime.now().strftime("%Y%m%d%H%M%S")

def run(num):
    def on_msg(ws, msg):        
        # print(f"==== Msg({num}) : ", datetime.datetime.now().strftime('%m/%d %H:%M:%S'), " ",msg)
        
        write_content = {
                "user":num,
                "action": "WS_MSG",
                "start_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "end_time":"",
                "status_code":0,
                "diff": -1,
                "response":str(msg)
            }        
        general.write_csv(filename, write_content)

    def on_error(ws, err):
        try :
            # general.writeLog(filename, f"==== No.{num} Error info: {err}")
            print(f"==== No.{num} Error info: {err}")
            write_content = {
                "user":num,
                "action": "WS_Error",
                "start_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "end_time":"",
                "status_code":"",
                "diff": "",
                "response":str(err)
            } 
            general.write_csv(filename, write_content)
            

        except Exception as e :
            print(e.with_traceback)

    def on_closed(ws, status_code, close_msg):
        write_content = {
                "user":num,
                "action": "WS_Closed",
                "start_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "end_time":"",
                "status_code":str(status_code),
                "diff": "",
                "response":str(close_msg)
            } 
        general.write_csv(filename, write_content)

    def on_open(ws):
        ws.send("e3a88a66c0ed5fa5f0e0b1ace2b33f5c", websocket.ABNF.OPCODE_BINARY)
        v = 1
    ws = websocket.WebSocketApp(f"{ws_url}/websocket/15000", on_message=on_msg, on_error=on_error, on_close=on_closed)
    ws.on_open = on_open    
    ws.run_forever(ping_interval=20,ping_timeout=15)

for i in range(totaluser):
    write_content = {
                "user":i,
                "action": "Start",
                "start_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "end_time":"",
                "status_code":0,
                "diff": -1,
                "response":""
    }
    print(f"===== No.{i} start : "+datetime.datetime.now().strftime('%m/%d %H:%M:%S'))
    general.write_csv(filename, write_content)
    ws_threads.append(threading.Thread(target = run, args = (i, )))
    ws_threads[i].start()
    time.sleep(0.1)
    