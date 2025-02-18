import requests
import json
import random
from base64 import b64encode
import re
import json
import string
from datetime import datetime
import concurrent.futures
import unidecode
import time

class VTB:
    def __init__(self, username, password, account_number,proxy_list=None):
        self.proxies = None
        self.time_login = time.time()
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
        self.url = {
            'captcha': 'https://api-ipay.vietinbank.vn/api/get-captcha/',
            'login': 'https://api-ipay.vietinbank.vn/ipay/wa/signIn',
            'getCustomerDetails': 'https://api-ipay.vietinbank.vn/ipay/wa/getCustomerDetails',
            'getEntitiesAndAccounts': 'https://api-ipay.vietinbank.vn/ipay/wa/getEntitiesAndAccounts',
            'getCmsData': 'https://api-ipay.vietinbank.vn/ipay/wa/getCmsData',
            'getBillPayees': 'https://api-ipay.vietinbank.vn/ipay/wa/getBillPayees',
            'creditAccountList': 'https://api-ipay.vietinbank.vn/ipay/wa/creditAccountList',
            'getAvgAccountBal': 'https://api-ipay.vietinbank.vn/ipay/wa/getAvgAccountBal',
            'getHistTransactions': 'https://api-ipay.vietinbank.vn/ipay/wa/getHistTransactions',
            'getAccountDetails': 'https://api-ipay.vietinbank.vn/ipay/wa/getAccountDetails',
            'getCodeMapping': 'https://api-ipay.vietinbank.vn/ipay/wa/getCodeMapping',
            'napasTransfer': 'https://api-ipay.vietinbank.vn/ipay/wa/napasTransfer',
            'makeInternalTransfer': 'https://api-ipay.vietinbank.vn/ipay/wa/makeInternalTransfer',
            'getPayees': 'https://api-ipay.vietinbank.vn/ipay/wa/getPayees',
            'authenSoftOtp': 'https://api-ipay.vietinbank.vn/ipay/wa/authenSoftOtp'
        }
        self.browser_info = "Chrome-98.04758102"
        self.lang = 'vi'
        self.client_info = '127.0.0.1;MacOSProMax'
        self.timeout = 15
        self.public_key = "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDLenQHmHpaqYX4IrRVM8H1uB21\nxWuY+clsvn79pMUYR2KwIEfeHcnZFFshjDs3D2ae4KprjkOFZPYzEWzakg2nOIUV\nWO+Q6RlAU1+1fxgTvEXi4z7yi+n0Zs0puOycrm8i67jsQfHi+HgdMxCaKzHvbECr\n+JWnLxnEl6615hEeMQIDAQAB\n-----END PUBLIC KEY-----"
        self.session_id = None
        self.account_number = account_number
        self.ipay_id = None
        self.token_id = None
        self.username = username
        self.access_code = password
        self.captcha_code = None
        self.captcha_id = None
        self.request_id = None
        self.sign = None
        self.customer_number = None
        self.bsb = None
        self.account_type = None
        self.currency_code = None
        self.is_login = False
        
    def save_data(self):
        data = {
            'username': self.username,
            'password': self.access_code,
            'accountNumber': self.account_number,
            'sessionId': self.session_id,
            'ipayId': self.ipay_id,
            'tokenId': self.token_id,
            'customerNumber': self.customer_number,
            'currencyCode': self.currency_code,
            'bsb': self.bsb,
            'accountType': self.account_type,
        }
        with open(f"data/{self.username}.json", "w") as file:
            json.dump(data, file)

    def parse_data(self):
        try:
            with open(f"data/{self.username}.json", "r") as file:
                data = json.load(file)
                self.username = data['username']
                self.access_code = data['password']
                self.access_code = data['password']
                self.account_number = data.get('accountNumber', '')
                self.account_type = data.get('accountType', '')
                self.customer_number = data.get('customerNumber', '')
                self.bsb = data.get('bsb', '')
                self.token_id = data.get('tokenId', '')
                self.ipay_id = data.get('ipayId', '')
                self.session_id = data.get('sessionId', '')
                self.currency_code = data.get('currencyCode', '')
        except FileNotFoundError:
            pass

    def get_captcha(self):
        self.captcha_id = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=9))
        headers = self.header_null()
        response = requests.get(self.url['captcha'] + self.captcha_id, headers=headers, timeout=self.timeout,proxies=self.proxies)
        svg = response.text
        self.captcha_code = self.bypass_captcha(svg)
        return True

    def do_login(self):
        self.request_id = self.generate_request_id()
        self.get_captcha()
        params = {
            'accessCode': self.access_code,
            'browserInfo': self.browser_info,
            'captchaCode': self.captcha_code,
            'captchaId': self.captcha_id,
            'clientInfo': self.client_info,
            'lang': self.lang,
            'requestId': self.request_id,
            'userName': self.username,
            'screenResolution': "1201x344"
        }
        
        headers = self.header_null()
        body = self.make_body_request_json(params)
        response = requests.post(self.url['login'], headers=headers, data=body, timeout=self.timeout,proxies=self.proxies)
        login = response.json()
        if 'error' in login and not login['error']:
            self.is_login = True 
            self.time_login = time.time()
            self.session_id = login['sessionId']
            self.customer_number = login['customerNumber']
            self.ipay_id = login['ipayId']
            self.token_id = login['tokenId']
            info = self.get_entities_and_accounts()
            self.bsb = info['accounts'][0]['bsb']
            self.account_type = info['accounts'][0]['type']
            self.currency_code = info['accounts'][0]['currencyCode']
            self.save_data()
            return {
                'code': 200,
                'success': True,
                'message': 'Đăng nhập thành công',
                'data': login
            }
        elif 'errorMessage' in login and 'sai tên đăng nhập hoặc mật khẩu' in login['errorMessage']:
            return {
                'code': 444,
                'success': False,
                'message': login['errorMessage']
            }
        elif 'errorMessage' in login and 'bị khóa' in login['errorMessage']:
            return {
                'code': 408,
                'success': False,
                'message': login['errorMessage']
            }
        elif 'errorMessage' in login:
            return {
                'code': 400,
                'success': False,
                'message': login['errorMessage'],
            }
        else:
            return {
                'code': 500,
                'success': False,
                'message': 'Internal Server Error!',
            }
    def get_balance(self,account_number):
        if not self.is_login:
            login = self.do_login()
            if not login['success']:
                return login
        arr = self.get_entities_and_accounts()
        if arr['accounts']:
            amount = 0
            for v in arr['accounts']:
                if v['number'] == account_number:
                    amount = v['accountState']['availableBalance']
                    total_balance = v['accountState']['balance']
                    if int(amount) < 0:
                        return {'code':448,'success': False, 'message': 'Blocked account with negative balances!',
                                'data': {
                                    'balance':int(amount)
                                }
                                }
                    elif int(amount) == 0 and int(total_balance) > int(amount):
                                return {'code':449,'success': False, 'message': 'Blocked account!',
                                'data': {
                                    'balance':int(amount),
                                    'total_balance':int(total_balance)
                                }
                                }
                    else:
                        return {'code':200,'success': True, 'message': 'Thành công',
                                'data':{
                                    'account_number':self.account_number,
                                    'balance':int(amount)
                        }}
            return {'code':404,'success': False, 'message': 'account_number not found!'} 
        else: 
            return {'code':520 ,'success': False, 'message': 'Unknown Error!'} 
    def get_entities_and_accounts(self):
        self.request_id = self.generate_request_id()
        params = {
            'lang': self.lang,
            'requestId': self.request_id
        }
        headers = self.header_null()
        body = self.make_body_request_json(params)
        response = requests.post(self.url['getEntitiesAndAccounts'], headers=headers, data=body, timeout=self.timeout,proxies=self.proxies)
        return response.json()
    def get_transaction(self, limit,start_date, end_date):
        if not self.is_login:
            login = self.do_login()
            if not login['success']:
                return login
        self.request_id = self.generate_request_id()
        params = {
        'accountNumber': self.account_number,
        'endDate': end_date,
        'lang': 'vi',
        'maxResult': str(limit),
        'pageNumber': 0,
        'requestId': self.request_id,
        'searchFromAmt': '',
        'searchKey': '',
        'searchToAmt': '',
        'startDate': start_date,
        'tranType': ''
    }
        headers = self.header_null()
        body = self.make_body_request_json(params)
        response = requests.post(self.url['getHistTransactions'], headers=headers, data=body, timeout=self.timeout,proxies=self.proxies)
        if response.status_code == 401:
            return {'code':401,'success': False, 'message': 'Unauthorized!'}
        
        if response.status_code != 200:
            return {'code':response.status_code,'success': False, 'message': 'Unknown error!'}
        try:
            result = response.json()
        except json.decoder.JSONDecodeError:
            result = {
                "status" : "500"
            }
        if 'error' in result:  
            if not result['error'] and 'transactions' in result:
                return {'code':200,'success': True, 'message': 'Thành công',
                            'data':{
                                'transactions':result['transactions'],
                    }}
            elif result['error'] and 'errorMessage' in result and 'vượt quá số lượt' in result['errorMessage']:
                return {'code':429,'success': False, 'message': 'Too Many Requests!'}
            else:
                return {'code':400,'success': False, 'message': result['errorMessage']}
        else:
            return {'code':520 ,'success': False, 'message': 'Unknown Error!'} 

    # Add other methods following the same pattern
    def build_query_string(self,params):
        query_string = "&".join(f"{key}={value}" for key, value in params.items())
        return query_string
    def make_body_request_json(self, params):
        if self.session_id:
            params['sessionId'] = self.session_id
        return self.encrypt_data(params)
    def encrypt_data(self, data):
        url = "https://encrypt1.pay2world.vip/api.php?act=encrypt_viettin"

        payload = json.dumps(data)
        headers = {
        'Content-Type': 'application/json',
        }
        response = requests.request("POST", url, headers=headers, data=payload)

        return json.loads(response.text)

    def bypass_captcha(self,svg):
        model = {
            "MCLCLCLCLCLCCLCLCLCLCLCLCCLCLCLCLCCLCLCLCLCCZMCCLCLCCLCLCCLCLCCLCZ": 0,
            "MLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLZ": 1,
            "MLLLLLLLLLLLLCLCLCCLCLCLLLLLLLLLLLLLLLLLLLLLLLLLLLLLZ": 2,
            "MCLCCLCLCCLCLCLLLLLLLLLLLCCCCCLLLLLLLLLLLLCCCCCCCCLLLLLCCCLCCLCCLCLCCZ": 3,
            "MLLLLLLLLLLLLLLLLLCLCLCCLCLCLLLLLLLLLLLLLLLLLLLLLLLLLZMLLLLLLLLLLLLLLLZMLLLZ": 4,
            "MCLCLCLCLCLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLCCLLLLLLLCLCLCZ": 5,
            "MCLCLCLCLCCCLCLCLCLCLCLCLCLCLCLCLCLCLCLCLCLCCLCLCZMLCCCCLCLCCLCZ": 6,
            "MLCLCCLCLCLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLCZ": 7,
            "MCLCLCLCCLCCLCLCLCLCCLCLCLCLCCLCCLCLCLCCLCLCCLCLCZMLCLCCCCLCZMLCCLCLCCCCLCZ": 8,
            "MLCLCLCLCLCLCCLCLCLCLCCLCLCLCLCCCCCLCLCLCLCLCLCLCLCZMLCCCCCLCLCCCCLCZ": 9
        }
        chars = {}
        matches = re.findall(r'<path fill="(.*?)" d="(.*?)"/>', svg)
        if len(matches) != 6:
            return len(matches)
        
        paths = [match[1] for match in matches]
        for path in paths:
            p = re.search(r"M([0-9]+)", path)
            if p:
                pattern = re.sub(r"[0-9 \.]", "", path)
                chars[int(p.group(1))] = model[pattern]
        
        chars = dict(sorted(chars.items()))
        return "".join(str(chars[key]) for key in chars)

    def generate_request_id(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12)) + '|' + str(int(datetime.now().timestamp()))

    def header_null(self):
        headers = {
            "Accept-Encoding": "gzip",
            "Accept-Language": "vi-VN",
            "Accept": "application/json",
            "Cache-Control": "no-store, no-cache",
            "User-Agent": "okhttp/3.11.0"
        }
        if self.session_id:
            headers["sessionId"] = self.session_id
        return headers
    def name_internal_transfer(self, beneficiary_account):
        self.requestId = self.generate_request_id()
        params = {
            'accountNumber': beneficiary_account,
            'formAction': "inquiryToAcctDetail",
            'lang': self.lang,
            'requestId': self.requestId
        }
        response = requests.post(
            self.url['makeInternalTransfer'],
            headers=self.header_null(),
            data=self.make_body_request_json(params)
            ,proxies=self.proxies
        )
        result =  response.json()
        if 'toAccountName' in result:
            result['beneficiaryName'] = result['toAccountName']
        return result
    def name_napas_transfer(self, beneficiary_account, beneficiary_bin):
        self.requestId = self.generate_request_id()
        params = {
            'beneficiaryAccount': beneficiary_account,
            'beneficiaryBin': beneficiary_bin,
            "beneficiaryType": "account",
            'fromAccount': self.account_number,
            'formAction': "validateToAccount",
            'lang': self.lang,
            'requestId': self.requestId
        }
        response = requests.post(
            self.url['napasTransfer'],
            headers=self.header_null(),
            data=self.make_body_request_json(params)
            ,proxies=self.proxies
        )
        return response.json()
    def mapping_bank_code(self,bank_name):
        with open('banks.json','r', encoding='utf-8') as f:
            data = json.load(f)
        for bank in data['data']:
            if bank['shortName'].lower() == bank_name.lower():
                return bank['bin']
        return None
    def get_bank_name(self, ben_account_number, bank_name):
        if not self.is_login or time.time() - self.time_login > 300:
            login = self.do_login()
            if not login['success']:
                return login
        if bank_name == 'VietinBank':
            return self.name_internal_transfer(ben_account_number)
        else:
            bank_code = self.mapping_bank_code(bank_name)
            return self.name_napas_transfer(ben_account_number,bank_code)
    def convert_to_uppercase_no_accents(self,text):
        # Remove accents
        no_accents = unidecode.unidecode(text)
        # Convert to uppercase
        return no_accents.upper()
    def check_bank_name(self,ben_account_number, bank_name, ben_account_name):
        get_name_from_account = self.get_bank_name(ben_account_number, bank_name)
        print('get_name_from_account_vtb',ben_account_number,get_name_from_account)
        if get_name_from_account and 'error' in get_name_from_account and not get_name_from_account['error'] and 'beneficiaryName' in get_name_from_account and get_name_from_account['beneficiaryName']:
            input_name = self.convert_to_uppercase_no_accents(ben_account_name).lower().strip()
            output_name = get_name_from_account['beneficiaryName'].lower().strip()
            if output_name == input_name or output_name.strip().replace(' ','') == input_name.strip().replace(' ',''):
                return True
            else:
                return output_name
        self.is_login = False
        self.save_data()
        return False

# def process_line(line):
#     parts = line.split()
#     account_name = ' '.join(parts[:-2])
#     account_number = parts[-2]
#     bank_name = parts[-1]
#     check_bank_name =  vtb.check_bank_name(account_number, bank_name, account_name), line
#     return check_bank_name

# username = "0886438795"
# password = ""
# account_number = "109879087651"


# vtb = VTB(username, password, account_number)
# response = vtb.do_login()
# print(response)

# with open('test_cases.txt', 'r',encoding="utf8") as file:
#     lines = file.readlines()

# with concurrent.futures.ThreadPoolExecutor() as executor:
#     futures = [executor.submit(process_line, line) for line in lines]
#     for future in concurrent.futures.as_completed(futures):
#         result, line = future.result()
#         print(f'{line.strip()}, || {result}')