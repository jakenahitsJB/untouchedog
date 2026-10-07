import re
import os
import sys
import json
import time
import requests
import threading
from collections import deque
from datetime import datetime
from modules.walmart import GetWalmart
from modules.twitter import GetTwitter
from modules.doordash import GetDoordash
from modules.facebook import GetFacebook
from modules.zestimate import GetZestimate
from modules.microsoft import GetMicrosoft
from modules.utils import ExtractEmails, FormatPhone
from concurrent.futures import ThreadPoolExecutor, as_completed

if sys.platform == "win32":
    os.system("")

CONFIG = json.load(open("config.json"))
ValidProxy = False
LocalThread = threading.local()
CleanProxy = f"http://{CONFIG['proxy'].replace('http://', '')}"

def GetSession():
    if not hasattr(LocalThread, "session"):
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=CONFIG["threads"], pool_maxsize=CONFIG["threads"])
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        LocalThread.session = session
    return LocalThread.session

def CheckEmail(email):
    session = GetSession()
    try:
        response = session.get("https://api.hellolookup.com/lookup/get", params={"email": email, "key": CONFIG["hellolookup_api_key"]})
        if response.status_code != 200:
            return {"response": response.status_code, "email": email}
        elif "Not found" in response.text:
            return {"response": 404, "email": email}

        responseData = response.json()
        recoveryDigits = []
        preferedNumber = ''
        zestimateHouseValue = None

        if CONFIG['recovery_options']['enabled'] and ValidProxy == True:
            options = CONFIG["recovery_options"]["options"]

            if options.get("doordash"):
                doordash = GetDoordash(email, CleanProxy)
                if doordash:
                    recoveryDigits.append(doordash)

            if options.get("walmart"):
                walmart = GetWalmart(email, CleanProxy)
                if walmart:
                    recoveryDigits.append(walmart)
                pass

            if options.get("facebook"):
                facebook = GetFacebook(email, CleanProxy)
                if facebook:
                    recoveryDigits.append(facebook)
                pass

            if options.get("twitter"):
                twitter = GetTwitter(email, CleanProxy)
                if twitter:
                    recoveryDigits.extend(twitter)
                pass
                
            if options.get("microsoft"):
                ms_hints, _, _ = GetMicrosoft(email, CleanProxy) or ([], None, None)
                if ms_hints:
                    recoveryDigits.extend(ms_hints)
                pass

            if recoveryDigits:
                hints = [re.sub(r'\D', '', h)[-2:] for h in recoveryDigits]
                phones = responseData.get('phone') or []
                if isinstance(phones, str):
                    phones = [phones]
                for phone in phones:
                    digits = re.sub(r'\D', '', str(phone))
                    if any(digits.endswith(h) for h in hints):
                        d = digits[-10:]
                        preferedNumber = f"+1 ({d[0:3]}) {d[3:6]}-{d[6:10]}"
                        break
                else:
                    return {"response": 422, "email": email}
            else:
                return {"response": 422, "email": email}

        if CONFIG['zestimate'] and ValidProxy == True:
            zestimateHouseValue = GetZestimate(responseData.get('address'), CleanProxy)
        
        return { 
            "response": 200,
            "email": email, 
            "full_name": responseData.get('full_name'), 
            "preferedNumber": FormatPhone(preferedNumber) if CONFIG['recovery_options']['enabled'] and ValidProxy else FormatPhone(responseData.get('phone')), 
            "address": responseData.get('address'),
            "dob": responseData.get('dob'),
            "ssn": responseData.get('ssn'),
            "wealthscore": responseData.get('wealthscore'),
            "zestimateHouseValue": zestimateHouseValue
        }

    except:
        #lmfao
        pass

def ShowStartup(lines):
    active_recovery = [k for k, v in CONFIG["recovery_options"]["options"].items() if v]

    print('\n\n  -- Config ----------\n')
    print(f'  Threads: {CONFIG["threads"]}')
    print(f'  Proxy: {ValidProxy}')
    print(f'  Zestimate: {CONFIG["zestimate"]}')
    print(f"  Recovery: {', '.join([item.capitalize() for item in active_recovery]) if active_recovery else 'None'}") 
    print(f'  Mode: ')
    print(f'  Loaded Lines: {len(lines)}')
    print('\n  ---------------------')

    input(f"\n  [>] Press enter to start \n")

if __name__ == "__main__":
    sys.stdout.write("\033]0;@hellosoftware\007")
    sys.stdout.flush()

    print(f'[ ~ ] Validating API Key: {CONFIG["hellolookup_api_key"]}')
    validationResponse = requests.get(f"https://api.hellolookup.com/key/status?key={CONFIG['hellolookup_api_key']}")

    if validationResponse.status_code == 401 or validationResponse.status_code == 400:
        print("[ - ] Invalid HelloLookup API key, please ensure it's correct @HelloLookupBot")
        sys.exit(1)

    days_remaining = json.loads(validationResponse.text).get("days", "N/A")
    print(f"[ + ] Time Remaining: {days_remaining} days")
    print(f'[ ~ ] Checking proxy: {CleanProxy}')

    try:
        validationResponse = requests.get('https://google.com', proxies={"http" : CleanProxy, "https" : CleanProxy}, timeout=10)
        ValidProxy = True
    except Exception as e:
        print(e)
        print(f'[ - ] Proxy is invalid, no recovery or zestimate modules will be used.')
        ValidProxy = False

    emailList = ExtractEmails(CONFIG["input"])
    totalEmails = len(emailList)

    ShowStartup(emailList)
    lock = threading.Lock()
    stop_timer = threading.Event()
    stats = {"valids": 0, "no_recovery": 0, "invalids": 0}
    recent_hits = deque(maxlen=11)
    start_time = None
    ui_state = {"dirty": True, "last_render_time": 0.0, "started": False}
    render_interval = 0.25

    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)
    result_filename = datetime.now().strftime("%m-%d-%y-%H-%M") + ".txt"
    result_path = os.path.join(results_dir, result_filename)
    result_path_display = "/" + result_path.replace("\\", "/")
    C_RESET = "\033[0m"
    C_CYAN = "\033[96m"
    C_GREEN = "\033[38;5;118m"
    C_YELLOW = "\033[93m"
    C_RED = "\033[91m"
    C_WHITE = "\033[97m"
    C_DIM = "\033[90m"

    def _clear_screen():
        print("\033[2J\033[H", end="")

    def _render_ui():
        processed = stats["valids"] + stats["no_recovery"] + stats["invalids"]
        percent = (processed / totalEmails * 100) if totalEmails else 0.0

        if start_time is None:
            elapsed = 0.0
            cpm = 0
        else:
            elapsed = max(time.time() - start_time, 1e-6)
            cpm = int((processed / elapsed) * 60) if elapsed > 0 else 0

        ui_state["started"] = True
        frame_lines = [
            "",
            f"  {C_WHITE}            .''{C_RESET}",
            f"  {C_WHITE}  ._.-.___.' (`\\{C_RESET}",
            f"  {C_WHITE} //((        ( `'{C_RESET}",
            f"  {C_WHITE}'/ )\\ ).__. ) {C_RESET}",
            f"  {C_WHITE}' <' `\\ ._/'\\{C_RESET}",
            f"  {C_WHITE}   `   \\     \\{C_RESET}",
            "",
            f"  {C_WHITE}@HelloSoftware Autodoxer{C_RESET}",
            "",
            f"  {C_DIM}Time Remaning:{C_RESET} {C_YELLOW}{days_remaining} Days{C_RESET}",
            f"  {C_DIM}Results:{C_RESET} {C_CYAN}{result_path_display}{C_RESET}",
            "",
            (
                f"  {C_GREEN}Valids: {stats['valids']}{C_RESET} | "
                f"{C_YELLOW}No Recovery: {stats['no_recovery']}{C_RESET} | "
                f"{C_RED}Invalids: {stats['invalids']}{C_RESET} | "
                f"{C_WHITE}{processed}/{totalEmails} ({percent:.2f}%) | CPM: {cpm}{C_RESET}"
            ),
            "",
            f"  {C_DIM}-- Recent Hits ------------------------{C_RESET}",
            "",
        ]

        if recent_hits:
            frame_lines.extend(hit for hit in recent_hits)
        else:
            frame_lines.append(f"  {C_DIM}Loading...{C_RESET}")

        frame = "\n".join(frame_lines)
        sys.stdout.write("\033[H\033[J" + frame + "\n")
        sys.stdout.flush()

    def _timer():
        while not stop_timer.is_set():
            with lock:
                now = time.time()
                if ui_state["dirty"] and (now - ui_state["last_render_time"]) >= render_interval:
                    _render_ui()
                    ui_state["last_render_time"] = now
                    ui_state["dirty"] = False
            time.sleep(0.1)

    threading.Thread(target=_timer, daemon=True).start()

    with open(result_path, "a", encoding="utf-8") as valids_file:
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=CONFIG["threads"]) as executor:
            futures = [executor.submit(CheckEmail, email) for email in emailList]

            for future in as_completed(futures):
                result = future.result()
                if result is None:
                    continue
                with lock:
                    if result["response"] == 200:
                        stats["valids"] += 1
                        zest = f"Zestimate: ${result['zestimateHouseValue']:,.0f}" if result['zestimateHouseValue'] else 'Wealth Score: ' + result['wealthscore']
                        wealth = result.get("wealthscore") or "N/A"
                        hit_line = (
                            f"  {C_GREEN}+{C_RESET} {result['email']} | {result['full_name'] or 'N/A'}"
                            f" | {result['preferedNumber'] or 'N/A'}"
                            f" | {result['address'] or 'N/A'}"
                            + (f" | SSN: {result['ssn'] or 'N/A'}" if CONFIG["ssn"] else "")
                            + (f" | DOB: {result['dob'] or 'N/A'}" if CONFIG["dob"] else "")
                            + f" | {zest}"
                        )
                        file_line = (
                            f"{result['email']} | {result['full_name'] or 'N/A'}"
                            f" | {result['preferedNumber'] or 'N/A'}"
                            f" | {result['address'] or 'N/A'}"
                            + (f" | SSN: {result['ssn'] or 'N/A'}" if CONFIG["ssn"] else "")
                            + (f" | DOB: {result['dob'] or 'N/A'}" if CONFIG["dob"] else "")
                            + f" | {zest} "
                        )
                        recent_hits.appendleft(hit_line)
                        valids_file.write(file_line + "\n")
                        valids_file.flush()
                        ui_state["dirty"] = True
                    elif result["response"] == 422:
                        stats["no_recovery"] += 1
                        ui_state["dirty"] = True
                    else:
                        stats["invalids"] += 1
                        ui_state["dirty"] = True

    stop_timer.set()
    with lock:
        _render_ui()
    print("\nCompleted. Results saved to:", result_path_display)
