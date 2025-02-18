import requests
import json
import time
import concurrent.futures
import unidecode
import random

# from smart_otp import get_smart_otp
class SeaBank:
    def __init__(self, username, password, account_number,proxy_list=None):
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
        self.file = f"data/{username}.txt"
        self.password = password
        self.username = username
        self.is_login = False
        self.account_number = account_number
        self.id_token = ""
        self.time_login = time.time()
        self.username_id = ""
        self.customer_id = ""
        if not self._file_exists():
            self.save_data()
        else:
            self.parse_data()
            self.username = username
            self.password = password
            self.account_number = account_number
            self.is_login = False

    def _file_exists(self):
        try:
            with open(self.file, 'r'):
                return True
        except FileNotFoundError:
            return False

    def save_data(self):
        data = {
            'username': self.username,
            'password': self.password,
            'account_number': self.account_number,
            'id_token': self.id_token,
            'username_id': self.username_id,
            'account_number': self.account_number
        }
        with open(self.file, 'w') as f:
            json.dump(data, f)

    def parse_data(self):
        with open(self.file, 'r') as f:
            data = json.load(f)
            self.username = data['username']
            self.password = data['password']
            self.account_number = data.get('account_number', '')
            self.customerId = data.get('customerId', '')
            self.id_token = data.get('id_token', '')
            self.username_id = data.get('username_id', '')
            self.account_number = data.get('account_number', '')

    def do_login(self):
        param = {
            "username": self.username,
            "password": self.password,
            "rememberMe": False,
            "context": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "channel": "SEAMOBILE3.0",
            "subChannel": "SEANET",
            "passwordType": "PLAINTEXT",
            "captcha": None,
            "location": None,
            "longitude": None,
            "latitude": None,
            "ipAddress": None,
            "machineName": None,
            "machineType": None,
            "application": None,
            "version": None,
            "contextFull": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.100.0"
        }
        result = self.curl_post('https://ebankbackend.seanet.vn/canhan/api/authenticate-hash', param)
        result['success'] = False
        if result['code'] == '00':
            self.is_login = True
            self.time_login = time.time()
            result['success'] = True
            self.username_id = result['data']['username']
            self.id_token = result['data']['id_token']
            self.customer_id = result['data']['customerId']
            self.account_number = result['data']['mainAccount']
            self.save_data()
        
        return result
    
    def check_bank_name_out(self,bank_code,account_number):
        param = {
            "bankID": bank_code,
            "benAccount": account_number,
            "senderAccount": self.account_number
        }
        return self.curl_post('https://ebankms2.seanet.vn/p0405/api/common/enq-check-acc', param, True)
    
    def check_bank_name_in(self,account_number):
        return self.curl_post('https://ebankms2.seanet.vn/p0405/api/swib-enquiry/check-customer-info/'+str(account_number))
    
    def mapping_bank_code(self,bank_name):
        with open('banks.json','r', encoding='utf-8') as f:
            data = json.load(f)
        for bank in data['data']:
            if bank['shortName'].lower() == bank_name.lower():
                return bank['bin']
        return None
    def get_bank_name(self, ben_account_number, bank_name):
        if not self.is_login or time.time() - self.time_login > 1200:
            login = self.do_login()
            if not login['success']:
                return login
        if 'bank_name' == 'SeABank':
            return self.check_bank_name_in(ben_account_number)
        else:
            bank_code = self.mapping_bank_code(bank_name)
            return self.check_bank_name_out(bank_code,ben_account_number)
    
    def get_list_bank(self):
        return self.curl_get('https://ebankms2.seanet.vn/p0405/api/get-list-bank')

    def curl_get(self, url):
        try:
            headers = self.header_null(True)
            # proxy_url = "http://103.189.75.146:40508"
            # proxy_username = "linhvudieu329"
            # proxy_password = "l0Ks3Jp"

            # Construct the proxy credentials
            # proxy_credentials = f"{proxy_username}:{proxy_password}"
            # proxy_auth = requests.auth.HTTPProxyAuth(proxy_username, proxy_password)

            # # Set up the proxy dictionary
            # proxies = {
            #     "http": f"http://{proxy_credentials}@{proxy_url}",
            #     "https": f"http://{proxy_credentials}@{proxy_url}"
            # }
            response = requests.get(url, headers=headers, timeout=60,proxies=self.proxies)
            result = response.json()
            return result
        except Exception as e:
            return False

    def curl_post(self, url, data=None, with_authen=False):
        try:
            headers = self.header_null(True)
            # proxy_url = "103.189.75.146:40508"
            # proxy_username = "linhvudieu329"
            # proxy_password = "l0Ks3Jp"

            # # Construct the proxy credentials
            # proxy_credentials = f"{proxy_username}:{proxy_password}"
            # proxy_auth = requests.auth.HTTPProxyAuth(proxy_username, proxy_password)

            # # Set up the proxy dictionary
            # proxies = {
            #     "http": f"http://{proxy_credentials}@{proxy_url}",
            #     "https": f"http://{proxy_credentials}@{proxy_url}"
            # }
            headers = self.header_null(with_authen)
            response = requests.post(url, headers=headers, json=data, timeout=60,proxies=self.proxies)
            result = response.json()
            return result
        except Exception as e:
            return False

    def header_null(self, with_authen=False):
        header = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://seanet.vn',
        'referer': 'https://seanet.vn/',
        'sec-ch-ua': '"Microsoft Edge";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0'
        }
        if with_authen:
            header['Authorization'] = 'Bearer ' + self.id_token

        return header
    def convert_to_uppercase_no_accents(self,text):
        # Remove accents
        no_accents = unidecode.unidecode(text)
        # Convert to uppercase
        return no_accents.upper()
    def check_bank_name(self,ben_account_number, bank_name, ben_account_name):
        get_name_from_account = self.get_bank_name(ben_account_number, bank_name)
        print('get_name_from_account',get_name_from_account)
        if get_name_from_account and  'code' in get_name_from_account and get_name_from_account['code'] == "00" and 'data' in get_name_from_account and 'accountInfo' in get_name_from_account['data']:
            input_name = self.convert_to_uppercase_no_accents(ben_account_name).lower().strip()
            output_name = get_name_from_account['data']['accountInfo']['accountName'].lower().strip()
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
#     check_bank_name =  seabank.check_bank_name(account_number, bank_name, account_name), line
#     return check_bank_name
# username = ""
# password = ""
# account_number = ""
# seabank = SeaBank(username,password,account_number)

# login = seabank.do_login()
# print(login)
# with open('test_cases.txt', 'r',encoding="utf8") as file:
#     lines = file.readlines()

# with concurrent.futures.ThreadPoolExecutor() as executor:
#     futures = [executor.submit(process_line, line) for line in lines]
#     for future in concurrent.futures.as_completed(futures):
#         result, line = future.result()
#         print(f'{line.strip()}, || {result}')