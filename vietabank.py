import requests
import json
import time
from requests.cookies import RequestsCookieJar
import re
import urllib.parse
import html
import concurrent.futures
import unidecode

api_key = "CAP-6C2884061D70C08F10D6257F2CA9518C"  # your api key of capsolver
site_url = "https://ebanking.vietabank.com.vn/"  # page url of your target site


def capsolver(site_key):
    payload = {
        "clientKey": api_key,
        "task": {
            "type": 'ReCaptchaV3TaskProxyLess',
            "websiteKey": site_key,
            "websiteURL": site_url
        }
    }
    res = requests.post("https://api.capsolver.com/createTask", json=payload)
    resp = res.json()
    task_id = resp.get("taskId")
    if not task_id:
        print("Failed to create task:", res.text)
        return
    print(f"Got taskId: {task_id} / Getting result...")

    while True:
        time.sleep(1)  # delay
        payload = {"clientKey": api_key, "taskId": task_id}
        res = requests.post("https://api.capsolver.com/getTaskResult", json=payload)
        resp = res.json()
        status = resp.get("status")
        if status == "ready":
            return resp.get("solution", {}).get('gRecaptchaResponse')
        if status == "failed" or resp.get("errorId"):
            print("Solve failed! response:", res.text)
            return
class VietaBank:
    def __init__(self,username, password, account_number,proxy_list=None):
        self.keyanticaptcha = "b8246038ce1540888c4314a6c043dcae"
        self.cookies = RequestsCookieJar()
        self.session = requests.Session()
        self.tokenNo = ''
        self.password = password
        self.username = username
        self.account_number = account_number
        self.url_post = ''
        self.url_accountactivityprepare = ''
        self._ss = ''
        self.is_login = False
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
    def check_title(self,html_content):
        pattern = r'<title>(.*?)</title>'
        match = re.search(pattern, html_content)
        return match.group(1) if match else None
    def check_error_message(self,html_content):
        pattern = r'<div id="ul.errors" class="errorblock" style="color:red; ">(.*?)</div>'
        match = re.search(pattern, html_content)
        return match.group(1) if match else None
    def extract_data_cId(self,html_content):
        pattern = r'<input id="data_cId" name="data_cId" type="hidden" value="(.*)"/>'
        match = re.search(pattern, html_content)
        return match.group(1) if match else None
    def extract_data_sitekey(self,html_content):
        pattern = r'<button id="btnfind" name="btnfind" data-sitekey="(.*)" type="button" data-action="submit"'
        match = re.search(pattern, html_content)
        return match.group(1) if match else None
    def extract_url_post(self,html_content,account_number):
        pattern = r'<a href="/(.*)">'+account_number+'</a>'
        match = re.search(pattern, html_content)
        return match.group(1) if match else None
    def extract_url_accountactivityprepare(self,html_content):
        pattern = r'<a href="(.*)"  class="btn btn-primary btn-sm">Lịch sử biến động số dư</a>'
        match = re.search(pattern, html_content)
        return match.group(1) if match else None
    def extract_transaction(self,html_content):
        pattern = r'var transHis = (.*)];'
        match = re.search(pattern, html_content)
        return match.group(1)+']' if match else []
    def extract_account_name(self,html_content):
        pattern = r'<input id="flddestaccountname" name="rqBene\.beneficiaryDTO\[0\]\.paymentTemplateDTO\[0\]\.domesticImReqDataDTO\.destAccount\.accountDesc" class="form-control eng" title="T&ecirc;n chủ thẻ" data-toggle="tooltip" data-placement="top" readonly="readonly" type="text" value="(([aA-zZ]|\s)*)"/>'
        match = re.search(pattern, html_content)
        return match.group(1) if match else None
    def extract_account_number(self,html_content):
        pattern = r'<a href="/accountdetailsview\.html\?pid=\w+&fcid=asmp">(\d+)</a>\s*-\s*.*?<td.*?>([\d,.]+)</td>'

        matches = re.findall(pattern, html_content, re.DOTALL)

        extracted_data = []
        for match in matches:
            account_number = match[0]
            account_balance = float(match[1].replace(',', ''))
            account_info = {'account_number': account_number, 'balance': account_balance}
            extracted_data.append(account_info)

        if extracted_data:
            return (extracted_data)
        else:
            return None
    def login(self):
        url = "https://ebanking.vietabank.com.vn/"
        payload = {}
        headers = {}
        response = self.session.get(url, headers=headers, data=payload,proxies=self.proxies)

        url = "https://ebanking.vietabank.com.vn/"
        payload = 'ipify=0.0.0.0&disable-pwd-mgr-1=disable-pwd-mgr-1&disable-pwd-mgr-2=disable-pwd-mgr-2&disable-pwd-mgr-3=disable-pwd-mgr-3&askRename=&askRenameMsg=&actionFlg=&idChannelUser='+str(self.username)+'&password='+urllib.parse.quote(str(self.password))
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.100.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://ebanking.vietabank.com.vn',
        'Connection': 'keep-alive',
        'Referer': 'https://ebanking.vietabank.com.vn/',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
        }

        response = self.session.post(url, headers=headers, data=payload,proxies=self.proxies)
        
        self._ss = str(int(time.time() * 1000))
        title = self.check_title(response.text)
        if title == 'Tổng quan tài khoản':
            self.is_login = True
            self.time_login = time.time()
            return {
                'code': 200,
                'success': True,
                'message': 'Đăng nhập thành công',
                'data':{
                'tokenNo': self.tokenNo
                }
            }

        else:
            error_message = self.check_error_message(response.text)
            if error_message is not None:
                check_error_message = html.unescape(error_message)
            else:
                check_error_message = None
            if check_error_message:
                if 'Tên đăng nhập hoặc mật khẩu không hợp lệ' in check_error_message:
                    return {'code':444,'success': False, 'message': (check_error_message)} 
                return {
                    'code':400,
                    'success': False,
                    'message': (check_error_message)
                }
            else:
                return {
                    'code':520,
                    'success': False,
                    'message': 'Unknow Errors!'
                }
    def mapping_bank_code(self,bank_name):
        with open('banks.json','r', encoding='utf-8') as f:
            data = json.load(f)
        for bank in data['data']:
            if bank['shortName'].lower() == bank_name.lower():
                bin_code = bank['bin']
                with open('banks_vab.json','r', encoding='utf-8') as f:
                    data = json.load(f)
                for bank in data['udfFields']:    
                    if bank['udfValue'] == bin_code:
                        return {
                            'bin': bin_code,
                            'name': bank['udfName'],
                            'code': bank['udfObjectValue']
                            }
        return None
    def get_bank_name(self, ben_account_number, bank_name):
        if not self.is_login or time.time() - self.time_login > 1800:
            login = self.login()
            if not login['success']:
                return login
        url = "https://ebanking.vietabank.com.vn/domesticimmetransfer.html"

        payload = {}
        headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Referer': 'https://ebanking.vietabank.com.vn/fundtransfer.html',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
        'sec-ch-ua': '"Chromium";v="124", "Microsoft Edge";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
        }

        response =  self.session.get(url, headers=headers, data=payload,proxies=self.proxies)
        data_cId = self.extract_data_cId(response.text)
        bank_info = self.mapping_bank_code(bank_name)
        url = "https://ebanking.vietabank.com.vn/domesticimmetransfer.html"
    
        payload = {'rqBene.beneficiaryDTO[0].paymentTemplateDTO[0].idTemplate': '0',
        'sidata.si_type': 'TN',
        'sidata.next_exec_date': '',
        'sidata.executionFrequency': '1',
        'sidata.exec_days': '0',
        'sidata.exec_mths': '0',
        'sidata.exec_yrs': '0',
        'sidata.first_exec_date': '',
        'sidata.final_exec_date': '',
        'feeamt': '0.0',
        'vat': '0.0',
        'feeMin': '0.0',
        'feeMax': '0.0',
        'feePercent': '0.0',
        'cardInfo': '',
        'rqBene.beneficiaryDTO[0].paymentTemplateDTO[0].domesticImReqDataDTO.beneficiaryBankDetails[0].beneficiaryCodeType': 'ATA',
        'rqBene.beneficiaryDTO[0].paymentTemplateDTO[0].domesticImReqDataDTO.beneficiaryBankDetails[0].swiftCode': bank_info['bin'],
        'destbankname2': bank_info['name'] + ' ('+bank_info['code']+')',
        'rqBene.beneficiaryDTO[0].paymentTemplateDTO[0].domesticImReqDataDTO.destAccount.nbrAccount': ben_account_number,
        'rqBene.beneficiaryDTO[0].paymentTemplateDTO[0].domesticImReqDataDTO.destAccount.accountDesc': '',
        'destbankname': '',
        'transferamt': '',
        'rqBene.beneficiaryDTO[0].paymentTemplateDTO[0].domesticImReqDataDTO.narrative': '',
        '__templateName': '',
        'rqBene.beneficiaryDTO[0].paymentTemplateDTO[0].templateName': '',
        '__templatelevel': 'P',
        'rqBene.beneficiaryDTO[0].paymentTemplateDTO[0].typeTxn': '',
        'flgAction': 'getCardInfo',
        'ipify': '',
        '_ls': '1',
        '_ss': '1',
        'data_cId': str(data_cId)}
        files=[

        ]
        headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Origin': 'https://ebanking.vietabank.com.vn',
        'Referer': 'https://ebanking.vietabank.com.vn/domesticimmetransfer.html',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
        'sec-ch-ua': '"Chromium";v="124", "Microsoft Edge";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
        }

        response = self.session.post(url, headers=headers, data=payload,files=files,proxies=self.proxies)
        account_name = self.extract_account_name(response.text)
        return account_name
    def convert_to_uppercase_no_accents(self,text):
        # Remove accents
        no_accents = unidecode.unidecode(text)
        # Convert to uppercase
        return no_accents.upper()
    def check_bank_name(self,ben_account_number, bank_name, ben_account_name):
        get_name_from_account = self.get_bank_name(ben_account_number, bank_name)
        print('get_name_from_account',get_name_from_account)
        if get_name_from_account and isinstance(get_name_from_account, str):
            input_name = self.convert_to_uppercase_no_accents(ben_account_name).lower().strip()
            output_name = get_name_from_account.lower().strip()
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
#     check_bank_name =  vietabank.check_bank_name(account_number, bank_name, account_name), line
#     return check_bank_name
    
    
# username = "0332570526"
# password = ""
# account_number = "00365302"
# vietabank = VietaBank(username,password,account_number)

# login = vietabank.login()
# print(login)
# with open('test_cases.txt', 'r',encoding="utf8") as file:
#     lines = file.readlines()

# with concurrent.futures.ThreadPoolExecutor() as executor:
#     futures = [executor.submit(process_line, line) for line in lines]
#     for future in concurrent.futures.as_completed(futures):
#         result, line = future.result()
#         print(f'{line.strip()}, || {result}')
