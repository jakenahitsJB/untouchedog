import json
import tls_client

def GetMicrosoft(email: str, proxy: str=None):

    hints = []
    two_fa = None
    email_hints = []

    email_type = email.split("@")[1].split(".")[0]

    session = None
    for _ in range(3):
        try:
            session = tls_client.Session(
                client_identifier="chrome_112",
                random_tls_extension_order=True
            )

            if proxy:
                session.proxies = {
                    'http': proxy,
                    'https': proxy
                }

            response = session.get(
                f"https://account.live.com/ResetPassword.aspx?mn={email}",
                headers={
                    'authority': 'account.live.com',
                    'accept': (
                        'text/html,application/xhtml+xml,application/xml;q=0.9,'
                        'image/avif,image/webp,image/apng,*/*;q=0.8,'
                        'application/signed-exchange;v=b3;q=0.7'
                    ),
                    'accept-language': 'en-GB,en;q=0.9',
                    'cache-control': 'no-cache',
                    'pragma': 'no-cache',
                    'sec-ch-ua': (
                        '"Not.A/Brand";v="8", "Chromium";v="114", "Opera GX";v="100"'
                    ),
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'document',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-site': 'none',
                    'sec-fetch-user': '?1',
                    'upgrade-insecure-requests': '1',
                    'user-agent': (
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/131.0.0.0 Safari/537.36'
                    ),
                }
            )
            break
        except Exception:
            continue
    else:
        return None, None, None

    try:
        email_data = json.loads(
            response.text.split(
                'oProofList":'
            )[1].split("],")[0] + "]"
        )

        two_fa = False

    except Exception:
        return None, None, None

    for item in email_data:

        item_type = item.get("type")

        name = item.get("name")

        if item_type == "Email":
            email_hints.append(name)

        elif item_type == "Sms":
            hints.append(name)

        elif item_type == "SQSA":
            hints.append(f"Security question: {name}")

        elif item_type == "TOTPAuthenticatorV2":
            two_fa = True

    return hints, two_fa, email_hints