import json
import csv
import os
import requests
from bs4 import BeautifulSoup   # pip install beautifulsoup4
from time import sleep
from random import randint
import re as re


class MeterReader():
    ###### START OF SCRIPT ###### 
    def get_login_creds(self):
        login_creds = {}
        meter_mprn = os.environ.get("METER_MPRN")
        esb_username = os.environ.get("ESB_USER")
        esb_password = os.environ.get("ESB_PASSWORD")
        login_creds["meter_mprn"] = meter_mprn
        login_creds["esb_username"] = esb_username
        login_creds["esb_password"] = esb_password
        return login_creds

    def get_energy_consumption(self):
        debug_mode=False
        if debug_mode:print("##### REQUEST 1 -- GET [https://myaccount.esbnetworks.ie/] ######")
        login_creds = self.get_login_creds()
        meter_mprn = login_creds["meter_mprn"]
        esb_user_name = login_creds["esb_username"]
        esb_password = login_creds["esb_password"]

        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
        })    

        try:
            request_1_response = session.get('https://myaccount.esbnetworks.ie/', allow_redirects=True, timeout= (10,5))     # timeout -- 10sec for connect and 5sec for response
        except requests.exceptions.Timeout:
            print("[FAILED] The request timed out, server is not responding. Try again later.")
            session.close()
            raise SystemExit(0)
        except requests.exceptions.RequestException as e:
            print("An error occurred:", e)
            session.close()
            raise SystemExit(0)

        result = re.findall(r"(?<=var SETTINGS = )\S*;", str(request_1_response.content))
        settings = json.loads(result[0][:-1])
        tester_soup = BeautifulSoup(request_1_response.content, 'html.parser')
        page_title = tester_soup.find("title")
        request_1_response_cookies = session.cookies.get_dict()
        x_csrf_token = settings['csrf']
        transId = settings['transId']

        if debug_mode:
            print("[!] Request #1 Page Title :: ", page_title.text)
            print("[!] Request #1 Status Code ::", request_1_response.status_code)
            print("[!] Request #1 Response Headers ::", request_1_response.headers)
            print("[!] Request #1 Cookies Captured ::", request_1_response_cookies)
            print("x_csrf_token ::", x_csrf_token)
            print("transId ::", transId)

        x_ms_cpim_sso = request_1_response_cookies.get('x-ms-cpim-sso:esbntwkscustportalprdb2c01.onmicrosoft.com_0')
        x_ms_cpim_csrf = request_1_response_cookies.get('x-ms-cpim-csrf')
        x_ms_cpim_trans = request_1_response_cookies.get('x-ms-cpim-trans')

        if debug_mode:
            print("##### creating x_ms_cpim cookies ######")
            print("x_ms_cpim_sso ::", request_1_response_cookies.get('x-ms-cpim-sso:esbntwkscustportalprdb2c01.onmicrosoft.com_0'))
            print("x_ms_cpim_csrf ::", request_1_response_cookies.get('x-ms-cpim-csrf'))
            print("x_ms_cpim_trans ::", request_1_response_cookies.get('x-ms-cpim-trans'))
            print("##### REQUEST 2 -- POST [SelfAsserted] ######")

        sleeping_delay= randint(10,20)
        if debug_mode:print('random sleep for',sleeping_delay,'seconds...')
        sleep(sleeping_delay)

        request_2_response = session.post(
            'https://login.esbnetworks.ie/esbntwkscustportalprdb2c01.onmicrosoft.com/B2C_1A_signup_signin/SelfAsserted?tx=' + transId + '&p=B2C_1A_signup_signin', 
            data={
            'signInName': esb_user_name, 
            'password': esb_password, 
            'request_type': 'RESPONSE'
            },
            headers={
            'x-csrf-token': x_csrf_token,
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://login.esbnetworks.ie',
            'Dnt': '1',
            'Sec-Gpc': '1',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Priority': 'u=0',
            'Te': 'trailers',
            },
            cookies={
                'x-ms-cpim-csrf':request_1_response_cookies.get('x-ms-cpim-csrf'),
            #    'x-ms-cpim-sso:esbntwkscustportalprdb2c01.onmicrosoft.com_0':request_1_response_cookies.get('x-ms-cpim-sso:esbntwkscustportalprdb2c01.onmicrosoft.com_0'),
                'x-ms-cpim-trans':request_1_response_cookies.get('x-ms-cpim-trans'),
            },
            allow_redirects=False)

        request_2_response_cookies = session.cookies.get_dict()
        if debug_mode:
            print("[!] Request #2 Status Code ::", request_2_response.status_code)
            print("[!] Request #2 Response Headers ::", request_2_response.headers)
            print("[!] Request #2 Cookies Captured :: ", request_2_response_cookies)
            print("[!] Request #2 text :: ", request_2_response.text)
            print("##### REQUEST 3 -- GET [API CombinedSigninAndSignup] ######")

        print(f"RECEIVED STATUS CODE OF {request_2_response.status_code} from login")
        request_3_response = session.get(
            'https://login.esbnetworks.ie/esbntwkscustportalprdb2c01.onmicrosoft.com/B2C_1A_signup_signin/api/CombinedSigninAndSignup/confirmed',
            params={
            'rememberMe': False,
            'csrf_token': x_csrf_token,
            'tx': transId,
            'p': 'B2C_1A_signup_signin',
            },
            headers={
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Dnt": "1",
            "Sec-Gpc": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=0, i",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Te": "trailers",
            },
            cookies={
                "x-ms-cpim-csrf":request_2_response_cookies.get("x-ms-cpim-csrf"),
            #    "x-ms-cpim-sso:esbntwkscustportalprdb2c01.onmicrosoft.com_0": request_2_response_cookies.get("x-ms-cpim-sso:esbntwkscustportalprdb2c01.onmicrosoft.com_0"),
                'x-ms-cpim-trans':request_2_response_cookies.get("x-ms-cpim-trans"),
            },
        )
        print(f"RECEIVED STATUS CODE OF: %S from login", request_3_response.status_code)
        tester_soup = BeautifulSoup(request_3_response.content, 'html.parser')
        page_title = tester_soup.find("title")
        request_3_response_cookies = session.cookies.get_dict()

        if debug_mode:
            print("[!] Page Title :: ", page_title.text)      # will print "Loading..." if failed
            print("[!] Request #3 Status Code ::", request_3_response.status_code)
            print("[!] Request #3 Response Headers ::", request_3_response.headers)
            print("[!] Request #3 Cookies Captured :: ", request_3_response_cookies)
            print("[!] Request #3 Content :: ", request_3_response.content)
            print("##### TEST IF SUCCESS ######")

        request_3_response_head_test = request_3_response.text[0:21]
        if (request_3_response_head_test == "<!DOCTYPE html PUBLIC"):
            page_title = tester_soup.find("title")
            if debug_mode:
                print("[PASS] SUCCESS -- ALL OK [PASS]")
                print("[!] Page Title :: ", page_title.text)
        else: 
            session.close()
            try:
                tester_soup_msg = tester_soup.find('h1')
                tester_soup_msg = tester_soup_msg.text
                print("[FAILED] Page response ::", tester_soup_msg)
            except: tester_soup_msg = ""
            try:
                no_js_msg = tester_soup.find('div', id='no_js')
                no_js_msg = no_js_msg.text
                print("[FAILED] Page response :: ", no_js_msg)
            except: no_js_msg = ""
            try:
                no_cookie_msg = tester_soup.find('div', id='no_cookie')
                no_cookie_msg = no_cookie_msg.text
                print("[FAILED] Page response :: ", no_cookie_msg)
            except: no_cookie_msg = ""
            print("[Script Message] Unable to reach login page -- too many retries (max=2 in 24h) or prior sessions was not closed properly. Please try again after midnight.")
            raise SystemExit(0)
            
        if debug_mode:print("##### REQUEST - SOUP - state & client_info & code ######")
        soup = BeautifulSoup(request_3_response.content, 'html.parser')
        try:
            form = soup.find('form', {'id': 'auto'})
            login_url_ = form['action']
            state_ = form.find('input', {'name': 'state'})['value']
            
            client_info_ = form.find('input', {'name': 'client_info'})['value']
            code_ = form.find('input', {'name': 'code'})['value']
            if debug_mode:
                print("login url ::" ,login_url_)
                print("state_ ::", state_)
                print("client_info_ ::", client_info_)
                print("code_ ::", code_)
        except Exception as e:
            print(f"Exception occurred while parsing form: {e}")
        
        if debug_mode:print("##### REQUEST 4 -- POST [signin-oidc] ######")
        sleeping_delay= randint(2,5)
        if debug_mode:print('random sleep for',sleeping_delay,'seconds...')
        sleep(sleeping_delay)

        request_4_headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://login.esbnetworks.ie",
            "Dnt": "1",
            "Sec-Gpc": "1",
            "Referer": "https://login.esbnetworks.ie/",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-site",
            "Priority": "u=0, i",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Te": "trailers",
        }

        request_4_response = session.post(
                login_url_,
                allow_redirects=False,
                data={
                'state': state_,
                'client_info': client_info_,
                'code': code_,
                },
                headers=request_4_headers,
            )

        request_4_response_cookies = session.cookies.get_dict()
        if debug_mode:
            print("[!] Request #4 Status Code ::", request_4_response.status_code)  # expect 302
            print("[!] Request #4 Response Headers ::", request_4_response.headers)
            print("[!] Request #4 Cookies Captured ::", request_4_response_cookies)
            print("[!] Request #4 Content ::", request_4_response.content)
            print("##### REQUEST 5 -- GET [https://myaccount.esbnetworks.ie] ######")

        request_5_url = "https://myaccount.esbnetworks.ie"
        request_5_headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://login.esbnetworks.ie/",
            "Dnt": "1",
            "Sec-Gpc": "1",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-site",
            "Priority": "u=0, i",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Te": "trailers",
        }
        request_5_cookies = {
            "ARRAffinity":request_4_response_cookies.get("ARRAffinity"),
            "ARRAffinitySameSite":request_4_response_cookies.get("ARRAffinitySameSite"),
        }

        request_5_response = session.get(request_5_url,headers=request_5_headers,cookies=request_5_cookies)
        request_5_response_cookies = session.cookies.get_dict()
        if not request_5_response.status_code in (200, 202):
            print(f"[ERROR] Request #5 failed with status {request_5_response.status_code}")
            print(request_5_response.text)
            session.close()
            return None
        if debug_mode:
            print("[!] Request #5 Status Code ::", request_5_response.status_code)
            print("[!] Request #5 Response Headers ::", request_5_response.headers)
            print("[!] Request #5 Cookies Captured ::", request_5_response_cookies)
            # print("[!] Request #5 Content ::", request_5_response.content)
            print("##### Welcome page block #####")
            
        user_welcome_soup = BeautifulSoup(request_5_response.text,'html.parser')
        welcome_page_title_ = user_welcome_soup.find('title')
        if debug_mode:print("[!] Page Title ::", welcome_page_title_.text)                   # it should print "Customer Portal"
        welcome_page_title_ = user_welcome_soup.find('h1', class_='esb-title-h1')
        if debug_mode:print("[!] Confirmed User Login ::", welcome_page_title_.text)    # It should print "Welcome, Name Surname"
        asp_net_core_cookie = request_5_response_cookies.get(".AspNetCore.Cookies")

        if debug_mode:print("##### REQUEST 6 -- GET [Api/HistoricConsumption] ######")
        sleeping_delay= randint(3,8)
        if debug_mode:print('random sleep for',sleeping_delay,'seconds...')
        sleep(sleeping_delay)
        request_6_url = "https://myaccount.esbnetworks.ie/Api/HistoricConsumption"
        request_6_cookies = {
            "ARRAffinity":request_4_response_cookies.get("ARRAffinity"),
            "ARRAffinitySameSite":request_4_response_cookies.get("ARRAffinitySameSite"),
            ".AspNetCore.Cookies":asp_net_core_cookie,
        }
        request_6_headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Dnt": "1",
            "Sec-Gpc": "1",
            "Referer": "https://myaccount.esbnetworks.ie/",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Priority": "u=0, i",
            "Te": "trailers",
        }

        request_6_response = session.get(request_6_url, headers=request_6_headers,cookies=request_6_cookies)
        request_6_response_cookies = session.cookies.get_dict()

        if not request_6_response.status_code in range(200, 202):
            print(f"[ERROR] Request #6 failed with status {request_6_response.status_code}")
            print(request_6_response.text)
            session.close()
            return None

        if debug_mode:
            print("[!] Request #6 Status Code ::", request_6_response.status_code)
            print("[!] Request #6 Response Headers ::", request_6_response.headers)
            print("[!] Request #6 Cookies Captured ::", request_6_response_cookies)
            print("##### My Energy Consumption - Customer Portal #####")

        try: 
            consumption_soup = BeautifulSoup(request_6_response.text,'html.parser')
            consumption_page_title_ = consumption_soup.find('title')
            welcome_page_title_ = consumption_soup.find('h1', class_='esb-title-h1')
        
            if consumption_page_title_ is None:
                print("[ERROR] Could not find <title> in request 6 response!")
                print("[DEBUG] Response snippet:", request_6_response.text[:500])
            else:
                print("[!] Page Title ::", consumption_page_title_.text)

            if welcome_page_title_ is None:
                print("[ERROR] Could not find <h1 class='esb-title-h1'> in request 6 response!")
                print("[DEBUG] Response snippet:", request_6_response.text[:500])
            else:
                print("[!] 'esb-title-h1' ::", welcome_page_title_.text)
        except Exception as e:
            print(f"[ERROR] Exception while parsing request 6 HTML: {e}")
            print("[DEBUG] Full response text:")
            print(request_6_response.text[:1000])
            return None
        
        if debug_mode:
            print("[!] Page Title ::", consumption_page_title_.text)    # it should print "My Energy Consumption - Customer Portal"
            print("[!] 'esb-title-h1' ::", welcome_page_title_.text)    # It should print "My Energy Consumption"
            print("##### REQUEST 7 -- GET [file download token] ######")
        sleeping_delay= randint(2,5)
        if debug_mode:print('random sleep for',sleeping_delay,'seconds...')
        sleep(sleeping_delay)

        request_7_url = "https://myaccount.esbnetworks.ie/af/t"
        request_7_headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "X-Returnurl": "https://myaccount.esbnetworks.ie/Api/HistoricConsumption",
            "Dnt": "1",
            "Sec-Gpc": "1",
            "Referer": "https://myaccount.esbnetworks.ie/Api/HistoricConsumption",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=0",
            "Te": "trailers",
        }
        request_7_cookies = {
            "ARRAffinity":request_4_response_cookies.get("ARRAffinity"),
            "ARRAffinitySameSite":request_4_response_cookies.get("ARRAffinitySameSite"),
        }
        request_7_response = session.get(request_7_url,headers=request_7_headers,cookies=request_7_cookies)
        request_7_response_cookies = session.cookies.get_dict()
        file_download_token = json.loads(request_7_response.text)["token"]
        if not request_7_response.status_code in range(200, 202):
            print(f"[ERROR] Request #7 failed with status {request_7_response.status_code}")
            print(request_7_response.text)
            session.close()
            return None
        
        if debug_mode:
            print("[!] Request #7 Status Code ::", request_7_response.status_code)
            print("[!] Request #7 Response Headers ::", request_7_response.headers)
            print("[!] Request #7 Cookies Captured ::", request_7_response_cookies)
            # print("[!] Request #7 Content ::", request_7_response.content)
            print("File download token :: ",file_download_token)
            print("##### REQUEST 8 -- GET [/DataHub/DownloadHdfPeriodic] ######")
        request_8_url = "https://myaccount.esbnetworks.ie/DataHub/DownloadHdfPeriodic"
        request_8_headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://myaccount.esbnetworks.ie/Api/HistoricConsumption",
            "Content-Type": "application/json",
            "X-Returnurl": "https://myaccount.esbnetworks.ie/Api/HistoricConsumption",
            "X-Xsrf-Token": file_download_token,
            "Origin": "https://myaccount.esbnetworks.ie",
            "Dnt": "1",
            "Sec-Gpc": "1",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=4",
            "Cache-Control": "max-age=0",
            "Te": "trailers",
        }
        payload_data = {
            "mprn": meter_mprn,
            "searchType": "day"  ### <<<< !!! THIS IS WHERE YOU SELECT WHICH FILE YOU WANT !!!
        }
        print(f"Calling {request_8_url} with payload: {payload_data}")
        request_8_response = session.post(request_8_url, headers=request_8_headers, json=payload_data)
        if not request_8_response.status_code in range (200, 202):
            print(f"[ERROR] Request #8 failed with status {request_8_response.status_code}")
            print(f"[ERROR] Request #8 failed with response headers {request_8_response.headers}")
            session.close()
            return None
        
        if debug_mode:
            print("[!] Request #8 Status Code ::", request_8_response.status_code)
            print("[!] Request #8 Response Headers ::", request_8_response.headers)
            print("[END] HTTP Requests completed. Closing session.")
        session.close()

        if debug_mode:print("#### Getting file attributes ####")
        file_size_ = request_8_response.headers.get("Content-Length")
        file_name_ = request_8_response.headers.get("Content-Disposition")
        file_name_ = file_name_.split(";")
        file_name_ = file_name_[1].split("=")
        file_name_ = file_name_[1]
        if debug_mode:
            print("[!] File size, bytes ::",file_size_)
            print("[!] Disposition ::",file_name_)     # it should print [attachment; filename=HDF_kW_mprn_date.csv; filename*=UTF-8''HDF_kW_mprn_date.csv]
            print("[!] File Name ::",file_name_)
            print("##### Checking/converting received CSV file/object #####")
        if (isinstance(request_8_response.content, bytes)):
            if debug_mode:print("[!] Object class is 'bytes', decoding to 'utf-8' and continuing...")
            csv_file = request_8_response.content.decode("utf-8")
        elif(isinstance(request_8_response.content, str)):
            if debug_mode:print("[!] Object class is 'string', continuing...")
            csv_file = request_8_response.content
        else:
            print("[FAIL] received object is neither 'bytes' nor 'string, stopping here, please check/validate [request_8_response.content]")
            raise SystemExit(0)
        if debug_mode:
            print("[!] CSV data sample ::")
            print(csv_file[0:500])
        try:
            if debug_mode:print("[!] Converting CSV to JSON...")
            if(csv_file[0:4] == "MPRN"):
                my_json = []
                csv_reader = csv.DictReader(csv_file.split('\n'))
                for row in csv_reader:
                    my_json.append(row)
                if debug_mode:print("[COMPLETED] JSON file created. Use [json_file] .")
            else:
                print("[FAIL] Something is wrong with CSV file header structure, cant convert to JSON. Expected [csv_file[0:4] == 'MPRN'] but failed.")
        except:
            print("[FAIL] Something is wrong with CSV file structure, cant convert to JSON, check/validate if [csv.DictReader(csv_file.split('\n'))] works.")
            raise SystemExit(0)
        return my_json