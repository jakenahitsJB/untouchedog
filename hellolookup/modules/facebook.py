import re
import tls_client
from typing import Optional

def GetFacebook(email: str, proxy: str=None):
     try:
          session = tls_client.Session(
               client_identifier="safari_ios_16_0",
               random_tls_extension_order=True
          )

          if proxy:
               session.proxies = {
                    'http': proxy,
                    'https': proxy
               }

          res0 = session.get(
               "https://www.facebook.com/login/identify/?ctx=recover&ars=facebook_login&next=https://www.facebook.com/&from_login_screen=0",
               headers={
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; Redmi 7 MIUI/V11.0.6.0.PFLMIXM) [FBAN/MessengerLite;FBAV/115.0.0.2.114;FBPN/com.facebook.mlite;FBLC/ar_EG;FBBV/257412622;FBCR/Orange - STAY SAFE;FBMF/Xiaomi;FBBD/xiaomi;FBDV/Redmi 7;FBSV/9;FBCA/arm64-v8a:null;FBDM/{density=2.0,width=720,height=1369};]'
               },
               allow_redirects=True
          )

          datr = re.search(
               r'"_js_datr","([^"]+)",',
               res0.text
          ).group(1)

          jazoest = re.search(
               r'name="jazoest" value="([^"]+)"',
               res0.text
          ).group(1)

          lsd = re.search(
               r'name="lsd" value="([^"]+)"',
               res0.text
          ).group(1)

          __hs = re.search(
               r'"haste_session":"([^"]+)"',
               res0.text
          ).group(1)

          __ccg = re.search(
               r'"connectionClass":"([^"]+)"',
               res0.text
          ).group(1)

          __rev = re.search(
               r'"rev":([^,]+),',
               res0.text
          ).group(1)

          __hsi = re.search(
               r'"hsi":"([^"]+)"',
               res0.text
          ).group(1)

          __spin_r = re.search(
               r'"__spin_r":([^,]+),',
               res0.text
          ).group(1)

          __spin_b = re.search(
               r'"__spin_b":"([^"]+)"',
               res0.text
          ).group(1)

          __spin_t = re.search(
               r'"__spin_t":([^,]+),',
               res0.text
          ).group(1)

          res1 = session.post(
               'https://www.facebook.com/ajax/login/help/identify.php?next=https://www.facebook.com/&ctx=recover',
               headers={
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Connection': 'keep-alive',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Cookie': f'datr={datr}; wd=1600x900',
                    'Host': 'www.facebook.com',
                    'Origin': 'https://www.facebook.com',
                    'Referer': 'https://www.facebook.com/login/identify/?ctx=recover&ars=facebook_login&next=https://www.facebook.com/&from_login_screen=0',
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                    'X-ASBD-ID': '129477',
                    'X-FB-LSD': lsd
               },
               data={
                    'jazoest': jazoest,
                    'lsd': lsd,
                    'email': email,
                    'did_submit': '1',
                    '__user': '0',
                    '__a': '1',
                    '__req': '4',
                    '__hs': __hs,
                    'dpr': '1',
                    '__ccg': __ccg,
                    '__rev': __rev,
                    '__s': 'hnxfuh:qxjmwx:w2kqh2',
                    '__hsi': __hsi,
                    '__dyn': '7xeUmwkHg7ebwKBAg5S1Dxu13wqovzEdEc8uxa0CEbo1nEhwem0nCq1ewcG0KEswaq0yE7i0n24o5-0ha2l0Fwqo31w9O0H8jwae4Ueo2swwwNwmE2ewnE2Lx-0lK3qazo11E2ZwrU6C0hq1Iw7zwtU5K',
                    '__csr': '',
                    '__spin_r': __spin_r,
                    '__spin_b': __spin_b,
                    '__spin_t': __spin_t
               },
               allow_redirects=True
          )

          sfiu = res1.cookies.get(
               'sfiu'
          )

          redir_url_match = re.search(
               r'"([^"]+)",true,false]]]}',
               res1.text
          )

          if not redir_url_match:
               return None

          redir_link = (
               'https://www.facebook.com/recover/initiate/?is_from_lara_screen=1&next=https%3A%2F%2Fwww.facebook.com%2F'
          )

          recov = session.get(
               redir_link,
               headers={
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                    'Accept': '*/*',
                    'Referer': 'https://www.facebook.com/login/identify/?ctx=recover&ars=facebook_login&next=https%3A%2F%2Fwww.facebook.com%2F&from_login_screen=0',
                    'Cookie': f'datr={datr}; sfiu={sfiu}',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.9',
               },
               cookies={
                    'datr': datr,
                    'sfiu': sfiu
               },
               allow_redirects=True
          )

          phone_hints = re.findall(
               r'\+[*]+\d{2}',
               recov.text
          )

          unique_hints = list(set(
               phone_hints
          ))

          return unique_hints[0] if unique_hints else None

     except Exception as e:
          return None