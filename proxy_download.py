from requests import get
from selenium import webdriver
import random
import csv
import time
from bs4 import BeautifulSoup as bs


data = open("url.csv")
url = list(csv.reader(data))
f_url = url[0][0]
print("running url :",f_url)


class Queue:
    def __init__(self):
        self.queue = []

    def get(self):
        if self.qsize() != 0:
            return self.queue.pop()

    def put(self, item):
        if item not in self.queue:
            self.queue.append(item)

    def qsize(self):
        return len(self.queue)

    def __str__(self):
        return str(self.queue)


class Proxy:
    def __init__(self):
        self.anony_proxis = 'https://free-proxy-list.net/anonymous-proxy.html'
        self.new_proxies = 'https://free-proxy-list.net'
        self.socks_proxies = 'https://socks-proxy.net'
        self.ssl_proxies = 'https://sslproxies.org'
        self.qproxy = None
        self.psize = 0
        self.country = None
        self.port = None

    def fetch(self, url):
        proxies = bs(get(url).text, 'html.parser').find('tbody').findAll('tr')
        for proxy in proxies:
            pjson = self.parse(proxy.findAll('td'))
            if pjson:
                if self.psize:
                    if self.qproxy.qsize() < self.psize:
                        self.qproxy.put(pjson)
                    else:
                        break
                else:
                    self.qproxy.put(pjson)

    def parse(self, proxy):
        pjson = {'ip': proxy[0].string, 'port': proxy[1].string,
                 'anonymity': proxy[4].string,
                 'country': proxy[3].string,
                 'updated': proxy[7].string,
                 'https': proxy[6].string}

        if all([self.country, self.port]):
            if pjson['country'] == self.country:
                if pjson['port'] == self.port:
                    return pjson

        elif self.port:
            return None if self.port != pjson['port'] else pjson

        elif self.country:
            return None if self.country != pjson['country'] else pjson

        else:
            return pjson

    def scrape(self, size=None, port=None, country=None, new_proxies=False, anony_proxies=False, socks_proxies=False,
               ssl_proxies=False):

        self.port = str(port) if port else None
        self.country = country
        self.qproxy = Queue()
        self.psize = size

        if new_proxies:
            self.fetch(self.new_proxies)

        if anony_proxies:
            self.fetch(self.anony_proxies)

        if socks_proxies:
            self.fetch(self.socks_proxies)

        if ssl_proxies:
            self.fetch(self.ssl_proxies)

        proxies = self.qproxy
        self.qproxy = Queue()
        return proxies

list_proxy = []
def main():
    prx = Proxy()
    proxies = prx.scrape(new_proxies=True, size=50)
    while proxies.qsize():
        proxy = proxies.get()
        IP = proxy['ip']
        PORT = proxy['port']
        COUNTRY = proxy['country']
        data_proxy = IP+":"+PORT
        print(data_proxy)



        chrome_options = webdriver.ChromeOptions()
        #chrome_options.add_argument('--user-agent=%s' % userAgent)
        chrome_options.add_argument('--proxy-server=%s' % data_proxy)
        chrome_options.add_argument("--headless")
        #chrome_options.add_argument("--start-maximized")
        driver = webdriver.Chrome(executable_path='./chromedriver', chrome_options=chrome_options)
        driver.get(f_url)
        #driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => false,});")
        time.sleep(3)
        try:
            driver.find_element_by_tag_name('link')
            list_proxy.append([data_proxy])
            with open('proxy.csv', 'wt') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
                for M in list_proxy:
                    spamwriter.writerow(M)
            print("proxy save")
            driver.quit()





        except:
            print("proxy not working")
            driver.quit()


if __name__ == '__main__':
    main()