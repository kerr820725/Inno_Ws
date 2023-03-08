from Function import platform_function
import configparser , sys , socket , threading , time , datetime 
from Function import general_function as general
from functools import reduce

config = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
config.read('config.ini', encoding="utf-8")


totaluser = config['sport_parlay_bet']['totaluser']
vend = config['sport_parlay_bet']['vend']
sport_bet_loop = config['sport_parlay_bet']['sport_bet_loop']
desposit_amount = config['sport_parlay_bet']['desposit_amount'] # 衝直金額
bet_amount = config['sport_parlay_bet']['bet_amount'] # 投注金額 
sport = config['sport_parlay_bet']['sport'] # 指定運動
parlay_type = config['sport_parlay_bet']['parlay_type'] # 指定串關 模式
single = config['sport_parlay_bet']['single'] # true 為 一般 , 其他為 串關
bet_status = config['sport_parlay_bet']['bet_status'] # 是否要打 bet status

'''
inplay_type = config['sport_parlay_bet']['inplay_type'] # 是否串關
if inplay_type == 'true':
    inplay_type = 'inplay'
else:
    inplay_type = 'false'
'''


print('totaluser: %s , vend: %s , sport_bet_loop: %s , single: %s '%(totaluser , vend , sport_bet_loop  , single)   )
print('desposit_amount: %s , bet_amount: %s , sport: %s  , parlay_type: %s , bet_status : %s '%(desposit_amount , bet_amount , sport ,parlay_type , bet_status )   )

adminacc = "autoqa01"
adminpw = "test1234" # 後台
pw = "test1234" # 前台



env = platform_function.get_env(vend)

pc_name = socket.gethostname()

if '-' in pc_name:
    prefix = 'qa'+pc_name.split('-')[-1]
else:
    prefix = 'qa'+pc_name

csv_name = 'sport_parlay_bet'+datetime.datetime.now().strftime("%Y%m%d%H%M%S")


total_user_list = [i for i in range( int( totaluser ) ) ]

#prefix= 'kerr'


def write_csv(acc , action , start_time , end_time , status_code , diff , response   ):
    write_content = {
        "user":acc,
        "action":   action  ,
        "start_time": start_time, 
        "end_time": end_time,
        "status_code": status_code ,
        "diff": diff ,
        "response": response
    } 
    
    general.write_csv(csv_name, write_content)


adminToken = platform_function.loginAdmin(env, adminacc, adminpw)  # 後台登入

#print('adminToken: %s'% adminToken )

user_stoken_dict = {} # key 為 user , value為 sport token
# 先確認 user 相關 , 是否存在 / 充值 / 登入
for i in total_user_list:
    try:
        acc = prefix+"{:03d}".format(i+1)
        isExist = platform_function.checkAccount(env, acc)

        if not isExist : 
            print('%s 需創建帳號'%acc)
            isExist = platform_function.createAccount(env, acc, pw)
        
        ptoken, status_code, response_sec, start_time, end_time, response = platform_function.loginPlatfomuser(env,  acc, pw) # 平台登入
        write_csv(acc = acc , action = '/user/token' , start_time = start_time , end_time = end_time 
             , status_code = status_code , diff = response_sec , response = response  )
              
        platform_function.admin_deposit( env = env , adminToken = adminToken , acc = acc  , amount= desposit_amount , deposit_num = prefix )  # 充值發起 / 審核


        start_time , end_time  , status_code , response_sec , response  , sport_token = platform_function.loginSportuser(env = env,  
            acc = acc , token = ptoken   ) # 拿體育 token
        write_csv(acc = acc , action = '/thirdparty/game/entry' , start_time = start_time , end_time = end_time 
             , status_code = status_code , diff = response_sec , response = response  )

        user_stoken_dict[acc] = sport_token

        print('acc: %s 登入成功'%acc)

    except Exception as e:
        print('error: %s'%e)



sport_parlay = platform_function.Sport_Parlay_Bet(   env = env  , csv_name = csv_name  ) 
staus = sport_parlay.parlay_info(   token = sport_token , sport = sport , acc = acc  , sinlge = single  ) # 抓資訊 抓一次就可



if staus is not False:

    for i in range( int( sport_bet_loop )): 

        for user in user_stoken_dict.keys():
            
            threads_list = []
            
            # bet_status 是 true 會打 bet/status
            t = threading.Thread( target=  sport_parlay.sport_bet , args = ( sport , user_stoken_dict[user] , user , bet_amount ,  parlay_type , single  , bet_status  ) ) 
            threads_list.append(t)
            
            t.start()
            # bet status 先註解
            #if orderno is not False:
                #sport_parlay.sport_bet_status( orderno = orderno ,  token = user_stoken_dict[user]   )

        for i in threads_list:
            i.join()
        
        time.sleep(2)
    
        
    
    print('投注筆數: %s  , 失敗筆數: %s '%(sport_parlay.count , sport_parlay.fail_count )  )
    
    
    time_bet_list = sorted(sport_parlay.cal_response_dict['game_bet'] )
    bet_time_total = round(reduce(lambda x , y: float(x) + float(y), time_bet_list  )  ,4 )# 該game/bet 執行時間總和
    ava_bet = round(  bet_time_total / len(time_bet_list)  , 4  )
    print('game/bet 平均回應: %s , 最快回應: %s , 最慢回應: %s  , 筆數: %s '%( ava_bet , time_bet_list[0] , time_bet_list[-1] ,  len(time_bet_list)  )          )
    
    if bet_status == 'true':
        try:
            time_status_list = sorted(sport_parlay.cal_response_dict['bet_status'] )
            status_time_total = round(reduce(lambda x , y: float(x) + float(y), time_status_list  )  ,4 )# 該bet_status 執行時間總和
            ava_bet = round(  status_time_total / len(time_status_list)  , 4  )
            print('bet/status 平均回應: %s , 最快回應: %s , 最慢回應: %s  , 筆數: %s '%( ava_bet , time_status_list[0] , time_status_list[-1] ,  len(time_status_list)  )          )
        except: # 有可能 bet status 裡 ,是沒有資料 (投注失敗)
            pass 