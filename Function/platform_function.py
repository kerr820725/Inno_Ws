from Function.rsa import *
#from rsa import * 
import requests
import os, json
import datetime
import hashlib , csv
import time , random , string
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, PKCS1_v1_5
from base64 import b64encode, b64decode
from Function import general_function as general
from Logger import create_logger
from collections import defaultdict
import pytz

from Logger import create_logger

log = create_logger()

tw = pytz.timezone('Asia/Taipei')

device = "mobile"
# devicemode = ""
apptype =  "2"

def get_env(s) -> dict:    
    env = {
        "vd004_cloudfront": {
            "Name": "瑞銀2.0",
            "vendor_id":"vd004",
            "platform_URL": "https://68w.me",
            "admin_URL": "https://en-vd004-tiger-admin.innouat.site",
            "agent_URL": "https://en-vd004-tiger-agent.innouat.site",
            "sport_URL": "https://en-vd004-inno-sport.innouat.site",
            "platform_api_URL": "https://cloudfront-sports-api.innouat.site/platform",
            "sport_api_URL": "https://cloudfront-sports-api.innouat.site/product",
            "ws_url":"cloudfront-sports-api.innouat.site/product",
            "lottery_api_url": "https://gaming-lottery-uat.lianfa.co",
            "lottery_api_referer": "https://lottery-uat.lianfa.co",
            "currency": ["CNY","IDR","VND","MYR","ETH","BTC","LTC","USDT_OMNI","USDT_ERC20","USD","HKD"],
            "vend": "UA5",
            "lottery_id": ""
        },
        "vd004_aliyun":{
            "Name": "瑞銀2.0",
            "vendor_id":"vd004",
            "platform_URL": "https://68w.me",
            "admin_URL": "https://en-vd004-tiger-admin.innouat.site",
            "agent_URL": "https://en-vd004-tiger-agent.innouat.site",
            "sport_URL": "https://en-vd004-inno-sport.innouat.site",
            "platform_api_URL": "https://aliyun-sports-api.pokemanfix.com/platform",
            "sport_api_URL": "https://aliyun-sports-api.pokemanfix.com/product",
            "ws_url":"aliyun-sports-api.pokemanfix.com/product",
            "lottery_api_url": "https://gaming-lottery-uat.lianfa.co",
            "lottery_api_referer": "https://lottery-uat.lianfa.co",
            "currency": ["CNY","IDR","VND","MYR","ETH","BTC","LTC","USDT_OMNI","USDT_ERC20","USD","HKD"],
            "vend": "UA5",
            "lottery_id": ""
        },
        "vd004_apeiro":{
            "Name": "瑞銀2.0",
            "vendor_id":"vd004",
            "platform_URL": "https://68w.me",
            "admin_URL": "https://en-vd004-tiger-admin.innouat.site",
            "agent_URL": "https://en-vd004-tiger-agent.innouat.site",
            "sport_URL": "https://en-vd004-inno-sport.innouat.site",
            "platform_api_URL": "https://apeiro-sports-api.pokemanfix.com/platform",
            "sport_api_URL": "https://apeiro-sports-api.pokemanfix.com/product",
            "ws_url":"apeiro-sports-api.pokemanfix.com/product",
            "lottery_api_url": "https://gaming-lottery-uat.lianfa.co",
            "lottery_api_referer": "https://lottery-uat.lianfa.co",
            "currency": ["CNY","IDR","VND","MYR","ETH","BTC","LTC","USDT_OMNI","USDT_ERC20","USD","HKD"],
            "vend": "UA5",
            "lottery_id": ""
        },
        "vd004_tencent":{
            "Name": "瑞銀2.0",
            "vendor_id":"vd004",
            "platform_URL": "https://68w.me",
            "admin_URL": "https://en-vd004-tiger-admin.innouat.site",
            "agent_URL": "https://en-vd004-tiger-agent.innouat.site",
            "sport_URL": "https://en-vd004-inno-sport.innouat.site",
            "platform_api_URL": "https://tencent-sports-api.pokemanfix.com/platform",
            "sport_api_URL": "https://tencent-sports-api.pokemanfix.com/product",
            "ws_url":"tencent-sports-api.pokemanfix.com/product",
            "lottery_api_url": "https://gaming-lottery-uat.lianfa.co",
            "lottery_api_referer": "https://lottery-uat.lianfa.co",
            "currency": ["CNY","IDR","VND","MYR","ETH","BTC","LTC","USDT_OMNI","USDT_ERC20","USD","HKD"],
            "vend": "UA5",
            "lottery_id": ""
        },
        "vd004_tencent_cf":{
            "Name": "瑞銀2.0",
            "vendor_id":"vd004",
            "platform_URL": "https://68w.me",
            "admin_URL": "https://en-vd004-tiger-admin.innouat.site",
            "agent_URL": "https://en-vd004-tiger-agent.innouat.site",
            "sport_URL": "https://en-vd004-inno-sport.innouat.site",
            "platform_api_URL": "https://tencent-cf-sports-api.pokemanfix.com/platform",
            "sport_api_URL": "https://tencent-cf-sports-api.pokemanfix.com/product",
            "ws_url":"tencent-cf-sports-api.pokemanfix.com/product",
            "lottery_api_url": "https://gaming-lottery-uat.lianfa.co",
            "lottery_api_referer": "https://lottery-uat.lianfa.co",
            "currency": ["CNY","IDR","VND","MYR","ETH","BTC","LTC","USDT_OMNI","USDT_ERC20","USD","HKD"],
            "vend": "UA5",
            "lottery_id": ""
        },
        "vd004_apeiro2":{
            "Name": "瑞銀2.0",
            "vendor_id":"vd004",
            "platform_URL": "https://68w.me",
            "admin_URL": "https://en-vd004-tiger-admin.innouat.site",
            "agent_URL": "https://en-vd004-tiger-agent.innouat.site",
            "sport_URL": "https://en-vd004-inno-sport.innouat.site",
            "platform_api_URL": "https://apeiro-sports-api.fumengwangluokeji.com/platform",
            "sport_api_URL": "https://apeiro-sports-api.fumengwangluokeji.com/product",
            "ws_url":"apeiro-sports-api.fumengwangluokeji.com/product",
            "lottery_api_url": "https://gaming-lottery-uat.lianfa.co",
            "lottery_api_referer": "https://lottery-uat.lianfa.co",
            "currency": ["CNY","IDR","VND","MYR","ETH","BTC","LTC","USDT_OMNI","USDT_ERC20","USD","HKD"],
            "vend": "UA5",
            "lottery_id": ""
        },
        "vd004":{
            "Name": "瑞銀2.0",
            "vendor_id":"vd004",
            "platform_URL": "https://68w.me",
            "admin_URL": "https://en-vd004-tiger-admin.innouat.site",
            "agent_URL": "https://en-vd004-tiger-agent.innouat.site",
            "sport_URL": "https://en-vd004-inno-sport.innouat.site",
            "platform_api_URL": "https://tiger-api.innouat.site/platform",
            "sport_api_URL": "https://sports-api.innouat.site/product",
            "ws_url":"sports-api.innouat.site/product",
            "lottery_api_url": "https://gaming-lottery-uat.lianfa.co",
            "lottery_api_referer": "https://lottery-uat.lianfa.co",
            "currency": ["CNY","IDR","VND","MYR","ETH","BTC","LTC","USDT_OMNI","USDT_ERC20","USD","HKD"],
            "vend": "UA5",
            "lottery_id": ""
        },
        "vd004_stg":{
            "Name": "瑞銀2.0_STG",
            "vendor_id":"vd004",
            "platform_URL": "https://en-vd004-tiger-portal.innostg.site",
            "admin_URL": "https://en-vd004-tiger-admin.innostg.site",
            "agent_URL": "https://en-vd004-tiger-agent.innostg.site",
            "sport_URL": "https://en-vd004-inno-sport.innostg.site",
            "platform_api_URL": "https://tiger-api.innostg.site/platform",
            "sport_api_URL": "https://sports-api.innostg.site/product",
            "lottery_api_url": "https://gaming-lottery-stg.lianfa.co",
            "lottery_api_referer": "https://en-vd004-lottery-game-stg.lianfa.co/",
            "currency": ["CNY","IDR","VND","MYR","ETH","BTC","LTC","USDT_ERC20","USD","HKD","THB","JPY","KRW","INR","BCH","DOGE","DASH","ETC"],
            "vend": "ST5",
            "lottery_id": ""
        },
        "vd002_dev":{
            "Name": "古哥2.0_Dev",
            "vendor_id":"vd002",
            "platform_URL": "https://en-vd002-tiger-portal.innodev.site",
            "admin_URL": "https://en-vd002-tiger-admin.innodev.site",
            "agent_URL": "https://en-vd002-tiger-agent.innodev.site",
            "sport_URL": "https://en-vd002-inno-sport.innodev.site",
            "platform_api_URL": "https://tiger-api.innodev.site/platform",
            "sport_api_URL": "https://sports-api.innodev.site/product",
            "lottery_api_url": "https://gaming-lottery-dev.lianfa.co",
            "lottery_api_referer": "https://lottery-dev.lianfa.co",
            "currency": ["CNY","IDR","VND","MYR","ETH","BTC","LTC","USDT_OMNI","USDT_ERC20","USD","HKD"],
            "vend": "DEV",
            "lottery_id": "0"
        },
        "vd001":{
            "Name": "長城",
            "vendor_id":"vd001",
            "platform_URL": "https://en-vd001-tiger-portal.innouat.site",
            "admin_URL": "https://en-vd001-tiger-admin.innouat.site",
            "agent_URL": "https://en-vd001-tiger-agent.innouat.site",
            "sport_URL": "https://en-vd001-inno-sport.innouat.site",
            "platform_api_URL": "https://tiger-api.innouat.site/platform",
            "sport_api_URL": "https://sports-api.innouat.site/product",
            "lottery_api_url": "https://gaming-lottery-uat.lianfa.co",
            "lottery_api_referer": "https://lottery-uat.lianfa.co",
            "currency": ["CNY","IDR","VND"],
            "vend": "UA2",
            "lottery_id": "42"
        },
        "vd001_stg":{
            "Name": "長城_STG",
            "vendor_id":"vd001",
            "platform_URL": "https://en-vd001-tiger-portal.innostg.site",
            "admin_URL": "https://en-vd001-tiger-admin.innostg.site",
            "agent_URL": "https://en-vd001-tiger-agent.innostg.site",
            "sport_URL": "https://en-vd001-inno-sport.innostg.site",
            "platform_api_URL": "https://tiger-api.innostg.site/platform",
            "sport_api_URL": "https://sports-api.innostg.site/product",
            "lottery_api_url": "https://gaming-lottery-stg.lianfa.co",
            "lottery_api_referer": "https://lottery-stg.lianfa.co",
            "currency": ["CNY","IDR","VND"],
            "vend": "ST2",
            "lottery_id": "87"
        },
        "vd002":{
            "platform_URL": "https://93a.me",
            "vendor_id":"vd002",
            "admin_URL": "https://admin.93a.me",
            "agent_URL": "https://en-vd002-tiger-agent.innouat.site",
            "sport_URL": "https://en-vd002-inno-sport.innouat.site",
            "platform_api_URL": "https://tiger-api.innouat.site/platform",
            "sport_api_URL": "https://sports-api.innouat.site/product",
            "lottery_api_url": "https://gaming-lottery-uat.lianfa.co",
            "lottery_api_referer": "https://lottery-uat.lianfa.co",
            "currency": ["CNY","IDR","VND","MYR","ETH","BTC","LTC","USDT_OMNI","USDT_ERC20","USD","HKD"],
            "vend": "UA3",
            "lottery_id": "43"
        },
        "vd002_stg":{
            "Name": "谷歌_STG",
            "vendor_id":"vd002",
            "platform_URL": "https://en-vd002-tiger-portal.innostg.site",
            "admin_URL": "https://en-vd002-tiger-admin.innostg.site",
            "agent_URL": "https://en-vd002-tiger-agent.innostg.site",
            "sport_URL": "https://en-vd002-inno-sport.innostg.site",
            "platform_api_URL": "https://tiger-api.innostg.site/platform",
            "sport_api_URL": "https://sports-api.innostg.site/product",
            "lottery_api_url": "https://gaming-lottery-stg.lianfa.co",
            "lottery_api_referer": "https://lottery-stg.lianfa.co",
            "currency": ["CNY","IDR","VND","MYR","ETH","BTC","LTC","USDT_ERC20","USD","HKD","THB","JPY","KRW","INR","BCH","DOGE","DASH","ETC"],
            "vend": "ST3",
            "lottery_id": "89"
        },
        "vd003":{
            "Name": "新6",
            "vendor_id":"vd003",
            "platform_URL": "https://en-vd003-tiger-portal.innouat.site",
            "admin_URL": "https://en-vd003-tiger-admin.innouat.site",
            "agent_URL": "https://en-vd003-tiger-agent.innouat.site",
            "sport_URL": "https://en-vd003-inno-sport.innouat.site",
            "platform_api_URL": "https://tiger-api.innouat.site/platform",
            "sport_api_URL": "https://sports-api.innouat.site/product",
            "lottery_api_url": "https://gaming-lottery-uat.lianfa.co",
            "lottery_api_referer": "https://lottery-uat.lianfa.co",
            "currency": ["CNY","IDR","VND","MYR","ETH","BTC","LTC","USDT_OMNI","USDT_ERC20","USD","HKD"],
            "vend": "UA4",
            "lottery_id": "44"
        },
        "vd003_stg":{
            "Name": "新6_STG",
            "vendor_id":"vd003",
            "platform_URL": "https://en-vd003-tiger-portal.innostg.site",
            "admin_URL": "https://en-vd003-tiger-admin.innostg.site",
            "agent_URL": "https://en-vd003-tiger-agent.innostg.site",
            "sport_URL": "https://en-vd003-inno-sport.innostg.site",
            "platform_api_URL": "https://tiger-api.innostg.site/platform",
            "sport_api_URL": "https://sports-api.innostg.site/product",
            "lottery_api_url": "https://gaming-lottery-stg.lianfa.co",
            "lottery_api_referer": "https://lottery-stg.lianfa.co",
            "currency": ["CNY","IDR","VND","MYR","ETH","BTC","LTC","USDT_OMNI","USDT_ERC20","USD","HKD","THB","JPY","KRW","INR","BCH","DOGE","DASH","ETC"],
            "vend": "ST4",
            "lottery_id": "90"
        },
    }
    return env.get(s)

def get_cks(vend, account):
    """ 組合CKS \n
    account: 帳號 \n
    vend: 業主\n
    addtime: 增加秒數, 預設0 \n
    """
    ts = str(int(time.time()))#Timestamp 取10碼
    mash = str(ts[:4])+str(vend)  + str(account) + str(ts[4:]) #插入帳號ex “ufo001”  於timestamp前4後6: 1628 ufo001 611208
    h = hashlib.md5(mash.encode('utf-8')).hexdigest()#執行>Md5 hash
    j = str(ts) + str(h[:2]) + str(h[-3:])
    # print(j)
    return j.lower()

def checkAccount(env, acc):
    isExist = False
    url = f'{env["platform_api_URL"]}/user/accounts?account={acc}'
    headers = {
        'Content-Type': 'application/json',
        "referer": env["platform_URL"],
        "device": device ,
        # "devicemode": devicemode,
        "time-zone": "GMT+8",
        "apptype": apptype
    }
    payload = {
        "account": acc
    }

    response = requests.request("GET", url, headers=headers).json()
    #print('checkAccount response: %s'%response)
    if 'isExist' in response['data']:
        isExist = response['data']['isExist']

    return isExist

def createAccount(env, acc, pw):
    url = f'{env["platform_api_URL"]}/user/nonce'
    headers = {
        'Content-Type': 'application/json',
        "referer": env["platform_URL"],
        "device": device,
        # "devicemode": devicemode,
        "time-zone": "GMT+8",
        "apptype": apptype
    }
    payload = {
        "imageWidth": 280, 
        "imageHeight": 155, 
        "jigsawWidth": 52, 
        "jigsawHeight": 52
	}

    response = requests.request("POST", url, headers=headers, json=payload).json()
    clientNonce = response['data']['clientNonce']

    url = f'{env["platform_api_URL"]}/user/accounts'
    payload = {
        "account":acc,
        "password": encrypt(pw).decode("utf-8"),
        "confirmPassword": encrypt(pw).decode("utf-8"),
        "currency": "CNY",
        "locale":"zh_CN",
        "device":device,
        "clientNonce":clientNonce,
        "type":1
    }

    response = requests.request("POST", url, headers=headers, json=payload).json()
    if 'account' in response['data'] and response['data']['account'] == acc:
        return True

    return False
    
def loginAdmin(env, adminacc="autoqa01", adminpw="test1234"):
    payload = {"account": adminacc, "auth": "", "password": encrypt(adminpw).decode("utf-8")}
    headers = {
        'Content-Type': 'application/json',
        "referer": env["admin_URL"],
        "device": device,
        # "devicemode": devicemode,
        "time-zone": "GMT+8",
        "apptype": apptype        
    }
    url = f'{env["platform_api_URL"]}/admin/token'

    try:
        response = requests.request("POST", url, headers=headers, json=payload)
        response_json = response.json()
        
        return response_json['data']['token']
    except Exception as e:
        log.error('後臺帳號: %s登入有誤: %s , response: %s '%(adminacc, e , response.text  )  )
        return ''

def loginPlatfomuser(env, acc="qatool01", pw="test1122") -> str:
    
    url = f'{env["platform_api_URL"]}/user/token'
    cks = get_cks(env['vendor_id'], acc )

    headers = {
        'Content-Type': 'application/json',
        "referer": env["platform_URL"],
        "device": device,
        # "devicemode": devicemode,
        "time-zone": "GMT+8",
        "apptype": apptype,
        "cks": cks
    }
    payload = {
        "account": acc,
        "password": encrypt(pw).decode("utf-8"),
        "clientNonce": None,
        "device": device
    }
    start_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')
    
    status_code = '-1' # 預設值
    response_sec = '-1'
    ptoken = 'none'
    end_time = ''
    
    try:
        r = requests.request("POST", url, headers=headers, json=payload)
        
        end_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')
        status_code = r.status_code
        response_sec = r.elapsed.total_seconds()

        try:
            response = r.json()
            response_msg = 'msg: %s , code: %s'%(response['msg'] ,  response['code'])
            
            if not response.get('data'):
                ptoken = "none"
            else:
                ptoken = response['data']['token']

        except Exception as ex:
            response_msg = 'user/token fail: %s , error: %s'%(r.text , ex) 
            log.error(response_msg  )
            ptoken = 'none'

    
    except Exception as e: # 走到這 是 api 連response都沒有
        response_msg = 'acc: %s user/token error: %s'% (acc  , e) 
        log.error(response_msg )


    return ptoken, status_code, response_sec, start_time, end_time, response_msg

def loginSportuser(env, acc, token ) :
    url = f'{env["platform_api_URL"]}/thirdparty/game/entry'
    cks = get_cks(env['vendor_id'], acc )

    headers = {
        'Content-Type': 'application/json',
        "referer": env["platform_URL"],
        "device": device,
        # "devicemode": devicemode,
        "time-zone": "GMT+8",
        "apptype": apptype,
        "authorization": f'Bearer {token}',
        "cks":cks
    }
    Param = {
        "providerCode": 1,
        "device": device
    }

    start_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')
    r = requests.request("GET", url, headers=headers, params=Param)
    status_code = r.status_code
    response_sec = r.elapsed.total_seconds()
    end_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')

    try:
        response = r.json()
        response_msg = 'msg: %s , code: %s'%(response['msg'] ,  response['code'])

        if not response.get('data'):
            log.info('thirdparty/game/entry response: %s'%response)
            sport_token = response
        else:
            sport_token =  response['data']['token']
    except:
        response_msg = 'FAIL'
        sport_token = 'none'


    return start_time , end_time  , status_code , response_sec , response_msg  , sport_token


def extension(env, acc, token ):
    url = f'{env["platform_api_URL"]}/user/token/extension'
    cks = get_cks(env['vendor_id'], acc )

    headers = {
        'Content-Type': 'application/json',
        "referer": env["platform_URL"],
        "device": device,
        # "devicemode": devicemode,
        "time-zone": "GMT+8",
        "apptype": apptype,
        "cks": cks,
        "authorization": "Bearer "+token
    }
    payload = {        
    }

    start_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')
    
    status_code = '-1' # 預設值
    response_sec = '-1'

    end_time = ''
    try:
        r = requests.request("PUT", url, headers=headers, json=payload)
        try:
            response = r.json()
            response_msg = 'msg: %s , code: %s'%(response['msg'] ,  response['code'])
        except:
            log.error('user/token/extension fail: %s'%r.text)
            response_msg = 'fail'
        status_code = r.status_code
        response_sec = r.elapsed.total_seconds()
        end_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')
    
    except Exception as e: # 走到這 是 api 連response都沒有
        response_msg = 'token/extension error: %s'%e
        log.error(response_msg)

    return status_code, response_sec, start_time, end_time, response_msg


def deposit(env, acc, token, cardId , type_ = ''):
    headers = {
        'Content-Type': 'application/json',
        "referer": env["platform_URL"],
        "device": device,
        # "devicemode": devicemode,
        "time-zone": "GMT+8",
        "apptype": apptype,
        "currency": "CNY",
        "authorization": "Bearer "+token
    }
    data = {"cardId":cardId,
            "transferTime": datetime.datetime.now().astimezone(tw).strftime("%Y-%m-%d %H:%M:%S"),
            "transferType":"2",
            "depositorName":acc,
            "userBankcardNo":"",
            "transferMethod":"",
            "amount":"1000"
            }
    
    url = f'{env["platform_api_URL"]}/payment/deposit'

    start_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')
    r = requests.request("POST", url, headers=headers, json=data)
    
    end_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')
    status_code = r.status_code
    response_sec = r.elapsed.total_seconds()
    response = r.json()
    
    response_msg = 'msg: %s , code: %s'%(response['msg'] ,  response['code'])

    log.info('deposit response_msg: %s'%response_msg)

    try:
        order_no = response['data']['orderNo']
    except:
        order_no = ''
    
    if type_ == '':
        return order_no

    return start_time , end_time  , status_code , response_sec , response_msg 

def approve_deposit(env, adminToken, orderNo):
    payload = {"memo": "",
            "orderNumber": orderNo,
            "status": 0
    }    
    
    headers = {
        'Content-Type': 'application/json',
        "referer": env["admin_URL"],
        "device": device,
        # "devicemode": devicemode,
        "time-zone": "GMT+8",
        "apptype": apptype,
        "currency": "CNY",
        "authorization": "Bearer "+adminToken
    }
    url = f'{env["platform_api_URL"]}/admin/depositRecordStatus'
    response = requests.request("PUT", url, headers=headers, json=payload).json()
    payload.update({"status": 2})
    response = requests.request("PUT", url, headers=headers, json=payload).json()
    # print(response)
    return response

def admin_deposit(env, adminToken, acc , deposit_num = '' , amount = ''): # type 帶 approve 是put 審核 , type其他是 Post 衝直
    
    
    try:
        headers = {
            'Content-Type': 'application/json',
            "referer": env["admin_URL"],
            "device": device,
            # "devicemode": devicemode,
            "time-zone": "GMT+8",
            "apptype": apptype,
            "currency": "CNY",
            "authorization": "Bearer "+adminToken
        }
        
        # post 
        url = f'{env["platform_api_URL"]}/admin/deposit/op'
        deposit_num = deposit_num + datetime.datetime.now().astimezone(tw).strftime('%Y%md%H%M%S%f')

        post_payload = {
            "account":f"{acc}",
            "amount":f"{amount}",
            "currency": "CNY",
            "remark":"AutoTest",
            "orderNumber":f"{deposit_num}",
            "opMethod":0
        
                }      

        response = requests.request("POST", url, headers=headers, json=post_payload).json()

    except Exception as e:
        log.error('admin/deposit/op post error: %s '%e )
        return False

    try:
        #put 
        put_payload = {
            "orderNumber": f"{deposit_num}",
            "status": "2",
            "memo": "AutoAccept"
        
                } 
        response = requests.request("PUT", url, headers=headers, json=put_payload).json()
        
        return True
    
    except Exception as e:
        print('admin/deposit/op put error: %s '%e )
        return False



def change_wallet(env , currency , ptoken):# 切換幣別

    url = f'{env["platform_api_URL"]}/payment/wallets/active?currency=%s'%currency
    
    headers = {
        'Content-Type': 'application/json',
        "referer": env["platform_URL"],
        "device": device,
        # "devicemode": devicemode,
        "time-zone": "GMT+8",
        "apptype": apptype,
        # "cks": cks,
        "authorization": "Bearer "+ptoken
    }
    try:
        response = requests.request("PUT", url, headers = headers )
        r_json = response.json()
    
        return True
    except:
        print('change_wallet: %s'%response.text)
        return False

def get_wallet_list(env, acc, ptoken):
    url = f'{env["platform_api_URL"]}/payment/wallets/list'

    headers = {
        'Content-Type': 'application/json',
        "referer": env["platform_URL"],
        "device": device,
        # "devicemode": devicemode,
        "time-zone": "GMT+8",
        "apptype": apptype,
        # "cks": cks,
        "authorization": "Bearer "+ptoken
    }
    payload = {        
    }
    start_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')
        
    status_code = '-1' # 預設值
    response_sec = '-1'
    amount = -1
    end_time = ''
    try:
        r = requests.request("GET", url, headers=headers, json=payload)
        

        status_code = r.status_code
        response_sec = r.elapsed.total_seconds()
        
        amount = -1
        try:
            response = r.json()
            response_msg = 'msg: %s , code: %s'%(response['msg'] ,  response['code'])

            if response.get('data'):
                if 'wallets' in response['data']:
                    amount = response['data']['wallets'][0]['amount']
        except Exception as ex:
            response_msg = 'FAIL'

        end_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')
    
    except Exception as e: # 走到這 是 api 連response都沒有
        response_msg = 'wallets/list error: %s'%e
        print(response_msg)
        


    return status_code, response_sec, amount, start_time, end_time, response_msg

def get_coupon_summary(env, acc, ptoken):
    url = f'{env["platform_api_URL"]}/payment/coupon/summary'

    headers = {
        'Content-Type': 'application/json',
        "referer": env["platform_URL"],
        "device": device,
        # "devicemode": devicemode,
        "time-zone": "GMT+8",
        "apptype": apptype,
        # "cks": cks,
        "currency": "CNY",
        "Accept-Language":"zh-hk",
        "authorization": "Bearer " + ptoken
    }
    payload = {        
    }
    start_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')
    
    status_code = '-1' # 預設值
    response_sec = '-1'
    availableSize = ""
    end_time = ''
    try:
        r = requests.request("GET", url, headers=headers, json=payload)
        
        status_code = r.status_code
        response_sec = r.elapsed.total_seconds()
        availableSize = "size not available"
        
        try:
            response = r.json()
            response_msg = 'msg: %s , code: %s'%(response['msg'] ,  response['code'])
            if response.get('data'):
                if 'availableSize' in response['data']:
                    availableSize = response['data']['availableSize']
        except Exception as ex:
            response_msg = 'FAIL' 

        end_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')
    
    except Exception as e: # 走到這 是 api 連response都沒有
        response_msg = 'payment/coupon/summary error: %s'%e
        print(response_msg)
    
    return status_code, response_sec, availableSize, start_time, end_time, response_msg

def get_coupon_list(env, acc, ptoken):
    url = f'{env["platform_api_URL"]}/payment/coupon/list'

    headers = {
        'Content-Type': 'application/json',
        "referer": env["platform_URL"],
        "device": device,
        # "devicemode": devicemode,
        "time-zone": "GMT+8",
        "apptype": apptype,
        "currency": "CNY",
        "Accept-Language":"zh-hk",
        "authorization": "Bearer " + ptoken
    }
    payload = {        
    }
    start_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')

    status_code = '-1' # 預設值
    response_sec = '-1'
    availableAmount = ""
    end_time = ''
    try:
    
        r = requests.request("GET", url, headers=headers, json=payload)
        
        status_code = r.status_code
        response_sec = r.elapsed.total_seconds()
        availableAmount = "amount not available"

        try:
            response = r.json()
            response_msg = 'msg: %s , code: %s'%(response['msg'] ,  response['code'])
            availableAmount = response['data']['all'][0]['availableAmount']
        except Exception as ex:
            response_msg = 'FAIL'
    
        end_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')
    
    except Exception as e: # 走到這 是 api 連response都沒有
        response_msg = 'payment/coupon/list error: %s'%e
        print(response_msg)

    return status_code, response_sec, availableAmount, start_time, end_time, response_msg

def get_bankcard(env, acc, token ,type_ = ''):# type_ 預設空 只回傳 bankcard
    url = f'{env["platform_api_URL"]}/payment/availableBankCards'

    headers = {
        'Content-Type': 'application/json',
        "referer": env["platform_URL"],
        "device": device,
        # "devicemode": devicemode,
        "time-zone": "GMT+8",
        "apptype": apptype,
        # "cks": cks,
        "currency": "CNY",
        "authorization": "Bearer "+token
    }
    payload = {        
    }
    start_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')
    r = requests.request("GET", url, headers=headers, json=payload)

    end_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')
    status_code = r.status_code
    response_sec = r.elapsed.total_seconds()

    response = r.json()
    response_msg = 'msg: %s , code: %s'%(response['msg'] ,  response['code'])
    #print('get_bankcard response_msg: %s'%response_msg)
    
    try:
        bankcard =  response['data']['accounts'][0]['cardId']
    except:
        bankcard = ''
    if type_ == '':
        return bankcard
    
    return start_time , end_time  , status_code , response_sec , response_msg ,  bankcard

def rain_apply(env, acc, user_dict, promotionType, promotionId):

    url = f'{env["platform_api_URL"]}/promotion/promotion/apply'
    headers = {
        'Content-Type': 'application/json',
        "referer": env["platform_URL"],
        "device": device,
        # "devicemode": devicemode,
        "time-zone": "GMT+8",
        "apptype": apptype,
        # "cks": cks,
        "currency": "CNY",
        "authorization": "Bearer "+user_dict[acc]['ptoken']
    }
    payload = {
        "id":promotionId,
	    "promotionType":promotionType
    }
    apply_start_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')
    
    status_code = '-1' # 預設值
    response_sec = '-1'
    amount = -1
    apply_end_time = ''
    try:
        r = requests.request("POST", url, headers=headers, json=payload)


        status_code = r.status_code
        response_sec = r.elapsed.total_seconds()

        try:
            response = r.json()
            if response.get('data'):
                if 'amount' in response['data']:
                    amount = response['data']['amount']
        except Exception as ex:
            response = r.text

        apply_end_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e: # 走到這 是 api 連response都沒有
        response = 'acc: %s promotion/promotion/apply error: %s'%(acc , e)
        print(response)

    return status_code, response_sec, amount, apply_start_time, apply_end_time, response

def get_announcement_list(env, acc, ptoken):
    url = f'{env["platform_api_URL"]}/user/announcement/list?publishPlatform=1'
    headers = {
        'Content-Type': 'application/json',
        "referer": env["platform_URL"],
        "device": device,
        # "devicemode": devicemode,
        "time-zone": "GMT+8",
        "apptype": apptype,
        # "cks": cks,
        "currency": "CNY",
        "authorization": "Bearer "+ptoken
    }
    payload = {
        
    }
    start_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')

    status_code = '-1' # 預設值
    response_sec = '-1'

    end_time = ''
    
    try:
        r = requests.request("GET", url, headers=headers, json=payload)    
        status_code = r.status_code
        response_sec = r.elapsed.total_seconds()    
        try:
            response = r.json()
            response_msg = 'msg: %s , code: %s'%(response['msg'] ,  response['code'])
        except Exception as ex:
            response_msg = r.text

        end_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')

    except Exception as e: # 走到這 是 api 連response都沒有
        response_msg = 'user/announcement/list error: %s'%e
        print(response_msg)
    
    return status_code, response_sec, start_time, end_time, response_msg

def get_userinfo(env, acc, ptoken):
    url = f'{env["platform_api_URL"]}/user/userinfo'
    headers = {
        'Content-Type': 'application/json',
        "referer": env["platform_URL"],
        "device": device,
        # "devicemode": devicemode,
        "time-zone": "GMT+8",
        "apptype": apptype,
        # "cks": cks,
        "currency": "CNY",
        "authorization": "Bearer "+ptoken
    }
    payload = {
        
    }
    start_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')
    r = requests.request("GET", url, headers=headers, json=payload)    
    status_code = r.status_code
    response_sec = r.elapsed.total_seconds()
    try:
        response = r.json()
    except Exception as ex:
        response = r.text

    end_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')
    
    return status_code, response_sec, start_time, end_time, response


def sport_index(env , acc ,ptoken ):
    url = f'{env["sport_api_URL"]}/business/sport/index/menu'
    headers = {
        'Content-Type': 'application/json',
        "referer": env["sport_URL"],
        "device": device,
        # "devicemode": devicemode,
        "time-zone": "GMT+8",
        "apptype": apptype,
        # "cks": cks,
        "currency": "CNY",
        "authorization": "Bearer "+ptoken
    }
    payload = {
        
    }
    start_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')
    r = requests.request("GET", url, headers=headers, json=payload)    
    status_code = r.status_code
    response_sec = r.elapsed.total_seconds()
    try:
        response = r.json()['code']
        print('sport_index: %s'%response)
    except Exception as ex:
        response = r.text

    end_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')
    
    return status_code, response_sec, start_time, end_time, response


class Rain_Api:
    def __init__(self  , env , csv_name , ptoken , ):
        self.env = env
        self.ptoken = ptoken
        self.sport_headers = {
        'Content-Type': 'application/json',
        "referer": self.env["sport_URL"],
        "device": device,
        # "devicemode": devicemode,
        "time-zone": "GMT+8",
        "apptype": apptype,
        "currency": "CNY",
        }
        self.csv_name = csv_name
        self.platform_headers = {
        'Content-Type': 'application/json',
        "referer": self.env["platform_URL"],
        "device": device,
        # "devicemode": devicemode,
        "time-zone": "GMT+8",
        "apptype": apptype,
        # "cks": cks,
        "currency": "CNY",
        "authorization": "Bearer "+ self.ptoken
        }
        self.sport_url = f'{self.env["sport_api_URL"]}'
        self.platform_url = f'{self.env["platform_api_URL"]}'

        self.sport_sid_mapping = {'football' : 1 , 'basketball': 2  , 'tennis': 3   ,'baseball': 4} 

        self.after_api_mapping = { 'index_menu': { 'req_method': 'GET' , 'api_path': 'business/sport/index/menu', 'payload': {} ,'range': 1 , 'type': 'product'} ,
            'check_balance': { 'req_method': 'PUT' , 'api_path': 'thirdparty/transfer/check-balance' ,  'payload': {} ,'range': 1 , 'type': 'platfrom' } ,
            'message_settings': { 'req_method': 'GET' , 'api_path':  'user/message/settings', 'payload': {} ,'range': 1 , 'type': 'platfrom'}  , 
            'bets_setting': { 'req_method': 'GET' , 'api_path': 'business/bets/setting', 'payload': {} ,'range': 1 , 'type': 'product' } ,
            'unReadRecords': { 'req_method': 'GET' , 'api_path':  'thirdparty/user/orders/sport/unReadRecords', 'payload': {} ,'range': 1  , 'type': 'platfrom'   },
            'special_matches': { 'req_method': 'GET' , 'api_path': 'business/sport/special/matches', 'payload': {} ,'range': 1 , 'type': 'product' } ,
            'tournament_info': { 'req_method': 'GET' , 'api_path': 'business/sport/tournament/info?sid=&sort=tournament&inplay=', 'payload': {} ,'range': 1 , 'type': 'product'  } ,
            'match_info': { 'req_method': 'POST' , 'api_path': 'business/popular/match/info', 'payload': {} ,'range': 1 , 'type': 'product' } ,
            'userinfo': { 'req_method': 'GET' , 'api_path': 'user/userinfo', 'payload': {} ,'range': 1  , 'type': 'platfrom'   } ,
            'unreadCount': { 'req_method': 'GET' , 'api_path': 'user/message/unreadCount', 'payload': {} ,'range': 1 , 'type': 'platfrom'  } ,
            'wallets_list': { 'req_method': 'GET' , 'api_path': 'payment/wallets/list', 'payload': {} ,'range': 1 , 'type': 'platfrom'  } ,
            'match_simple': { 'req_method': 'GET' , 'api_path': 'business/sport/match/simple?sid=&iidList=&inplay=', 'payload': {} ,'range': 1  , 'type': 'product'  } ,
        } 

    def _write_csv(self , acc , start_time  , end_time , status_code , response_sec , response , action_url):

        write_content = {
                    "user":acc,
                    "action":  action_url ,
                    "start_time": start_time,
                    "end_time":end_time,
                    "status_code":status_code,
                    "diff": response_sec,
                    "response":response
                }

        with open(self.csv_name+'.csv', 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['user', 'action', 'start_time', 'end_time', 'status_code', 'diff', 'response']

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if csvfile.tell() == 0:
                writer.writeheader()
        
            writer.writerow(write_content)
            csvfile.close() 


    def after_api(self , acc , ):



        api_list =  list(self.after_api_mapping.keys() )
        try:
            for api in api_list:
                req_method = self.after_api_mapping[api]['req_method']
                
                if api == 'tournament_info':
                    payload = self.after_api_mapping[api]['payload']

                    index_menu_list = ( list (index_menu_dict.keys()   ) )
                    random.shuffle(   index_menu_list ) #隨機 滾球 / 今日
                    inplay_type = index_menu_list[0]
                    
                    inplay_type_sport = list(index_menu_dict[inplay_type].keys())
                    random.shuffle(   inplay_type_sport ) #隨機 滾球 / 今日 的運動
                    random_sport  = inplay_type_sport[0]
                    
                    if index_menu_dict[inplay_type][random_sport] == 0:# 如果隨機 的inplay 和 隨機運動 數量是 0 .直接 給 false(非滾球)

                        #print('after inplay_type : %s,random_sport: %s 數量為0 '%(inplay_type ,random_sport ) )
                        return True
                    
                    else:
                        random_sid = self.sport_sid_mapping[random_sport]
                    
                    action_url =  self.after_api_mapping['tournament_info']['api_path'].replace("sid=", 'sid=%s'%random_sid  ).replace('inplay=', 'inplay=%s'%inplay_type)
                    print('action_url: %s'%action_url)
                
                elif api  == 'match_info': # 需取得 payloda data

                    payload = iid_list # tournament_info response 轉換取得
                    action_url = self.after_api_mapping[api]['api_path']


                elif api == 'match_simple':
                    payload = self.after_api_mapping[api]['payload']
                    action_url =  self.after_api_mapping['match_simple']['api_path'].replace("sid=", 'sid=%s'%random_sid  ).replace('inplay=', 'inplay=%s'%inplay_type).replace('iidList=', 'iidList=%s'%iid_string)
                
                else:
                    action_url = self.after_api_mapping[api]['api_path']
                    payload = self.after_api_mapping[api]['payload']
                    
                url_type = self.after_api_mapping[api]['type']
                    
                start_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')
                
                if url_type == 'product': 
                    url = f'{self.sport_url}/%s'%action_url 
                    headers =  self.sport_headers
                else:
                    url = f'{self.platform_url}/%s'%action_url 
                    headers =  self.platform_headers
                
                r = requests.request(req_method , url, headers=headers , json=payload)


                status_code = r.status_code
                response_sec = r.elapsed.total_seconds()
                try:
                    response = r.json()
                    if str(response['code']) != '0':
                        pass
                        #print('acc: %s , api: %s response : %s'%(acc ,  api,  response))
                    response_msg = 'msg: %s , code : %s'%(response['msg'] , response['code']    )
                except Exception as ex:
                    response_msg = 'FAIL'
                    print('acc: %s , api: %s ,fail: %s '%(acc , api , response_msg) )


                end_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')

                if api == 'tournament_info':
                    iid_list = []# 這邊存放  iid , sid , inplay 直 ,會給 match info post data用
                    iid_string = ""# 這邊要延展 iid  , 會給 match/simple iidList 使用
                    count = 0
                    stop_flag = ''
                    for tournaments_dict in response['data']['tournaments']:
                        for match_dict in tournaments_dict['matches']:
                            new_dict = {}
                            new_dict['iid'] = match_dict['iid']

                            iid_string +=  '%s,'%match_dict['iid']
                            new_dict['sid'] = match_dict['sid']
                            
                            new_dict['inplay'] = match_dict['inplay']
                            iid_list.append(new_dict)
                            count += 1
                            if count > 5:
                                stop_flag = 'true'
                                break
                        if stop_flag == 'true':
                            break
                    #assig_iid = iid_list[0]['iid'] # 抓出一個 iid 給 後面 抓 賠率  match_details 和 投注 game_bet 使用

                elif api == 'index_menu':
                    index_menu_dict = {}
                    
                    inplay_response = response['data']['ipc'] # 滾球
                    del inplay_response['totalCount']
                    index_menu_dict['true'] = inplay_response
                    
                    today_response = response['data']['tc']# 今日
                    del today_response['filter']
                    del today_response['totalCount']
                    
                    index_menu_dict['false'] = today_response

                if url_type == 'product':
                    action_url = '/product/'+action_url
                else:
                    action_url = '/platform/'+action_url 

                self._write_csv(  acc , start_time  , end_time , status_code , response_sec , response_msg , action_url   )


        except Exception as e:
            print('api: %s error: %s'%(api , e))
        return True


class Sport_Api:
    def __init__(self  , env , csv_name , before_delay ):
        self.env = env
        self.before_delay = before_delay
        self.csv_name = csv_name
        self.sport_headers = {
        'Content-Type': 'application/json',
        "referer": self.env["sport_URL"],
        "device": device,
        # "devicemode": devicemode,
        "time-zone": "GMT+8",
        "apptype": apptype,
        "currency": "CNY",
        }
        self.sport_sid_mapping = {'football' : 1 , 'basketball': 2  , 'tennis': 3   ,'baseball': 4} 

        self.sport_url = f'{self.env["sport_api_URL"]}'
        self.sport_before_api_mapping = {'cashout_marketSetting': { 'req_method': 'GET' , 'api_path': 'game/cashout/marketSetting', 'payload': {} ,'range': 1 } ,
            'cashout_setting': { 'req_method': 'GET' , 'api_path': 'game/cashout/setting', 'payload': {} ,'range': 1 } , 
            'index_menu': { 'req_method': 'GET' , 'api_path': 'business/sport/index/menu', 'payload': {} ,'range': 3 } ,
            'tournament_info': { 'req_method': 'GET' , 'api_path': 'business/sport/tournament/info?sid=&sort=tournament&inplay=', 'payload': {} ,'range': 1  } ,
            'match_info': { 'req_method': 'POST' , 'api_path': 'business/popular/match/info', 'payload': {} ,'range': 1 } ,
            'match_simple': { 'req_method': 'GET' , 'api_path': 'business/sport/match/simple?sid=&iidList=&inplay=', 'payload': {} ,'range': 3 } ,
            'special_matches': { 'req_method': 'GET' , 'api_path': 'business/sport/special/matches', 'payload': {} ,'range': 1 } ,
            'match_details': { 'req_method': 'GET' , 'api_path': {'true':  'business/sport/inplay/match?iid=&sid=' , 'false': 'business/sport/prematch/match?iid=&sid='} ,     
                'payload': {} ,'range': 0 } ,
            'game_bet': { 'req_method': 'POST' , 'api_path': 'game/bet', 'payload': {} ,'range': 0 } ,
        
        
        }
    
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

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if csvfile.tell() == 0:
                writer.writeheader()
        
            writer.writerow(write_content)
            csvfile.close() 



    def before_api(self , acc , ptoken , stoken ):

        
        self.sport_headers['authorization'] =  "Bearer "+ stoken
        api_list =  list(self.sport_before_api_mapping.keys() )
        try:
            for api in api_list:
                api_range = self.sport_before_api_mapping[api]['range']
                for i in range(api_range):
                    if api  == 'match_info': # 需取得 payloda data

                        payload = iid_list # tournament_info response 轉換取得
                        action_url = self.sport_before_api_mapping[api]['api_path']

                    elif api == 'match_simple':
                        payload = self.sport_before_api_mapping[api]['payload']
                        action_url =  self.sport_before_api_mapping['match_simple']['api_path'].replace("sid=", 'sid=%s'%random_sid  ).replace('inplay=', 'inplay=%s'%inplay_type).replace('iidList=', 'iidList=%s'%iid_string)

                    elif api == 'match_details':# 取得賠率相關
                        payload = self.sport_before_api_mapping[api]['payload']
                        action_url =  self.sport_before_api_mapping['match_details']['api_path'][inplay_type].replace("sid=", 'sid=%s'%random_sid  ).replace('iid=', 'iid=%s'%assig_iid)


                    elif api == 'tournament_info':
                        try:
                            payload = self.sport_before_api_mapping[api]['payload']

                            index_menu_list = ( list (index_menu_dict.keys()   ) )
                            random.shuffle(   index_menu_list ) #隨機 滾球 / 今日
                            inplay_type = index_menu_list[0]
                            
                            inplay_type_sport = list(index_menu_dict[inplay_type].keys())
                            random.shuffle(   inplay_type_sport ) #隨機 滾球 / 今日 的運動
                            random_sport  = inplay_type_sport[0]
                         
                            if index_menu_dict[inplay_type][random_sport] == 0:# 如果隨機 的inplay 和 隨機運動 數量是 0 .直接 給 false(非滾球)

                                #print('before inplay_type : %s,random_sport: %s 數量為0 '%(inplay_type ,random_sport ) )
                                return True
                            
                            else:
                                random_sid = self.sport_sid_mapping[random_sport]
                            
                            action_url =  self.sport_before_api_mapping['tournament_info']['api_path'].replace("sid=", 'sid=%s'%random_sid  ).replace('inplay=', 'inplay=%s'%inplay_type)
                            #print('tournament_info action_url : %s'%action_url)
                        except Exception as e:
                            print('tournament_info error : %s'%e)

                    elif api == 'game_bet':
                        
                        
                        action_url = self.sport_before_api_mapping[api]['api_path']
                        random_string = "".join(random.choice(string.ascii_letters + string.digits) for i in range(32)   ).lower() # 組出 英文 / 數字 32長度 給  transid 使用 (single)
                        
        
                        payload = {"marketType":"HK","singles":[{"idx":0,"id": f"{random_sid}|{assig_iid}|{assign_market}|a|0" ,"ante":30,"transId": random_string }],
                        "outrights":[],"parlays":[],
                        "tickets":[{"sid": random_sid ,"tid":tid ,"iid":assig_iid ,"market": assign_market ,"beton":"a","odds": odds ,"k": k ,
                            "inp": inplay_type,"outright":False,"score": score ,"orderPhase":1, "v":"a"}]
                        }
                        

                    
                    else: # data / url 不用做任何邏輯  ,　直接吃　預設給的　

                        payload = self.sport_before_api_mapping[api]['payload']
                        action_url = self.sport_before_api_mapping[api]['api_path']
                    
                    url =  '%s/%s'%(self.sport_url , action_url )
                    req_method = self.sport_before_api_mapping[api]['req_method']

                    start_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')
                    
                    try:
                        r = requests.request(req_method , url, headers = self.sport_headers, json=payload)  
                    
                    except Exception as e:
                        response_msg = 'api: %s error: %s'%(api ,  e)
                        #print(response_msg)
                        self._write_csv(  acc , start_time  , '' , '-1' , '' , response_msg , action_url   )
                        return False


                    time.sleep(int(self.before_delay)  )  
                    status_code =  r.status_code
                    response_sec = r.elapsed.total_seconds()
                    try:
                        response = r.json()
                        if str(response['code']) != '0':
                            pass
                            #print('acc : %s ,api: %s response : %s'%( acc, api,  response))
                        response_msg = 'msg: %s , code : %s'%(response['msg'] , response['code']    )
                    except Exception as ex:
                        response_msg = 'Fail'
                        #print('acc: %s , api: %s ,fail : %s '%(acc , api , response_msg) )
    

                    end_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')
                    self._write_csv(  acc , start_time  , end_time , status_code , response_sec , response_msg , action_url   )

                    if api == 'tournament_info':
                        iid_list = []# 這邊存放  iid , sid , inplay 直 ,會給 match info post data用
                        iid_string = ""# 這邊要延展 iid  , 會給 match/simple iidList 使用
                        count = 0
                        stop_flag = ''
                        for tournaments_dict in response['data']['tournaments']:
                            for match_dict in tournaments_dict['matches']:
                                new_dict = {}
                                new_dict['iid'] = match_dict['iid']

                                iid_string +=  '%s,'%match_dict['iid']
                                new_dict['sid'] = match_dict['sid']
                                
                                new_dict['inplay'] = match_dict['inplay']
                                iid_list.append(new_dict)
                                count += 1
                                if count > 5:
                                    stop_flag = 'true'
                                    break
                            if stop_flag == 'true':
                                break
                        assig_iid = iid_list[0]['iid'] # 抓出一個 iid 給 後面 抓 賠率  match_details 和 投注 game_bet 使用
                        #print('iid_list: %s , iid_string: %s , assig_iid: %s'%(iid_list , iid_string , assig_iid ) )
                    
                    elif api == 'index_menu':
                        index_menu_dict = {}
                        
                        inplay_response = response['data']['ipc'] # 滾球
                        del inplay_response['totalCount']
                        index_menu_dict['true'] = inplay_response
                        
                        today_response = response['data']['tc']# 今日
                        del today_response['filter']
                        del today_response['totalCount']
                        
                        index_menu_dict['false'] = today_response
                        #print('index_menu_dict: %s'%index_menu_dict)

                    elif api == 'match_details':
                        
                        
                        #bet 先不用 ,　先註解 data 資料
                        tid = response['data']['data']['tid']
                        market_dict = response['data']['data']['market'] # 存放個玩法的 賠率 
                        #print('market_dict : %s'%market_dict)
                        
                        score = ''
                        if inplay_type == 'true':# 滾球 才有
                            score = response['data']['data']['detail']['score']
                        
                        market_option = ['1x2' , 'ah']
                        for market in market_option:
                            if market in list(market_dict.keys()):
                                assign_market = market
                                odds_data = market_dict[assign_market]
                                if type(odds_data) is list:
                                    try:
                                        k = market_dict[assign_market][0]['k']
                                    except:
                                        k = ''
                                    odds =  market_dict[assign_market][0]['a']
                                else:# dict
                                    try:
                                        k = market_dict[assign_market]['k']
                                    except:
                                        k = ''
                                    odds =  market_dict[assign_market]['a']
                            
                                break
                        #print( 'tid : %s , score: %s , assign_market: %s , k: %s , odds: %s '%(tid , score , assign_market  ,k , odds )     )
                        


            return True
        
        except Exception as e:
            #print('acc : %s , api: %s error: %s'%(acc , api , e))
            return False



class Platform_Api:
    def __init__(self , env  , ptoken , csv_name , before_delay ):
        self.env = env
        self.before_delay = before_delay
        self.csv_name = csv_name
        self.platform_headers = {
        'Content-Type': 'application/json',
        "referer": self.env["platform_URL"],
        "device": device,
        # "devicemode": devicemode,
        "time-zone": "GMT+8",
        "apptype": apptype,
        # "cks": cks,
        "currency": "CNY",
        "authorization": "Bearer "+ ptoken
        }
        self.platform_url = f'{self.env["platform_api_URL"]}'
        self.before_api_mapping = { 'wallets_list': { 'req_method': 'GET' , 'api_path': 'payment/wallets/list', 'payload': {} ,'range': 1 } ,
            'check_balance': { 'req_method': 'PUT' , 'api_path': 'thirdparty/transfer/check-balance', 'payload': {} ,'range': 1  } ,
            'sysmaintenances': { 'req_method': 'GET' , 'api_path': 'sysmaintenance/sysmaintenances', 'payload': {} ,'range': 1 } ,
            'unreadCount': { 'req_method': 'GET' , 'api_path': 'user/message/unreadCount', 'payload': {} ,'range': 1 } ,
            'userinfo': { 'req_method': 'GET' , 'api_path': 'user/userinfo', 'payload': {} ,'range': 1 } ,
            'promotion_triggering': { 'req_method': 'GET' , 'api_path': 'promotion/promotion/br/triggering', 'payload': {} ,'range': 1 } ,
            'sysmaintenance_health': { 'req_method': 'GET' , 'api_path': 'sysmaintenance/health', 'payload': {} ,'range': 1 } ,
            #'unReadRecords': { 'req_method': 'GET' , 'api_path':  'thirdparty/user/orders/sport/unReadRecords', 'payload': {} ,'range': 1 },
            'message_settings': { 'req_method': 'GET' , 'api_path':  'user/message/settings', 'payload': {} ,'range': 1 },
            'currency_mapping': { 'req_method': 'GET' , 'api_path':  'thirdparty/game/currency/mapping', 'payload': {} ,'range': 1 },
            'promotionMasters': { 'req_method': 'GET' , 'api_path':  'promotion/promotionMasters?appType=8&currency=CNY', 'payload': {} ,'range': 1 },
            'availableBalance': { 'req_method': 'GET' , 'api_path':  'payment/wallets/availableBalance', 'payload': {} ,'range': 1 },
        
        }


    def before_api(self , acc) :
        
        api_list =  list(self.before_api_mapping.keys() )
        

        for api in api_list:
            action_url = self.before_api_mapping[api]['api_path']
            payload = self.before_api_mapping[api]['payload']
            req_method = self.before_api_mapping[api]['req_method']
            
            url = f'{self.platform_url}/%s'%action_url 
            start_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')
            
            try:
                r = requests.request(req_method , url, headers= self.platform_headers, json=payload)
            except Exception as e:
                response_msg = 'api: %s error: %s'%(api ,  e)
                log.error(response_msg)
                self._write_csv(  acc , start_time  , '' , '-1' , '' , response_msg , action_url   )
                return False
            
            
            time.sleep(int( self.before_delay) )

            status_code = r.status_code
            response_sec = r.elapsed.total_seconds()
            try:
                response = r.json()
                if str(response['code']) != '0':
                    pass
                    #print('acc : %s , api: %s response : %s'%(acc ,  api,  response))
                response_msg = 'msg: %s , code : %s'%(response['msg'] , response['code']    )
            except Exception as ex:
                response_msg = 'FAIL'
                log.error('acc: %s , api: %s ,fail: %s '%(acc , api , response_msg) )


            end_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')
            
            self._write_csv(  acc , start_time  , end_time , status_code , response_sec , response_msg , action_url   )
    
    
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

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if csvfile.tell() == 0:
                writer.writeheader()
        
            writer.writerow(write_content)
            csvfile.close() 

# 給 體育 串關頭注用  ,先串10 場邏輯
class Sport_Parlay_Bet:
    def __init__(self , env   , csv_name = '' ):
        self.env = env
        self.log = create_logger()#

        self.sport_url = f'{self.env["sport_api_URL"]}'
        self.sport_headers = {
            'Content-Type': 'application/json',
            "referer": self.env["platform_URL"],
            "device": device,
            # "devicemode": devicemode,
            "time-zone": "GMT+8",
            "apptype": apptype,
            "currency": "CNY",
            "accept-language": "zh-hk"
        }
        self.sport_api_mapping = {'category': { 'req_method': 'GET' , 'api_path': 'business/sport/prematch/category?sid=&date=', 'payload': {}  } ,
            'tournament': { 'req_method': 'GET' , 'api_path': 'business/sport/tournament/info?sid=&sort=tournament&inplay=&date=', 'payload': {}   } ,
            'match': { 'req_method': 'GET' , 'api_path': 'business/sport/prematch/match?iid=&sid=' ,'payload': {} } ,
            'game_bet': { 'req_method': 'POST' , 'api_path': 'game/bet', 'payload': {} } ,
            'status': { 'req_method': 'POST' , 'api_path': 'game/bet/status', 'payload': {} } , 

        }

        self.sport_sid_mapping = {'football' : 1 , 'basketball': 2  , 'tennis': 3   ,'baseball': 4} 
        #self.parlay_len = parlay_len
        self.count , self.fail_count = 0 , 0 # 紀錄 投注 筆數 / 成功筆數
        self.csv_name = csv_name
        self.cal_response_dict = defaultdict(list) # 用來計算 game/bet ,  bet/status 的計算時間

    def parlay_combo(self , parlay_type): # 組出 相關 parlay data 邏輯
        parlay_data_dict  =  { '3-1': {'parlay_l': 3 , 'option': 1 , 'idx': [0,1,2] } ,
            '3-4': {'parlay_l': 3 , 'option': 4 , 'idx': [0,1,2] } ,
            '4-1': {'parlay_l': 4 , 'option': 1 , 'idx': [0,1,2 ,3]  } ,
            '4-11': {'parlay_l': 4 , 'option': 11 , 'idx': [0,1,2 ,3]  } ,  
            '5-1': {'parlay_l': 5 , 'option':  1 , 'idx': [0,1,2 ,3 , 4]  } ,  
            '5-26': {'parlay_l': 5 , 'option': 26 , 'idx': [0,1,2 ,3 , 4 ]  } ,
            '6-1': {'parlay_l': 6 , 'option':  1 , 'idx': [0,1,2 ,3 , 4 , 5]  } ,  
            '6-57': {'parlay_l': 6 , 'option': 57 , 'idx': [0,1,2 ,3 , 4 , 5 ]  } ,
            '7-1': {'parlay_l': 7 , 'option':  1 , 'idx': [0,1,2 ,3 , 4 , 5 , 6]  } ,  
            '7-120': {'parlay_l': 7 , 'option': 120 , 'idx': [0,1,2 ,3 , 4 , 5 , 6  ]  } ,
            '8-1': {'parlay_l': 8 , 'option':  1 , 'idx': [0,1,2 ,3 , 4 , 5 , 6 , 7]  } ,  
            '8-247': {'parlay_l': 8 , 'option': 247 , 'idx': [0,1,2 ,3 , 4 , 5 , 6 , 7 ]  } ,
            '9-1': {'parlay_l': 9 , 'option':  1 , 'idx': [0,1,2 ,3 , 4 , 5 , 6 , 7 , 8 ]  } ,  
            '9-502': {'parlay_l': 9 , 'option': 502 , 'idx': [0,1,2 ,3 , 4 , 5 , 6 , 7 , 8 ]  } ,
            '10-1': {'parlay_l': 10 , 'option':  1 , 'idx': [0,1,2 ,3 , 4 , 5 , 6 , 7 , 8  , 9]  } ,  
            '10-1013': {'parlay_l': 10 , 'option': 1013 , 'idx': [0,1,2 ,3 , 4 , 5 , 6 , 7 , 8 , 9 ]  } ,

        }
        
        if parlay_type != 'random':
            try:
                parlay_data_value = parlay_data_dict[parlay_type]
                
                self.parlay_l = parlay_data_value['parlay_l']
                self.option = parlay_data_value['option']
                self.idx = parlay_data_value['idx']


            except:
                self.log.error('parlay_type: %s 不再  parlay_data_dict 裡 ,給預設 3串1  '%parlay_type )  
                self.parlay_l =  3
                self.option = 1 
                self.idx = [0,1,2]
        else:
            # random
            parlay_type_list = list(parlay_data_dict.keys()) 
            random.shuffle( parlay_type_list )

            parlay_data_value = parlay_data_dict[parlay_type_list[0]  ] 
            self.parlay_l = parlay_data_value['parlay_l']
            self.option = parlay_data_value['option']
            self.idx = parlay_data_value['idx']

        #self.log.info( 'parlay_type : %s '%parlay_data_dict  )
        
        return True


    def tran_game_data(self ,sid , bet_amount , parlay_type , single , assign_iid ):# 投注 資料 
        random_string = "".join(random.choice(string.ascii_letters + string.digits) for i in range(32)   ).lower() # 組出 英文 / 數字 32長度 給  transid 使用 (single)
        ticket_list = []
        
        if single == 'true': # 一班
            order_data = {"marketType":"EU","parlays":[],
            "singles":[{"ante":"%s"%bet_amount,"idx": 0 ,"transId":random_string }],"outrights":[] }
        else: # 串關
            self.parlay_combo(parlay_type = parlay_type) # 組出 parlay 相關 內容        
            order_data = {"marketType":"EU","parlays":[{"parlay":  self.parlay_l , "option": self.option,"ante":"%s"%bet_amount,"idx": self.idx ,"transId":random_string }],
            "singles":[],"outrights":[] }
        
        if  self.inplay_type == 'inplay':
            inp = True
        else:
            inp = False

        for  iid in self.match_dict.keys():
            order_dict = {'sid': sid , 'iid': iid , 'market': self.match_dict[iid]['market'] , 'beton': 'h' 
            , 'odds': self.match_dict[iid]['odds'] , 'tid': self.match_dict[iid]['tid'], 
                'k': self.match_dict[iid]['k'] , "inp":inp ,"outright": False ,"orderPhase":3 , "v":"a" , 'score':  self.match_dict[iid]['score']  }
            
            if assign_iid == 'true': # 聊天室 壓測
                self.chat_assign_sport['odds'] = self.match_dict[iid]['odds']
                self.chat_assign_sport['market'] = self.match_dict[iid]['market']
                self.chat_assign_sport['sid'] = sid

            ticket_list.append(order_dict)

        order_data['tickets'] = ticket_list
        return order_data

    def sport_bet(self ,sport = 'football' , token='' , acc = '' , bet_amount= '' , parlay_type= '' , single='' , 
            status= ''  ,assign_iid = ''  ): # single帶 true 是投注 single , status帶true 才打 bet/status
        
        self.count += 1
        
        sid = self.sport_sid_mapping[sport]

        order_data = self.tran_game_data(sid = sid , bet_amount = bet_amount , parlay_type = parlay_type , single = single , assign_iid =assign_iid ) # 組出 game bet data資料
        #print('order_data: %s'%order_data)

        url = f'{self.sport_url}/%s'%self.sport_api_mapping['game_bet']['api_path']

        self.sport_headers['authorization'] = "Bearer "+ token

        start_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')

        self.log.info('user: %s , bet start_time: %s'%(acc , start_time ))

        
        init_start =  time.time() 
        r = requests.request('POST' , url, headers = self.sport_headers, json = order_data)
        #print('order_data: %s'%order_data)
        all_end_time = time.time() 

        all_time = round(all_end_time - init_start,4) # 計算 bet 時間
        


        end_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')
        status_code = r.status_code
        diff = r.elapsed.total_seconds() 
        
        try:
            
            r_json = r.json()
            response = 'msg: %s , code: %s '%(r_json['msg'] , r_json['code'])
            if r_json['code'] != 0:
                assert False
            
            self.cal_response_dict['game_bet'].append(all_time)# 存放 回應時間
            #print('game_bet response: %s'%r_json)
            
            
            
            if single == 'true': # 一班
                try:
                    orderno = r_json['data']['submitted']['singles'][0]['orderno']
                    delay =  float( r_json['data']['submitted']['singles'][0]['delay'] /1000 )
                    self.log.info('acc: %s , orderno: %s , delay: %s '%(  acc , r_json['data'] , delay ))
                except:
                    fail_msg ='subCode: %s , msg: %s '%(r_json['data']['failed']['parlays'][0]['subCode'] , r_json['data']['failed']['parlays'][0]['msg'] )
                    self.log.error('fail_msg : %s'%fail_msg)
                    assert False
            else: # 串關
                try:
                    orderno = r_json['data']['submitted']['parlays'][0]['orderno']
                    delay =  float( r_json['data']['submitted']['parlays'][0]['delay'] /1000 )
                    self.log.info('acc: %s , orderno: %s , delay: %s '%(  acc , r_json['data'] , delay ))
                except:
                    fail_msg ='subCode: %s , msg: %s '%(r_json['data']['failed']['parlays'][0]['subCode'] , r_json['data']['failed']['parlays'][0]['msg'] )
                    self.log.error('fail_msg : %s'%fail_msg)
                    assert False

                    
            write_content = { "user":acc, "action": '/product/game/bet' , "start_time": start_time, "end_time": end_time,"status_code": status_code ,"diff": diff ,
            "response": response }
            general.write_csv( self.csv_name, write_content)

            if status == 'true':
                time.sleep(delay)
                self.sport_bet_status( orderno = orderno , token = token  , acc =acc ) 

            if assign_iid == 'true': # 聊天室 bet 壓測
                self.chat_assign_sport['orderno'] = orderno
                #self.order_info[acc] = self.chat_assign_sport
                return self.chat_assign_sport
            
            return orderno

        except Exception as e:
            self.log.error('acc: %s , sport_bet api error: %s , response: %s'%(acc ,  e , r.text)   )
            write_content = { "user":acc, "action": '/product/game/bet' , "start_time": start_time, "end_time": end_time,"status_code": status_code ,"diff": diff ,
            "response": r.text }
            general.write_csv( self.csv_name, write_content)
            
            self.fail_count += 1
            return False
        

        
        
    def sport_bet_status(self , orderno , token , acc ):
        url = f'{self.sport_url}/%s'%self.sport_api_mapping['status']['api_path']

        self.sport_headers['authorization'] = "Bearer "+ token
        
        start_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')
        init_start =  time.time() 
        r = requests.request('POST' , url, headers = self.sport_headers, json = [orderno] ) 
        all_end_time = time.time() 

        all_time = round(all_end_time - init_start, 4) # 計算 bet 時間

        end_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')
        status_code = r.status_code
        diff = r.elapsed.total_seconds() 
        
        try:
            
            r_json = r.json()
            if r_json['code'] != 0:
                assert False
            response = 'msg: %s , code: %s '%(r_json['msg'] , r_json['code'])
            write_content = { "user":acc, "action": '/product/game/bet/stauts' , "start_time": start_time, "end_time": end_time,"status_code": status_code ,"diff": diff ,
                "response": response }
            general.write_csv( self.csv_name, write_content)
        
            #order_statu = r_json['data']['orders']
            self.log.info('order_statu: %s'%r_json)
            self.cal_response_dict['bet_status'].append(all_time)# 存放 回應時間
            return True

    
        except Exception as e:
            self.log.error('sport_bet_status api error: %s , response: %s'%( e , r.text)   )
            write_content = { "user":acc, "action": '/product/game/bet/stauts' , "start_time": start_time, "end_time": end_time,"status_code": status_code ,"diff": diff ,
                "response": r.text }
            general.write_csv( self.csv_name, write_content)
            
            return False

    
    def trana_match_data(self , url ,iid_list , assign_iid , sinlge ): # 用來 組match iid 傳進來的 所有 賠率
        self.match_dict = {} # 用來 存放 給 game bet 投注 資料
        
        if assign_iid == 'true' :# 指定 iid
            #iid_list = [assign_iid]
            self.chat_assign_sport= {} # 給 體育聊天室壓測 曬單 , 需存相關 聯賽資訊
            self.order_info = {} # key 當user , value 當 chat_assign_sport
        
        for iid in iid_list:
            

            api_url = url.replace('iid=', 'iid=%s'%iid) 
            
            r = requests.request("GET" , api_url, headers = self.sport_headers, json= {} )  
            try:
                r_json = r.json()
                if r_json['code'] != 0:
                    assert False
                if assign_iid == 'true':
                    json_data = r_json['data']['data']
                    self.chat_assign_sport['tournamentName'] = json_data['tnName']
                    self.chat_assign_sport['homeName'] = json_data['home']['name']
                    self.chat_assign_sport['awayName'] = json_data['away']['name']
                    self.chat_assign_sport['kickOffTime'] = json_data['kickoffDT']
                    self.chat_assign_sport['tid'] = json_data['tid']
                    self.chat_assign_sport['homeId'] = json_data['home']['id']
                    self.chat_assign_sport['awayId'] = json_data['away']['id']


            except Exception as e:
                #self.log.error('trana_match_data api: match  ,error: %s , response: %s'%(  e , r.text)   )
                continue

            market_dict = r_json['data']['data']['market'] # 存放個玩法的 賠率 
            tid = r_json['data']['data']['tid']
            try:
                score = r_json['data']['data']['detail']['score']
            except:
                score = ''
            assign_market = 'ah'# 先Hardcode  让盘
            try:
                odds_data = market_dict[assign_market]
            except:
                assign_market = '1x2'# ah 如果沒有
                odds_data = market_dict[assign_market]
            try:
                if type(odds_data) is list:
                    try:
                        k = market_dict[assign_market][0]['k']
                    except:
                        k = ''
                    odds =  market_dict[assign_market][0]['h']
                else:# dict
                    try:
                        k = market_dict[assign_market]['k']
                    except:
                        k = ''
                    odds =  market_dict[assign_market]['h']
                
                #parlay_odds =  float(odds) + 1 # 串關odds + 1
            
            except: # 可能此iid沒有 ah 也沒有 1x2
                self.log.error('iid : %s 沒有 ah /1x2 玩法 , 找下一個 ')
                continue
            new_dict = {'tid': tid , 'market': assign_market , 'k': k , 'odds': str(odds) , 'score' : score   }  # 每個iid 的value 
            self.match_dict[iid] = new_dict
            

            self.log.info('比賽名稱: %s'%self.name_dict[iid]   )
            self.log.info('iid: %s  , odds data: %s'%(iid , market_dict[assign_market]   ) )
            if len( self.match_dict.keys() ) == 10  or sinlge == 'true' :#single 找一場即可
                return True
            
        
    def parlay_info(self ,  sport= 'football' , token = '' ,acc = '' , inplay_type = 'inplay_false' , assign_iid = '' ,sinlge = ''  ): # assign_iid 是給 指定 iid , 用在 聊天室 指定iid投注
        
    
        try:
            sid = self.sport_sid_mapping[sport]
        except: #  檢查 config 帶的sport 輸入
            self.log.error('sport輸入 config : %s 有誤'%sport)
            return False
        self.inplay_type = inplay_type
        
        tomaro_day = (datetime.datetime.now() + datetime.timedelta(days = +1 )) .strftime('%Y%m%d')# 一天候

        for req_api in ['category' , 'tournament' , 'match'  ]:
            url = self.sport_api_mapping[req_api]['api_path']
            payload = self.sport_api_mapping[req_api]['payload']
            req_method = self.sport_api_mapping[req_api]['req_method']
            
            if req_api == 'category': # 取得 tid大事聯賽
                api_url = url.replace('sid=', 'sid=%s'%sid).replace('date=', 'date=%s'%tomaro_day)
            elif req_api == 'tournament':# 取得iid
                
                if inplay_type == 'inplay': # 滾球
                    api_url = url.replace('sid=', 'sid=%s'%sid).replace('date=', 'date=%s'%tomaro_day).replace('inplay=', 'inplay=true')
                else: # 其他 非滾球
                    api_url = url.replace('sid=', 'sid=%s'%sid).replace('date=', 'date=%s'%tomaro_day).replace('inplay=', 'inplay=false') + "&tidList=%s"%tid_string

            elif req_api == 'match': # 將iid 送進去 拿到相關賠率
                if inplay_type == 'inplay':                
                    api_url = url.replace('sid=', 'sid=%s'%sid).replace('prematch', 'inplay')
                else:
                    api_url = url.replace('sid=', 'sid=%s'%sid)
                
                url = f'{self.sport_url}/{api_url}'
                self.trana_match_data(url = url , iid_list = iid_list  , assign_iid = assign_iid  , sinlge =sinlge ) # 會組出 self.match_dict
                #print('match_dict: %s'%self.match_dict)
                return True # 不走下面打請求 , 會在 trana_match_data loop iid 打

            else: 
                api_url = url
            
            url = f'{self.sport_url}/{api_url}'


            self.sport_headers['authorization'] = "Bearer "+ token

            start_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')

            r = requests.request(req_method , url, headers = self.sport_headers , json=payload)  
            
            end_time = datetime.datetime.now().astimezone(tw).strftime('%Y-%m-%d %H:%M:%S')
            status_code = r.status_code
            diff = r.elapsed.total_seconds()
            
            try:
                r_json = r.json()
                response = 'msg: %s , code: %s '%(r_json['msg'] , r_json['code'])
                if r_json['code'] != 0:
                    assert False
            except Exception as e:
                self.log.error('parlay_bet api: %s ,error: %s , response: %s'%(req_api , e , r.text)   )
                write_content = { "user":acc, "action": api_url , "start_time": start_time, "end_time": end_time,"status_code": status_code ,"diff": diff ,
                "response": r.text  }
                general.write_csv( self.csv_name, write_content)
                
                return False

            # 正常走這
            write_content = { "user":acc, "action": api_url , "start_time": start_time, "end_time": end_time,"status_code": status_code ,"diff": diff ,
                "response": response  }
            general.write_csv( self.csv_name, write_content)
            
            try:
                if req_api == 'category':
                    tid_list =[]
                    for re_dict in r_json['data']['categories']:
                        tournaments_info = re_dict['tournaments']
                        for t_dict in tournaments_info:
                            tid_list.append(  t_dict['tid'] )
                    '''
                    if len(tid_list) < 10:
                        parlay_len = len(tid_list)
                    else:
                        parlay_len = 10
                    '''
                    len_tid = len(tid_list)
                    tid_string = ",".join (list( map( lambda x: str(x), tid_list   ))[:len_tid] )
                    #print('tid_list : %s , tid_sting : %s'%(tid_list , tid_string)  )

                elif req_api == 'tournament':
                    iid_list = []
                    self.name_dict = {}
                    #print(' tournament: %s'%r_json['data']['tournaments'])
                    for re_dict in r_json['data']['tournaments']:
                        match_info = re_dict['matches']
                        for m_dict in match_info:
                            iid_list.append( m_dict['iid'] )
                            tnName = m_dict['tnName'] 
                            home_name = m_dict['home']['name']
                            away_name = m_dict['away']['name']
                            self.name_dict[m_dict['iid']] = '%s - %s / %s '%(tnName ,home_name, away_name )

                    #print('iid_list: %s'%iid_list)
                else:
                    self.log.info('api : %s , response: %s'%( req_api , r_json))

            except Exception as e:
                self.log.error('解析parlay_bet api: %s ,error: %s , response: %s'%(req_api , e , r.text)   ) 
                return False





    
'''

vend = "vd002_stg"
env = get_env(vend)

acc = 'kerr001'
pw = "test1234"
csv_name = 'test'

ptoken, status_code, response_sec, start_time, end_time, response = loginPlatfomuser(env,  acc, pw)

Rain_Api(   env = env , csv_name = csv_name  , ptoken=ptoken    ).after_api(acc=acc   )

'''


