import threading
import queue
import requests

q = queue.Queue()
valid_proxies = []
valid_proxies_lock = threading.Lock()  # Lock for thread-safe access to valid_proxies
max_valid_proxies = 10  # Stop after 10 valid proxies
stop_event = threading.Event()  # Event to signal threads to stop

with open("proxy_list.txt", "r") as f:
    proxies = f.read().split("\n")
    for p in proxies:
        q.put(p)


def check_proxies():
    global q, valid_proxies

    while not q.empty() and not stop_event.is_set():
        proxy = q.get()

        try:
            res = requests.get("http://ipinfo.io/json",
                               proxies={"http": proxy, "https": proxy},
                               timeout=5)
        except:
            continue

        if res.status_code == 200:
            with valid_proxies_lock:
                if len(valid_proxies) < max_valid_proxies:
                    valid_proxies.append(proxy)
                    print(f"Valid proxy found: {proxy}")
                if len(valid_proxies) >= max_valid_proxies:
                    stop_event.set()  # Signal to stop threads


# Create and start threads
threads = []
for _ in range(2):
    t = threading.Thread(target=check_proxies)
    t.start()
    threads.append(t)

# Wait for all threads to finish
for t in threads:
    t.join()

# Write valid proxies to file once done
with open('valid_proxies.txt', 'w') as file:
    for item in valid_proxies:
        file.write(f"{item}\n")
