
import hashlib
import requests
import json
import base64
import random
import string
import base64
import json
import os
import hashlib
import time
import uuid
from datetime import datetime
import random
import concurrent.futures
import unidecode
from bypass_ssl_v3 import get_legacy_session
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session_requests = get_legacy_session()


class MBBANK:
    def __init__(self,corp_id, username, password, account_number,proxy_list=None):
        self.proxy_list = proxy_list
        if self.proxy_list:
            self.proxy_info = self.proxy_list.pop(0)
            proxy_host, proxy_port, username_proxy, password_proxy = self.proxy_info.split(':')
            self.proxies = {
                'http': f'socks5://{username_proxy}:{password_proxy}@{proxy_host}:{proxy_port}',
                'https': f'socks5://{username_proxy}:{password_proxy}@{proxy_host}:{proxy_port}'
            }
        else:
            self.proxies = None
        self.session = requests.Session()
        self.authToken = ""
        self.clientIp = ""
        self.time_login = time.time()
        self.guid = ""
        self.uuid = ""
        self.is_login = False
        self.key_captcha = "CAP-6C2884061D70C08F10D6257F2CA9518C"
        self.file = f"data/{username}.txt"
        self.url = {
    "getCaptcha": "https://ebank.mbbank.com.vn/corp/common/generateCaptcha",
    "login": "https://ebank.mbbank.com.vn/corp/common/do-login-v2",
    "authen-service": "https://vcbdigibiz.vietcombank.com.vn/w1/authen-service/v1/api-",
    "getHistories": "https://ebank.mbbank.com.vn/corp/transaction/v2/getTransactionHistoryV3",
    "tranferOut": "https://vcbdigibiz.vietcombank.com.vn/w1/transferout-service/v1/maker/init-247-acc",
    "genOtpOut": "https://vcbdigibiz.vietcombank.com.vn/w1/napas-service/v1/transfer-gen-otp",
    "genOtpIn": "https://vcbdigibiz.vietcombank.com.vn/w1/transfer-service/v1/transfer-gen-otp",
    "confirmTranferOut": "https://vcbdigibiz.vietcombank.com.vn/w1/transferout-service/v1/maker/confirm-247-acc",
    "confirmTranferIn": "https://vcbdigibiz.vietcombank.com.vn/w1/transferin-service/v1/maker/confirm",
    "tranferIn": "https://vcbdigibiz.vietcombank.com.vn/w1/transferin-service/v1/maker/init",
    "getBanks": "https://vcbdigibiz.vietcombank.com.vn/w1/contact-service/v1/bank/list",
    "getAccountDeltail": "https://vcbdigibiz.vietcombank.com.vn/w1/bank-service/v1/get-account-detail",
    "getlistAccount": "https://ebank.mbbank.com.vn/corp/balance/v2/getBalance",
}
        self.lang = 'VN'
        self._timeout = 60
        self.appVersion = ""
        self.clientOsVersion = "WINDOWS"
        self.browserVersion = "126.0.0.0"
        self.browserName = "Edge"
        self.deviceCode = ""
        self.deviceName = "" 
        self.checkAcctPkg = "1"
        self.captcha1st = ""
        self.challenge = ""
        self.defaultPublicKey = "-----BEGIN PUBLIC KEY-----\n\
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAikqQrIzZJkUvHisjfu5Z\n\
CN+TLy//43CIc5hJE709TIK3HbcC9vuc2+PPEtI6peSUGqOnFoYOwl3i8rRdSaK1\n\
7G2RZN01MIqRIJ/6ac9H4L11dtfQtR7KHqF7KD0fj6vU4kb5+0cwR3RumBvDeMlB\n\
OaYEpKwuEY9EGqy9bcb5EhNGbxxNfbUaogutVwG5C1eKYItzaYd6tao3gq7swNH7\n\
p6UdltrCpxSwFEvc7douE2sKrPDp807ZG2dFslKxxmR4WHDHWfH0OpzrB5KKWQNy\n\
zXxTBXelqrWZECLRypNq7P+1CyfgTSdQ35fdO7M1MniSBT1V33LdhXo73/9qD5e5\n\
VQIDAQAB\n\
-----END PUBLIC KEY-----"
        self.clientPublicKey = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCg+aN5HEhfrHXCI/pLcv2Mg01gNzuAlqNhL8ojO8KwzrnEIEuqmrobjMFFPkrMXUnmY5cWsm0jxaflAtoqTf9dy1+LL5ddqNOvaPsNhSEMmIUsrppvh1ZbUZGGW6OUNeXBEDXhEF8tAjl3KuBiQFLEECUmCDiusnFoZ2w/1iOZJwIDAQAB"
        self.clientPrivateKey = "-----BEGIN RSA PRIVATE KEY-----\n\
MIICXQIBAAKBgQCg+aN5HEhfrHXCI/pLcv2Mg01gNzuAlqNhL8ojO8KwzrnEIEuq\n\
mrobjMFFPkrMXUnmY5cWsm0jxaflAtoqTf9dy1+LL5ddqNOvaPsNhSEMmIUsrppv\n\
h1ZbUZGGW6OUNeXBEDXhEF8tAjl3KuBiQFLEECUmCDiusnFoZ2w/1iOZJwIDAQAB\n\
AoGAEGDV7SCfjHxzjskyUjLk8UL6wGteNnsdLGo8WtFdwbeG1xmiGT2c6eisUWtB\n\
GQH03ugLG1gUGqulpXtgzyUYcj0spHPiUiPDAPY24DleR7lGZHMfsnu20dyu6Llp\n\
Xup07OZdlqDGUm9u2uC0/I8RET0XWCbtOSr4VgdHFpMN+MECQQDbN5JOAIr+px7w\n\
uhBqOnWJbnL+VZjcq39XQ6zJQK01MWkbz0f9IKfMepMiYrldaOwYwVxoeb67uz/4\n\
fau4aCR5AkEAu/xLydU/dyUqTKV7owVDEtjFTTYIwLs7DmRe247207b6nJ3/kZhj\n\
gsm0mNnoAFYZJoNgCONUY/7CBHcvI4wCnwJBAIADmLViTcjd0QykqzdNghvKWu65\n\
D7Y1k/xiscEour0oaIfr6M8hxbt8DPX0jujEf7MJH6yHA+HfPEEhKila74kCQE/9\n\
oIZG3pWlU+V/eSe6QntPkE01k+3m/c82+II2yGL4dpWUSb67eISbreRovOb/u/3+\n\
YywFB9DxA8AAsydOGYMCQQDYDDLAlytyG7EefQtDPRlGbFOOJrNRyQG+2KMEl/ti\n\
Yr4ZPChxNrik1CFLxfkesoReXN8kU/8918D0GLNeVt/C\n\
-----END RSA PRIVATE KEY-----"
        if not os.path.exists(self.file):
            self.username = username
            self.password = password
            self.account_number = account_number
            self.corp_id = corp_id
            self.deviceId = ""
            self.refNo = ""
            self.sessionId = ""
            self.mobileId = ""
            self.clientId = ""
            self.cif = ""
            self.res = ""
            self.browserToken = ""
            self.browserId = ""
            self.E = ""
            self.tranId = ""
            self.accountName = ""
            self.browserId = hashlib.md5(self.username.encode()).hexdigest()
            self.save_data()
            
        else:
            self.parse_data()
            self.username = username
            self.password = password
            self.account_number = account_number
            self.is_login = False
            self.corp_id = corp_id
        self.init_guid()
    def save_data(self):
        data = {
            
            'corp_id': self.corp_id,
            'username': self.username,
            'password': self.password,
            'account_number': self.account_number,
            'sessionId': getattr(self, 'sessionId', ''),
            'mobileId': getattr(self, 'mobileId', ''),
            'clientId': self.clientId,
            'cif': getattr(self, 'cif', ''),
            'E': getattr(self, 'E', ''),
            'res': getattr(self, 'res', ''),
            'tranId': getattr(self, 'tranId', ''),
            'browserToken': getattr(self, 'browserToken', ''),
            'browserId': self.browserId,
            'refNo': self.refNo,
            'deviceId': self.deviceId,
            'accountName': self.accountName,
            
        }
        with open(self.file, 'w') as f:
            json.dump(data, f)

    def parse_data(self):
        with open(self.file, 'r') as f:
            data = json.load(f)
        self.corp_id = data.get('corp_id', '')    
        self.username = data.get('username', '')
        self.password = data.get('password', '')
        self.account_number = data.get('account_number', '')
        self.sessionId = data.get('sessionId', '')
        self.mobileId = data.get('mobileId', '')
        self.clientId = data.get('clientId', '')
        self.token = data.get('token', '')
        self.accessToken = data.get('accessToken', '')
        self.authToken = data.get('authToken', '')
        self.cif = data.get('cif', '')
        self.res = data.get('res', '')
        self.tranId = data.get('tranId', '')
        self.browserToken = data.get('browserToken', '')
        self.browserId = data.get('browserId', '')
        self.E = data.get('E', '')
        self.refNo = data.get('refNo', '')
        self.deviceId = data.get('deviceId', '')
        self.accountName = data.get('accountName', '')
    def init_guid(self):
        self.refNo = self.make_ref_no()
        self.deviceId = self.generate_random_string()
        self.save_data()
        
        
    def generate_random_string(self,length=32):
        characters = '0123456789abcdefghijklmnopqrstuvwxyz'
        characters_length = len(characters)
        random_string = ''.join(random.choice(characters) for _ in range(length))
        return random_string
    def createTaskCaptcha(self, base64_img):
        url_1 = 'https://captcha.pay2world.vip//mbbiz'
        url_2 = 'https://captcha1.pay2world.vip//mbbiz'
        url_3 = 'https://captcha2.pay2world.vip//mbbiz'
        print(base64_img)
        payload = json.dumps({
        "image_base64": base64_img
        })
        headers = {
        'Content-Type': 'application/json'
        }
        
        for _url in [url_1, url_2, url_3]:
            try:
                response = requests.request("POST", _url, headers=headers, data=payload, timeout=10)
                if response.status_code in [404, 502]:
                    continue
                return json.loads(response.text)
            except:
                continue
        return {}
    def make_ref_no(self,user_id=None):
        if user_id:
            return f"{user_id}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        return f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    def generate_captcha(self):
        url = self.url['getCaptcha']
        payload = {
            'deviceId': self.deviceId,
            'refNo': self.refNo
        }
        response = self.curlPost(url,data=payload)
        return (response)
        
    def solveCaptcha(self):
        generate_captcha = self.generate_captcha()
        if 'encryptedCaptcha' in generate_captcha:
            self.encryptedCaptcha = generate_captcha['encryptedCaptcha']
            base64_captcha_img = generate_captcha['imageBase64']
        else:
            return {"status": False, "msg": "Error generate_captcha"}
        result = self.createTaskCaptcha(base64_captcha_img)
        # captchaText = self.checkProgressCaptcha(json.loads(task)['taskId'])
        if result['prediction']:
            captcha_value = result['prediction']
            return {"status": True, "key": self.guid, "captcha": captcha_value}
        else:
            return {"status": False, "msg": "Error getTaskResult"}


    def encrypt_data(self, data):
        url = "https://babygroupvip.com/vietcombank/encrypt_biz"

        payload = json.dumps(data)
        headers = {
        'Content-Type': 'application/json',
        }
        response = requests.request("POST", url, headers=headers, data=payload)

        return json.loads(response.text)
    def decrypt_data(self, cipher):
        url = "https://babygroupvip.com/vietcombank/decrypt_biz"

        payload = json.dumps(cipher)
        headers = {
        'Content-Type': 'application/json',
        }
        response = requests.request("POST", url, headers=headers, data=payload)

        return json.loads(response.text)

    def curlPost(self, url, data):
        headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json; charset=UTF-8',
        'Origin': 'https://ebank.mbbank.com.vn',
        'Referer': 'https://ebank.mbbank.com.vn/cp/pl/login?logout=1',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
        'X-Request-Id': '2024062116262750',
        'biz-platform': 'biz-1.0',
        'biz-tracking': '/cp/pl/login/1',
        'biz-version': '1.1.31942.1616',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
        }
        if self.sessionId:
            headers['Authorization'] = 'Bearer ' + self.sessionId

        response = self.session.post(url, headers=headers, data=json.dumps(data),proxies=self.proxies)
        try:
            result = response.json()
        except ValueError:
            result = response.text

        return result

    def checkBrowser(self, type=1):
        param = {
            "clientOsVersion": self.clientOsVersion,
            "browserVersion": self.browserVersion,
            "browserName": self.browserName,
            "E": self.getE() or "",
            "browserId": self.browserId,
            "lang": self.lang,
            "mid": 3008,
            "cif": "",
            "clientId": "",
            "mobileId": "",
            "sessionId": "",
            "browserToken": self.browserToken,
            "user": self.username
        }
        result = self.curlPost(self.url['authen-service'] + "3008", param)
        if "tranId" in result["transaction"]:
            return self.chooseOtpType(result["transaction"]["tranId"], type)
        else:
            return {
                'code': 400,
                'success': True,
                'message': "checkBrowser failed",
                "param": param,
                'data': result or ""
            }

    def chooseOtpType(self, tranID, type=1):
        param = {
            "clientOsVersion": self.clientOsVersion,
            "browserVersion": self.browserVersion,
            "browserName": self.browserName,
            "E": self.getE() or "",
            "browserId": self.browserId,
            "lang": self.lang,
            "mid": 3010,
            "cif": "",
            "clientId": "",
            "mobileId": "",
            "sessionId": "",
            "browserToken": self.browserToken,
            "tranId": tranID,
            "type": type,  # 1 la sms,5 la smart
            "user": self.username
        }
        result = self.curlPost(self.url['authen-service'] + "3010", param)
        if result["code"] == "00":
            self.tranId = tranID
            self.saveData()
            self.challenge = result.get("challenge", "")
            return {
                    'code': 200,
                    'success': True,
                    'message': 'Thành công',
                "result": {
                    "browserToken": self.browserToken,
                    "tranId": result.get("tranId", ""),
                    "challenge": result.get("challenge", "")
                },
                "param": param,
                'data': result or ""
            }
        else:
            return {
                'code': 400,
                'success': False,
                'message': result["des"],
                "param": param,
                'data': result or ""
            }

    def submitOtpLogin(self, otp):
        param = {
            "clientOsVersion": self.clientOsVersion,
            "browserVersion": self.browserVersion,
            "browserName": self.browserName,
            "E": self.getE() or "",
            "browserId": self.browserId,
            "lang": self.lang,
            "mid": 3011,
            "cif": "",
            "clientId": "",
            "mobileId": "",
            "sessionId": "",
            "browserToken": self.browserToken,
            "tranId": self.tranId,
            "otp": otp,
            "challenge": self.challenge,
            "user": self.username
        }
        result = self.curlPost(self.url['authen-service'] + "3011", param)
        if result["data"]["code"] == "00":
            self.sessionId = result["sessionId"]
            self.mobileId = result["userInfo"]["mobileId"]
            self.clientId = result["userInfo"]["clientId"]
            self.cif = result["userInfo"]["cif"]
            session = {"sessionId": self.sessionId, "mobileId": self.mobileId, "clientId": self.clientId, "cif": self.cif}
            self.res = result
            self.saveData()
            
            if result["allowSave"]:
                sv = self.saveBrowser()
                if sv["code"] == "00":
                    self.is_login = True
                    return {
                        'code': 200,
                        'success': True,
                        'message': 'Thành công',
                        'saved_browser': True,
                        "d": sv,
                        'session': session,
                        'data': result or ""
                    }
                else:
                    return {
                        'code': 400,
                        'success': False,
                        'message': sv["des"],
                        "param": param,
                        'data': sv or ""
                    }
            else:
                return {
                        'code': 200,
                        'success': True,
                        'message': 'Thành công',
                        'saved_browser': False,
                        'session': session,
                        'data': result or ""
                    }
        else:
            return {
                'code': 500,
                'success': False,
                'message': result["des"],
                "param": param,
                'data': result or ""
            }

    def saveBrowser(self):
        param = {
            "clientOsVersion": self.clientOsVersion,
            "browserVersion": self.browserVersion,
            "browserName": self.browserName,
            "E": self.getE() or "",
            "browserId": self.browserId,
            "browserName": "Microsoft Edge 125.0.0.0",
            "lang": self.lang,
            "mid": 3009,
            "cif": self.cif,
            "clientId": self.clientId,
            "mobileId": self.mobileId,
            "sessionId": self.sessionId,
            "user": self.username
        }
        result = self.curlPost(self.url['authen-service'] + "3009", param)
        return result

    def do_login(self):
        solveCaptcha = self.solveCaptcha()
        if not solveCaptcha["status"]:
            return solveCaptcha
        param = {
            
            "corpId": self.corp_id,
            "deviceId": self.deviceId,
            "encryptedCaptcha": self.encryptedCaptcha,
            "password": self.password,
            "captcha": solveCaptcha["captcha"],
            "refNo": self.refNo,
            "userId": self.username,
        }
        result = self.curlPost(self.url['login'], param)
        
        if 'result' in result and 'responseCode' in result['result'] and result['result']['responseCode'] == "00":
            self.sessionId = result['sessionId']
            self.accountName = result['cust']['acct_list'][self.account_number]['acctNm']
            session = {
                "sessionId": self.sessionId,
            }
            self.save_data()
            self.is_login = True
            return {
                'code': 200,
                'success': True,
                'message': "success",
                'session': session,
                'data': result if result else ""
            }
        elif 'result' in result and 'message' in result['result']:
            return {
                'code': 500,
                'success': False,
                'message': result['result']['message'],
                "param": param,
                'data': result if result else ""
            }     
        else:
            return {
                'code': 500,
                'success': False,
                'message': "Unknow error",
                "param": param,
                'data': result if result else ""
            }

    def saveData(self):
        data = {
            'username': self.username,
            'password': self.password,
            'account_number': self.account_number,
            'sessionId': self.sessionId,
            'mobileId': self.mobileId,
            'clientId': self.clientId,
            'cif': self.cif,
            'E': self.E,
            'res': self.res,
            'tranId': self.tranId,
            'browserToken': self.browserToken,
            'browserId': self.browserId,
        }
        with open(f"data/{self.username}.txt", "w") as file:
            json.dump(data, file)

    def parseData(self):
        with open(f"data/{self.username}.txt", "r") as file:
            data = json.load(file)
            self.username = data["username"]
            self.password = data["password"]
            self.account_number = data.get("account_number", "")
            self.sessionId = data.get("sessionId", "")
            self.mobileId = data.get("mobileId", "")
            self.clientId = data.get("clientId", "")
            self.token = data.get("token", "")
            self.accessToken = data.get("accessToken", "")
            self.authToken = data.get("authToken", "")
            self.cif = data.get("cif", "")
            self.res = data.get("res", "")
            self.tranId = data.get("tranId", "")
            self.browserToken = data.get("browserToken", "")
            self.browserId = data.get("browserId", "")
            self.E = data.get("E", "")

    def getE(self):
        ahash = hashlib.md5(self.username.encode()).hexdigest()
        imei = '-'.join([ahash[i:i+4] for i in range(0, len(ahash), 4)])
        return imei.upper()

    def getCaptcha(self):
        captchaToken = ''.join(random.choices(string.ascii_uppercase + string.digits, k=30))
        url = self.url['getCaptcha'] + captchaToken
        response = requests.get(url,proxies=self.proxies)
        result = base64.b64encode(response.content).decode('utf-8')
        return result

    def getlistAccount(self):
        if not self.is_login:
            login = self.do_login()
            if not login['success']:
                return login
        param = {
            'refNo': self.refNo
        }
        result = self.curlPost(self.url['getlistAccount'], param)
        if 'acct_list' in result and 'refNo' in result:
            for account in result['acct_list']:
                if self.account_number == account['acctNo']:
                    if float(account['currentBalance']) < 0 or account['blockedAmount']:
                        return {'code':448,'success': False, 'message': 'Blocked account!',
                                'data': {
                                    'balance':float(account['currentBalance'])
                                }
                                }
                    else:
                        return {'code':200,'success': True, 'message': 'Thành công',
                                'data':{
                                    'account_number':self.account_number,
                                    'balance':float(account['currentBalance'])
                        }}
            return {'code':404,'success': False, 'message': 'account_number not found!'} 
        else: 
            return {'code':520 ,'success': False, 'message': 'Unknown Error!'} 

    def getlistDDAccount(self):
        param = {
            "clientOsVersion": self.clientOsVersion,
            "browserVersion": self.browserVersion,
            "browserName": self.browserName,
            "browserId": self.browserId,
            "E": self.getE() or "",
            "mid": 35,
            "cif": self.cif,
            "serviceCode": "0551",
            "user": self.username,
            "mobileId": self.mobileId,
            "clientId": self.clientId,
            "sessionId": self.sessionId
        }
        result = self.curlPost(self.url['getlistDDAccount'], param)
        return result

    def getAccountDeltail(self):
        param = {
            "clientOsVersion": self.clientOsVersion,
            "browserVersion": self.browserVersion,
            "browserName": self.browserName,
            "E": self.getE() or "",
            "browserId": self.browserId,
            "accountNo": self.account_number,
            "accountType": "D",
            "mid": 13,
            "cif": self.cif,
            "user": self.username,
            "mobileId": self.mobileId,
            "clientId": self.clientId,
            "sessionId": self.sessionId
        }
        result = self.curlPost(self.url['getAccountDeltail'], param)
        return result

    def getHistories(self, fromDate="16/06/2023", toDate="16/06/2023", account_number='', page=1,size=15,limit = 100):
        if not self.is_login:
                login = self.do_login()
                if not login['success']:
                    return login
        param = {
            "accountName": self.accountName,
            "accountNo": account_number if account_number else self.account_number,
            "currency": "VND",
            "fromDate": fromDate,
            "refNo": self.refNo,
            "toDate": toDate,
            "page": page,
            "size": size,
            "top": limit
        }
        result = self.curlPost(self.url['getHistories'], param)
        if 'result' in result and 'responseCode' in result['result'] and  result['result']['responseCode'] == '00' and 'transactionHistoryList' in result:
            return {'code':200,'success': True, 'message': 'Thành công',
                            'data':{
                                'transactions':result['transactionHistoryList'],
                    }}
        else:
            return  {
                    "success": False,
                    "code": 503,
                    "message": "Service Unavailable!"
                }

    def getBanks(self):
        param = {
            "clientOsVersion": self.clientOsVersion,
            "browserVersion": self.browserVersion,
            "browserName": self.browserName,
            "E": self.getE() or "",
            "browserId": self.browserId,
            "lang": self.lang,
            "fastTransfer": "1",
            "mid": 23,
            "cif": self.cif,
            "user": self.username,
            "mobileId": self.mobileId,
            "clientId": self.clientId,
            "sessionId": self.sessionId
        }
        result = self.curlPost(self.url['getBanks'], param)
        return result
    def check_bank_name_out(self,bank_code,account_number):
        param = {
            "accountNo": account_number,
            "refNo": self.refNo,
            "amount": None,
            "benBankCd": bank_code
        }
        result =  self.curlPost('https://ebank.mbbank.com.vn/corp/transfer/getDomesticInfo', param)
        if 'benName' in result:
            result['customerName'] = result['benName']
        return result
    
    def check_bank_name_in(self,account_number):
        param = {
            "accountNumber": account_number,
            "refNo": self.refNo,
            "sourceAccount": self.account_number
        }
        return self.curlPost('https://ebank.mbbank.com.vn/corp/transfer/getVABenName',param)
    
    def mapping_bank_code(self,bank_name):
        with open('banks.json','r', encoding='utf-8') as f:
            data = json.load(f)
        for bank in data['data']:
            if bank['shortName'].lower() == bank_name.lower():
                with open('mbbank_biz.json','r', encoding='utf-8') as f:
                    data = json.load(f)
                for bank_2 in data['listBank']:
                    if bank_2['smlCode'] == bank['bin']:
                        return bank_2['bankId']
                    
        return None
    def get_bank_name(self, ben_account_number, bank_name):
        if not self.is_login or time.time() - self.time_login > 900:
            login = self.do_login()
            if not login['success']:
                return login
        if bank_name == 'MBBank':
            result =  self.check_bank_name_in(ben_account_number)
        else:
            bank_code = self.mapping_bank_code(bank_name)
            result =  self.check_bank_name_out(bank_code,ben_account_number)
        if 'Credentials are required to access this resource' in result:
            login = self.do_login()
            if not login['success']:
                return login
        if bank_name == 'MBBank':
            result =  self.check_bank_name_in(ben_account_number)
        else:
            bank_code = self.mapping_bank_code(bank_name)
            result =  self.check_bank_name_out(bank_code,ben_account_number)
        return result
    def convert_to_uppercase_no_accents(self,text):
        # Remove accents
        no_accents = unidecode.unidecode(text)
        # Convert to uppercase
        return no_accents.upper()
    def check_bank_name(self,ben_account_number, bank_name, ben_account_name):
        get_name_from_account = self.get_bank_name(ben_account_number, bank_name)
        print('get_name_from_account_mbbiz',get_name_from_account)
        if get_name_from_account and 'result' in get_name_from_account and 'responseCode' in get_name_from_account['result'] and get_name_from_account['result']['responseCode'] == "00" and ('customerName' in get_name_from_account) and get_name_from_account['customerName']:
            input_name = self.convert_to_uppercase_no_accents(ben_account_name).lower().strip()
            output_name = get_name_from_account['customerName'].lower().strip()
            if output_name == input_name or output_name.strip().replace(' ','') == input_name.strip().replace(' ',''):
                return True
            else:
                return output_name
        return False

# def process_line(line):
#     parts = line.split()
#     account_name = ' '.join(parts[:-2])
#     account_number = parts[-2]
#     bank_name = parts[-1]
#     check_bank_name =  mbbank.check_bank_name(account_number, bank_name, account_name), line
#     return check_bank_name

# corp_id = "0110061284"
# username = "KETOAN"
# password = ""
# account_number = "881234566666"
# mbbank = MBBANK(corp_id,username,password,account_number)

# st = time.time()
# login = mbbank.do_login()
# print('login',login)


# with open('test_cases.txt', 'r',encoding="utf8") as file:
#     lines = file.readlines()

# with concurrent.futures.ThreadPoolExecutor() as executor:
#     futures = [executor.submit(process_line, line) for line in lines]
#     for future in concurrent.futures.as_completed(futures):
#         result, line = future.result()
#         print(f'{line.strip()}, || {result}')

# while True: 
#     print(time.time()-st)
#     res = mbbank.check_bank_name("0621000456871", "Vietcombank", "TRAN DUY QUANG")
#     print(res)
#     time.sleep(10)