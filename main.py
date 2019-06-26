from config import *

# external
import SeleniumLibrary

# internal
from library.ad import Ad
from library.browser import Browser
from library.user import User
from library.logger import Logger

log = Logger().log

# my_ad = Ad(debug=True)
#
# # my ads details
# print("product_id: " + ( my_ad.product_id if my_ad.product_id else "None" ) )
# print("category_id: " + ( my_ad.category_id if my_ad.category_id else "None" ) )
# print("description: " + ( my_ad.description if my_ad.description else "None" ) )
# print("price: " + ( my_ad.price if my_ad.price else "None" ) )
# print("images: " + ( str(my_ad.images) if my_ad.images else "None" ) )
#
# # kijiji details
# print("ad_description: " + ( my_ad.ad_description if my_ad.ad_description else "None" ) )
# print("ad_title: " + ( my_ad.ad_title if my_ad.ad_title else "None" ) )
# print("ad_type: " + ( my_ad.ad_type if my_ad.ad_type else "None" ) )


# configure firefox
# profile = webdriver.FirefoxProfile()
# profile.set_preference("media.peerconnection.enabled", False)  # disable WebRTC to prevent IP leaks
# profile.set_preference("network.proxy.type", 1)
# profile.set_preference("network.proxy.http", proxy_host)  # HTTP PROXY
# profile.set_preference("network.proxy.http_port", int(proxy_port))
# profile.set_preference("network.proxy.ssl", proxy_host)  # SSL  PROXY
# profile.set_preference("network.proxy.ssl_port", int(proxy_port))
# profile.set_preference('network.proxy.socks', proxy_host)  # SOCKS PROXY
# profile.set_preference('network.proxy.socks_port', int(proxy_port))
# profile.update_preferences()

# driver = webdriver.Firefox(firefox_profile=profile)
# driver.get('https://www.ip-secrets.com/')
# proxy = {
# 	'proxyType':'manual',
# 	'httpProxy':'36.89.169.170:8080',
# }
# dc = {
# 	'proxy':proxy,
# }
# firefox = Browser('chrome', desired_capabilities=dc)
# firefox.driver.get('http://www.ip-secrets.com/')





ff = Browser('ff')



ff.goto('https://html.com/input-type-hidden/')
title = ff.get_title()

t = ff.wait_for_page_to_contain('EGFERGREGRRRGRGRG', negate=True)
print(t)

ff.driver.close()
ff.driver.quit()



#
# id = test.driver.current_window_handle
# print('id: '+id)
# test.driver.find_element_by_class('iyelp').click()


# words = [
# 	'john: dfg',
# 	'id=33',
# 	'id=33:3',
# 	'id:33=3',
# 	'my class : my id : er',
# 	'id is=my id = er',
# 	'my id: 33: should be 33: 33:like ya',
# 	'my id = 33'
# ]
#
# import re
#
# for word in words:
# 	index = re.search('^ ?((\w+ )?(\w+)) ?[:=] ?(.+)', word)
# 	print('{'+index.group(1)+'}', '===', '{'+index.group(4)+'}')




