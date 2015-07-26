def change_proxy(log_msg=True):
    from settings import TOR_PROXY_HOST, TOR_PROXY_PORT, TOR_PROXY_PASS
    import telnetlib
    from scrapy import log

    if log_msg:
        log.msg('CHANGE TOR PROXY %s:%s' % (TOR_PROXY_HOST, TOR_PROXY_PORT))

    tn = telnetlib.Telnet(TOR_PROXY_HOST, TOR_PROXY_PORT)
    tn.read_until("Escape character is '^]'.", 1)
    tn.write('AUTHENTICATE "%s"\r\n' % TOR_PROXY_PASS)
    tn.read_until("250 OK", 1)
    tn.write("signal NEWNYM\r\n")
    tn.read_until("250 OK", 1)
    tn.write("quit\r\n")
    tn.close()


import os
def get_proxies(provider='any', country=None):
    proxies = []
    if provider == 'any':
        if country:
            for root, dirs, files in os.walk('../../../tmp/proxies/country/%s/' % country):
                for file in files:
                    with open('%s%s' % (root, file)) as f:
                        # merge all proxies into list
                        proxies = proxies + f.read().split()
                    f.close()
    elif provider == 'tor':
        proxies = ['http://localhost:8123']
    else:
        pass
    return proxies

import random
def get_proxy(country, provider):
    proxies = get_proxies(provider=provider, country=country)
    if len(proxies) > 1:
        proxy = random.choice(proxies)
    else:
        proxy = None
    print 'get_proxy: %s %s %s' % (country, provider, proxy)
    return proxy
