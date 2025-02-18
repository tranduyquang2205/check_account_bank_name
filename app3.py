from fastapi import FastAPI, HTTPException,HTTPException, Request
from concurrent.futures import ThreadPoolExecutor, TimeoutError, CancelledError
import uvicorn
from pydantic import BaseModel
import random
import time
import configparser
import sys
import traceback
import threading
from typing import List

# Import your bank classes
from acb import ACB
# from mbbank_biz import MBBANK
from mbbank import MBBANK
from bvbank import BVBank
from seabank import SeaBank
from techcombank_biz import Techcombank
from vietabank import VietaBank
from vietinbank import VTB
from zalopay import Zalopay
from ocb import OCB
from shb import SHB
from api_response import APIResponse
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio


WHITELISTED_IPS = [
    '103.57.223.111',
    '103.56.163.65',
    '103.57.223.209',
    '103.57.220.100',
    '202.92.7.227',
    '202.92.7.228',
    '3.0.239.143',
    '202.92.7.230',
    '115.75.209.253',
    '127.0.0.1',
    '0.0.0.0'
]
class IPWhitelistMiddleware:
    def __init__(self, app: FastAPI, allowed_ips: List[str]):
        self.app = app
        self.allowed_ips = allowed_ips

    async def __call__(self, request: Request, call_next):
        client_ip = request.client.host
        if client_ip not in self.allowed_ips:
            print(f"Access denied for IP: {client_ip}")
            return APIResponse.json_format({'code':503,'result': False, 'message': 'Unknown error!'})
        return await call_next(request)
# Map the class names to the actual classes
BANK_CLASSES = {
    'ACB': ACB,
    'MBBANK': MBBANK,
    'Techcombank': Techcombank,
    'VTB': VTB,
    'SeaBank': SeaBank,
    'VietaBank': VietaBank,
    'Zalopay': Zalopay,
    'SHB': SHB,
    'OCB': OCB,
    'BVBank': BVBank
}
bank_access_limits = {
    'ACB': {'limit': 20, 'interval': timedelta(minutes=1)},
    'MBBANK': {'limit': 1, 'interval': timedelta(seconds=10)},
    'BVBank': {'limit': 100000, 'interval': timedelta(seconds=10)},
    'Techcombank': {'limit': 1000000, 'interval': timedelta(minutes=1)},
    'VTB': {'limit': 1, 'interval': timedelta(minutes=1)},
    'SeaBank': {'limit': 30, 'interval': timedelta(minutes=1)},
    'VietaBank': {'limit': 1000000, 'interval': timedelta(minutes=1)},
    'SHB': {'limit': 1000000, 'interval': timedelta(minutes=1)},
    'Zalopay': {'limit': 10, 'interval': timedelta(hours=1)},
    'OCB': {'limit': 100, 'interval': timedelta(minutes=1)}
}
bank_access_log = defaultdict(list)

def is_bank_available(bank_name):
    current_time = datetime.now()
    access_logs = bank_access_log[bank_name]
    access_logs = [log for log in access_logs if log > current_time - bank_access_limits[bank_name]['interval']]
    bank_access_log[bank_name] = access_logs
    return len(access_logs) < bank_access_limits[bank_name]['limit']
def log_bank_access(bank_name):
    bank_access_log[bank_name].append(datetime.now())
# Read configuration from config file
config = configparser.ConfigParser()
config.read('config.ini')

def parse_proxy_list(proxy_list_str):
    if proxy_list_str.lower() in ['none', 'empty']:
        return None
    return proxy_list_str.split(',')

banks = []
for section in config.sections():
    for bank_name in BANK_CLASSES.keys():
        if section.startswith(f"{bank_name}_"):
            bank_class = BANK_CLASSES[bank_name]
            params = {k: v for k, v in config[section].items()}
            if 'proxy_list' in params:
                params['proxy_list'] = parse_proxy_list(params['proxy_list'])
            print(bank_name,params)
            bank_instance = bank_class(**params)
            banks.append(bank_instance)
# print(banks)
async def check_bank(bank, account_number, bank_name, account_name):
    try:
        print(bank.__class__.__name__)
        if bank.__class__.__name__ == 'BVBank':
            return await bank.check_bank_name(account_number, bank_name, account_name)
        return bank.check_bank_name(account_number, bank_name, account_name)
    except CancelledError:
        print(1111)
        return False

app = FastAPI()
app.middleware("http")(IPWhitelistMiddleware(app, WHITELISTED_IPS))

class BankInfo(BaseModel):
    account_number: str
    bank_name: str
    account_name: str

@app.post('/check_bank_name', tags=["check_bank_name"])
async def check_bank_name(input: BankInfo):
    account_number = input.account_number
    bank_name = input.bank_name
    account_name = input.account_name
    # print(account_number, bank_name, account_name)
    completion_event = threading.Event()
    result_container = []
    # def task_wrapper(bank, account_number, bank_name, account_name):
    #     return asyncio.run(aync_task_wrapper(bank, account_number, bank_name, account_name))
    def run_async_task_in_executor(loop, coro, *args):
        return asyncio.run_coroutine_threadsafe(coro(*args), loop)
    async def task_wrapper(bank, account_number, bank_name, account_name):
        try:
            result = await check_bank(bank, account_number, bank_name, account_name)
            if not completion_event.is_set() and (result is True or isinstance(result, str)):
                result_container.append((result, bank))
                completion_event.set()
                log_bank_access(bank.__class__.__name__)
                for future in futures:
                    future.cancel()
                print('cancel')
            elif not completion_event.is_set() and result is False:
                completion_event.set()
                result_container.append((result, bank))
        except CancelledError:
            print(11111)
            pass
        except Exception as e:
            print(f"Error processing bank {bank}: {e}")

    with ThreadPoolExecutor(max_workers=1) as executor:
        available_banks = [bank for bank in banks if is_bank_available(bank.__class__.__name__)]
        if len(available_banks) < 1:
            return APIResponse.json_format({'result': False, 'message': 'Not enough banks available'})
        selected_banks = random.sample(available_banks, min(1, len(available_banks))) 
        remaining_banks = [bank for bank in banks if bank not in selected_banks]
        # futures = await [executor.submit(task_wrapper, bank, account_number, bank_name, account_name) for bank in selected_banks]
        futures = [executor.submit(task_wrapper, bank, account_number, bank_name, account_name) for bank in selected_banks]
        start_time = time.time()
        
        try:
            completion_event.wait(timeout=7)
            try:
                if result_container:
                    for result, bank in result_container:
                        print(f'result_{bank.__class__.__name__}', result)
                        if result is True:
                            return (APIResponse.json_format({'result': result, 'bank': bank.__class__.__name__}))
                        elif isinstance(result, str):
                            return APIResponse.json_format({'result': False, 'true_name': result.upper().replace(' ', ''), 'bank': bank.__class__.__name__})
                        elif result == False or result is None:
                            continue
            except Exception as e:
                response = str(e)
                print(traceback.format_exc())
                print(sys.exc_info()[2])
                return APIResponse.json_format(response)
        except TimeoutError:
            return APIResponse.json_format({'result': False, 'message': 'timeout'})

        all_false = all(result == False for result, bank in result_container)
        if all_false:
            print("Both tasks returned False, retrying...")
            completion_event = threading.Event()
            result_container = []
            with ThreadPoolExecutor(max_workers=1) as executor:
                available_banks = [bank for bank in remaining_banks if is_bank_available(bank.__class__.__name__)]
                if len(available_banks) < 1:
                    return APIResponse.json_format({'result': False, 'message': 'Not enough banks available'})

                selected_banks = random.sample(available_banks, min(1, len(available_banks)))
                futures = [executor.submit(task_wrapper, bank, account_number, bank_name, account_name) for bank in selected_banks]
                start_time = time.time()
                
                try:
                    completion_event.wait(timeout=7)
                    try:
                        if result_container:
                            for result, bank in result_container:
                                print(f'result_{bank.__class__.__name__}', result)
                                if result is True:
                                    return APIResponse.json_format({'result': result, 'bank': bank.__class__.__name__})
                                elif isinstance(result, str):
                                    return APIResponse.json_format({'result': False, 'true_name': result.upper().replace(' ', ''), 'bank': bank.__class__.__name__})
                                elif result == False or result is None:
                                    return APIResponse.json_format({'result': False, 'message': 'bank system error'})
                    except Exception as e:
                        response = str(e)
                        print(traceback.format_exc())
                        print(sys.exc_info()[2])
                        return APIResponse.json_format(response)
                except TimeoutError:
                    return APIResponse.json_format({'result': False, 'message': 'timeout'})
        else:
            return APIResponse.json_format({'result': False, 'message': 'error'})

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=3000)
