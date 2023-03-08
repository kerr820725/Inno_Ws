import protobufs.pb_test_pb2 as pb
import requests , json  , websocket  , datetime
from Logger import create_logger
log  = create_logger()


class Im_Chat: # 異步 的會在  async_main 宣告
    def __init__(self , iid  ):
        self.iid = iid
        self.req = pb.Request()# 建立proto
        self.chat_id_wrapper = pb.ChatIDsWrapper() # message ChatIDsWrapper
        self.msg_entity = pb.MessageEntity() # message MessageEntity 


    def chat_connenct(self  ): # 連線   
    
        self.req.reqID = "123" # 隨機產
        self.req.command = 9   #  9 : SUBSCRIBE_CHAT 

        self.chat_id_wrapper.chatIDs.append(self.iid   ) # repeated  (iid)


        self.req.data.Pack(   self.chat_id_wrapper    )
        
        return self.req.SerializeToString()


    def send_msg(self , content = ''  ): #   , content 發送內容


        self.req.reqID = "123" # 隨機產
        self.req.command = 2 # 2:  SEND_MESSAGE  

        self.msg_entity.content  =  content # 發送內容
        self.msg_entity.chatID =  self.iid
        
        self.req.data.Pack(  self.msg_entity  )

        return self.req.SerializeToString()


def run(num, chat_ws_url):
    def on_msg(ws='', msg=''):        
        print(f"==== Msg({num}   {msg  }) :"  )
        str_msg = msg.decode('utf8', 'ignore') # bytes -> str
        
        try:
            Push  = pb.Push()
            Push.ParseFromString(msg)
            value = Push.data.value # bytes
            print(f'type_url: {Push.data.type_url} , command: {Push.command} , msg: {Push.msg} , value: {Push.data.value } ')
            


        except Exception as e:
            print('error: %s '%e )

        if 'TextingMessageWrapper'  in str_msg:
           req = pb.TextingMessageWrapper() 

        elif 'ReadPointerWrapper' in str_msg:
            req = pb.ReadPointerWrapper() 

        elif 'ChatIDsWrapper' in str_msg:
            req = pb.ChatIDsWrapper()
            
            


        elif 'GroupsWrapper' in str_msg:
           req = pb.GroupsWrapper()  
 
        elif 'MessageEntityWrapper' in str_msg: 
            req = pb.MessageEntityWrapper()

        elif  'MessageEntity' in str_msg:
            req = pb.MessageEntity()  
            
         


        req.ParseFromString(value)
        log.info(req)

        


    def on_error(ws, err):
        try :

            print(f"==== No.{num} Error info: {err}")

        except Exception as e :
            print(e.with_traceback)

    def on_closed(ws, status_code, close_msg):
        print(f"==== No.{num} Closed : status:  {status_code } , msg: {close_msg}  " )


    def on_open(ws):
        im_chat = Im_Chat(iid =  234 ) # 建立 im 連線
        
        connect_msg = im_chat.chat_connenct()
        ws.send( connect_msg  , opcode=0x2  )
        
        now_time =  datetime.datetime.now().strftime('%H:%M:%S')
        send_msg_ = im_chat.send_msg(content =  '%s'%now_time   )
        ws.send( send_msg_  , opcode=0x2  )
        log.info('send 成功')



 
    ws = websocket.WebSocketApp(f"{chat_ws_url} " , on_message=on_msg, on_error=on_error, on_close=on_closed)
    ws.on_open = on_open    
    ws.run_forever(ping_interval=20,ping_timeout=15)



         
'''

#一般  同步寫法

r = requests.session()

payload = {"vdID": 1, "name": "kerr", "password": "test1234", "vip": 2, "avatar": 16, "language": "zh-cn"}
response = r.post(url= 'http://172.28.40.157:8080/im/gateway/api/users/login'   ,data= json.dumps(payload)   )

print(response.text   )
chat_ws_url = response.json()['data']['link']
print(chat_ws_url)


run(num = 1 , chat_ws_url = chat_ws_url )

'''
