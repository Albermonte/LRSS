import requests
import time
from concurrent.futures import ThreadPoolExecutor

CONNECTIONS = 10000
list_of_urls = []
for i in range(CONNECTIONS):
    list_of_urls.append("http://localhost:3000/test")


def get_url(url):
    return requests.get(url)


time1 = time.time()

with ThreadPoolExecutor(max_workers=CONNECTIONS) as pool:
    pool.map(get_url, list_of_urls)

time2 = time.time()
print(f'Took {time2-time1:.2f} s')
