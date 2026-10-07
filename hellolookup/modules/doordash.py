import tls_client 
from typing import Union

def GetDoordash(email: str, proxy: str) -> Union[str, None]:
    for attempt in range(3):
        try:
            session = tls_client.Session(
                client_identifier="chrome_112",
                random_tls_extension_order=True
            )

            session.proxies = {
                'http': proxy,
                'https': proxy
            }

            cookies = {
                'ddweb_session_id': '177dd910-828f-4cd9-822a-05f2c7757326:1:0199e944-f9cb-7888-a948-30a68eabfafd',
                'dd_delivery_correlation_id': 'ef5dc36d-17f1-4578-9f85-fac26ef04133',
                'dd_device_id': 'dx_43c827f1e1394b3a919023352be9db7e',
                'dd_device_session_id': 'a8a34c7c-dfd8-4a13-b753-a68af52420f4',
                'dd_session_id': 'sx_253bdb07349b41cb81466e20a29b0c8f',
                'dd_market_id': '-1',
                'dd_signature_agent': 'notAgent',
                'XSRF-TOKEN': 'c63bdc2d-0da5-4972-bbc1-3f04f4259149',
                'dd-identity-session-id': '515463e9-1410-4a97-83e8-a117b013ee4c',
                '__cf_bm': 'cDn8xhkN5eoajDolJx9X5zI8voVspF8QI9tYk0EpRF4-1760555301-1.0.1.1-VnqAJZ4sg.dVq7AcmTOVmWj4OoQ_ciT026sO1HMKdzAch6.I2zURD7U4fpT2He_8FZikCeBZ1vk3.QcF5YpXBGu.5nQ.TxH0xSkAZxSRnsY',
                '_cfuvid': 'dFadljFf5V3M7yyaAgsRD4O65y3NdcQQWErTKd5FVH8-1760555301317-0.0.1.1-604800000',
                'cookie_tracking_enabled': '4-false',
                'dd_language': 'en-US',
                'authState': 'e472cb6d-59a9-425a-a95a-5885da7590f4',
            }

            headers = {
                'accept': 'application/json',
                'accept-language': 'en-US',
                'access-control-allow-origin': '*',
                'cache-control': 'no-cache',
                'content-type': 'application/json',
                'origin': 'https://identity.doordash.com',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'sec-ch-ua': '"Brave";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'sec-gpc': '1',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
                'x-xsrf-token': 'c63bdc2d-0da5-4972-bbc1-3f04f4259149',
            }

            json_data = {
                'client_id': '1666519390426295040',
                'clientId': '1666519390426295040',
                'layout': 'identity_web_iframe',
                'deviceId': None,
                'redirectUri': 'https://www.doordash.com/post-login/',
                'responseType': 'code',
                'scope': '*',
                'state': '/home||0654f526-9378-492e-a7bb-c169c2eebb4b',
                'username': email,
            }

            response = session.post(
                'https://identity.doordash.com/v2/auth/guided/email',
                cookies=cookies,
                headers=headers,
                json=json_data
            )

            if response.status_code == 200:
                data = response.json()

                if data['userInfo']['maskedPhoneNumber'] != None:
                    hint = data['userInfo']['maskedPhoneNumber']
                    return hint

                else:
                    return None

            else:
                if attempt == 2:  
                    return None
                continue

        except Exception:
            if attempt == 2:
                return None
            continue

    return None