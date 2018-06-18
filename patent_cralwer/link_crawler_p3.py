import re 
import datetime 
import time 
from downloader_p3 import Downloader
from mogon_cache import MongoCache
from scrape_callback2_p3 import ScrapeCallback
import lxml.html
import json
import itertools

def link_crawler(seed_url,link_regx=None,delay=5,max_depth=2,max_urls=-1,user_agent=None,proxies=None,num_retries=1,scrape_callback=None,cache=None):
	D = Downloader(delay=delay,user_agent=user_agent,proxies=proxies,cache=cache)
	for number in range(0,21933):
		url = seed_url
		print('number=',number)
		params = {
				'resultPagination.limit': 12,
				'resultPagination.sumLimit': 10,
				'resultPagination.start':12*number,
				'resultPagination.totalCount': 263185,
				'searchCondition.sortFields': '-APD,+PD',
				'searchCondition.searchType': 'Sino_foreign',
				"searchCondition.extendInfo['MODE']": 'MODE_SMART',
				"searchCondition.searchExp": "复合文本=(发动机)",
				'searchCondition.executableSearchExp': "VDB:(TBI='发动机')",
				'searchCondition.literatureSF': "复合文本=(发动机)",
				'searchCondition.resultMode': 'undefined',
				'searchCondition.searchKeywords': '[发][ ]{0,}[动][ ]{0,}[机][ ]{0,}'}
		try:
			html = D(url,params=params).decode('utf-8')
		except Exception as e:
			raise e
		else:
			if scrape_callback:
				scrape_callback.__call__(html)

	

seed_url = 'http://www.pss-system.gov.cn/sipopublicsearch/patentsearch/showSearchResult-startWa.shtml'
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
link_crawler(seed_url=seed_url,user_agent=user_agent,scrape_callback=ScrapeCallback(),cache = MongoCache())