import urllib.request 
import urllib.parse 
import socket 
from datetime import datetime 
import time 
import random
import gzip
import re
import browsercookie
import json

DEFAULT_AGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
DEFAULT_DELAY = 2
DEFAULT_TIMEOUT = 200
DEFAULT_RETRIES = 1


class Throttle:
	def __init__(self,delay):
		self.delay = delay
		self.domains = {}

	def wait(self,url):
		domain = urllib.parse.urlparse(url).netloc
		last_accessed = self.domains.get(domain)

		if self.delay > 0 and last_accessed is not None:
			sleep_sec = self.delay-(datetime.now() - last_accessed).seconds
			if sleep_sec>0:
				time.sleep(sleep_sec)
		self.domains[domain] = datetime.now()

class Downloader:
	def __init__(self,delay=DEFAULT_DELAY,user_agent=DEFAULT_AGENT,proxies=None,num_retries=DEFAULT_RETRIES,timeout=DEFAULT_TIMEOUT,opener=None,cache=None):
		socket.setdefaulttimeout(timeout)
		self.throttle = Throttle(delay)
		self.user_agent=user_agent 
		self.proxies = proxies 
		self.num_tries=num_retries
		self.cache = cache
		self.opener = opener
		self.cj = browsercookie.chrome()


	def __call__(self,url,params =None):
		result = None
		if result is None:
			self.throttle.wait(url)
			proxy = random.choice(self.proxies) if self.proxies else None
			headers = self.header_making()
			result = self.download(url,cookies=self.cj,headers=headers,proxy=proxy,num_tries=self.num_tries,data=params)
		return result['html']

	def header_making(self):
		headers= {}
		headers['Accept'] = "*/*"
		headers['X-Requested-With'] = 'XMLHttpRequest'
		headers['User-Agent'] = self.user_agent
		headers['Referer'] = 'http://www.pss-system.gov.cn/sipopublicsearch/patentsearch/searchHomeIndex-searchHomeIndex.shtml'
		headers['Host'] = 'www.pss-system.gov.cn'
		headers['Origin']='http://www.pss-system.gov.cn'
		return headers



	def download(self,url,cookies,headers,proxy,num_tries,data=None):
		print('Downloading:',url)

		if data != None:
			encoded_data = urllib.parse.urlencode(data).encode(encoding='UTF8')
		request = urllib.request.Request(url,headers=headers,data=encoded_data) or {}
		opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies)) or self.opener 
		if proxy:
			proxy_para = {urllib.parse.urlparse(url).scheme:proxy}
			opener.add_handler(urllib.request.ProxyHandler(proxy_para))
		try:
			#发送请求
			response = opener.open(request)
			headers_info = response.info()
			if 'Content-Encoding' in headers_info and 'gzip' == headers_info['Content-Encoding']:
				html=gzip.decompress(response.read())
			else:
				html = response.read()
			#print('html=',html)
			code = response.code
		except urllib.error.URLError as e:
			print('Download error',e.reason)
			html = ''
			if hasattr(e,'code'):
				code = e.code
				if num_tries>0 and 500<=code<600:
					html = self.download(url,headers,proxy,num_tries-1)
			else:
				code = e.code
		return {'html':html,'code':code}


if __name__ == '__main__':
	url = 'http://www.pss-system.gov.cn/sipopublicsearch/patentsearch/showSearchResult-startWa.shtml'
	data = {
	'resultPagination.limit': 12,
	'resultPagination.sumLimit': 10,
	'resultPagination.start': 0,
	'resultPagination.totalCount': 263185,
	'searchCondition.sortFields': '-APD,+PD',
	'searchCondition.searchType': 'Sino_foreign',
	"searchCondition.extendInfo['MODE']": 'MODE_SMART',
	"searchCondition.searchExp": "复合文本=(发动机)",
	'searchCondition.executableSearchExp': "VDB:(TBI='发动机')",
	'searchCondition.literatureSF': "复合文本=(发动机)",
	'searchCondition.resultMode': 'undefined',
	'searchCondition.searchKeywords': '[发][ ]{0,}[动][ ]{0,}[机][ ]{0,}'}
	D = Downloader()
	html = D(url,params=data).decode('utf-8')
	data_json = json.loads(html)
	print('data_json = ',type(data_json))
	data_info = data_json['searchResultDTO']['searchResultRecord']
	#print('data_info=',data_info)
	print('len(data_info)',len(data_info))
	for item in data_info:
		print('item=',item['fieldMap'],'\n')
