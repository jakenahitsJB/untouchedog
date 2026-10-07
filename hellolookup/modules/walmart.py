import tls_client

def FilterCookies(cookie_jar):
    akavpau_p2 = None
    ak_bmsc = None

    for cookie in cookie_jar:
        if cookie.name == 'akavpau_p2':
            akavpau_p2 = cookie.value

        elif cookie.name == 'ak_bmsc':
            ak_bmsc = cookie.value

    return akavpau_p2, ak_bmsc


def GetWalmart(email: str, proxy: str):
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

            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'accept-language': 'en-US,en;q=0.5',
                'cache-control': 'no-cache',
                'pragma': 'no-cache',
                'priority': 'u=0, i',
                'sec-ch-ua': '"Brave";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'sec-gpc': '1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            }

            get_cookies_req = session.get(
                'https://www.walmart.com/',
                headers=headers
            )

            if get_cookies_req.status_code == 200:
                first_req_cookies = get_cookies_req.cookies

                akavpau_p2, ak_bmsc = FilterCookies(
                    first_req_cookies
                )

                cookies = {
                    'sod': 'torbit1760592882',
                    'vtc': 'UNe36WPUzHuYjFjwvTjzZ4',
                    'io_id': 'd7f6325d-8410-4b94-98c5-0e6c75445dbd',
                    'ACID': '49b96235-3d26-4922-936a-f79d4479da88',
                    'hasACID': 'true',
                    'userAppVersion': 'usweb-1.227.0-a36e74bb2d65fd10b493905d55ea8c39ce04ac93-0131858r',
                    'abqme': 'true',
                    '_pxhd': '765da8b641a64e668fe3cea08cbf2e02f0e6526a6b8936b855820c4fd2a5bf1a:d54cf25b-aa51-11f0-8605-6113afa0b708',
                    'AID': 'wmlspartner=0:reflectorid=0000000000000000000000:lastupd=1760592896170',
                    'assortmentStoreId': '3081',
                    'hasLocData': '1',
                    'locGuestData': 'eyJpbnRlbnQiOiJTSElQUElORyIsImlzRXhwbGljaXQiOmZhbHNlLCJzdG9yZUludGVudCI6IlBJQ0tVUCIsIm1lcmdlRmxhZyI6ZmFsc2UsImlzRGVmYXVsdGVkIjp0cnVlLCJwaWNrdXAiOnsibm9kZUlkIjoiMzA4MSIsInRpbWVzdGFtcCI6MTc2MDU5MjkzODczNywic2VsZWN0aW9uVHlwZSI6IkRFRkFVTFRFRCJ9LCJzaGlwcGluZ0FkZHJlc3MiOnsidGltZXN0YW1wIjoxNzYwNTkyOTM4NzM3LCJ0eXBlIjoicGFydGlhbC1sb2NhdGlvbiIsImdpZnRBZGRyZXNzIjpmYWxzZSwicG9zdGFsQ29kZSI6Ijk1ODI5IiwiZGVsaXZlcnlTdG9yZUxpc3QiOlt7Im5vZGVJZCI6IjMwODEiLCJ0eXBlIjoiREVMSVZFUlkiLCJ0aW1lc3RhbXAiOjE3NjA1OTI5Mzg3MzUsImRlbGl2ZXJ5VGllciI6bnVsbCwic2VsZWN0aW9uVHlwZSI6IkRFRkFVTFRFRCIsInNlbGVjdGlvblNvdXJjZSI6bnVsbH1dLCJjaXR5IjoiU2FjcmFtZW50byIsInN0YXRlIjoiQ0EifSwicG9zdGFsQ29kZSI6eyJ0aW1lc3RhbXAiOjE3NjA1OTI5Mzg3MzcsImJhc2UiOiI5NTgyOSJ9LCJtcCI6W10sIm1wRGVsU3RvcmVDb3VudCI6MCwic2hvd0xvY2FsRXhwZXJpZW5jZSI6ZmFsc2UsInNob3dMTVBFbnRyeVBvaW50IjpmYWxzZSwibXBVbmlxdWVTZWxsZXJDb3VudCI6MCwidmFsaWRhdGVLZXkiOiJwcm9kOnYyOjQ5Yjk2MjM1LTNkMjYtNDkyMi05MzZhLWY3OWQ0NDc5ZGE4OCJ9',
                    'bm_mi': '09620CFA6D719A64BF48B38919EFB811~YAAQww0uF38Z1t2ZAQAAyUeE6x2AfmsmtgqH8+HVThrQEbEPODBEiarQE7QELNqgVxg5KLSrsP8W2ZWsJMTSNVcpQJ1rndkRJIUYQ9s0iDM8cbBk6ZQ68CXC1MXUiC4Lp1twAoi/z6ONDcLm9oTnWUOO2wPzQRjSEtoY0eWdmZEdYgsTTswDLgEqV26RN8C2cUI1GQ4lx4zvWmEWeUJQhjkVrlFd1jMucuyR0r+wdjreNaJ+JtCqHxOiTX4hM5/dFV3wCzVCul9cqvCeF48L6dJDCtqA2sP3neFb6H0b1ZmBI611ConsXB+IjV8Rs1Gcc/rgRuaQ1lhza4k=~1',
                    'bm_sv': 'B8EED6588E1B8121F71D89D74AA57F4B~YAAQww0uF2Ua1t2ZAQAAEmOE6x0iam7XsZnfrLVOivUsSLlPJO7/6x3pG+CA3DAReMOIvRT7hQeKnP0ZQhBOLhbR2U6JJ4BFYHUjM85MfguajzGwWsTBuST89LS3WBG8P38uwttO61BmvuPLjw6nlsfpM4TgqcmqW6PPGmM00WzMbI2pSOJ4AWyEIQTa5q4QnYLqlm3L/JGC/cIdH8bF8ip482P3ddadDlDUsFj0L7IgEZFq9s2SEDPT7OqWYZKK0wo=~1',
                    'ak_bmsc': ak_bmsc,
                    'xpth': 'x-o-mart%2BB2C~x-o-mverified%2Bfalse',
                    'xpa': '-hwLU|-kyYS|08AdI|1AWnT|1DB8T|1NNjM|4mZde|5cN6c|6NdNU|74ap0|893dT|Dx-cj|FrVMT|HkEMg|In9ru|NFxyq|NToGZ|Oi5D4|PIAR-|QPToB|QTp9u|TCS94|X9ur9|Zg-hl|_H77Z|ajPmy|c-vBg|dsCtt|jM1ax|o0JjB|pQ-wz|rH8ha|rOzL6|uwH_b|ymSlh|zPPmU|zWyXC',
                    'exp-ck': '-hwLU11AWnT21DB8T44mZde15cN6c16NdNU174ap01893dT1FrVMT1HkEMg3In9ru1NFxyq1NToGZ2QPToB1TCS941Zg-hl3c-vBg1rH8ha2rOzL61uwH_b2zPPmU1',
                    'bstc': 'aFpYojdGK3dvuUu2LPHKZM',
                    'xpm': '1%2B1760597195%2BUNe36WPUzHuYjFjwvTjzZ4~%2B0',
                    'xptc': 'assortmentStoreId%2B3081~_m%2B9',
                    'xptwg': '1316977262:BB2B9047E0A3D0:1C899BF:E8098F77:65142E63:6BA3CEF9:',
                    '_intlbu': 'false',
                    '_m': '9',
                    '_shcc': 'US',
                    'locDataV3': 'eyJpc0RlZmF1bHRlZCI6dHJ1ZSwiaXNFeHBsaWNpdCI6ZmFsc2UsImludGVudCI6IlNISVBQSU5HIiwicGlja3VwIjpbeyJub2RlSWQiOiIzMDgxIiwiZGlzcGxheU5hbWUiOiJTYWNyYW1lbnRvIFN1cGVyY2VudGVyIiwiYWRkcmVzcyI6eyJwb3N0YWxDb2RlIjoiOTU4MjkiLCJhZGRyZXNzTGluZTEiOiI4OTE1IEdFUkJFUiBST0FEIiwiY2l0eSI6IlNhY3JhbWVudG8iLCJzdGF0ZSI6IkNBIiwiY291bnRyeSI6IlVTIn0sImdlb1BvaW50Ijp7ImxhdGl0dWRlIjozOC40ODI2NzcsImxvbmdpdHVkZSI6LTEyMS4zNjkwMjZ9LCJzY2hlZHVsZWRFbmFibGVkIjp0cnVlLCJ1blNjaGVkdWxlZEVuYWJsZWQiOnRydWUsImFsbG93ZWRXSUNBZ2VuY2llcyI6WyJDQSJdLCJzdXBwb3J0ZWRBY2Nlc3NUeXBlcyI6WyJQSUNLVVBfU1BFQ0lBTF9FVkVOVCIsIlBJQ0tVUF9JTlNUT1JFIiwiUElDS1VQX0NVUkJTSURFIl0sInRpbWVab25lIjoiQW1lcmljYS9Mb3NfQW5nZWxlcyIsInN0b3JlQnJhbmRGb3JtYXQiOiJXYWxtYXJ0IFN1cGVyY2VudGVyIiwic2VsZWN0aW9uVHlwZSI6IkRFRkFVTFRFRCJ9XSwic2hpcHBpbmdBZGRyZXNzIjp7ImxhdGl0dWRlIjozOC40ODI2NzcsImxvbmdpdHVkZSI6LTEyMS4zNjkwMjYsInBvc3RhbENvZGUiOiI5NTgyOSIsImNpdHkiOiJTYWNyYW1lbnRvIiwic3RhdGUiOiJDQSIsImNvdW50cnlDb2RlIjoiVVMiLCJsb2NhdGlvbkFjY3VyYWN5IjoibG93IiwiZ2lmdEFkZHJlc3MiOmZhbHNlLCJhbGxvd2VkV0lDQWdlbmNpZXMiOlsiQ0EiXX0sImFzc29ydG1lbnQiOnsibm9kZUlkIjoiMzA4MSIsImRpc3BsYXlOYW1lIjoiU2FjcmFtZW50byBTdXBlcmNlbnRlciIsImludGVudCI6IlBJQ0tVUCJ9LCJpbnN0b3JlIjpmYWxzZSwiZGVsaXZlcnkiOnsibm9kZUlkIjoiMzA4MSIsImRpc3BsYXlOYW1lIjoiU2FjcmFtZW50byBTdXBlcmNlbnRlciIsImFkZHJlc3MiOnsicG9zdGFsQ29kZSI6Ijk1ODI5IiwiYWRkcmVzc0xpbmUxIjoiODkxNSBHRVJCRVIgUk9BRCIsImNpdHkiOiJTYWNyYW1lbnRvIiwic3RhdGUiOiJDQSIsImNvdW50cnkiOiJVUyJ9LCJnZW9Qb2ludCI6eyJsYXRpdHVkZSI6MzguNDgyNjc3LCJsb25naXR1ZGUiOi0xMjEuMzY5MDI2fSwic2NoZWR1bGVkRW5hYmxlZCI6ZmFsc2UsInVuU2NoZWR1bGVkRW5hYmxlZCI6ZmFsc2UsImFjY2Vzc1BvaW50cyI6W3siYWNjZXNzVHlwZSI6IkRFTElWRVJZX0FERFJFU1MifV0sImlzRXhwcmVzc0RlbGl2ZXJ5T25seSI6ZmFsc2UsImFsbG93ZWRXSUNBZ2VuY2llcyI6WyJDQSJdLCJzdXBwb3J0ZWRBY2Nlc3NUeXBlcyI6WyJERUxJVkVSWV9BRERSRVNTIl0sInRpbWVab25lIjoiQW1lcmljYS9Mb3NfQW5nZWxlcyIsInN0b3JlQnJhbmRGb3JtYXQiOiJXYWxtYXJ0IFN1cGVyY2VudGVyIiwic2VsZWN0aW9uVHlwZSI6IkRFRkFVTFRFRCJ9LCJpc2dlb0ludGxVc2VyIjpmYWxzZSwibXBEZWxTdG9yZUNvdW50IjowLCJyZWZyZXNoQXQiOjE3NjA2MTQ1Mzg3NDEsInZhbGlkYXRlS2V5IjoicHJvZDp2Mjo0OWI5NjIzNS0zZDI2LTQ5MjItOTM2YS1mNzlkNDQ3OWRhODgifQ==',
                    'xptwj': 'uz:0058d1904bb9abbb0b21:6H6dG1PF440XJShkwE/wFuYlIPqwqkNe1HF9btrz4MDcDmjjF4WIieUES/7cQUXoaFn42o4RfRD7tg9yw9acMrrWoEUNdgdTH+PbLVwutboD+NPJ0TgjKFARGpCySibyb8kMjbjf0qxTvWCefMPJ1CCpPaNzoEwClFIV5S+NJeU3uXNPd0LfvPg=',
                    'TS01a90220': '01b324378698dc69ec9eb82eeec19573bc32df29a7a516a458fff89ff622bfa8e798bffc396ef19f092a32ec767dd37ec6332ceced',
                    'com.wm.reflector': '"reflectorid:0000000000000000000000@lastupd:1760597368000@firstcreate:1760592882278"',
                    'TS013f65e0': '01d4d70d611ce93da07612117fafcb7a0a8bb7d0e472c882d01824f2a52a8d076cdb9303f20c849434a2c741e768d8e4fe80b6d349',
                    'TS0160b754': '01d4d70d611ce93da07612117fafcb7a0a8bb7d0e472c882d01824f2a52a8d076cdb9303f20c849434a2c741e768d8e4fe80b6d349',
                    'TS012af430': '01d4d70d611ce93da07612117fafcb7a0a8bb7d0e472c882d01824f2a52a8d076cdb9303f20c849434a2c741e768d8e4fe80b6d349',
                    'akavpau_p1': akavpau_p2,
                    'TS2a5e0c5c027': '08765c7261ab2000d13c668e3bad1566e158f0bfa6a59eaa5685058d5906af32682155f58f710194083193afcd113000a51d7688a46ea5721f0cb551d6d29f3a7cd5b2c71f29961cdfaf2eafcd123b6ce4045304bbe5ca171312029778722107',
                    'if_id': 'FMEZARSFlZomiHPjj7gc60JsssNsIQXA6ENl/vNxmG/Mx3GfLthg4bC4DswR+jOkxneg772KyBxU5+8Ob6JbNEqQoTXuNK55vtMTEPvr8/vlCNJCzNw1mKvp2+EhRm6SbTSiVOeroTNjtY/rtH0tB6UJKikaAnmeSDAv6aJ0/r259PmMU3IOw2+4LqUm2nrcna0JI5ZsE+Oppf5XQUNc/irPsxf3a5iYy6e0prmbN3aNV4TRi7U08Yx1z228MJlv0kR7+aTToU2vZpcaw1uohX7TlZzEcOYnHNXsXqjyi24m4PASSqg37dSEpG/b26u5KhldFIJztDxfnwX0p+c=',
                    'TS016ef4c8': '011b390b44258bb40fc6f8a192ce2a2eeaac764307750d03e7809eaa48fc8e1aa86c7da526a5282bd177ee18f72201986f5996ec1c',
                    'TS01f89308': '011b390b44258bb40fc6f8a192ce2a2eeaac764307750d03e7809eaa48fc8e1aa86c7da526a5282bd177ee18f72201986f5996ec1c',
                    'TS8cb5a80e027': '0856d35f9dab200064bdcbf1fcc36ea00e3a40b5d0e47220902feb589de54dc722fcd0af7e76b2fd08bd037cbe113000ae66feee502148dfa52729ef56e79041f9e8a860e4c40ce5b8df629d1cac56f9e4c6fb729fc6593bb513d0d1259503fe',
                }

                headers = {
                    'accept': 'application/json',
                    'accept-language': 'en-US',
                    'cache-control': 'no-cache',
                    'content-type': 'application/json',
                    'device_profile_ref_id': 'wgsdcw3rudoefyk4wu_ygwrr3pte-nqt6vam',
                    'origin': 'https://identity.walmart.com',
                    'pragma': 'no-cache',
                    'priority': 'u=1, i',
                    'referer': 'https://identity.walmart.com/account/login?client_id=5f3fb121-076a-45f6-9587-249f0bc160ff&redirect_uri=https%3A%2F%2Fwww.walmart.com%2Faccount%2FverifyToken&scope=openid+email+offline_access&tenant_id=elh9ie&state=%2Fall-departments&code_challenge=71RPwT-w5pCYoLT9H7kt4hzHepK6KJEwQKoe23Nbo2Y',
                    'sec-ch-ua': '"Brave";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"macOS"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin',
                    'sec-gpc': '1',
                    'tenant-id': 'elh9ie',
                    'traceparent': '00-186ee5fb5c53665bbe58f2cf0a9507ba-07b19748df5eac67-00',
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
                    'wm_mp': 'true',
                    'wm_page_url': 'https://identity.walmart.com/account/login?client_id=5f3fb121-076a-45f6-9587-249f0bc160ff&redirect_uri=https%3A%2F%2Fwww.walmart.com%2Faccount%2FverifyToken&scope=openid+email+offline_access&tenant_id=elh9ie&state=%2Fall-departments&code_challenge=71RPwT-w5pCYoLT9H7kt4hzHepK6KJEwQKoe23Nbo2Y',
                    'wm_qos.correlation_id': 'kSejKGSaAXVsE5W1uierCysEmgs426uPQ9bj',
                    'x-apollo-operation-name': 'GetLoginOptions',
                    'x-enable-server-timing': '1',
                    'x-latency-trace': '1',
                    'x-o-bu': 'WALMART-US',
                    'x-o-ccm': 'server',
                    'x-o-correlation-id': 'kSejKGSaAXVsE5W1uierCysEmgs426uPQ9bj',
                    'x-o-gql-query': 'query GetLoginOptions',
                    'x-o-mart': 'B2C',
                    'x-o-platform': 'rweb',
                    'x-o-platform-version': 'usweb-1.227.0-a36e74bb2d65fd10b493905d55ea8c39ce04ac93-0131858r',
                    'x-o-segment': 'oaoh',
                }

                json_data = {
                    'query': 'query GetLoginOptions($input:UserOptionsInput!){getLoginOptions(input:$input){loginOptions{...LoginOptionsFragment}phoneCollectionRequired authCode errors{...LoginOptionsErrorFragment}}}fragment LoginOptionsFragment on LoginOptions{loginId loginIdType emailId phoneNumber{number countryCode isoCountryCode}canUsePassword canUsePhoneOTP canUseEmailOTP loginPhoneLastFour maskedPhoneNumberDetails{loginPhoneLastFour countryCode isoCountryCode}loginMaskedEmailId signInPreference loginPreference lastLoginPreference hasRemainingFactors isPhoneConnected otherAccountsWithPhone loginMaskedEmailId hasPasskeyOnProfile accountDomain residencyRegion{residencyCountryCode residencyRegionCode}}fragment LoginOptionsErrorFragment on IdentityLoginOptionsError{code message version}',
                    'variables': {
                        'input': {
                            'loginId': email,
                            'loginIdType': 'EMAIL',
                            'ssoOptions': {
                                'wasConsentCaptured': True,
                                'callbackUrl': 'https://www.walmart.com/account/verifyToken',
                                'clientId': '5f3fb121-076a-45f6-9587-249f0bc160ff',
                                'scope': 'openid email offline_access',
                                'state': '/all-departments',
                                'challenge': '71RPwT-w5pCYoLT9H7kt4hzHepK6KJEwQKoe23Nbo2Y',
                            },
                        },
                    },
                }

                response = session.post(
                    'https://identity.walmart.com/orchestra/idp/graphql',
                    cookies=cookies,
                    headers=headers,
                    json=json_data
                )


                if (response.status_code == 200 and response.json()['data']['getLoginOptions']['loginOptions']['loginPhoneLastFour'] is not None):
                    return response.json()['data']['getLoginOptions']['loginOptions']['loginPhoneLastFour']

                else:
                    if attempt == 2:  
                        return None
                    continue

            else:
                if attempt == 2: 
                    return None
                continue

        except Exception:
            if attempt == 2:
                return None
            continue

    return None