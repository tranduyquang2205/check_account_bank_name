from fastapi import FastAPI, HTTPException
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
import uvicorn
from pydantic import BaseModel
import random
import time
import configparser
from acb import ACB
from mbbank_biz import MBBANK
from seabank import SeaBank
from techcombank_biz import Techcombank
from vietabank import VietaBank
from vietinbank import VTB
from api_response import APIResponse
import sys
import traceback
import threading

# Read configuration from config file
config = configparser.ConfigParser()
config.read('config.ini')

def parse_proxy_list(proxy_list_str):
    if proxy_list_str.lower() in ['none', 'empty']:
        return None
    return proxy_list_str.split(',')
BANK_CLASSES = {
    'ACB': ACB,
    'MBBANK': MBBANK,
    'Techcombank': Techcombank,
    'VTB': VTB,
    'SeaBank': SeaBank,
    'VietaBank': VietaBank,
}
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

def check_bank(bank, account_number, bank_name, account_name):
    print(bank.__class__.__name__)
    return bank.check_bank_name(account_number, bank_name, account_name)


app = FastAPI()

class BankInfo(BaseModel):
    account_number: str
    bank_name: str
    account_name: str

@app.post('/check_bank_name', tags=["check_bank_name"])
def check_bank_name(input: BankInfo):
    # try:
        account_number = input.account_number
        bank_name = input.bank_name
        account_name = input.account_name

        completion_event = threading.Event()
        result_container = []
        def task_wrapper(bank, account_number, bank_name, account_name):
            try:
                result = check_bank(bank, account_number, bank_name, account_name)
                if not completion_event.is_set() and result is True or isinstance(result, str):
                    result_container.append((result, bank))
                    completion_event.set()
                elif not completion_event.is_set() and result is False:
                    result_container.append((result, bank))
            except Exception as e:
                print(f"Error processing bank {bank}: {e}")

        with ThreadPoolExecutor(max_workers=2) as executor:
            selected_banks = random.sample(banks, 2)
            futures = [executor.submit(task_wrapper, bank, account_number, bank_name, account_name) for bank in selected_banks]
            start_time = time.time()
            
            try:
                completion_event.wait(timeout=6)
                try:
                    if result_container:
                        for result, bank in result_container:
                            print(f'result_{bank.__class__.__name__}',result)
                            if result is True:
                                return APIResponse.json_format({'result': result, 'bank': bank.__class__.__name__})
                            elif isinstance(result, str):
                                return APIResponse.json_format({'result': False, 'true_name': result.upper().replace(' ', ''), 'bank': bank.__class__.__name__})
                            elif result == False or result is None:
                                    continue
                except Exception as e:
                    try:
                        remaining_banks = [bank for bank in banks if bank not in selected_banks]
                        futures = [executor.submit(task_wrapper, bank, account_number, bank_name, account_name) for bank in remaining_banks]
                        completion_event.wait(timeout=6)
                        try:
                            if result_container:
                                for result, bank in result_container:
                                    print(f'result_{bank.__class__.__name__}',result)
                                    if result is True:
                                        return APIResponse.json_format({'result': result, 'bank': bank.__class__.__name__})
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
                        return APIResponse.json_format({'result': False ,'message': 'timeout'})
            except TimeoutError:
            #     return APIResponse.json_format({'message': 'timeout'})

            # if time.time() - start_time >= 6:
                # Retry with another set of banks
                remaining_banks = [bank for bank in banks if bank not in selected_banks]
                futures = [executor.submit(task_wrapper, bank, account_number, bank_name, account_name) for bank in remaining_banks]

                try:
                    completion_event.wait(timeout=6)
                    try:
                        if result_container:
                            for result, bank in result_container:
                                print(f'result_{bank.__class__.__name__}',result)
                                if result is True:
                                    return APIResponse.json_format({'result': result, 'bank': bank.__class__.__name__})
                                elif isinstance(result, str):
                                    return APIResponse.json_format({'result': False, 'true_name': result.upper().replace(' ', ''), 'bank': bank.__class__.__name__})
                                elif result == False or result is None:
                                        continue
                    except Exception as e:
                        try:
                            selected_banks = random.sample(banks, 2)
                            futures = [executor.submit(task_wrapper, bank, account_number, bank_name, account_name) for bank in selected_banks]
                            completion_event.wait(timeout=6)
                            try:
                                if result_container:
                                    for result, bank in result_container:
                                        print(f'result_{bank.__class__.__name__}',result)
                                        if result is True:
                                            return APIResponse.json_format({'result': result, 'bank': bank.__class__.__name__})
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
                            return APIResponse.json_format({'result': False ,'message': 'timeout'})
                except TimeoutError:
                    return APIResponse.json_format({'result': False ,'message': 'timeout'})

            # return APIResponse.json_format({'result': False})
        all_false = all(result == False for result, bank in result_container)
        if all_false:
            print("Both tasks returned False, retrying...")
            with ThreadPoolExecutor(max_workers=2) as executor:
                selected_banks = random.sample(banks, 2)
                futures = [executor.submit(task_wrapper, bank, account_number, bank_name, account_name) for bank in selected_banks]
                start_time = time.time()
                
                try:
                    completion_event.wait(timeout=6)
                    try:
                        if result_container:
                            for result, bank in result_container:
                                print(f'result_{bank.__class__.__name__}',result)
                                if result is True:
                                    return APIResponse.json_format({'result': result, 'bank': bank.__class__.__name__})
                                elif isinstance(result, str):
                                    return APIResponse.json_format({'result': False, 'true_name': result.upper().replace(' ', ''), 'bank': bank.__class__.__name__})
                                elif result == False or result is None:
                                        continue
                    except Exception as e:
                        try:
                            remaining_banks = [bank for bank in banks if bank not in selected_banks]
                            futures = [executor.submit(task_wrapper, bank, account_number, bank_name, account_name) for bank in remaining_banks]
                            completion_event.wait(timeout=6)
                            try:
                                if result_container:
                                    for result, bank in result_container:
                                        print(f'result_{bank.__class__.__name__}',result)
                                        if result is True:
                                            return APIResponse.json_format({'result': result, 'bank': bank.__class__.__name__})
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
                            return APIResponse.json_format({'result': False ,'message': 'timeout'})
                except TimeoutError:
                #     return APIResponse.json_format({'message': 'timeout'})

                # if time.time() - start_time >= 6:
                    # Retry with another set of banks
                    remaining_banks = [bank for bank in banks if bank not in selected_banks]
                    futures = [executor.submit(task_wrapper, bank, account_number, bank_name, account_name) for bank in remaining_banks]

                    try:
                        completion_event.wait(timeout=6)
                        try:
                            if result_container:
                                for result, bank in result_container:
                                    print(f'result_{bank.__class__.__name__}',result)
                                    if result is True:
                                        return APIResponse.json_format({'result': result, 'bank': bank.__class__.__name__})
                                    elif isinstance(result, str):
                                        return APIResponse.json_format({'result': False, 'true_name': result.upper().replace(' ', ''), 'bank': bank.__class__.__name__})
                                    elif result == False or result is None:
                                            continue
                        except Exception as e:
                            try:
                                selected_banks = random.sample(banks, 2)
                                futures = [executor.submit(task_wrapper, bank, account_number, bank_name, account_name) for bank in selected_banks]
                                completion_event.wait(timeout=6)
                                try:
                                    if result_container:
                                        for result, bank in result_container:
                                            print(f'result_{bank.__class__.__name__}',result)
                                            if result is True:
                                                return APIResponse.json_format({'result': result, 'bank': bank.__class__.__name__})
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
                                return APIResponse.json_format({'result': False ,'message': 'timeout'})
                    except TimeoutError:
                        return APIResponse.json_format({'result': False ,'message': 'timeout'})
                return APIResponse.json_format({'result': False})
        else:
            raise APIResponse.json_format({'result': False ,'message': 'error'})
    # except Exception as e:
    #     response = str(e)
    #     print(traceback.format_exc())
    #     print(sys.exc_info()[2])
    #     return APIResponse.json_format(response)

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=3000)


    # account_number = "024042205"
    # bank_name = "MBBank"
    # account_name = "tran duy quang"

    # with ThreadPoolExecutor(max_workers=2) as executor:
    #     while True:
    #         selected_banks = random.sample(banks, 2)
    #         futures = [executor.submit(check_bank, bank, account_number, bank_name, account_name) for bank in selected_banks]
    #         start_time = time.time()

    #         for future in as_completed(futures, timeout=5):
    #             try:
    #                 result = future.result()
    #                 if result:
    #                     print({'result': True, 'bank': str(selected_banks[futures.index(future)].__class__.__name__)})
    #                     break
    #             except Exception as e:
    #                 continue

    #         if time.time() - start_time >= 5:
    #             continue

    #         print(({'result': False}))
    #         break