import lxml.html 
from pymongo import MongoClient,errors
from datetime import datetime,timedelta
import pymongo
import requests#遇到抓取script变量时，使用requests抓取网页源码
import re
import json
import time

class ScrapeCallback:
	def __init__(self,client=None,expires=timedelta(days=30)):
		self.db = pymongo.MongoClient("localhost",27017).cache
		self.db.data_info.create_index('timestamp',expireAfterSeconds=expires.total_seconds())

	def __call__(self,html):
		#print('html=',html)
		data_json = json.loads(html)
		items=[]
		time.sleep(4)
		try:
			data_info = data_json['searchResultDTO']['searchResultRecord']
		except Exception as e:
			print('job_data=',job_data)
		for item in data_info:
			try:
				self.db.data_info.insert(item)
			except errors.DuplicateKeyError as e:
				pass


