import requests
import json
import hashlib
import urllib.parse
import unidecode
import time
import concurrent.futures

class Zalopay:
    def __init__(self, cookies,proxy_list=None):
      self.cookies = cookies[1:-1]
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
      
    def mapping_bank_code(self,bank_name):
        with open('banks.json','r', encoding='utf-8') as f:
            data = json.load(f)
        for bank in data['data']:
            if bank['shortName'].lower() == bank_name.lower():
                  return bank['code']
    def check_bank_name_out(self,bank_code,account_number):
        url = "https://scard.zalopay.vn/v1/mt/ibft-switch/tof/inquiry"

        payload = json.dumps({
          "bank_code": bank_code,
          "bank_number": account_number,
          "type": 0
        })
        headers = {
          'Connection': 'keep-alive',
          'Host': 'scard.zalopay.vn',
          'Origin': 'https://social.zalopay.vn',
          'Accept': '*/*',
          'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 ZaloPayClient/9.12.1 OS/17.5.1 Platform/ios Secured/true ZaloPayWebClient/9.12.1',
          'Content-Length': '58',
          'Accept-Encoding': 'gzip, deflate, br',
          'Content-Type': 'application/json',
          'Accept-Language': 'vi-VN,vi;q=0.9',
          # 'Referer': 'https://social.zalopay.vn/spa/v2/chuyen-tien?from_source=home_zalopay&maccesstoken=ci-5BXWn56irhpqoLlDDV87IgoKJ05S9DmfiqhwqC8O_mzSnqlTLuLBwYsM4v6NrmFlfyGq4Hj-WMSnYbB4DKpi1AO36KoZdoeiR8hlpdxU7E-T6voxcK3SvYC9EInvWXbHQ89Zg8O-F0xtm1jNtW_PWXWAOKWQZ0Udz2bPbzsyFe_HKGFtcEgpJHTG7qV1vjmKZFlwAaWbl-sL8ocwMCJBNbVnpaCGPTRxaQiIB_amKUcY9GdxWRBJvi23ZkTfTdIALBLMcaPVE9ZokocY0tA&muid=LV8v6DucgTfKq-gDoOa2DeDYKW_ldi-v4gFGgKeXbOE&appid=1313&isroot=false&main-app=true',
          'Cookie': self.cookies,
          'Sec-Fetch-Mode': 'cors',
          'Sec-Fetch-Dest': 'empty',
          'Sec-Fetch-Site': 'same-site'
        }

        result = requests.request("POST", url, headers=headers, data=payload)
        try:
          result = result.json()
        except:
          result = result.text
        if 'bank_holder_name' in result:
            result['customerName'] = result['bank_holder_name']
        return result                    
    def get_bank_name(self, ben_account_number, bank_name):

        bank_code = self.mapping_bank_code(bank_name)
        result =  self.check_bank_name_out(bank_code,ben_account_number)
        # if 'bank_holder_name' not in result:
        #     bank_code = self.mapping_bank_code(bank_name)
        #     result =  self.check_bank_name_out(bank_code,ben_account_number)


        return result
    def convert_to_uppercase_no_accents(self,text):
        # Remove accents
        no_accents = unidecode.unidecode(text)
        # Convert to uppercase
        return no_accents.upper()
    def check_bank_name(self,ben_account_number, bank_name, ben_account_name):
        get_name_from_account = self.get_bank_name(ben_account_number, bank_name)
        print('get_name_from_account',get_name_from_account)
        if get_name_from_account and 'customerName' in get_name_from_account and get_name_from_account['customerName']:
            input_name = self.convert_to_uppercase_no_accents(ben_account_name).lower().strip()
            output_name = get_name_from_account['customerName'].lower().strip()
            if output_name == input_name or output_name.strip().replace(' ','') == input_name.strip().replace(' ',''):
                return True
            else:
                return output_name
        return False
      

# cookies = ''

# st = time.time()
# zalopay = Zalopay(cookies)

# def process_line(line):
#     parts = line.split()
#     account_name = ' '.join(parts[:-2])
#     account_number = parts[-2]
#     bank_name = parts[-1]
#     check_bank_name =  zalopay.check_bank_name(account_number, bank_name, account_name), line
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
#     res = zalopay.check_bank_name("0621000456871", "Vietcombank", "TRAN DUY QUANG")
#     print(res)
#     time.sleep(10)