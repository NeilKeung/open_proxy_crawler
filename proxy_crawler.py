import re,time,trip,requests,datetime,warnings,asyncio
import pandas as pd
from ipwhois.net import Net
from ipwhois.asn import IPASN
warnings.simplefilter(action='ignore', category=UserWarning)

@trip.coroutine
def get_proxies():
    """
    this function is to get proxies from publishing websites. Used python module trip, which is a combination of requests and tornado,
    can handle requests with multi-coroutine. We have to be careful of the max TCP packages that the machine can send, cause this function
    consume all TCP packages sending quantity. 
    """
    global ITL#used to iterate URL_SET
    this_web_has = 0#the total number of proxies this web page has.
    ITL += 1 
    #re for IP and Port infomation, eg"127.0.0.1:8080".
    pi = r'(?:((?:\d|[1-9]\d|1\d{2}|2[0-5][0-5])\.(?:\d|[1-9]\d|1\d{2}|2[0-5][0-5])\.(?:\d|[1-9]\d|1\d{2}|2[0-5][0-5])\.(?:\d|[1-9]\d|1\d{2}|2[0-5][0-5]))\D+?(6[0-5]{2}[0-3][0-5]|[1-5]\d{4}|[1-9]\d{1,3}|[0-9]))'
    ipandportlist = []
    print(URL_SET[ITL])
    try:
        r = yield trip.get(URL_SET[ITL], timeout=30, headers=header)#used trip.
        p = re.findall(pi, r.text)
        for each in p:
            str1 = str(each)
            str1 = str1.replace(',', ':')
            str1 = str1.replace('(', '')
            str1 = str1.replace(')', '')
            str1 = str1.replace('\'', '')
            str1 = str1.replace(' ', '')
            ipandportlist.append(str1)
            this_web_has += 1
    except Exception as detail:
        print('This website has a problem.', detail)
        get_proxies()
    print(URL_SET[ITL]+' has '+str(this_web_has)+' proxies.')
    return ipandportlist

@trip.coroutine
def test_proxy(proxy):
    """
    This function is used to test if the proxy server is still in service. We send every proxy candidate a request to get web
    page 'http://httpbin.org/get' for us. If the correct web page is returned then this proxy pass 
    test.This function also used trip to max its speed. 
    """
    global valid_proxy
    try:
        r = yield trip.get('http://httpbin.org/get', timeout=40,
            proxies={'http': proxy, 'https': proxy })
        if 'httpbin' in r.text:
            valid_proxy.append(proxy)
            print('currently, we have '+str(len(valid_proxy))+' valid proxies')
    except Exception as detail:
        print ("ERROR:", detail)
    else:
        raise trip.Return(proxy)
def main():
    proxies = yield get_proxies()
    r = yield [test_proxy(p.strip()) for p in proxies]
def test_only():
    r = yield [test_proxy(old.strip()) for old in allproxy]
def getip(list):
    """
    Method to extract IP addresses from IP and port combination
    eg: get"207.0.0.1" from "207.0.0.1:8888".
    """
    global IPlist
    global PORTlist
    copy = list.copy()
    for i in range(0, len(copy)):
        oneip = copy[i]
        oneip1 = oneip.split(":")
        oneip2 = oneip1[0]
        IPlist.append(oneip2)
        PORTlist.append(oneip1[1])
def ASN(oneIP):
    """
    function to get one single IP to help us look at its ASN.
    """
    str1 = str(oneIP)
    net = Net(str1)
    obj = IPASN(net)
    print('Im looking up '+str1)
    res = yield obj.lookup()
@asyncio.coroutine
def getASN(oneIP):
    putin(next(ASN(oneIP)))
def putin(results):
    """
    Function to put together the ASN info we get and make a list. Later, this list will be made into pandas
    forms and output as .csv files.
    """
    global ASNlist
    global ASNinfolist
    result = results
    ASN = result['asn']
    ASNinfo = result['asn_description']
    ASNlist.append(ASN)
    ASNinfolist.append(ASNinfo)
if __name__ == '__main__':
    start_time = time.time()
    """
    Those are the free proxies publishing websites we have now. They will be passed to getproxy() to extrated useful proxies.
    """
    URL_SET = ['https://31f.cn/city/%E6%B7%B1%E5%9C%B3/','https://31f.cn/region/浙江','https://31f.cn/region/北京/','https://31f.cn/region/广东/#',
           'https://31f.cn/region/安徽/','http://www.31f.cn', 'https://free-proxy-list.net/anonymous-proxy.html', 'http://www.mimiip.com/gngao/1',
           'http://www.mimiip.com/gngao/2','http://www.mimiip.com/gngao/3','http://www.mimiip.com/gngao/4',
           'http://www.mimiip.com/gngao/5','http://www.mimiip.com/gngao/6','https://www.us-proxy.org/','https://www.kuaidaili.com/free/inha/2/',
           'https://www.kuaidaili.com/free/inha/3/','https://www.kuaidaili.com/free/inha/4/','https://www.kuaidaili.com/free/inha/5/',
           'https://www.kuaidaili.com/free/intr/5/','http://www.ip181.com/','https://www.free-proxy-list.net/',
           'https://free-proxy-list.net/anonymous-proxy.html', 'https://www.proxynova.com/proxy-server-list/country-us/',
           'https://www.ip-adress.com/proxy-list','https://www.proxynova.com/proxy-server-list/', 'http://www.proxy-daily.com/',
           'https://www.ip-adress.com/proxy-list','http://202.112.51.31:5010/get_all/','http://www.data5u.com/','http://www.goubanjia.com/']
    """
    Those are the initilizing files. Including:
    a header for all requests we gonna make. 
    a localtime for file naming.
    a group of list to teporarily store info we ger in the process and help to make our output files.
    """
    header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36'}
    localtime = str(datetime.datetime.now().year) + str(datetime.datetime.now().month) + str(datetime.datetime.now().day)#used to name files.
    ITL = 0
    ASNinfolist = []
    ASNlist = []
    PORTlist = []
    IPlist = [] 
    valid_proxy = []
    """
    These lines does the job of reading the proxies we got yesterday and re-test them.
    """
    j = open('allproxy.txt', 'r')  
    allproxy = j.readlines()
    for n in range(0,len(URL_SET)):
        if ITL <= len(URL_SET)-2:
            trip.run(main)
    print(len(allproxy))
    trip.run(test_only)
    valid_proxy = list(set(valid_proxy))
    j.close()
    """
    Write all useful IPs into "allproxy.txt" file.
    """
    f = open('allproxy.txt', 'w')
    for each in valid_proxy:
        f.write(each+'\n')
    f.close()
    """
    Used asyncio to speed up the process of checking ASN info.
    """      
    loop = asyncio.get_event_loop()
    tasks = [getASN(host) for host in IPlist]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
    """
    make output files.
    """  
    IP_alive = pd.DataFrame({'IP': IPlist})
    Port_alive = pd.DataFrame({'PORT': PORTlist})
    ASN_alive = pd.DataFrame({'ASN': ASNlist})
    ASN_alive_info = pd.DataFrame({'ASN_INFO': ASNinfolist})
    dfalive = [IP_alive, Port_alive, ASN_alive, ASN_alive_info]
    result = pd.concat(dfalive, axis=1)
    result.to_excel(localtime+str(n)+'.xlsx')
    result.to_csv(localtime+'.csv')
    print(time.time() - start_time)
