import asyncio       , time   , sys   
import   aiohttp  , configparser  , socket , selectors
from Function.rsa import *
from Function import platform_function as platform 
from Function import general_function as general
from Logger import create_logger
import async_function
import test_proto_w
import protobufs.pb_test_pb2 as pb

from collections import deque

from datetime import datetime
from websockets import connect
from aiohttp import ClientSession




#tw = pytz.timezone('Asia/Taipei')



log  = create_logger()




class Async_Stress:
    __slots__ = ('TIMEOUT',  'count' , 'pw'  , 'apptype' , 'device' , 'user_token' , 'env' , 'rain_ws_url' , 'sport_ws_url'   ,
     'user_num',  'semaphore' , 'ws_run_list' , 'chat_iid' , 'chat_sport' , 'chat_sid' , 'before_delay' , 'msg_delay' , 'chat_send' , 
     'bet_sport_iid' , 'bet_sport_sid' , 'bet_inplay' , 'deposit_open' , 'before_api' , 'sport_api_class' ,   'platform_api_class'  , 'adminToken' , 'prefix' ,
     'csv_platform_api' , 'csv_sport_api' ,'csv_chat_ws' ,'csv_rain_ws' ,'csv_sport_ws' , 'config', 'im_chat_url' , 'im_chat_proto'  )   
    
    def __init__(self) -> None:

        self.TIMEOUT = 60
        self.count = 0
        self.pw = 'test1234'
        pc_name = socket.gethostname()
        if '-' in pc_name :
            self.prefix = 'qa'+ pc_name.split('-')[-1]
        else:
            self.prefix = 'qa'+ pc_name


        self.apptype  = '2'
        self.device = "mobile"

        self.user_token = {}

        self.config = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
        self.return_config()


        vend = self.config['ws_main_run']['vend']

        self.env =  platform.get_env(vend)

        self.im_chat_url =   "http://im-api.innodev.site/im/gateway/api/users/login"                    #"http://172.28.40.157:8080/im/gateway/api/users/login"
        if 'stg' in vend:
            self.rain_ws_url = "wss://tiger-api.innostg.site/platform"
            self.sport_ws_url = 'wss://sports-api.innostg.site'
      

        else:
            self.rain_ws_url = "wss://tiger-api.innouat.site/platform"
            self.sport_ws_url = 'wss://sports-api.innouat.site'
     

        self.user_num = int(  self.config['ws_main_run']['totaluser'] )
        self.semaphore = (  int(self.config['ws_main_run']['semaphore']  )  )

        self.ws_run_list =  list(map(str.strip, self.config['ws_main_run']['run'].split(',')))   # rain,chat   執行 哪個ws
        self.chat_iid = self.config['sport_chart']['chat_iid']
        self.chat_sport = self.config['sport_chart']['chat_sport']
        
        sport_sid_mapping = {'football' : 1 , 'basketball': 2  , 'tennis': 3   ,'baseball': 4}
        self.chat_sid = sport_sid_mapping[self.chat_sport]

        self.before_delay = self.config['paltform_rain_ws']['before_delay'].split(':')
        chat_delay = self.config['sport_chart']['chat_delay'].split(':')
        self.msg_delay = int(chat_delay[0])
        #self.rain_user_dict = defaultdict(list)
        self.chat_send = self.config['ws_main_run']['chat_send']

        self.bet_sport_iid = self.config['paltform_rain_ws']['bet_sport_iid']
        self.bet_sport_sid = self.config['paltform_rain_ws']['bet_sport_sid']
        self.bet_inplay = self.config['paltform_rain_ws']['bet_inplay']

        self.deposit_open = self.config['ws_main_run']['deposit_open']
        self.before_api = self.config['paltform_rain_ws']['before_api'] # 如果只帶 sport 就是 只有 sport api


        current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")   
        
        self.csv_platform_api = 'async_platform_api'+current_datetime # 平台 api 登入寫入
        self.csv_sport_api = 'async_sport_api'+current_datetime
        self.csv_chat_ws =  'async_ws_chat'+current_datetime # 聊天室
        self.csv_rain_ws = 'async_ws_rain'+current_datetime # 包含apply
        self.csv_sport_ws = 'async_ws_sport'+current_datetime # 體育相關訂閱

        self.sport_api_class = async_function.Sport_Api(   env  = self.env , csv_name = self.csv_sport_api , 
                apptype = self.apptype , device = self.device  ,   bet_sport_iid = self.bet_sport_iid , bet_sport_sid = self.bet_sport_sid ,
                 bet_inplay = self.bet_inplay              )

        self.platform_api_class = async_function.Platform_Api(   env  = self.env , csv_name = self.csv_platform_api  ,
                        apptype = self.apptype , device = self.device )


        self.im_chat_proto = test_proto_w.Im_Chat(iid =  int(self.chat_iid) ) # 建立 im 連線
        
        log.info(f" ws_run_list: {self.ws_run_list} , chat_iid: {self.chat_iid} ,  chat_sport: {self.chat_sport} , before_delay : {self.before_delay} , msg_delay : {self.msg_delay } , chat_send: {self.chat_send}     ")

        log.info(f'bet_sport_iid: {self.bet_sport_iid}  , bet_sport_sid: {self.bet_sport_sid}  , bet_inplay: {self.bet_inplay}   ')

        log.info(f'deposit_open : {self.deposit_open} , before_api : {self.before_api} ')

    
    def return_config(self):
        try:

            self.config.read('config.ini', encoding="utf-8")


            if len(sys.argv) >= 2:# 傳入 外部 config
                log.info(sys.argv) # 會是一個list
                config_list = sys.argv

                for i in config_list: 
                    if '=' in i : # 傳入格式 必須是 參數名稱 =  value  ,ex: totaluser=1
                        config_arg = i.split('=' )
                        key_name = config_arg[0].strip()
                        key_value = config_arg[1].strip()

                        if key_value == '':# 防呆 , 如果傳進來 totaluser= 1 , 有空格  就會有錯誤
                            continue
                    
                        # 判斷 key_name , config_key 為要 set 進去的 名稱
                        if key_name in ['run', 'totaluser' , 'vend' , 'semaphore' , 'chat_send' , 'deposit_open' ]:
                            config_key = 'ws_main_run'
                        elif key_name in ['before_api' , 'before_delay' , 'bet_sport_iid' , 'bet_sport_sid' , 'bet_inplay' ]:
                            config_key = 'paltform_rain_ws'
                        elif key_name in ['chat_sport' , 'chat_iid' , 'chat_delay' , 'chat_event' ]:
                            config_key = 'sport_chart'
                        else:
                            log.error('key_name : %s , 不在 config key 裡'%key_name)
                            continue

                        self.config.set( config_key ,key_name , key_value   )

                file = open("config.ini", 'w' , encoding='utf-8')
                self.config.write(file) 
                file.close()
        except Exception as e:
            log.error('config main_ws error: %s'%e)
    
    
    
    
    
    
    # data : {'sport': {0: [api, api1] , 1:[api, api1] , 2: [api, api1]   }  ,   platform: {0: [api, api1] , 1:[api, api1] , 2: [api, api1]   }   }
    '''
    除了 bet(單純投注) 外, 其他 做 sport/ platform api , 比例 會有3個list 
    如果 分配的比例 1 list長度 小於 0 , 即使 range0 的api delay較少 , 也會因為失真
    所以會將 每個range 的list 長度 補齊 一致
    '''
    def Api_task(self): # 這邊是回傳  platform /sport 的 資料結構 , key 當sport / platform , value 分別為 秒數區分api
        if self.before_api == 'bet': #只做投注
            api_task_dict = {'sport': {0: ['tournament_info', 'match_details', 'game_bet'] }  }

        else:

            api_task_dict = {}


            sport_api_list = []
            for api in self.sport_api_class.sport_before_api_mapping.keys():

                sport_api_list.append(api)
            
            api_task_dict['sport'] = sport_api_list


           
            platform_api_list = []
            for api in self.platform_api_class.before_api_mapping.keys():

                platform_api_list.append(api)

            api_task_dict['platform'] = platform_api_list
            #log.info('sport api len: %s'%len(api_task_dict['sport'])   )
            #log.info('platform api len : %s'%len(api_task_dict['platform'])      )

        log.info('api_task_dict: %s'%api_task_dict )
        

        return api_task_dict

    def write_csv(self , acc , action  , start_time , end_time , status_code ,response_sec  , response , csv_type = 'platform_api' 
        , brListId= '' ): # cvv_type 預設 空 是寫入  一般 csv  , 其他寫入 聊天室監聽csv  . brlist rain 才會用到
        
        if csv_type == 'rain':
            write_content = {
            "user":acc,
            "action":action  , 
            "start_time": start_time,
            "end_time":end_time,
            "status_code":status_code,
            "diff": response_sec,
            #"brListId": brListId, 
            "response":response
            }
            csv_file = self.csv_rain_ws

            general.write_csv(csv_file, write_content , type = list(write_content.keys() )  ) 
        
        else:
            write_content = {
            "user":acc,
            "action":action  , 
            "start_time": start_time,
            "end_time":end_time,
            "status_code":status_code,
            "diff": response_sec,
            "response":response
            }


            if csv_type == 'platform_api':
                csv_file =  self.csv_platform_api # normalcsv_chat_name
            
            elif csv_type == 'sport_api':
                csv_file = self.csv_sport_api
            
            
            elif csv_type == 'sport': 
                csv_file = self.csv_sport_ws

            else: # chat
                csv_file = self.csv_chat_ws

            general.write_csv(csv_file, write_content)
        return True

    async def checkAccount(self , acc , session ):
        isExist = 'false'

        start_time = datetime.now()
        
        status_code = 'none' # 預設值
        response_sec = '-1'
        ptoken = 'none'
        end_time = 'none'
        
        url = f'{self.env["platform_api_URL"]}/user/accounts?account={acc}'
        headers = {
            'Content-Type': 'application/json',
            "referer": self.env["platform_URL"],
            "device": self.device ,
            # "devicemode": devicemode,
            "time-zone": "GMT+8",
            "apptype": self.apptype
        }

        try:


                
            async with session.get(url, timeout=self.TIMEOUT ,  headers= headers ) as resp:

                try:
                    r_text = await resp.text()
                    response = await resp.json()
                    
                    if 'isExist' in response['data']:
                        isExist = response['data']['isExist']
                                        
                except Exception as e :
                    log.error('checkAccount fail response: %s -  %s'%(r_text , e ) )   

            if isExist != True :
            
                end_time = datetime.now()
                status_code = resp.status
                response_sec = (end_time -  start_time  ).total_seconds()
                
                self.write_csv( acc = acc , action = '/platform/user/accounts' , start_time = start_time , end_time =end_time ,  status_code= status_code ,
                        response_sec = response_sec , response = r_text )

        except aiohttp.client_exceptions.ClientConnectorError as e: # network error 
            pass # 讓他走島下面  [acc] = {'isExist' : isExist  } 
        
        except asyncio.TimeoutError:
            pass

        except aiohttp.http.HttpProcessingError as e:
            pass
        except aiohttp.client_exceptions.ServerDisconnectedError as e:
            pass

        except Exception as e:
            log.error('checkAccount error: %s'%e)   
            response = 'checkAccount error: %s'%e

         
        
        self.user_token[acc] = {'isExist' : isExist  }
        return ''

    async def loginPlatfomuser(self  , acc , session ) -> str:
        


        url = f'{self.env["platform_api_URL"]}/user/token'
        cks = platform.get_cks( self.env['vendor_id'], acc )


        headers = {
            'Content-Type': 'application/json',
            "referer": self.env["platform_URL"],
            "device": self.device,
            # "devicemode": devicemode,
            "time-zone": "GMT+8",
            "apptype": self.apptype,
            'cks' : cks
        }

        payload = {
            "account": acc,
            "password": encrypt(self.pw ).decode("utf-8"),
            "clientNonce": None,
            "device": self.device
        }
        
        
        status_code = 'none' # 預設值
        response_sec = '-1'
        ptoken = 'none'
        end_time = 'none'
        r_text = ''

        retry_count = 0
        while True: # retry 不是 系統程式 的bug 
            try:
                
                start_time = datetime.now()
                #async with ClientSession() as session:
            

                async with session.post(url, timeout=self.TIMEOUT , json=payload ,  headers= headers ) as resp:

                    try:
                        r_text = await resp.text()
                        r_json = await resp.json()
                        self.count +=1
                        log.info('num: %s acc:  %s 登入 '%(self.count , acc))
                        ptoken = r_json['data']['token']
                    
                        
                    except Exception as e : # 走這邊正常 都是 帳密有錯誤 , 這種不retry
                        log.error('acc : %s login fail response : %s - %s'%(acc ,  r_text  , e)  )   
                status_code = resp.status
                end_time = datetime.now()
                response_sec = ( end_time - start_time ).total_seconds()
    
           
                log.info('login, resopnse: %s '%(  response_sec ) )
                self.write_csv( acc = acc , action = '/platform/user/token' , start_time = start_time , end_time =end_time ,  status_code= status_code ,
                response_sec = response_sec , response = r_text ) 

                self.user_token[acc] = {'ptoken' : ptoken , 'cks' : cks , 'num': self.count } # 外面會再針對  ptoken決定是不是要retry
                return True
            
            except aiohttp.client_exceptions.ClientConnectorError as e: # network error 
                pass

            except asyncio.TimeoutError:
                pass

            except aiohttp.http.HttpProcessingError as e:
                pass
            except aiohttp.client_exceptions.ServerDisconnectedError as e:
                pass
            except Exception as e:
                log.error('acc: %s login error: %s'%(acc ,e ))   
                
            retry_count +=1

            if retry_count>=5:
                log.error('acc : %s retry 五次 login 仍失敗'%acc )  
                self.user_token[acc] = {'ptoken' : ptoken , 'cks' : cks  } # 外面會再針對  ptoken決定是不是要retry
                return False

            

    async def admin_deposit(self , acc , session  ,  deposit_num = '' , amount = ''): # type 帶 approve 是put 審核 , type其他是 Post 衝直

        headers = {
            'Content-Type': 'application/json',
            "referer": self.env["admin_URL"],
            "device": self.device,
            # "devicemode": devicemode,
            "time-zone": "GMT+8",
            "apptype": self.apptype,
            "currency": "CNY",
            "authorization": "Bearer "+self.adminToken
        }
        
        # post 
        url = f'{self.env["platform_api_URL"]}/admin/deposit/op'
        deposit_num = deposit_num + datetime.now().strftime('%Y%md%H%M%S%f')

        post_payload = {
            "account":f"{acc}",
            "amount":f"{amount}",
            "currency": "CNY",
            "remark":"AutoTest",
            "orderNumber":f"{deposit_num}",
            "opMethod":0
        
                }      

        try:
                
            async with session.post(url, timeout=self.TIMEOUT , json=post_payload ,  headers= headers ) as resp:

                try:

                    r_text = await resp.text()
                    response = await resp.json()
                except Exception as e :
                    log.error('deposit fail response : %s'%r_text )
                    return ''

        except aiohttp.client_exceptions.ClientConnectorError as e: # network error 
            return 'False'

        except asyncio.TimeoutError:
            return 'False'

        except aiohttp.http.HttpProcessingError as e:
            return 'False'
        except Exception as e:
            log.error('deposit post error: %s'%e)   



        #put 
        put_payload = {
            "orderNumber": f"{deposit_num}",
            "status": "2",
            "memo": "AutoAccept"
        
                } 

        try:

            async with ClientSession() as session:
                
                async with session.put(url, timeout=self.TIMEOUT , json=put_payload ,  headers= headers ) as resp:

                    try:

                        r_text = await resp.text()
                        response = await resp.json()
                        return True
                    except Exception as e :
                        log.error('deposit fail response : %s'%r_text )
                        return ''

        except aiohttp.client_exceptions.ClientConnectorError as e: # network error 
            return 'False'

        except asyncio.TimeoutError:
            return 'False'

        except aiohttp.http.HttpProcessingError as e:
            return 'False'
        
        
        except Exception as e:
            log.error('deposit put error: %s'%e)
            return 'False' 

    async def createAccount_nonce(self , acc , session ):
         
        
        url = f'{self.env["platform_api_URL"]}/user/nonce'
        headers = {
        'Content-Type': 'application/json',
        "referer": self.env["platform_URL"],
        "device": self.device,
        # "devicemode": devicemode,
        "time-zone": "GMT+8",
        "apptype": self.apptype
        }

        

        payload = {
        "imageWidth": 280, 
        "imageHeight": 155, 
        "jigsawWidth": 52, 
        "jigsawHeight": 52
	    }



        if self.user_token[acc]['isExist']== True: # 已經建立過帳號
            return ''

        retry_count = 0
        clientNonce= 'none'
        while True:
            try:

                #async with ClientSession() as session:
                    
                async with session.post(url, timeout=100 , json=payload ,  headers= headers ) as resp:

                    try:

                        r_text = await resp.text()
                        response = await resp.json()
                        clientNonce = response['data']['clientNonce']
                        self.user_token[acc]['clientNonce'] = clientNonce
                        return True
                        
                    except Exception as e :
                        log.error('createAccount fail response : %s -  %s'%(r_text , e)  )   # api 有問題 的 就不retry 了
                        self.user_token[acc]['clientNonce'] = clientNonce # none
                        return ''
                          

            except aiohttp.client_exceptions.ClientConnectorError as e: # network error 
                pass # 讓他走島下面  [acc] = {'isExist' : isExist  } 
            
            except asyncio.TimeoutError:
                pass

            except aiohttp.http.HttpProcessingError as e:
                pass
            except aiohttp.client_exceptions.ServerDisconnectedError as e:
                pass
            except Exception as e:
                log.error('createAccount error: %s'%e)   
                response = 'createAccount error: %s'%e

            retry_count +=1 
            if retry_count >=5 :
                self.user_token[acc]['clientNonce'] = clientNonce # none
                log.error('createAccount_nonce retry 玩仍失敗 fail response '  ) 
                return ''

            
            
            
    async def createAccount_accounts(self , acc , session ):    
        url = f'{self.env["platform_api_URL"]}/user/accounts'
        headers = {
        'Content-Type': 'application/json',
        "referer": self.env["platform_URL"],
        "device": self.device,
        # "devicemode": devicemode,
        "time-zone": "GMT+8",
        "apptype": self.apptype
        }
        
        payload = {
            "account":acc,
            "password": encrypt(self.pw).decode("utf-8"),
            "confirmPassword": encrypt(self.pw).decode("utf-8"),
            "currency": "CNY",
            "locale":"zh_CN",
            "device": self.device,
            "clientNonce":self.user_token[acc]['clientNonce'],
            "type":1
        }

        retry_count = 0
        while True:
            try:

      
                    
                async with session.post(url, timeout=self.TIMEOUT , json=payload ,  headers= headers ) as resp:

                    try:
                            
                        r_text = await resp.text()
                        response = await resp.json()
                        log.info('acc: %s 創建帳號 ok'%acc)
                        return True
                        
                    except Exception as e :
                        log.error('createAccount fail response : %s -  %s'%(r_text , e)  ) 
                        return '' 

            
            except aiohttp.client_exceptions.ClientConnectorError as e: # network error 
                pass # 讓他走島下面  [acc] = {'isExist' : isExist  } 
            
            except asyncio.TimeoutError:
                pass

            except aiohttp.http.HttpProcessingError as e:
                pass
            except aiohttp.client_exceptions.ServerDisconnectedError as e:
                pass
            
            except Exception as e:
                pass

            retry_count +=1 
            if retry_count >=5 :
                log.error('createAccount_accounts retry 玩仍失敗 fail response '  ) 
                return ''


    async def change_wallet(self,   acc , session , currency = 'CNY'):# 切換幣別

        url = f'{self.env["platform_api_URL"]}/payment/wallets/active?currency=%s'%currency
        
        headers = {
            'Content-Type': 'application/json',
            "referer": self.env["platform_URL"],
            "device": self.device,
            # "devicemode": devicemode,
            "time-zone": "GMT+8",
            "apptype": self.apptype,
            # "cks": cks,
            "authorization": f"Bearer {self.user_token[acc]['ptoken'] }"
        }

        status_code = 'none' # 預設值
        response_sec = '-1'
        end_time = 'none'
        r_text = ''

        start_time = datetime.now()

        try:
            #async with ClientSession() as session:
            async with session.put(url, timeout=self.TIMEOUT ,  headers= headers  ) as resp:
                try:
                    r_text = await resp.text()
                    response = await resp.json()
                    
                except Exception as e :
                    log.error('change_wallet  fail: %s -  %s'%(r_text , e ))   

            end_time = datetime.now()
            status_code = resp.status
            response_sec = (end_time -  start_time ).total_seconds()
        
        except aiohttp.client_exceptions.ClientConnectorError as e: # network error 
            pass # 讓他走島下面  [acc] = {'isExist' : isExist  } 
        
        except asyncio.TimeoutError:
            pass

        except aiohttp.http.HttpProcessingError as e:
            pass
        except aiohttp.client_exceptions.ServerDisconnectedError as e:
            pass
        
        except Exception as e:
            log.error('change_wallet error: %s'%e)   
            r_text = 'change_wallet error: %s'%e


        self.write_csv( acc = acc , action = '/platform/payment/wallets/active?currency=CNY' , start_time = start_time , end_time =end_time ,  status_code= status_code ,
             response_sec = response_sec , response = r_text ) 

        return ''

    async def loginSportuser(self , acc , session ):
        while True:
            retry_count = 0
            stoken = 'none'
            try:
                url = f'{self.env["platform_api_URL"]}/thirdparty/game/entry'
                Param = {
                "providerCode": 1 ,
                "device": self.device
                }
                
                try:
                    cks = self.user_token[acc]['cks']
                except:
                    cks = platform.get_cks( self.env['vendor_id'], acc )

                headers = {
                    'Content-Type': 'application/json',
                    "referer": self.env["platform_URL"],
                    "device": self.device,
                    # "devicemode": devicemode,
                    "time-zone": "GMT+8",
                    "apptype": self.apptype,
                    'cks' : cks ,  
                    'authorization' : f"Bearer {self.user_token[acc]['ptoken'] }" 
                }

                status_code = 'none' # 預設值
                response_sec = '-1'
                
                end_time = 'none'
                r_text = ''

                start_time = datetime.now()

                try:
                    #async with ClientSession() as session:
                    async with session.get(url, timeout=self.TIMEOUT , params=Param ,  headers= headers  ) as resp:
                        try:
                            r_text = await resp.text()
                            response = await resp.json()

                            stoken =  response['data']['token']

                            
                        except Exception as e :
                            log.error('game/entry fail response: %s - %s'%(r_text , e ) )  

                    end_time = datetime.now()
                    response_sec = (end_time -  start_time ).total_seconds()
                    
                    #log.info('server_time: %s'%end_time)

                    status_code = resp.status

 

                    self.write_csv( acc = acc , action = '/platform/thirdparty/game/entry' , start_time = start_time , end_time =end_time ,  status_code= status_code ,
                    response_sec = response_sec , response = r_text ) 


                    self.user_token[acc]['stoken'] =  stoken
                    return ''


                except aiohttp.client_exceptions.ClientConnectorError as e: # network error 
                    pass # 讓他走島下面  [acc] = {'isExist' : isExist  } 
                
                except asyncio.TimeoutError:
                    pass

                except aiohttp.http.HttpProcessingError as e:
                    pass
                except aiohttp.client_exceptions.ServerDisconnectedError as e:
                    pass
                
                except Exception as e:
                    log.error('game/entry error: %s'%e)   
                    r_text = 'game/entry error: %s'%e

                retry_count +=1
                if retry_count >=5:
                    self.user_token[acc]['stoken'] =  stoken
                    return ''


                

            except:
                self.user_token[acc]['stoken'] =  stoken
                return ''
          


    async def extension(self , acc   ):
        url = f'{self.env["platform_api_URL"]}/user/token/extension'


        headers = {
            'Content-Type': 'application/json',
            "referer": self.env["platform_URL"],
            "device": self.device,
            # "devicemode": devicemode,
            "time-zone": "GMT+8",
            "apptype": self.apptype,
            "cks":  self.user_token[acc]['cks']  ,
            "authorization": f"Bearer {self.user_token[acc]['ptoken'] }" 
        }

        start_time = datetime.now()
        
        status_code = '-1' # 預設值
        response_sec = '-1'
        r_text = ''
        end_time = ''
        
        try:
            async with ClientSession() as session:
                async with session.put(url, timeout=self.TIMEOUT ,  headers= headers  ) as resp:
                    try:
                        r_text = await resp.text()
                        response = await resp.json()
                        
                    except Exception as e :
                        log.error('extension fail response  %s - %s  '%(r_text , e) )   

            
            end_time = datetime.now()
            status_code = resp.status
            response_sec = (end_time  -  start_time ).total_seconds()
        
        except aiohttp.client_exceptions.ClientConnectorError as e: # network error 
            if r_text == '':
                r_text = str(e)

        
        except Exception as e:
            log.error('user/token/extension error: %s'%e)   
            r_text = 'user/token/extension error: %s'%e


        self.write_csv( acc = acc , action = '/platform/user/token/extension' , start_time = start_time , end_time =end_time ,  status_code= status_code ,
             response_sec = response_sec , response = r_text ) 

        return ''
        
    async def wallet_list(self , acc):
        url = f'{self.env["platform_api_URL"]}/payment/wallets/list'

        headers = {
            'Content-Type': 'application/json',
            "referer": self.env["platform_URL"],
            "device": self.device,
            # "devicemode": devicemode,
            "time-zone": "GMT+8",
            "apptype": self.apptype,
            # "cks": cks,
            "authorization": "Bearer "+ self.user_token[acc]['ptoken']
        }


        start_time = datetime.now()
            
        status_code = '-1' # 預設值
        response_sec = '-1'
        amount = -1
        end_time = ''
        r_text = ''

        try:
            async with ClientSession() as session:
                async with session.get(url, timeout=self.TIMEOUT  ,  headers= headers ) as resp:
                    try:
                        r_text = await resp.text()
                        response = await resp.json()

                        amount = response['data']['wallets'][0]['amount']

                        
                    except Exception as e :
                        log.error('wallet_list fail response : %s -  %s'%(r_text , e ) )   

            end_time = datetime.now()
            status_code = resp.status
            response_sec = (end_time - start_time ).total_seconds()
        
        except aiohttp.client_exceptions.ClientConnectorError as e: # network error 
            if r_text == '':
                r_text = str(e)

        except asyncio.TimeoutError:
            #log.error('api: %s  TimeoutError'%api )
            return False

        except Exception as e:
            log.error('wallet_list error: %s'%e)   
            r_text = 'wallet_list error: %s'%e

        self.write_csv( acc = acc , action = '/platform/payment/wallets/list' , start_time = start_time , end_time =end_time ,  status_code= status_code ,
             response_sec = response_sec , response = r_text ) 

        return ''
    
    async def rain_apply(self ,acc , promotionId , promotionType , retry_count , loop='' ,  diff_sec =0 , semaphore = '' ):
        while True: # retry network error
            url = f'{self.env["platform_api_URL"]}/promotion/promotion/apply'
            headers = {
                'Content-Type': 'application/json',
                "referer": self.env["platform_URL"],
                "device": self.device,
                # "devicemode": devicemode,
                "time-zone": "GMT+8",
                "apptype": self.apptype,
                # "cks": cks,
                "currency": "CNY",
                "authorization": "Bearer "+ self.user_token[acc]['ptoken']
            }
            payload = {
                "id":promotionId,
                "promotionType":promotionType
            }
            
            
            status_code = '-1' # 預設值
            response_sec = '-1'
            amount = -1
            end_time = ''
            r_text = '' # 給預設


            if diff_sec < 0 :
                sleep_time = float(abs(diff_sec)) + 1 # 故意加個 1秒
                log.info('diff sec 小於0先 等待 : %s '%sleep_time )
                await asyncio.sleep(sleep_time)
                
            try:

                async with ClientSession() as session:
                    start_time = datetime.now()
                    log.info('apply 發送 ')
                    async with session.post(url, timeout=120 , json=payload ,  headers= headers ) as resp:


                        log.info('apply 送玩 ')
                        try:
                            r_text = await resp.text()
                            response = await resp.json()

                            amount = response['data']['rewards'][0]['amount']

                            
                        except Exception as e :
                            log.error('acc : %s rain_apply fail response : %s - %s'%(acc , r_text , e ) )   
                            
                        end_time = datetime.now()
                        #server_end_time = datetime.fromtimestamp(  response['time']  /1000  ).strftime("%Y-%m-%d %H:%M:%S.%f")
                        status_code = resp.status
                        response_sec = (end_time - start_time ).total_seconds()
                    

                        self.write_csv( acc = acc , action = '/platform/promotion/promotion/apply' , start_time = start_time , end_time =end_time ,  status_code= status_code ,
                                response_sec = response_sec , response = r_text   , csv_type= 'rain'   ) 

                        log.info(f'user: {acc}  , apply  done  , response_sec : {response_sec}  ')

                        return ''


            
            except aiohttp.client_exceptions.ClientConnectorError as e: # network error 
                    log.error(f'{acc}:  apply Connect failed: {e} , need retry: {retry_count} ')
                    retry_count += 1


            except Exception as e: # 沒預期的error
                if r_text  != '':   
                    
                    r_text = 'rain_apply error: %s'%e
                    log.error('acc: %s rain_apply , response: %s error: %s'%( acc ,r_text , e) )

                    self.write_csv( acc = acc , action = '/platform/promotion/promotion/apply' , start_time = start_time , end_time =end_time ,  status_code= status_code ,
                            response_sec = response_sec , response = r_text   , csv_type= 'rain'   ) 

                    return ''
                
                else: # r_text為空 , 這邊也走retry
                    log.error('acc: %s rain_apply , response: %s error: %s , need retry : %s '%( acc ,r_text , e , retry_count) )
                    retry_count += 1
            
            if retry_count >= 5: # 走到這 retry count 上限 
                return False

        
    async def sport_ws_progress(self , acc): # sport 體育 賠率 ws
        try:
            sport_ws_url  = f"{self.sport_ws_url}/product/websocket/ws?referer={self.env['platform_URL']}&token={self.user_token[acc]['stoken']}"   
            
            async with connect(sport_ws_url) as websocket:
                await websocket.send("CONNECT\naccept-version:1.0,1.1,2.0")
                
                if self.before_api == 'bet': # 只做 order status
                    await websocket.send("SUBSCRIBE\nid:1\ndestination:%s\nack:auto\n\n\x00\n"%f"/topic/match/event" )
 
                    await websocket.send("SUBSCRIBE\nid:2\ndestination:%s\nack:auto\n\n\x00\n"%f"/topic/order/status" )

               

                else:
            
                
                    await websocket.send("SUBSCRIBE\nid:1\ndestination:/topic/odds-diff/match/111111\nack:auto\n\n\x00\n")


                    await websocket.send("SUBSCRIBE\nid:2\ndestination:%s\nack:auto\n\n\x00\n"%f"/topic/odds-diff/match/{self.chat_iid}" )
     

                    await websocket.send("SUBSCRIBE\nid:3\ndestination:%s\nack:auto\n\n\x00\n"%f"/topic/match/inplay/info/{self.chat_iid}" )
 

                    await websocket.send("SUBSCRIBE\nid:4\ndestination:%s\nack:auto\n\n\x00\n"%f"/topic/match/event" )

                    
                    await websocket.send("SUBSCRIBE\nid:5\ndestination:%s\nack:auto\n\n\x00\n"%f"/topic/popular/match" )


                    await websocket.send("SUBSCRIBE\nid:6\ndestination:%s\nack:auto\n\n\x00\n"%f"/topic/order/status" )
   

                    await websocket.send("SUBSCRIBE\nid:7\ndestination:%s\nack:auto\n\n\x00\n"%f"/topic/match/bubble/GMT-04:00" )

                    await websocket.send("SUBSCRIBE\nid:8\ndestination:%s\nack:auto\n\n\x00\n"%f"/topic/order/status" )
              
               
               
                

                log.info('acc: %s sport ws connect ok'%acc)
                while True:
                    response = await websocket.recv()   
                    json_msg = response.replace("'", "\"")
                    #log.info('sport ws response: %s'%json_msg)
                    
                    if 'CONNECTED' in json_msg:
                        action = 'Sport_Connect'
                        split_msg = ''
                    elif 'destination' in json_msg:

                        action_url = json_msg.split('\n\n')[0].split('destination:')[1].split('\n')[0]
                        split_msg = json_msg.split('\n\n')[1]  
                        action = 'Sport_%s'%action_url
                    else:
                        action = 'Sport_others'
                        split_msg = json_msg


                    
                    self.write_csv( acc = acc , action = action , start_time = datetime.now() ,
                             end_time = '' ,  status_code= 0,
                                    response_sec = '' , response = split_msg , csv_type = 'sport'  ) 


        except Exception as e:
            if 'Network' not in str(e):
                log.error('sport ws error: %s'%e)
            #self.user_token[acc]['sport_ws_retry'] = 'true'
            self.write_csv( acc = acc , action = 'Sport_WS_Error' , start_time = datetime.now() ,
                             end_time = '' ,  status_code= 0,
                                    response_sec = '' , response = str(e)    , csv_type='sport'   ) 

            if 'server rejected' in str(e):
                self.user_token[acc]['sport_ws_retry'] = 'false'
            else:
                self.user_token[acc]['sport_ws_retry'] = 'true'
            
            return 'False'
        
    
    # 平台 ws 流程
    async def rain_ws_progress(self  , acc  ):
        
        try:
            brListId = '' # 預設 寫入excel
            wss_url = f"{self.rain_ws_url}/websocket/channel/private?token={self.user_token[acc]['ptoken'] }&appType=2&referer={self.env['platform_URL']}&device=mobile&language=zh_CN"
            async with connect(wss_url) as websocket:
                await websocket.send("CONNECT\naccept-version:1.0,1.1,2.0")
                log.info('acc: %s rain ws connect ok'%acc)
                
                self.write_csv( acc = acc , action = 'Rain_Connect' , start_time = datetime.now() ,
                             end_time = '' ,  status_code= 0,
                                    response_sec = '' , response = "" , csv_type='rain'   ) 
                
                while True:
    
                        
                    response = await websocket.recv()   
                    json_msg = response.replace("'", "\"")
                    
                    if 'brPartyTime' in response:
                        

                        rain_dict = json.loads(response)
                        local_receive_time = time.time()*1000 # python 當下接收時間
                        if 'brListId' in rain_dict['data']:
                            promotion_id = rain_dict['data']['brListId']
                            brListId = promotion_id
                        else:
                            promotion_id = rain_dict['data']['masterId']
                        
                        rain_begin = rain_dict['data']['begin'] # 紅包雨開始時間
                        #promotion_title = rain_dict['data']['title']
                        promotion_type = rain_dict['data']['promotionType']
                        diff_sec = (local_receive_time-rain_begin)/1000 
                        #countdownTime = rain_dict['data']['countdownTime']

                        #self.rain_user_dict[promotion_id].append(acc  ) 

                        self.write_csv( acc = acc , action = 'Rain' , start_time = rain_begin , end_time = local_receive_time ,  status_code= 0 ,
                                    response_sec = diff_sec , response = json_msg , csv_type='rain' , brListId = str( brListId)  ) 

                        log.info(f"acc : {acc}  local_receive_time: {local_receive_time }, begin: { rain_begin } , diff: {diff_sec}  ")

                        
                        
                        '''
                        if diff_sec <= 0:
                            sleep_time = float(abs(diff_sec)) + 1 # 故意加個 1秒

                            await asyncio.sleep(sleep_time)
                        '''

                        retry_count = 1 # 用來設定 apply停損點
                        
         
       
                        await self.rain_apply(  acc = acc , promotionId  = promotion_id , promotionType = promotion_type ,  retry_count= retry_count , diff_sec = diff_sec    )
       
                        
                        #asyncio.run_coroutine_threadsafe( self.rain_apply( acc = acc , promotionId  = promotion_id , promotionType = promotion_type ,  retry_count= retry_count , diff_sec = diff_sec , loop = apply_loop   )    , apply_loop     )
                        #asyncio.ensure_future( self.rain_apply( acc = acc , promotionId  = promotion_id , promotionType = promotion_type ,  retry_count= retry_count , diff_sec = diff_sec     ) )

                        #await self.wallet_list(  acc = acc)

                    
                    else:
                        self.write_csv( acc = acc , action = 'Rain_OtherWSMsg' , start_time = datetime.now() ,
                             end_time = "" ,  status_code= 0 ,
                                    response_sec = "" , response = ''    , csv_type='rain'    )  #response other 訊息 到後面excel 檔案大小會太大 
      
                        if 'availableBalance' in response: 
                            log.info(f"acc: {acc}, msg: {response} "  )




        except Exception as e:
            if  'Network' not in str(e) and str(e) != '':
                log.error('acc : %s  , rain ws error : %s'%(acc , e)  )

            self.write_csv( acc = acc , action = 'Rain_WS_Error' , start_time = datetime.now() ,
                             end_time = '' ,  status_code= 0,
                                    response_sec = '' , response = str(e)    , csv_type='rain'   ) 
            if 'server rejected' in str(e):
                self.user_token[acc]['ws_retry'] = 'false'
            else:
                self.user_token[acc]['ws_retry'] = 'true'
            return 'False'

    async def sport_ws_run(self , acc ): # 用來 ws retry  用
        
        if self.user_token[acc]['stoken'] == 'none':
            return ''

        while True: 
            await self.sport_ws_progress(acc)
            await asyncio.sleep( 3  ) 
            try:
                if self.user_token[acc]['sport_ws_retry'] == 'false':
                    return ''
            except:
                pass

            
    async def rain_ws_run(self , acc  ): # 用來 ws retry  用
        
        if self.user_token[acc]['ptoken'] == 'none':
            return ''

        while True: 
            await self.rain_ws_progress(acc )
            await asyncio.sleep( 3  ) 
            try:
                if self.user_token[acc]['ws_retry'] == 'false':
                    return ''
            except:
                pass
    
    async def chat_on_msg(self ,acc ,  ws):
        while True:
            try:
                msg = await ws.recv() 
            except:
                self.user_token[acc]['chat'] = 'false'
                return False

            end_time , diff  = '', ''  
            now_time =  datetime.now().strftime('%H:%M:%S')
            
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
                            
                        
                            now_time_date = datetime.datetime.strptime(now_time , '%H:%M:%S') 
                            
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

            #log.info('acc : %s , action : %s , diff: %s  recive ok '%(acc , action , diff )  )

            self.write_csv( acc = acc , action = 'on_msg_%s'%action   , start_time = now_time  ,
                end_time = end_time ,  status_code = '',   response_sec = diff , response = split_msg   ,  csv_type = 'on_msg'  ) 

    async def chat_on_im_msg(self  , acc , ws ):        
        
        while True:
            #await asyncio.sleep(int(10   )   )
            try:
                msg = await ws.recv() 

                str_msg = msg.decode('utf8', 'ignore') # bytes -> str
            except Exception as e:
                if 'sent 1000 (OK)' in str(e):
                    pass
                else:
                    log.error(f'chat_on_msg error: {e }')
                    
            action = 'other'
            
            try:
                Push  = pb.Push()
                Push.ParseFromString(msg)
                value = Push.data.value # bytes
                #log.info(f'type_url: {Push.data.type_url} , command: {Push.command} , msg: {Push.msg} , value: {Push.data.value } ')
                
            except Exception as e:
                log.error('chat_on_msg error: %s '%e )

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
                action = 'message'
                    


            req.ParseFromString(value)
            

            
            if action == 'message':
                content , end_time_date  , diff = ''  , '' , ''  
                try: 
                    
                    #split_msg = str(req)
                    
                    content =   str( req.content) # 本地 發送訊息時 的時間 , 程式發出的 content 會是時間格式 

                    split_msg = f'content:{content}  , senderName: {req.senderName}'

                    #end_time_date =  time.strftime("%H:%M:%S", time.localtime(req.timestamp)  ) # server 接收到 訊息的時間
                    
                    end_time_date = datetime.now()
                    #log.info(f'acc: {acc } recive msg ok , content: {content} ')
                    
                    try: # 這邊如果手動發送 不是時間訊息 , content 會有錯誤 
                        # server端接收時間 和  loacl 發送的 時間差
                        diff =  ( end_time_date-  datetime.strptime(content,'%Y-%m-%d %H:%M:%S.%f' ) ).total_seconds()        
                        

                        self.write_csv( acc = acc , action = 'on_msg_%s'%action   , start_time = content  ,
                        end_time = end_time_date ,  status_code = '',   response_sec = diff , response = split_msg   ,  csv_type = 'on_msg'  ) 

                    except:
                        pass
                    
                    
                
                except  Exception as e:
                    error_msg = str(e)
                    log.error(f' chat_on_msg revice error: {error_msg}' )
                    self.write_csv( acc = acc , action = 'on_msg_error'   , start_time = content  ,
                        end_time = end_time_date ,  status_code = '',   response_sec = diff , response = error_msg   ,  csv_type = 'on_msg'  ) 


    


    async def  chat_send_msg(self , ws  , acc ,  ): # 聊天室  發送訊息

        try:


            now_time =  datetime.now().strftime('%H:%M:%S') # 會拿來當作發送訊息 . 把年 月 拿掉 , 後端 吐回訊息 會被 ****



            str_msg = json.dumps(  {"type":"message","target":"","data":{"self":True ,"message":  now_time }}   )

            sub = "SEND\ndestination:%s\ncontent-type:%s\n%s\n%s\x00\n" % (    f"/app/chat.{self.chat_iid}"    , "application/json"   , '',str_msg   )
            await ws.send( sub )

            #log.info('acc: %s send ok'%acc)    
            self.write_csv( acc = acc , action = 'send_msg' , start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') ,
                                end_time = '' ,  status_code= 0,  csv_type = 'on_msg' , 
                                        response_sec = '' , response = '{"self":True ,"message":  %s }'%now_time   ) 
        except Exception as e:
            log.error(' chat send msg error: %s '%e   )

   

    async def im_chat_ws_progress(self  , acc):
        
        
        payload = {"vdID": 1, "name": acc , "password": "test1234", "vip": 2, "avatar": 16, "language": "zh-cn"}
        
        async with ClientSession() as session:
            async with session.post(url = self.im_chat_url  , timeout=self.TIMEOUT , json=payload  ) as resp:
                
                try:
                    response = await resp.json()
                    chat_ws_url = response['data']['link']
                    log.info(f'im chat login : {response} '   )


                    #test_proto_w.run(num = 1 , chat_ws_url = chat_ws_url )
                except Exception as e:
                    log.error(f' im_chat_ws_progress error: {e}')
                    return False

        try:
            connect_msg = self.im_chat_proto.chat_connenct()
            
            async with connect(chat_ws_url) as websocket:
    
                await websocket.send( connect_msg     )
                

                asyncio.ensure_future (  self.chat_on_im_msg(acc = acc , ws = websocket   )  )# 裡面是 while true , 需出來  , 掃 api
                

                
                while True:
                    if self.chat_send  == 'true':
                        #now_time =  datetime.now().strftime('%H:%M:%S.%f') # 會拿來當作發送訊息 . 把年 月 拿掉 , 後端 吐回訊息 會被 ****
                        now_time =  datetime.now()
                        #self.user_token[acc]['chat_now_time'] = now_time
                        
                        send_msg_ = self.im_chat_proto.send_msg(content =  '%s'%(now_time )  )
                
                        await websocket.send( send_msg_    )
                        log.info(f' acc: {acc }  send msg : {send_msg_ } ')
                        
                        self.write_csv( acc = acc , action = 'send_msg' , start_time = now_time   ,
                                end_time = '' ,  status_code= 0,  csv_type = 'on_msg' , 
                                        response_sec = '' , response = ''  )
                    
                    await asyncio.sleep( int( self.msg_delay )  ) 
    
        
        except Exception as e:
            error_msg = str(e)
            log.error(f'im chat ws error: {error_msg} ')
            self.write_csv( acc = acc , action = 'send_msg_error' , start_time = ''   ,
                                end_time = '' ,  status_code= -1,  csv_type = 'on_msg' , 
                                        response_sec = '' , response = error_msg )
            return False



    # 平台 ws 流程
    async def chat_ws_progress(self  , acc):
        
        try:
            wss_url = f"{self.sport_ws_url}/product/chat/ws-chat?channel={self.chat_iid}&sid={self.chat_sid}&token={self.user_token[acc]['stoken']}&referer={self.env['platform_URL']}&language=zh-cn"

            async with connect(wss_url) as websocket:
                await websocket.send("CONNECT\naccept-version:1.1,1.0")
                await websocket.send("SUBSCRIBE\nid:1\ndestination:/topic/chat.1111111\nack:auto\n\n\x00\n")
                await asyncio.sleep( 1  ) 

                await websocket.send("SUBSCRIBE\nid:2\ndestination:%s\nack:auto\n\n\x00\n"%f"/topic/chat.{self.chat_iid}" )
                await asyncio.sleep( 1  ) 

                await websocket.send("SUBSCRIBE\nid:3\ndestination:%s\nack:auto\n\n\x00\n"%f"/user/topic/chat.{self.chat_iid}" )
                await asyncio.sleep( 1  ) 

                log.info('acc: %s chat ws connect ok'%acc)
                
                self.write_csv( acc = acc , action = 'Chat_Connect' , start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') ,
                             end_time = '' ,  status_code= 0,
                                    response_sec = '' , response = "" , csv_type = 'on_msg'  ) 
                
                self.user_token[acc]['chat'] = 'true'
                
                asyncio.ensure_future(  self.chat_on_msg(acc = acc , ws = websocket   )  )# 裡面是 while true , 需出來  , 掃 api 

                
                while True:
                    if  self.user_token[acc]['chat'] == 'false':
                        return 'false'
                    if self.chat_send  == 'true':
                        await self.chat_send_msg(acc = acc , ws = websocket   )

                    await asyncio.sleep( int( self.msg_delay )  )

        except aiohttp.client_exceptions.ClientConnectorError as e:
            self.user_token[acc]['chat_ws_retry'] = 'true'
            return 'False'


        except Exception as e:
            log.error('acc : %s  , chat  ws error : %s'%(acc , e)  )

            self.write_csv( acc = acc , action = 'Chat_WS_Error' , start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') ,
                             end_time = '' ,  status_code= 0,
                                    response_sec = '' , response = str(e)  , csv_type = 'on_msg'  ) 
            if 'server rejected' in str(e):
                self.user_token[acc]['chat_ws_retry'] = 'false'
            else:
                self.user_token[acc]['chat_ws_retry'] = 'true'
            return 'False'
        
    async def chat_im_ws_run(self ,acc):
        try:
            await self.im_chat_ws_progress(acc)
        except Exception as e:
            log.error(f'chat_im_ws_run  error: {e}')
            return False


    async def chat_ws_run(self ,acc):
        
        while True: 
            await self.chat_ws_progress(acc)

            try:
                if self.user_token[acc]['chat_ws_retry'] == 'false':
                    return False 
            except:
                pass



    async def run_sport_api(self , acc , api_list , delay , loop=''   ): # 體育 api 


        new_init_data = 'true' # 是初始 會新抓好相關體育資料 ,  避免每次 都重新抓取新資料 ,game bet 的 iid 會因為 tournament/ match?iid=(抓賠率)  iid 一直更新
        
    

        async with ClientSession(   ) as session:   
            while True: 
                
                await self.sport_api_class.before_api(    acc = acc  , 
                        api_list = api_list , new_init_data = new_init_data , api_delay = delay , stoken= self.user_token[acc]['stoken']  ,  
                            num = self.user_token[acc]['num'] , session = session     )

                if self.before_api == 'bet' : # 初始拿到 新關資訊後  , 就直接滾 bet就可
                    
                    if self.sport_api_class.bet_stop_flag == 'true' or self.sport_api_class.bet_stop_flag == '': # tournament_info 沒 資料 
                        api_list = [  'tournament_info'  ,'match_details', 'game_bet']
                    else:
                        api_list = [ 'match_details', 'game_bet']
                        new_init_data = 'false'

                else: # 非bet 增加sleep ,否則後面登入 人數越多 ,越容易堵塞
                    await asyncio.sleep(10)
                
    
    async def run_mix_api(self , acc , api_task , delay , loop=''    ): # 打平台  api

        while True:
            new_init_data = 'true'
            for api in api_task['platform']:
                await self.platform_api_class.before_api(    acc = acc , ptoken =  self.user_token[acc]['ptoken'] ,
                    api = api , api_delay = delay  ,  num = self.user_token[acc]['num']    ) 


            await self.sport_api_class.before_api(    acc = acc  , 
                    api_list = api_task['sport'] , new_init_data = new_init_data , api_delay = delay , stoken= self.user_token[acc]['stoken']  ,  
                        num = self.user_token[acc]['num']   )

            new_init_data = 'false'



    async def run_platform_api(self , acc , api_list , delay , loop='' , session = ''    ): # 打平台  api

        
        async with ClientSession(  ) as session:
            while True:
                
                for api in api_list:
                    await self.platform_api_class.before_api(    acc = acc , ptoken =  self.user_token[acc]['ptoken'] ,
                        api = api , api_delay = delay  ,  num = self.user_token[acc]['num'] , session= session    ) 


    async def run_api(self , user_list='' , api_task='', loop_ ='' , acc = '' ):
        #log.info('user_list: %s'% user_list )
        for acc_ in  acc: 
            await self.api_progress( acc =  acc_ , api_task = api_task   )
            await asyncio.sleep(  1 )
        




    async def  run (self    ): # run  整個流程   main_progress
       

       

        user_list = [  self.prefix+"{:03d}".format( _+1 )      for _ in range(self.user_num)     ]
        

        api_task = self.Api_task()# 回傳 平台/體育 各api 頻率分布 data


        if self.deposit_open == 'true':  # 有要充值 財登入後台
            adminacc =  self.prefix+'admin'
            if 'qaqa'in adminacc:
                adminacc = adminacc.replace('qaqa', 'qa')
            
            log.info(  f'adminacc: {adminacc}   ')
            
            self.adminToken = platform.loginAdmin(self.env   , adminacc, self.pw )  # 後台登入


        
        if self.semaphore == 0:
            log.info('loop 登入')
            # loop 登入
            for acc in  user_list : 
                await self.main_progress( acc =  acc    )
                await(  self.run_api(user_list = [acc] , api_task = api_task , loop_= 'true' )   )
                await(  self.ws_prgoress(   acc = acc )   )

        else:
        

            

            init_assign = 0
            assign_login = int(self.semaphore) # 100
            
            if self.semaphore > self.user_num:
                login_range =  self.user_num
            else:
                login_range = round( self.user_num /self.semaphore)
            log.info('login_range: %s '%login_range )
        
            asign_user_dict = {}
            tasks = deque()
           
            for index_range in range( login_range    ) :
                
                login_user_list = user_list[init_assign:assign_login ] 

                jobs = deque()
  
                for acc in login_user_list:
                    jobs.append (    self.main_progress( acc =  acc    )                  )
                   



                for num , job in enumerate( asyncio.as_completed(jobs) )  :
                    await job
                    init_assign+=1
                    assign_login+=1
                

                log.info( 'index_range: %s , init_assign: %s , assign_login : %s '%(index_range ,  init_assign , assign_login)  )

                #log.info('user_token: %s'%self.user_token   )
                asign_user_dict[index_range] =  login_user_list
                #for acc in asign_user_dict[index_range]:
                
                
                f = asyncio.ensure_future(  self.ws_prgoress(acc = asign_user_dict[index_range]   )   ) # 裡面是 while true , 需出來  , ws 
                f1 = asyncio.ensure_future( self.run_api( acc = asign_user_dict[index_range]   , api_task = api_task     ) ) # 裡面是 while true , 需出來  , ws 
            
                tasks.append(f)
                tasks.append(f1)
     
                
                
                
      

            await asyncio.gather(*tasks)
           



       
        log.info('login done')

  
    async def main_progress(self   , acc    ):

        async with ClientSession() as session:
        
            await self.checkAccount(acc= acc , session = session )
            
            if self.user_token[acc]['isExist'] != True: # 已經建立過帳號
                await self.createAccount_nonce(acc= acc , session = session ) # /user/nonce
                if self.user_token[acc]['clientNonce'] == 'none':
                    return False
                await self.createAccount_accounts(acc= acc , session = session ) # user/accounts
                
            await self.loginPlatfomuser( acc = acc , session = session )

            if self.user_token[acc]['ptoken'] == 'none':
                return False
            
            await self.change_wallet(acc= acc , session = session )
            await self.loginSportuser(acc = acc , session = session  )  
            if self.user_token[acc]['stoken'] == 'none':
                return False
            

            
            

            if self.deposit_open == 'true' and self.adminToken!= '':
                try:
                    await self.admin_deposit(  acc = acc  , amount= 80000 , deposit_num = self.prefix   , session = session )  # 充值發起 / 審核
                    
                except Exception as e: # 別影響登入
                    log.error('acc: %s 充值錯誤 : %s'%(acc, e) )


    async def ws_prgoress(self , acc = ''  ):  


        for acc_ in acc:

            for run_ws in self.ws_run_list:
                
                if run_ws == 'rain':
                    f = asyncio.ensure_future(  self.rain_ws_run(acc = acc_  ,  )   ) # 裡面是 while true , 需出來  , ws 
                    
                    #asyncio.run_coroutine_threadsafe(  self.rain_ws_run(acc = acc  ) , ws_loop   )
         
                elif run_ws == 'chat':
                    
                    f = asyncio.ensure_future(  self.chat_ws_run(acc = acc_ )   ) # 裡面是 while true , 需出來  , ws
                    #asyncio.run_coroutine_threadsafe(  self.chat_ws_run(acc = acc ) , ws_loop   )  

                elif run_ws  == 'im_chat':
                    f = asyncio.ensure_future(  self.chat_im_ws_run(acc = acc_ )   ) # 裡面是 while true , 需出來  , ws

                else: # sport
                    f = asyncio.ensure_future(  self.sport_ws_run(acc = acc_ )   )    
                    #asyncio.run_coroutine_threadsafe(  self.sport_ws_run(acc = acc ) , ws_loop   )

            
      
           
        
        #await asyncio.gather(*tasks)

    async def api_progress(self , acc , api_task   ):

        if self.before_api == 'sport': # 體育api
            asyncio.ensure_future(     self.run_sport_api( acc = acc  , api_list = api_task['sport'] , delay =  self.before_delay[0]    ) ) 

            #asyncio.run_coroutine_threadsafe( self.run_sport_api( acc = acc  , api_list = api_task['sport'] , delay =  self.before_delay[0] , ) , thread_loop    )

        elif self.before_api == 'bet': # 單純投注
            #asyncio.run_coroutine_threadsafe( self.run_sport_api( acc = acc  , api_list = ['tournament_info', 'match_details', 'game_bet']  , delay =  self.before_delay[0] ) , thread_loop     )
            asyncio.ensure_future(     self.run_sport_api( acc = acc  , api_list =  ['tournament_info', 'match_details', 'game_bet'] , delay =  self.before_delay[0]    ) ) 


        elif self.before_api == 'apply':
            await self.rain_apply(  acc = acc , promotionId  = '1836' , promotionType = '4' , retry_count= 1   )
        
        elif self.before_api == 'platform':
            asyncio.ensure_future(     self.run_platform_api( acc = acc  , api_list = api_task['platform'] , delay =  self.before_delay[0]    ) ) 
            
            #asyncio.run_coroutine_threadsafe( self.run_platform_api( acc = acc  , api_list =   api_task['platform'] , delay =  self.before_delay[0] )  , thread_loop     )

        elif self.before_api == 'mix':
            #asyncio.run_coroutine_threadsafe( self.run_mix_api( acc = acc  , api_task =  api_task , delay =  self.before_delay[0] )  , thread_loop     )
            asyncio.ensure_future(     self.run_mix_api( acc = acc  , api_list = api_task , delay =  self.before_delay[0]    ) ) 
        
        
        else: # all
            #await(  self.run_all_api(acc = acc  , api_list =  api_task['platform']      , api_type = 'platform'      )   )# 平台 api
            #asyncio.run_coroutine_threadsafe( self.run_platform_api( acc = acc  , api_list = api_task['platform'] , delay =  self.before_delay[0]  ,)  , thread_loop     )
            asyncio.ensure_future(     self.run_platform_api( acc = acc  , api_list = api_task['platform'] , delay =  self.before_delay[0]    ) ) 


            #await(  self.run_all_api(acc = acc  , api_list = api_task['sport'] , api_type = 'sport'     )   )# 體育 api
            #asyncio.run_coroutine_threadsafe( self.run_sport_api( acc = acc  , api_list = api_task['sport'] , delay =  self.before_delay[0] , ) , thread_loop2     )
            asyncio.ensure_future(     self.run_sport_api( acc = acc  , api_list = api_task['sport'] , delay =  self.before_delay[0]    ) ) 


        
            #await(  self.run_all_api(acc = acc  , api_list = ['wallets_list10' , 'couponList4' , 'couponSummary20'] , api_type = 'platform'     )   ) # 增加api權重
            #asyncio.run_coroutine_threadsafe( self.run_platform_api( acc = acc  , api_list =  ['wallets_list10' , 'couponList4' , 'couponSummary20']  , delay =  self.before_delay[0] )    , thread_loop3     )
    




def start_loop(thread_loop_):

    asyncio.set_event_loop(thread_loop_)  

    thread_loop_.run_forever()  


def main_run():
    async_stress = Async_Stress()
    
    
    #all_api = asyncio.new_event_loop()
    #threading.Thread( target=start_loop , args=( all_api , )    ).start()

    '''
    if async_stress.before_api == 'all':
        thread_loop = asyncio.new_event_loop()
        threading.Thread( target=start_loop , args=( thread_loop , )    ).start()
        log.info('thread_loop start')

        
        thread_loop2 = asyncio.new_event_loop()
        threading.Thread( target=start_loop , args=( thread_loop2 , )    ).start()

        thread_loop3 = asyncio.new_event_loop()
        threading.Thread( target=start_loop , args=( thread_loop3 , )    ).start()

        

    else:
        thread_loop = asyncio.new_event_loop()
        threading.Thread( target=start_loop , args=( thread_loop , )    ).start()


    ws_loop = asyncio.new_event_loop()
    threading.Thread( target=start_loop , args=( ws_loop , )    ).start()

    #apply_loop = asyncio.new_event_loop()
    #threading.Thread( target=start_loop , args=( apply_loop , )    ).start()
    
    '''



    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)

    else: # linux 不支援   ProactorEventLoop 
          
        selector = selectors.PollSelector()
        loop = asyncio.SelectorEventLoop(selector)
        asyncio.set_event_loop(loop)

  
    loop.run_until_complete(   async_stress.run(  )    )
    
    loop.run_forever()  


 

if __name__ == '__main__':
    
    main_run()
    

    
