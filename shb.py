import json
import hashlib
import urllib.parse
import unidecode
import time
import concurrent.futures
import random

from bypass_ssl_v3 import get_legacy_session
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
class SHB:
    def __init__(self, username, password, account_number,device_id,cif_no,active_code,token=None,proxy_list=None):
        self.clientId = 'iuSuHYVufIUuNIREV0FB9EoLn9kHsDbm'
        self.URL = {
            "SHB": "https://mbanking.shb.com.vn/mbgwretail/process_new.aspx",
        }
        self.username = username
        self.password = password
        self.account_number = account_number
        self.file = f"data/shb/{username}.txt"
        self.TOKEN = token
        self.session = get_legacy_session()
        self.CIF_NO = cif_no
        self.ADJUST_ID = ''
        self.ACTIVE_CODE = active_code
        self.device_id = device_id
        self.res = ''
        self.is_login = False
        self.time_login = time.time()
        self.proxy_list = proxy_list
        if self.proxy_list:
            self.proxy_info = random.choice(self.proxy_list)
            proxy_host, proxy_port, username_proxy, password_proxy = self.proxy_info.split(':')
            self.proxies = {
                'http': f'http://{username_proxy}:{password_proxy}@{proxy_host}:{proxy_port}',
                'https': f'http://{username_proxy}:{password_proxy}@{proxy_host}:{proxy_port}'
            }
        else:
            self.proxies = None

        if not self.file_exists():
            self.save_data()
        else:
            self.parse_data()
            self.TOKEN = token
            self.CIF_NO = cif_no
            self.ACTIVE_CODE = active_code
            self.account_number = account_number
            self.username = username
            self.password = password
            self.save_data()

            


    def file_exists(self):
        try:
            with open(self.file):
                return True
        except FileNotFoundError:
            return False

    def save_data(self):
        data = {
            'username': self.username,
            'password': self.password,
            'account_number': self.account_number,
            'TOKEN': self.TOKEN,
            'ADJUST_ID': self.ADJUST_ID,
            'CIF_NO': self.CIF_NO,
            'ACTIVE_CODE': self.ACTIVE_CODE,
            'res': self.res,
        }
        with open(self.file, 'w') as f:
            json.dump(data, f)

    def parse_data(self):
        with open(self.file, 'r') as f:
            data = json.load(f)
            self.username = data['username']
            self.password = data['password']
            self.account_number = data['account_number']
            self.TOKEN = data.get('TOKEN', '')
            self.ADJUST_ID = data.get('ADJUST_ID', '')
            self.CIF_NO = data.get('CIF_NO', '')
            self.ACTIVE_CODE = data.get('ACTIVE_CODE', '')
            self.res = data.get('res', '')

    def header_default(self, token=''):
        header = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'mbanking.shb.com.vn',
            'User-Agent': 'SHB Mobile/5.14.13 (iPhone; iOS 15.7.7; Scale/2.00)',
        }
        return header

    def get_otp(self):
        data_dict = {
            "CMD": "ACTIVE_MOB_V2",
            "MOBILE_NO": self.username,
            "PWD": hashlib.md5(self.password.encode()).hexdigest(),
            "DeviceName": "iPhone16,2",
            "DeviceId": "175eb1ae42c5441a91d135f142688491",
            "AppVer": "5.22.1"
        }

        # Creating the formatted string
        formatted_string = '|'.join([f"{key}%23{value}" for key, value in data_dict.items()])
        data = f"REQ={formatted_string}"
        # data = f'CMD#ACTIVE_MOB|MOBILE_NO#{self.username}|PWD#{hashlib.md5(self.password.encode()).hexdigest()}'
        res = self.curl(data)
        return res

    def verify_otp(self, otp):
        data = f"CMD#ACTIVE_MOB_CONFIRM|MOBILE_NO#{self.username}|MOB_ACTIVE_CODE#{otp}"
        res = self.curl(data)
        if res['ERR_CODE'] == "00":
            self.CIF_NO = res['CIF_NO']
            self.TOKEN = res['TOKEN']
            self.ADJUST_ID = res['ADJUST_ID']
            self.ACTIVE_CODE = otp
            self.res = res
            self.save_data()
        return res
    def dict_to_str(self,data_dict):
        req_value = data_dict.pop('REQ', '')
        result = f'REQ%23{urllib.parse.quote(req_value, safe="")}'
        result += '%7C' + '%7C'.join(
            f'{k}%23{urllib.parse.quote(v, safe="")}' for k, v in data_dict.items()
        )
        result = result.replace("REQ%23","REQ=")
        return result
    def change_proxy(self):
        print('change_proxy')
        self.proxy_info = random.choice([item for item in self.proxy_list if item not in [self.proxy_info]])
        proxy_host, proxy_port, username_proxy, password_proxy = self.proxy_info.split(':')
        self.proxies = {
            'http': f'http://{username_proxy}:{password_proxy}@{proxy_host}:{proxy_port}',
            'https': f'http://{username_proxy}:{password_proxy}@{proxy_host}:{proxy_port}'
        }
    def do_login(self):
        # self.change_proxy()
        data_dict = {
            'REQ': 'CMD#CHECK_LOGIN',
            'CIF_NO': self.CIF_NO,
            'PWD': hashlib.md5(self.password.encode()).hexdigest(),
            'ACTIVE_CODE': self.ACTIVE_CODE,
            'APP_VER': '5.22.1',
            'DeviceName': 'iPhone17,2',
            'DeviceId': self.device_id,
            'AppVer': '5.22.1'
        }
        data = self.dict_to_str(data_dict)
        res = self.curl(data)
        res['success'] = False
        if res['ERR_CODE'] == "00":
            self.is_login = True
            res['success'] = True
            self.CIF_NO = res['CIF_NO']
            self.TOKEN = res['TOKEN']
            self.ADJUST_ID = res['ADJUST_ID']
            self.save_data()
        return res

    def get_transactions(self):
        data = f"CMD#GET_ACCT_CASA_INFO_N|CIF_NO#{self.CIF_NO}|ACCTNO#{self.account_number}|ENQUIRY_TYPE#LAST5|TOKEN#{self.TOKEN}"
        res = self.curl(data)
        if res['ERR_CODE'] == '00':
            transactions = []
            if res['RECORD_ACTIVITY'] != '{RECORD_ACTIVITY}':
                if isinstance(res['RECORD_ACTIVITY'][0], str):
                        v = res['RECORD_ACTIVITY']
                        transactions.append({
                            'date': v[0],
                            'amount': v[1],
                            'description': v[2],
                            'id': v[3],
                        })
                else:
                    for v in res['RECORD_ACTIVITY']:
                        transactions.append({
                            'date': v[0],
                            'amount': v[1],
                            'description': v[2],
                            'id': v[3],
                        })
            del res['RECORD_ACTIVITY']
            res['RECORD_ACTIVITY'] = transactions
        return res

    def get_balance(self):
        data = f"CMD#GET_ACCT_LIST_QRY_N|CIF_NO#{self.CIF_NO}|TOKEN#{self.TOKEN}"
        res = self.curl(data)
        if res['ERR_CODE'] == '00':
            res['BALANCE'] = res['RECORD'][4]
        return res

    def curl(self, data):
        try:
            headers = self.header_default()
            response = self.session.post(self.URL['SHB'], headers=headers, data=data,proxies=self.proxies,verify=False,timeout=7)
            return self.parse_response(response.text)
        except Exception as e:
            print('reason change proxy',e)
            self.change_proxy()
            return None

    def parse_response(self, msg):
        msg = msg.replace("<MSG>", "").replace("</MSG>", "")
        keyValuePairs = msg.split("|")
        data = {}
        for pair in keyValuePairs:
            key, value = pair.split("#", 1)
            if '$' in value:
                if 'BRC^' in value:
                    value = [v.split('$') for v in value.split('BRC^')]
                else:
                    value = value.split('$')
            data[key] = value
        return data
    def check_bank_name_out(self,bank_code,account_number):
        request_dict = {
            'REQ': 'CMD#GET_247_ACCT_HOLDER_NEW',
            'CIF_NO': self.CIF_NO,
            'ACCTNO': account_number,
            'BANK_CODE': str(bank_code),
            'TOKEN': self.TOKEN
        }
        data = self.dict_to_str(request_dict)
        # print(data)
        result = self.curl(data)
        if 'BEN_NAME' in result:
            result['customerName'] = result['BEN_NAME']
        return result
    
    def check_bank_name_in(self,account_number):
        request_dict = {
            "REQ": "CMD#GET_BENNAME_FROM_CASA_ACCOUNT",
            "CIF_NO": self.CIF_NO,
            "DES_ACCT": account_number,
            "TOKEN": self.TOKEN
        }
        data = self.dict_to_str(request_dict)
        result = self.curl(data)
        if 'DES_NAME' in result:
            result['customerName'] = result['DES_NAME']
        return result
    
    def mapping_bank_code(self,bank_name):
        with open('banks.json','r', encoding='utf-8') as f:
            data_1 = json.load(f)
        for bank_1 in data_1['data']:
            if bank_1['shortName'].lower() == bank_name.lower():
                bank_code =  bank_1['code']
                with open('banks_shb.json','r', encoding='utf-8') as f:
                    data_2 = json.load(f)
                for bank_2 in data_2:
                    if bank_2['bank_code'] == bank_code:
                        return bank_2['bank_cif']
                return None
        return None
                    
    def get_bank_name(self, ben_account_number, bank_name):
        if not self.is_login or time.time() - self.time_login > 300:
            login = self.do_login()
            if not login['success']:
                return login
        if bank_name == 'SHB':
            result =  self.check_bank_name_in(ben_account_number)
        else:
            bank_code = self.mapping_bank_code(bank_name)
            result =  self.check_bank_name_out(bank_code,ben_account_number)
        if 'ERR_DESC' in result and result['ERR_DESC'] == 'TOKEN INVALID':
            login = self.do_login()
            if not login['success']:
                return login
        if bank_name == 'SHB':
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
        print('get_name_from_account_SHB_'+self.username,ben_account_number,get_name_from_account)
        if get_name_from_account and 'ERR_CODE' in get_name_from_account and get_name_from_account['ERR_CODE'] == "00" and ('customerName' in get_name_from_account) and get_name_from_account['customerName']:
            input_name = self.convert_to_uppercase_no_accents(ben_account_name).lower().strip()
            output_name = get_name_from_account['customerName'].lower().strip()
            if output_name == input_name or output_name.strip().replace(' ','') == input_name.strip().replace(' ',''):
                return True
            else:
                return output_name
        return False
# username = "0886438795"
# password = ""
# account_number = "1022699595"
# device_id = "175eb1ae42c5441a91d135f142688491"
# shb = SHB(username, password, account_number,device_id)

# st = time.time()
# #OTP is required first login only, then youn can call action without it after login
# login = shb.do_login()
# print(login)

# get_otp = shb.get_otp()
# print(get_otp)
# if "ERR_CODE" in get_otp and get_otp["ERR_CODE"] == '00':
#     if get_otp['ERR_DESC'] == 'ACTIVE CODE GENERATED SUCCESSFULL':
#         otp = input("Enter OTP: ")
#         verify_otp = shb.verify_otp(otp)
#         if "ERR_CODE" in verify_otp and verify_otp["ERR_CODE"] == '00':
#             print('ACTIVE SUCCESSFULL')
#             get_balance = shb.get_balance()
#             print(get_balance)

#             get_transactions = shb.get_transactions()
#             print(get_transactions)
#         else:
#             print(f"OTP verification failed: {verify_otp['ERR_DESC']}")
#     else:
#         print(f"Login failed: {get_otp['ERR_DESC']}")
        
#OTP is required first login only, then youn can call action without it after login
# get_balance = shb.get_balance()
# print(get_balance)

# get_transactions = shb.get_transactions()
# print(get_transactions)


# def process_line(line):
#     parts = line.split()
#     account_name = ' '.join(parts[:-2])
#     account_number = parts[-2]
#     bank_name = parts[-1]
#     check_bank_name =  shb.check_bank_name(account_number, bank_name, account_name), line
#     return check_bank_name

# with open('test_cases.txt', 'r',encoding="utf8") as file:
#     lines = file.readlines()

# with concurrent.futures.ThreadPoolExecutor() as executor:
#     futures = [executor.submit(process_line, line) for line in lines]
#     for future in concurrent.futures.as_completed(futures):
#         result, line = future.result()
#         print(f'{line.strip()}, || {result}')

# while True: 
#     print(time.time()-st)
#     res = shb.check_bank_name("0621000456871", "Vietcombank", "TRAN DUY QUANG")
#     print(res)
#     time.sleep(10)