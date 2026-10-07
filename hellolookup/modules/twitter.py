import re
import tls_client

def GetTwitter(email: str,  proxy: str, user_agent: str = None) -> list:
    session = tls_client.Session(
        client_identifier="chrome_112",
        random_tls_extension_order=True
    )

    session.proxies = {
        'https': proxy,
        'http': proxy,
    }

    if not user_agent:
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/118.0.5993.90 Safari/537.36"
        )

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en,en-US;q=0.5',
        'Cache-Control': 'max-age=0',
        'Referer': 'https://www.google.com/',
        'Sec-Ch-Ua': '"Chromium";v="118", "Brave";v="118", "Not=A?Brand";v="99"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-User': '?1',
        'Sec-Gpc': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': user_agent
    }

    authenticity_token = None

    for _ in range(3):
        try:
            response = session.get(
                'https://x.com/account/begin_password_reset',
                headers=headers
            )

            authenticity_token = re.search(
                r'name="authenticity_token" value="([^"]+)"',
                response.text
            ).group(1)
            break

        except Exception:
            continue

    if not authenticity_token:
        return None

    headers['Referer'] = 'https://x.com/account/begin_password_reset'

    for _ in range(3):
        try:
            r2 = session.post(
                'https://x.com/account/begin_password_reset',
                headers=headers,
                data={
                    'authenticity_token': authenticity_token,
                    'account_identifier': email
                },
                allow_redirects=True
            )

            text = r2.text

            if "Enter your phone number to continue" in text:
                return None

            if "We couldn't find your account with that information" in text:
                return None

            if "You've exceeded the number of attempts" in text:
                return None

            if "Send an email to" in text and "Text a code to the phone number" not in text:
                return None

            if "Text a code to the phone number" in text:
                try:
                    phone_hint = re.search(
                        r'Text a code to the phone number ending in <strong dir="ltr">([^<]+)</strong>',
                        text
                    ).group(1)

                    return [phone_hint]
                except Exception:
                    return None

        except Exception:
            continue

    return None