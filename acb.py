import requests
import json
import random
import concurrent.futures
import unidecode
import time
class ACB:
    def __init__(self, username, password, account_number,proxy_list=None):
        self.connect = None  # You can initialize your database connection here
        self.clientId = 'iuSuHYVufIUuNIREV0FB9EoLn9kHsDbm'
        self.URL = {
            "LOGIN": "https://apiapp.acb.com.vn/mb/v2/auth/tokens",
            "REFRESH": "https://apiapp.acb.com.vn/mb/v2/auth/refresh",
        }
        self.time_login = time.time()
        self.token = ""
        self.refreshToken = ""
        self.password = password
        self.username = username
        self.account_number = account_number
        self.is_login = False
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
    def handleLogin(self):
        data = {
            'clientId': self.clientId,
            'username': self.username,
            'password': self.password
        }
        return self.curl_post(self.URL["LOGIN"], data)

    def refresh_token(self):
        response =  self.curl_post(self.URL["REFRESH"])
        if 'accessToken' in response and response['accessToken']:
            self.token = response['accessToken']
            if 'refreshToken' in response and response['refreshToken']:
                self.refreshToken = response['refreshToken']
        else:
            print(self.login())
        return response

    def get_bank_name(self, ben_account_number, bank_name):
        if not self.is_login or time.time() - self.time_login > 118:
            self.refresh_token()
        bank_code = self.mapping_bank_code(bank_name)
        status = False
        message = 'Error exception'
        data = {}
        url = f'https://apiapp.acb.com.vn/mb/legacy/ss/cs/bankservice/transfers/accounts/{ben_account_number}?bankCode={bank_code}&accountNumber={self.account_number}'

        count = 0
        while True:
            bankName = self.curl_get(url)
            if 'message' not in bankName or ('message' in bankName and  bankName['message'] != 'Unauthorized'):
                data = bankName
                status = True
                message = 'Successfully'
                break
            else:
                login = self.login()
                # print(login)

            count += 1
            if count > 2:
                message = 'Connect false'
                break

        return {'success': status, 'message': message, 'data': data}
    def convert_to_uppercase_no_accents(self,text):
        # Remove accents
        no_accents = unidecode.unidecode(text)
        # Convert to uppercase
        return no_accents.upper()
    def check_bank_name(self,ben_account_number, bank_name, ben_account_name):
        get_name_from_account = self.get_bank_name(ben_account_number, bank_name)
        print('get_name_from_account_acb',ben_account_number,get_name_from_account)
        if get_name_from_account and 'data' in get_name_from_account and 'data' in get_name_from_account['data']:
            if get_name_from_account['data']['data'] and 'ownerName' in get_name_from_account['data']['data']:
                input_name = self.convert_to_uppercase_no_accents(ben_account_name).lower().strip()
                output_name = get_name_from_account['data']['data']['ownerName'].lower().strip()
                if output_name == input_name or output_name.strip().replace(' ','') == input_name.strip().replace(' ',''):
                    return True
                else:
                    return output_name
        return False
    
    def load_user(self, username):
        # Implement database queries to load user here
        pass

    def login(self):
        if not self.username or not self.username:
            return {'success': 0, 'msg': 'Vui lòng nhập đầy đủ thông tin'}
        user = self.load_user(self.username)

        res = self.handleLogin()
        if 'accessToken' in res:
            self.token = res['accessToken']
            self.refreshToken = res['refreshToken']
            data = json.dumps(res)
            if not user:
                # Implement database insert here
                pass
            else:
                # Implement database update here
                pass
            self.is_login = True
            return {'code':200,'success': True, 'message': 'Đăng nhập thành công'}
        elif 'identity' in res and 'passwordExpireAlert' in res['identity'] and res['identity']['passwordExpireAlert']:
            
            return {'code':445,'success': False, 'message': 'passwordExpireAlert!'} 
        
        elif 'vn.com.acb.platform.authn.exception.UsernameOrPasswordIncorrectException' in res['error']:
            
            return {'code':444,'success': False, 'message': res['error']} 
        
        elif 'vn.com.acb.platform.authn.exception.UserLockedByAdminException' in res['error']:
            
            return {'code':449,'success': False, 'message': 'vn.com.acb.platform.authn.exception.UserLockedByAdminException'} 
        
        elif 'vn.com.acb.platform.authn.exception.UserLockedPasswordAttemptException' in res['error']:
            
            return {'code':443,'success': False, 'message': 'vn.com.acb.platform.authn.exception.UserLockedPasswordAttemptException'} 
        else:
            return {'code':400,'success': False, 'message': res['error']} 

    def curl_get(self, url):
        try:
            if url == "https://apiapp.acb.com.vn/mb/v2/auth/refresh":
                headers = self.header_null(refreshToken=True)
            else:
                headers = self.header_null()
            response = requests.get(url, headers=headers, timeout=60,proxies=self.proxies)
            result = response.json()
            return result
        except Exception as e:
            return False

    def curl_post(self, url, data=None):
        if url == "https://apiapp.acb.com.vn/mb/v2/auth/refresh":
            headers = self.header_null(refreshToken=True)
        else:
            headers = self.header_null()
        response = requests.post(url, headers=headers, json=data, timeout=60,proxies=self.proxies)
        result = response.json()
        return result

    def header_null(self,refreshToken = None):
            header = {
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'vi',
                'Connection': 'keep-alive',
                'Content-Type': 'application/json',
                'sec-ch-ua-mobile': '?0',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-site',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
            }
            if self.token:
                header['Authorization'] = 'Bearer ' + self.token
            if refreshToken:
                header['Authorization'] = 'Bearer ' + self.refreshToken
                

            return header
    def mapping_bank_code(self,bank_name):
        with open('banks.json','r', encoding='utf-8') as f:
            data = json.load(f)
        for bank in data['data']:
            if bank['shortName'].lower() == bank_name.lower():
                return bank['bin']
        return None
# def process_line(line):
#     parts = line.split()
#     account_name = ' '.join(parts[:-2])
#     account_number = parts[-2]
#     bank_name = parts[-1]
#     check_bank_name =  acb.check_bank_name(account_number, bank_name, account_name), line
#     return check_bank_name

# username = ""
# password = ""
# account_number="39888667"
# proxy_list = []
# acb = ACB(username, password, account_number,proxy_list)

# login = acb.login()

# print(login)
# with open('test_cases.txt', 'r',encoding="utf8") as file:
#     lines = file.readlines()

# with concurrent.futures.ThreadPoolExecutor() as executor:
#     futures = [executor.submit(process_line, line) for line in lines]
#     for future in concurrent.futures.as_completed(futures):
#         result, line = future.result()
#         print(f'{line.strip()}, || {result}')

