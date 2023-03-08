import configparser , sys , socket , datetime , time ,random
import platform_rain_ws , intergration_PlatformSportChat
from Function import platform_function as platform
from Function import general_function as general
from Logger import create_logger
import pytz

log = create_logger()
try:
    config = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
    config.read('config.ini', encoding="utf-8")


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
                if key_name in ['run', 'totaluser' , 'vend' ]:
                    config_key = 'ws_main_run'
                elif key_name in ['before_api' , 'before_delay' ]:
                    config_key = 'paltform_rain_ws'
                elif key_name in ['chat_sport' , 'chat_iid' , 'chat_delay' , 'chat_event' ]:
                    config_key = 'sport_chart'
                else:
                    log.error('key_name : %s , 不在 config key 裡'%key_name)
                    continue

                config.set( config_key ,key_name , key_value   )

        file = open("config.ini", 'w' , encoding='utf-8')
        config.write(file) 
        file.close()
except Exception as e:
    log.error('config main_ws error: %s'%e)


run_list =  list(map(str.strip, config['ws_main_run']['run'].split(',')))
totaluser = int(config['ws_main_run']['totaluser'] )
vend = config['ws_main_run']['vend']

log.info('WS執行點 -  run_list: %s , totaluser: %s , vend: %s '%( run_list , totaluser , vend  ))

log.info('sys : %s'%sys.platform)

chat_event = config['sport_chart']['chat_event'] # 控制聊天室 要做的事項 ,  all : 寄送訊息 / 投票  ,  msg : 寄送訊息 , vote : 投票

if 'stg' in vend:
    rain_ws_url = "wss://tiger-api.innostg.site/platform"
    sport_ws_url = 'wss://sports-api.innostg.site' 
else:
    rain_ws_url = "wss://tiger-api.innouat.site/platform"
    sport_ws_url = 'wss://sports-api.innouat.site'   

pc_name = socket.gethostname()
if '-' in pc_name:
    prefix = 'qa'+pc_name.split('-')[-1]
else:
    prefix = 'qa'+pc_name

tw = pytz.timezone('Asia/Taipei')

if sys.platform != 'win32': # docker 
    csv_name = 'docker_csv_normal'
    filename = 'docker_txt'
    prefix = prefix[0:6]
else:

    csv_name = prefix+'_csv_'+datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = prefix+'_ws_'+datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    

env = platform.get_env(vend)
pw = "test1234"

user_dict = {}


total_user_list = [i for i in range(totaluser) ]


adminacc = "autoqa01"
adminpw = 'test1234'

adminToken = platform.loginAdmin(env, adminacc, adminpw)  # 後台登入



def main_ws():
    break_flag = ''
    first_rain_start , first_chat_start , first_sport_start = 'true' , 'true' , 'true'
    for num in total_user_list:
        try:
            acc = prefix+"{:03d}".format( num+1 )
        
            isExist = platform.checkAccount(env, acc)

            if not isExist :
                isExist = platform.createAccount(env, acc, pw)

            ptoken, status_code, response_sec, start_time, end_time, response = platform.loginPlatfomuser(env = env,  acc = acc, pw = pw )
            
            write_content = {
                "user":acc,
                "action": "/platform/user/token",
                "start_time": start_time,
                "end_time":end_time,
                "status_code":status_code,
                "diff": response_sec,
                "response":response
            } 
            general.write_csv(csv_name, write_content)
            
            if response == 'Fail': # 登入 失敗 不用做 後面行為
                continue

            platform.change_wallet(env , currency = 'CNY' , ptoken = ptoken)# 切換幣別


            start_time , end_time  , status_code , response_sec , response  , stoken = platform.loginSportuser(env = env,  
                    acc = acc , token = ptoken ) # 拿體育 token)# 產 出 sport token
            write_content = {
                "user":acc,
                "action": "/platform/thirdparty/game/entry" ,
                "start_time": start_time,
                "end_time":end_time,
                "status_code":status_code,
                "diff": response_sec,
                "response":response
            } 
            general.write_csv(csv_name, write_content)

            
            
            #random.shuffle(run_list)
            #run = run_list[0]

            # ws 執行
            for run in run_list:

                # 紅包雨
                if run == 'rain':
                    platform_rain_ws.rain_ws(env = env ,num = num ,  ptoken = ptoken   , acc = acc  , exe_type = 'init'  , csv_name= csv_name , filename= ''  , 
                        ws_url = rain_ws_url , stoken = stoken , first_start=first_rain_start  ) 
                    first_rain_start = 'false'
                
                # 聊天室
                elif run == 'chat':
                    if 'bet' in chat_event:
                        platform.admin_deposit( env = env , adminToken = adminToken , acc = acc , amount= 1000 , deposit_num = prefix )  # 充值發起 / 審核

                    intergration_PlatformSportChat.chat_ws(env = env  ,  num = num ,  ptoken = ptoken   ,run_type = 'init' , acc = acc  ,  sport_ws_url = sport_ws_url , 
                        csv_name = csv_name , stoken = stoken , first_start = first_chat_start )
                    first_chat_start = 'false'
                
                # 體育
                elif run == 'sport': 
                    intergration_PlatformSportChat.sport_ws( env = env  ,  num = num ,   run_type = 'init' , acc = acc  , sport_ws_url = sport_ws_url ,
                        csv_name = csv_name  , filename= filename , first_sport_start = first_sport_start     )
                    first_sport_start = 'false'

                else:
                    log.error('輸入 run 值有誤')
                    break_flag = 'true'
                
                if break_flag =='true':
                    continue
                
                tw = pytz.timezone('Asia/Taipei')
                log.info(f"===== No.{num} acc: {acc} , start {run} : "+datetime.datetime.now().astimezone(tw).strftime('%m/%d %H:%M:%S') + '\n'  )
            #general.writeLog(filename, f"===== No.{num} acc: {acc} , start \n")
            #user_dict[acc] = ptoken

        except Exception as e:
            log.error('acc : %s main error: %s'%(acc , e) )

main_ws()

'''
    
while True:
    
    #for tmp in range(0, len(user_dict)):
    for acc in user_dict.keys():
        try:
            status_code, response_sec, start_time, end_time, response = platform.extension(env, acc , user_dict[acc]  )
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
            print('extension 有誤: %s '%e)

    time.sleep(500)


'''