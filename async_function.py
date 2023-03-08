import aiohttp    
from Logger import create_logger
from  datetime import datetime , timedelta
from random import choice
from string import ascii_letters , digits
from asyncio import sleep , TimeoutError
from csv import DictWriter



log  = create_logger()

#tw = pytz.timezone('Asia/Taipei')


TIMEOUT = 30

class Sport_Api:
    __slots__ = ('env',  'device' , 'apptype' , 'csv_name' , 'sport_sid_mapping' , 'iid_list' , 'assign_market' , 'bet_stop_flag' , 'orderno' , 'sport_url' 
    , 'sport_before_api_mapping' ,  'bet_sport_iid' , 'bet_sport_sid' , 'bet_inplay' , 'random_sid' , 'iid_string'  , 'assig_iid' , 'match_iid' ,  'tid' , 'score', 'k',
        'odds')
    def __init__(self  , env , csv_name  , apptype , device , bet_sport_iid ,bet_sport_sid , bet_inplay  ):
        self.env = env
        self.device = device
        self.apptype = apptype
        self.csv_name = csv_name
        

        
        self.sport_sid_mapping = {'football' : 1 , 'basketball': 2  , 'tennis': 3   ,'baseball': 4} 
        self.iid_list = [] # tournament_info 會做延展 ,如果沒抓到 , 會影響後面api運行
        self.assign_market , self.bet_stop_flag , self.orderno  = '' , '' , ''
        self.sport_url = f'{self.env["sport_api_URL"]}'
        # range 0 / 1/ 2 ,用來 區分 before_delay 的index 直 . ex: before_delay : [10 , 20 , 30] . range 0 就是 delay 10秒 
        # 體育相關 取得資訊  index_menu -> tournament_info -> match_details -> game_bet
        self.sport_before_api_mapping = {
            'index_menu': { 'req_method': 'GET' , 'api_path': 'business/sport/index/menu', 'payload': {} ,'range': 2 } ,
            'tournament_info': { 'req_method': 'GET' , 'api_path': 'business/sport/tournament/info?sid=&sort=tournament&inplay=', 'payload': {} ,'range': 0  } ,
            'match_info': { 'req_method': 'POST' , 'api_path': 'business/popular/match/info', 'payload': {} ,'range': 0 } ,
            'match_simple': { 'req_method': 'GET' , 'api_path': 'business/sport/match/simple?sid=&iidList=&inplay=', 'payload': {} ,'range': 5 } ,
            'match_details': { 'req_method': 'GET' , 'api_path': {'true':  'business/sport/inplay/match?iid=&sid=' , 'false': 'business/sport/prematch/match?iid=&sid='} ,     
                'payload': {} ,'range': 0 } , # match_details 的range不能小於 game_bet ,因為需取得相關資訊 
            'cart': { 'req_method': 'POST' , 'api_path': 'business/cart', 'payload': {} ,'range': 3  } ,
            'game_bet': { 'req_method': 'POST' , 'api_path': 'game/bet', 'payload': {} ,'range': 0  } ,
            'bet_status': { 'req_method': 'POST' , 'api_path': 'game/bet/status', 'payload': {} ,'range': 0  } ,
            'index_menu2': { 'req_method': 'GET' , 'api_path': 'business/sport/index/menu', 'payload': {} ,'range': 2 } ,
            'cart2': { 'req_method': 'POST' , 'api_path': 'business/cart', 'payload': {} ,'range': 3  } ,
            'match_simple2': { 'req_method': 'GET' , 'api_path': 'business/sport/match/simple?sid=&iidList=&inplay=', 'payload': {} ,'range': 5 } ,
            'popular_matches' : { 'req_method': 'GET' , 'api_path': 'business/popular/matches', 'payload': {} ,'range': 0  } ,
            'index_matches' : { 'req_method': 'GET' , 'api_path': 'business/sport/index/matches', 'payload': {} ,'range': 0  } ,
            'favorites' : { 'req_method': 'GET' , 'api_path': 'business/matches/app/favorites', 'payload': {} ,'range': 0  } ,  
            'match_simple3': { 'req_method': 'GET' , 'api_path': 'business/sport/match/simple?sid=&iidList=&inplay=', 'payload': {} ,'range': 5 } ,          
            'cashout_marketSetting': { 'req_method': 'GET' , 'api_path': 'game/cashout/marketSetting', 'payload': {} ,'range': 2 } ,
            'cart3': { 'req_method': 'POST' , 'api_path': 'business/cart', 'payload': {} ,'range': 3  } ,
            'limit-option_matches1': { 'req_method': 'GET' , 'api_path': 'business/bets/limit-option/matches', 'payload': {} ,'range': 3  } ,
            'cashout_setting': { 'req_method': 'GET' , 'api_path': 'game/cashout/setting', 'payload': {} ,'range': 1 } , 
            'special_matches': { 'req_method': 'GET' , 'api_path': 'business/sport/special/matches', 'payload': {} ,'range': 1 } ,
            'match_simple4': { 'req_method': 'GET' , 'api_path': 'business/sport/match/simple?sid=&iidList=&inplay=', 'payload': {} ,'range': 5 } ,
            'bulletin': { 'req_method': 'GET' , 'api_path': 'business/match/bulletin', 'payload': {} ,'range': 1  } , 
            'limit-option_matches2': { 'req_method': 'GET' , 'api_path': 'business/bets/limit-option/matches', 'payload': {} ,'range': 3  } ,
            'match_simple5': { 'req_method': 'GET' , 'api_path': 'business/sport/match/simple?sid=&iidList=&inplay=', 'payload': {} ,'range': 5 } ,
            'limit-option_matches3': { 'req_method': 'GET' , 'api_path': 'business/bets/limit-option/matches', 'payload': {} ,'range': 3  } ,
            'chat_history': { 'req_method': 'GET' , 'api_path': 'chat/historymessage?index=10&sid=&iid=', 'payload': {} ,'range': 1  } ,

            

        
        
        }

        self.bet_sport_iid = bet_sport_iid
        self.bet_sport_sid = bet_sport_sid
        self.bet_inplay = bet_inplay  # true / false  滾球與否
    
    def _write_csv(self , acc , start_time  , end_time , status_code , response_sec , response , action_url):
        
        
        if 'game/entry' in action_url:
            _action_url = '/platform/'+action_url
        else:
           _action_url = '/product/'+action_url 
        write_content = {
                    "user":acc,
                    "action": _action_url  ,
                    "start_time": start_time,
                    "end_time":end_time,
                    "status_code":status_code,
                    "diff": response_sec,
                    "response":response
                }

        with open(self.csv_name+'.csv', 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['user', 'action', 'start_time', 'end_time', 'status_code', 'diff', 'response']

            writer = DictWriter(csvfile, fieldnames=fieldnames)
            if csvfile.tell() == 0:
                writer.writeheader()
        
            writer.writerow(write_content)
            csvfile.close() 



    async def before_api(self , acc    , api_list , new_init_data , api_delay , stoken , num  , loop='' , session=''   ):

        sport_headers = {
        'Content-Type': 'application/json',
        "referer": self.env["sport_URL"],
        "device": self.device,
        # "devicemode": devicemode,
        "time-zone": "GMT+8",
        "apptype": self.apptype,
        "currency": "CNY",
        }
        sport_headers['authorization'] =  "Bearer "+ stoken


        try:
       
            for api in api_list:


                if api == '':
                    continue
                
                #log.info('api: %s , delay: %s'%(api , api_delay)  )

                if api  == 'match_info': # 需取得 payloda data
                    if not self.iid_list:
                        return ''
                    payload = self.iid_list # tournament_info response 轉換取得
                    action_url = self.sport_before_api_mapping[api]['api_path']

                elif api == 'period-match-score': # 賽事筆分
                    payload = self.sport_before_api_mapping[api]['payload']
                    action_url =  self.sport_before_api_mapping['period-match-score']['api_path'].replace("sid=", 'sid=%s'%self.random_sid  ).replace('iid=', 'iid=%s'%self.assig_iid)



                elif 'match_simple' in api :
                    payload = self.sport_before_api_mapping[api]['payload']
                    action_url =  self.sport_before_api_mapping['match_simple']['api_path'].replace("sid=", 'sid=%s'%self.random_sid  ).replace('inplay=', 'inplay=%s'%self.bet_inplay).replace('iidList=', 'iidList=%s'%self.iid_string)

                elif api == 'match_details':# 取得賠率相關
                    payload = self.sport_before_api_mapping[api]['payload']
                    self.match_iid = self.assig_iid
                    action_url =  self.sport_before_api_mapping['match_details']['api_path'][self.bet_inplay].replace("sid=", 'sid=%s'%self.random_sid  ).replace('iid=', 'iid=%s'%self.assig_iid)
                
                elif api == 'bet_status':
                    action_url = self.sport_before_api_mapping[api]['api_path']
                    if self.orderno == '':
                        continue
                    else:
                        payload = [self.orderno]

                elif api == 'chat_history':
                    payload = self.sport_before_api_mapping[api]['payload']
                    action_url =  self.sport_before_api_mapping['chat_history']['api_path'].replace("sid=", 'sid=%s'%self.random_sid  ).replace('iid=', 'iid=%s'%self.assig_iid)


                elif api == 'tournament_info':
                    try:
                        payload = self.sport_before_api_mapping[api]['payload']
                        if self.bet_sport_sid == '0': #不指定

               
                            self.random_sid = 1
                            action_url =  self.sport_before_api_mapping['tournament_info']['api_path'].replace("sid=", 'sid=%s'%self.random_sid  ).replace('inplay=', 'inplay=%s'%self.bet_inplay)

                        else: # 指定
                            self.random_sid = self.bet_sport_sid

                            action_url =  self.sport_before_api_mapping['tournament_info']['api_path'].replace("sid=", 'sid=%s'%self.bet_sport_sid  ).replace('inplay=', 'inplay=%s'%self.bet_inplay )

                    except Exception as e:
                        log.error('tournament_info error : %s'%e)
                        return ''


                elif api  == 'game_bet'  or   'cart' in api:
                    
                    if self.assign_market == '':

                        return ''
                    

                    action_url = self.sport_before_api_mapping[api]['api_path']
                    
                    if 'cart' in api :
                    
                        payload = {"bets":[{"sid": self.random_sid   ,"iid":self.assig_iid ,"inplay":self.bet_inplay,"outright":False,"market":self.assign_market}  ]  }                   
                    
                    
                    else:
                        random_string = "".join(choice(ascii_letters + digits) for i in range(32)   ).lower() # 組出 英文 / 數字 32長度 給  transid 使用 (single)
                        #log.info('acc: %s random_string: %s , stoken: %s '%( acc , random_string , stoken  ))

                        #log.info('k: %s'%self.k)
                        # 這邊都是 打away .所以 k 遇到- 轉正 , + 轉 -
                        try:
                            if self.k == '': 
                                pass
                            elif '-' in self.k: # - 
                                self.k = self.k.replace('-' , '+')
                            else: # + 
                                
                                self.k = self.k.replace('+' , '-')
                        except:
                            self.k = ''

                        
                        
                        
                        payload = {"marketType":"EU","singles":[{"idx":0,"id": f"{self.random_sid}|{self.assig_iid}|{self.assign_market}|a|0" ,"ante":30,"transId": random_string }],
                        "outrights":[],"parlays":[],
                        "tickets":[{"sid": self.random_sid ,"tid":self.tid ,"iid":self.assig_iid ,"market": self.assign_market ,"beton":"a","odds": self.odds ,"k": '%s'%self.k   ,
                            "inp": self.bet_inplay,"outright":False,"score": self.score ,"orderPhase":1, "v":"a"}]
                        }
       
                    

                
                else: # data / url 不用做任何邏輯  ,　直接吃　預設給的　

                    payload = self.sport_before_api_mapping[api]['payload']
                    action_url = self.sport_before_api_mapping[api]['api_path']
                
                url =  '%s/%s'%(self.sport_url , action_url )
                req_method = self.sport_before_api_mapping[api]['req_method']

                

                r_text , status_code = '' , ''
                try:
                    start_time = datetime.now()
                    if req_method == 'POST':


                        async with session.post(url, timeout=TIMEOUT , json=payload ,  headers= sport_headers ) as resp:
                            try:
                                r_text = await resp.text()
                                response = await resp.json()
                                status_code =  resp.status
                                code = response['code']
                                if str(code) == '0' :
                                    r_text = 'msg: %s , code: %s'%( response['msg'] , code  )
                                

                            except Exception as ex:
                                log.error('api: %s , fail . response : %s  ,status: %s '%(api , r_text , status_code )  )

                        
                    else:

        
                        async with session.get(url, timeout=TIMEOUT , params=payload ,  headers= sport_headers ) as resp:
                            try:
                                #r_text = await resp.text()
                                r_text = await resp.text()
                                response = await resp.json()
                                status_code =  resp.status
                                code = response['code']
                                if str(code) == '0' :
                                    r_text = 'msg: %s , code: %s'%( response['msg'] , code  )
                                

                            except Exception as ex:
                                log.error('api: %s , fail . response : %s  ,status: %s '%(api , r_text , status_code )  )

    
                            
                    end_time = datetime.now()
                    response_sec = ( end_time -  start_time ).total_seconds()
                    
                    if response_sec>=0:
                                log.info('num : %s , acc: %s , api: %s , resopnse: %s '%(num , acc ,  api , response_sec ) )     
                    self._write_csv(  acc , start_time   , end_time  , status_code , response_sec , r_text , action_url   )

                        

                except aiohttp.client_exceptions.ClientConnectorError as e: # network error 
                    log.error('api: %s ClientConnectorError'%api)
                    return False
                    
                except TimeoutError:
                    #log.error('api: %s  TimeoutError'%api )
                    return False

                except aiohttp.http.HttpProcessingError as e:
                    log.error('api: %s HttpProcessingError'%api)
                    return False
                except aiohttp.client_exceptions.ServerDisconnectedError as e:
                    log.error('api: %s ServerDisconnectedError'%api)   
                    return False
                
                except Exception as e: # 其他error
                    if r_text == '':
                        r_text = 'api: %s error: %s'%(api ,  e)
                    #print(response_msg)
                    self._write_csv(  acc , start_time   , '' , status_code , '' , r_text , action_url   )
                    return False
    
                if api =='game_bet':
                    self.orderno = response['data']['submitted']['singles'][0]['orderno']

                await sleep(int(api_delay  )   )
                
                if new_init_data != 'true': # 帶true 初始 才抓取相關 體育投注  資訊
                    continue


                if api == 'tournament_info':

                    self.iid_string = ""# 這邊要延展 iid  , 會給 match/simple iidList 使用
                    count = 0
                    stop_flag = ''
                
                    if len( response['data']['tournaments']) == 0:
                        log.info('tournaments data為空, 無法投注')
                        self.bet_stop_flag = 'true'
                        return ''
                    for tournaments_dict in response['data']['tournaments']:
                        
                        for match_dict in tournaments_dict['matches']:
                            new_dict = {}
                            new_dict['iid'] = match_dict['iid']

                            self.iid_string +=  '%s,'%match_dict['iid']
                            new_dict['sid'] = match_dict['sid']
                            
                            new_dict['inplay'] = match_dict['inplay']
                            self.iid_list.append(new_dict)
                            count += 1
                            if count > 5:
                                stop_flag = 'true'
                                break
                        if stop_flag == 'true':
                            break
                    
                    if self.bet_sport_sid != '0': # 不等於0 .就是指定
                        self.assig_iid = self.bet_sport_iid
                        self.iid_string = self.bet_sport_iid
                    else: # 等於0 自己找
                        self.assig_iid = self.iid_list[0]['iid'] # 抓出一個 iid 給 後面 抓 賠率  match_details 和 投注 game_bet 使用
                    
                    #log.info('iid_list: %s'%self.iid_list)
                
                elif api == 'index_menu':
                    '''
                    self.index_menu_dict = {}
                    
                    inplay_response = response['data']['ipc'] # 滾球
                    del inplay_response['totalCount']
                    self.index_menu_dict['true'] = inplay_response
                    
                    today_response = response['data']['tc']# 今日
                    del today_response['filter']
                    del today_response['totalCount']
                    
                    self.index_menu_dict['false'] = today_response
                    '''
                    pass


                elif api == 'match_details':
                    
                    
                    #bet 先不用 ,　先註解 data 資料
                    self.tid = response['data']['data']['tid']
                    market_dict = response['data']['data']['market'] # 存放個玩法的 賠率 
            
                    
                    self.score = ''
                    if self.bet_inplay == 'true':# 滾球 才有
                        self.score = response['data']['data']['detail']['score']
                    
                    market_option = ['1x2' , 'ah']
                    
                    for market in market_option:
                        if market in list(market_dict.keys()):
                            self.assign_market = market
                            odds_data = market_dict[self.assign_market]
                            if isinstance(odds_data ,  list ):
                                try:
                                    self.k = market_dict[self.assign_market][0]['k']
                                except:
                                    self.k = ''
                                self.odds =  market_dict[self.assign_market][0]['a']
                            else:# dict
                                try:
                                    self.k = market_dict[self.assign_market]['k']
                                except:
                                    self.k = ''
                                self.odds =  market_dict[self.assign_market]['a']
                        
                            break
                    
                    if self.assign_market == '':
                        log.info('self.assign_market 為空')

            return True
        
        except Exception as e:
            log.error('api: %s error: %s'%(api , e) )
   
            return False






class Platform_Api:
    __slots__ = ('env',  'device' , 'apptype' , 'csv_name' , 'platform_url' , 'before_api_mapping'   )
    def __init__(self , env   , csv_name   , device , apptype   ):
        self.env = env

        self.csv_name = csv_name
        self.device = device
        self.apptype = apptype

        
        
        self.platform_url = f'{self.env["platform_api_URL"]}'
        self.before_api_mapping = { 
            'extension': { 'req_method': 'PUT' , 'api_path':  'user/token/extension', 'payload': {} ,'range': 2 },
            'wallets_list': { 'req_method': 'GET' , 'api_path': 'payment/wallets/list', 'payload': {} ,'range': 5 } ,
            'check_balance': { 'req_method': 'PUT' , 'api_path': 'thirdparty/transfer/check-balance', 'payload': {} ,'range': 0  } ,
            'userinfo': { 'req_method': 'GET' , 'api_path': 'user/userinfo', 'payload': {} ,'range': 0 } ,
            
            'orders_summary': { 'req_method': 'GET' , 'api_path':  'thirdparty-report/user/orders/summary?startDate=x%2000%3A00%3A00&endDate=x%2023%3A59%3A59&betStatus=2&onlySport=false', 'payload': {} ,'range': 2 },
            'orders_currency_sum': { 'req_method': 'GET' , 'api_path':  'thirdparty-report/user/orders/currencySummary?startDate=x%2000%3A00%3A00&endDate=x%2023%3A59%3A59&unsettled=true&providers=1&dataType=0', 'payload': {} ,'range': 2 },
            'orders_sport': { 'req_method': 'GET' , 'api_path':  'thirdparty-report/user/orders/sport?startDate=x%2000%3A00%3A00&endDate=x%2023%3A59%3A59&betStatus=0&dataType=0&timeConditionType=LASTUPDATETIME', 'payload': {} ,'range': 2 },
        
            'wallets_list2': { 'req_method': 'GET' , 'api_path': 'payment/wallets/list', 'payload': {} ,'range': 5 } ,
            'promotionMasters': { 'req_method': 'GET' , 'api_path':  'promotion/promotionMasters?appType=8&currency=CNY', 'payload': {} ,'range': 0 },
            'couponList7': { 'req_method': 'GET' , 'api_path':  'payment/coupon/list', 'payload': {} ,'range': 1 },
            'availableBalance': { 'req_method': 'GET' , 'api_path':  'payment/wallets/availableBalance', 'payload': {} ,'range': 0 },
            'unreadCount': { 'req_method': 'GET' , 'api_path': 'user/message/unreadCount', 'payload': {} ,'range': 1 } ,
            'couponList12': { 'req_method': 'GET' , 'api_path':  'payment/coupon/list', 'payload': {} ,'range': 1 },
            'wallets_list3': { 'req_method': 'GET' , 'api_path': 'payment/wallets/list', 'payload': {} ,'range': 5 } ,
            'promotion_triggering': { 'req_method': 'GET' , 'api_path': 'promotion/promotion/br/triggering', 'payload': {} ,'range': 1 } ,
            'currency_mapping': { 'req_method': 'GET' , 'api_path':  'thirdparty/game/currency/mapping', 'payload': {} ,'range': 1 },
            'couponList11': { 'req_method': 'GET' , 'api_path':  'payment/coupon/list', 'payload': {} ,'range': 1 },
            'couponSummary': { 'req_method': 'GET' , 'api_path':  'payment/coupon/summary?needList=true', 'payload': {} ,'range': 5 },
            'couponList': { 'req_method': 'GET' , 'api_path':  'payment/coupon/list', 'payload': {} ,'range': 1 },
            'guanggaos': { 'req_method': 'GET' , 'api_path':  'user/guanggaos?device=2&currency=CNY', 'payload': {} ,'range': 1 },
            'allBanks': { 'req_method': 'GET' , 'api_path':  'payment/allBanks?currency=CNY' , 'payload': {} ,'range': 1 },
            'couponSummary2': { 'req_method': 'GET' , 'api_path':  'payment/coupon/summary?needList=true', 'payload': {} ,'range': 5 },
            'couponList5': { 'req_method': 'GET' , 'api_path':  'payment/coupon/list', 'payload': {} ,'range': 1 },
            'message_list': { 'req_method': 'GET' , 'api_path':  'user/message/list', 'payload': {'type': 0 ,"cursor": ""  } ,'range': 1 },
            'couponList10': { 'req_method': 'GET' , 'api_path':  'payment/coupon/list', 'payload': {} ,'range': 1 },
            'wallets_list4': { 'req_method': 'GET' , 'api_path': 'payment/wallets/list', 'payload': {} ,'range': 5 } ,
            'couponSummary3': { 'req_method': 'GET' , 'api_path':  'payment/coupon/summary?needList=true', 'payload': {} ,'range': 5 },
            'couponList6': { 'req_method': 'GET' , 'api_path':  'payment/coupon/list', 'payload': {} ,'range': 1 },

            
            
            'sysmaintenances': { 'req_method': 'GET' , 'api_path': 'sysmaintenance/sysmaintenances', 'payload': {} ,'range': 2 } ,
            'couponSummary4': { 'req_method': 'GET' , 'api_path':  'payment/coupon/summary?needList=true', 'payload': {} ,'range': 5 },
            'couponList20': { 'req_method': 'GET' , 'api_path':  'payment/coupon/list', 'payload': {} ,'range': 1 },
            'wallets_list5': { 'req_method': 'GET' , 'api_path': 'payment/wallets/list', 'payload': {} ,'range': 5 } ,
            
            'couponList8': { 'req_method': 'GET' , 'api_path':  'payment/coupon/list', 'payload': {} ,'range': 1 },
            'couponSummary5': { 'req_method': 'GET' , 'api_path':  'payment/coupon/summary?needList=true', 'payload': {} ,'range': 5 },
            'couponList19': { 'req_method': 'GET' , 'api_path':  'payment/coupon/list', 'payload': {} ,'range': 1 },
            'sysmaintenance_health': { 'req_method': 'GET' , 'api_path': 'sysmaintenance/health', 'payload': {} ,'range': 2 } ,
            'message_settings': { 'req_method': 'GET' , 'api_path':  'user/message/settings', 'payload': {} ,'range': 2 },
            'couponSummary6': { 'req_method': 'GET' , 'api_path':  'payment/coupon/summary?needList=true', 'payload': {} ,'range': 5 },
            'couponList2': { 'req_method': 'GET' , 'api_path':  'payment/coupon/list', 'payload': {} ,'range': 1 },
            'couponSummary7': { 'req_method': 'GET' , 'api_path':  'payment/coupon/summary?needList=true', 'payload': {} ,'range': 5 },
            'couponList18': { 'req_method': 'GET' , 'api_path':  'payment/coupon/list', 'payload': {} ,'range': 1 },
            'couponSummary8': { 'req_method': 'GET' , 'api_path':  'payment/coupon/summary?needList=true', 'payload': {} ,'range': 5 },
            'couponList3': { 'req_method': 'GET' , 'api_path':  'payment/coupon/list', 'payload': {} ,'range': 1 },
            'couponSummary9': { 'req_method': 'GET' , 'api_path':  'payment/coupon/summary?needList=true', 'payload': {} ,'range': 5 },
            'couponList17': { 'req_method': 'GET' , 'api_path':  'payment/coupon/list', 'payload': {} ,'range': 1 },
            'couponSummary10': { 'req_method': 'GET' , 'api_path':  'payment/coupon/summary?needList=true', 'payload': {} ,'range': 5 },
            'couponList9': { 'req_method': 'GET' , 'api_path':  'payment/coupon/list', 'payload': {} ,'range': 1 },
            'couponSummary11': { 'req_method': 'GET' , 'api_path':  'payment/coupon/summary?needList=true', 'payload': {} ,'range': 5 },
            'couponList4': { 'req_method': 'GET' , 'api_path':  'payment/coupon/list', 'payload': {} ,'range': 1 },
            'couponSummary12': { 'req_method': 'GET' , 'api_path':  'payment/coupon/summary?needList=true', 'payload': {} ,'range': 5 },
            'wallets_list6': { 'req_method': 'GET' , 'api_path': 'payment/wallets/list', 'payload': {} ,'range': 5 } ,
            'couponSummary13': { 'req_method': 'GET' , 'api_path':  'payment/coupon/summary?needList=true', 'payload': {} ,'range': 5 },
            'wallets_list7': { 'req_method': 'GET' , 'api_path': 'payment/wallets/list', 'payload': {} ,'range': 5 } ,
            'couponList13': { 'req_method': 'GET' , 'api_path':  'payment/coupon/list', 'payload': {} ,'range': 1 },
            'couponSummary14': { 'req_method': 'GET' , 'api_path':  'payment/coupon/summary?needList=true', 'payload': {} ,'range': 5 },
            'wallets_list8': { 'req_method': 'GET' , 'api_path': 'payment/wallets/list', 'payload': {} ,'range': 5 } ,
            'couponList15': { 'req_method': 'GET' , 'api_path':  'payment/coupon/list', 'payload': {} ,'range': 1 },
            'couponSummary15': { 'req_method': 'GET' , 'api_path':  'payment/coupon/summary?needList=true', 'payload': {} ,'range': 5 },
            'couponSummary16': { 'req_method': 'GET' , 'api_path':  'payment/coupon/summary?needList=true', 'payload': {} ,'range': 5 },
            'wallets_list9': { 'req_method': 'GET' , 'api_path': 'payment/wallets/list', 'payload': {} ,'range': 5 } ,
            'couponSummary17': { 'req_method': 'GET' , 'api_path':  'payment/coupon/summary?needList=true', 'payload': {} ,'range': 5 },
            'wallets_list10': { 'req_method': 'GET' , 'api_path': 'payment/wallets/list', 'payload': {} ,'range': 5 } ,
            'couponSummary18': { 'req_method': 'GET' , 'api_path':  'payment/coupon/summary?needList=true', 'payload': {} ,'range': 5 },
            'couponList14': { 'req_method': 'GET' , 'api_path':  'payment/coupon/list', 'payload': {} ,'range': 1 },
            'couponSummary19': { 'req_method': 'GET' , 'api_path':  'payment/coupon/summary?needList=true', 'payload': {} ,'range': 5 },
            'couponList16': { 'req_method': 'GET' , 'api_path':  'payment/coupon/list', 'payload': {} ,'range': 1 },
            'couponSummary20': { 'req_method': 'GET' , 'api_path':  'payment/coupon/summary?needList=true', 'payload': {} ,'range': 5 },
            



        }


    async def before_api(self , acc , ptoken ,  api , api_delay , num , loop='' , session ='' ) :

        
        platform_headers = {
        'Content-Type': 'application/json',
        "referer": self.env["platform_URL"],
        "device": self.device,
        # "devicemode": devicemode,
        "time-zone": "GMT+8",
        "apptype": self.apptype,
        # "cks": cks,
        "currency": "CNY",
        "accept-language" : "zh-hk" , 



        }

        platform_headers['authorization'] =  "Bearer "+ ptoken
        
        #for api in api_list:
            
    
        #log.info('api: %s , delay: %s'%(api , api_delay)  

        if api  in ['orders_currency_sum'  , 'orders_sport' , 'orders_summary' ]:
            
            start_date = (datetime.now()+ timedelta(days=-7 ) ).strftime('%Y-%m-%d')
            end_date = (datetime.now() +  timedelta(days=-1 ) ).strftime('%Y-%m-%d')
            action_url = self.before_api_mapping[api]['api_path'].replace('startDate=x','startDate=%s'%start_date).replace('endDate=x','endDate=%s'%end_date)

            #log.info('action_url : %s '%action_url )

            payload = self.before_api_mapping[api]['payload']
            req_method = self.before_api_mapping[api]['req_method']
        else:
            action_url = self.before_api_mapping[api]['api_path']
            payload = self.before_api_mapping[api]['payload']
            req_method = self.before_api_mapping[api]['req_method']
            
        url = f'{self.platform_url}/%s'%action_url 
        
            
        

        r_text , status_code = '' , ''
        try:

                
            start_time = datetime.now()
  
            if req_method == 'PUT':

                async with session.put(url, timeout=TIMEOUT , params=payload ,  headers= platform_headers ) as resp:
    
    
                    try:
            
                        r_text = await resp.text()
                        response = await resp.json()
                        status_code = resp.status
                        #log.info('api: %s , reso: %s'%(api ,response )  )
                        code = response['code']
                        if str(code) == '0' :
                            r_text = 'msg: %s , code: %s'%( response['msg'] , code  )
                    except Exception as ex:
                        log.error( 'api: %s  fail , response: %s , status: %s'%(api , r_text  ,  status_code)   )

                    

            elif req_method == 'POST':


                async with session.post(url, timeout=TIMEOUT , params=payload ,  headers= platform_headers ) as resp:

                    try:
                        
                        r_text = await resp.text()
                        response = await resp.json()
                        status_code = resp.status
                        #log.info('api: %s , reso: %s'%(api ,response )  )
                        code = response['code']
                        if str(code) == '0' :
                            r_text = 'msg: %s , code: %s'%( response['msg'] , code  )
                    except Exception as ex:
                        log.error( 'api: %s  fail , response: %s , status: %s'%(api , r_text  ,  status_code)   )
                    

            else:
    

                async with session.get(url, timeout=TIMEOUT , params=payload ,  headers= platform_headers ) as resp:

                    try:
                        
                        r_text = await resp.text()
                        response = await resp.json()
                        status_code = resp.status
                        #log.info('api: %s , reso: %s'%(api ,response )  )
                        code = response['code']
                        if str(code) == '0' :
                            r_text = 'msg: %s , code: %s'%( response['msg'] , code  )
                    except Exception as ex:

                        log.error( 'api: %s  fail , response: %s , status: %s'%(api , r_text  ,  status_code)   )
                    
            end_time = datetime.now()
            response_sec = ( end_time-  start_time ).total_seconds()
            

            if response_sec>=0:
                log.info('acc: %s , api: %s , resopnse: %s '%(acc ,  api , response_sec  ) )

            self._write_csv(  acc , start_time  , end_time , status_code , response_sec , r_text , action_url   )
            await sleep(int(api_delay   )   )

                
                

        
        except aiohttp.client_exceptions.ClientConnectorError as e: # network error 
            log.error('api: %s ClientConnectorError'%api)
            #continue
            return  ''
            
        except TimeoutError:
            #log.error('api: %s  TimeoutError'%api )
            #continue
            return  ''

        except aiohttp.http.HttpProcessingError as e:
            log.error('api: %s HttpProcessingError'%api)
            #continue
            return  ''
        except aiohttp.client_exceptions.ServerDisconnectedError as e:
            log.error('api: %s ServerDisconnectedError'%api)   
            #continue
            return  ''

        
        except Exception as e:
            if r_text == '':
                r_text = 'api: %s error: %s'%(api ,  e)
            #print(response_msg)
            self._write_csv(  acc , start_time  , '' , status_code , '' , r_text , action_url   )
            #continue
            return  ''


    
    
    def _write_csv(self , acc , start_time  , end_time , status_code , response_sec , response , action_url):
        
        write_content = {
                    "user":acc,
                    "action": '/platform/'+action_url ,
                    "start_time": start_time,
                    "end_time":end_time,
                    "status_code":status_code,
                    "diff": response_sec,
                    "response":response
                }

        with open(self.csv_name+'.csv', 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['user', 'action', 'start_time', 'end_time', 'status_code', 'diff', 'response']

            writer = DictWriter(csvfile, fieldnames=fieldnames)
            if csvfile.tell() == 0:
                writer.writeheader()
        
            writer.writerow(write_content)
            csvfile.close() 














