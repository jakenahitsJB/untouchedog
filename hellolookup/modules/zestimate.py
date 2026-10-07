import tls_client
from fake_useragent import UserAgent

GRAPHQL_QUERY = 'query HowMuchIsMyHomeWorthReviewQuery($zpid: ID!) {\n  property(zpid: $zpid) {\n    streetAddress\n    city\n    state\n    zipcode\n    bedrooms\n    bathrooms\n    livingArea\n    zestimate\n    homeStatus\n    photos(size: XL) {\n      url\n      __typename\n    }\n    ...OmpHomeWorthUpsell_property\n    isConfirmedClaimedByCurrentSignedInUser\n    isVerifiedClaimedByCurrentSignedInUser\n    ...UARequiredPropertyDimensions_property\n    ...ContactAgentForm_property\n    ...HomeInfo_property\n    __typename\n  }\n  viewer {\n    ...ContactAgentForm_viewer\n    __typename\n  }\n  abTests {\n    ...OmpHomeWorthUpsell_abTests\n    ...UARequiredPropertyDimensions_abTests\n    ...ContactAgentForm_abTests\n    __typename\n  }\n}\n\nfragment OmpHomeWorthUpsell_property on Property {\n  zpid\n  onsiteMessage(placementNames: ["HMIMHWTopSlot"]) {\n    ...onsiteMessage_fragment\n    __typename\n  }\n  __typename\n}\n\nfragment onsiteMessage_fragment on OnsiteMessageResultType {\n  eventId\n  decisionContext\n  messages {\n    skipDisplayReason\n    shouldDisplay\n    isGlobalHoldout\n    isPlacementHoldout\n    placementName\n    testPhase\n    bucket\n    placementId\n    passThrottle\n    lastModified\n    eventId\n    decisionContext\n    selectedTreatment {\n      id\n      name\n      component\n      status\n      renderingProps\n      lastModified\n      __typename\n    }\n    qualifiedTreatments {\n      id\n      name\n      status\n      lastModified\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment OmpHomeWorthUpsell_abTests on ABTests {\n  HMIMHW_ZO_NFS_UPSELL_ONSITE_MESSAGING: abTest(\n    trial: "HMIMHW_ZO_NFS_UPSELL_ONSITE_MESSAGING"\n  )\n  __typename\n}\n\nfragment UARequiredPropertyDimensions_property on Property {\n  currency\n  featuredListingTypeDimension\n  hasPublicVideo\n  hdpTypeDimension\n  listingTypeDimension\n  price\n  propertyTypeDimension\n  standingOffer {\n    isStandingOfferEligible\n    __typename\n  }\n  zpid\n  isZillowOwned\n  zillowOfferMarket {\n    legacyName\n    __typename\n  }\n  ...ShouldShowVideo_property\n  __typename\n}\n\nfragment ShouldShowVideo_property on Property {\n  homeStatus\n  isZillowOwned\n  hasPublicVideo\n  primaryPublicVideo {\n    sources {\n      src\n      __typename\n    }\n    __typename\n  }\n  richMediaVideos {\n    mp4Url\n    hlsUrl\n    __typename\n  }\n  __typename\n}\n\nfragment UARequiredPropertyDimensions_abTests on ABTests {\n  ZO_HDP_HOUR_ONE_VIDEO: abTest(trial: "ZO_HDP_HOUR_ONE_VIDEO")\n  __typename\n}\n\nfragment ContactAgentForm_property on Property {\n  streetAddress\n  state\n  city\n  zipcode\n  zpid\n  homeStatus\n  homeType\n  zestimate\n  homeType\n  isInstantOfferEnabled\n  zillowOfferMarket {\n    name\n    code\n    __typename\n  }\n  __typename\n}\n\nfragment ContactAgentForm_viewer on Viewer {\n  name\n  email\n  zuid\n  __typename\n}\n\nfragment ContactAgentForm_abTests on ABTests {\n  SHOW_PL_LEAD_FORM: abTest(trial: "SHOW_PL_LEAD_FORM")\n  __typename\n}\n\nfragment HomeInfo_property on Property {\n  streetAddress\n  city\n  state\n  zipcode\n  bedrooms\n  bathrooms\n  livingArea\n  homeStatus\n  homeType\n  contingentListingType\n  photos(size: XL) {\n    url\n    __typename\n  }\n  listing_sub_type {\n    is_newHome\n    is_FSBO\n    is_bankOwned\n    is_foreclosure\n    is_forAuction\n    is_comingSoon\n    __typename\n  }\n  __typename\n}\n'

def GetZestimate(address: str, proxy: str, log=print) -> None:
    last_error = None

    for attempt in range(1, 3):
        try:
            session = tls_client.Session(client_identifier='chrome_120')
            session.proxies = {'http': proxy, 'https': proxy}
            user_agent = UserAgent().chrome

            response = session.get(
                url='https://www.zillowstatic.com/autocomplete/v3/suggestions/',
                params={'q': address, 'resultTypes': 'allAddress', 'resultCount': '1'},
                headers={
                    'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Referer': 'https://www.zillow.com/how-much-is-my-home-worth/',
                    'sec-ch-ua-mobile': '?0',
                    'User-Agent': user_agent,
                    'sec-ch-ua-platform': '"Windows"',
                },
                timeout_seconds=6
            )

            if response.status_code != 200:
                raise Exception(f'autocomplete status {response.status_code}')

            if '"results":[]' in response.text:
                return None

            zpid = response.json()['results'][0]['metaData']['zpid']

            response = session.post(
                'https://www.zillow.com/graphql/',
                json={
                    'operationName': 'HowMuchIsMyHomeWorthReviewQuery',
                    'variables': {'zpid': zpid},
                    'query': GRAPHQL_QUERY,
                },
                headers={
                    'User-Agent': user_agent,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-CA,en-US;q=0.7,en;q=0.3',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Sec-GPC': '1',
                    'Pragma': 'no-cache',
                    'Cache-Control': 'no-cache',
                },
                timeout_seconds=6
            )

            if 'Access to this page has been denied' in response.text:
                raise Exception('access denied')

            return response.json()['data']['property']['zestimate']

        except Exception:
            pass

    return None
