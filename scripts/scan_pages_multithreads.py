#!/usr/bin/env python
# coding: utf-8
#
# author: https://github.com/vladiscripts
#
import time
from config import *
from scripts.db import db_session, Page, ErrRef, WarningTpls, Timecheck, queryDB
from scripts.scan_refs_of_page import ScanRefsOfPage
from scripts.scan_pages import open_requests_session, db_get_list_pages_for_scan, scan_page, do_scan, \
	download_and_scan_page
import requests
import urllib.request
from urllib.parse import quote
from threading import Thread
import threading
from threading import BoundedSemaphore


# class WorkerThread(threading.Thread):
# 	def __init__(self, url_list, url_list_lock):
# 		super(WorkerThread, self).__init__()
# 		self.url_list = url_list
# 		self.url_list_lock = url_list_lock
# 		self.maxconnections = 5
#
# 	def run(self):
#
#
#
# 		self.pool_sema.acquire()
#
# 		nexturl = self.grab_next_url()
# 		if nexturl == None: break
# 		self.retrieve_url(nexturl)
# 		pass
#
# 		self.pool_sema.release()
#
#
# 	def grab_next_url(self):
#
#
# 		self.url_list_lock.acquire(1)
# 		if len(self.url_list) < 1:
# 			nexturl = None
# 		else:
# 			nexturl = self.url_list[0]
# 			del self.url_list[0]
# 		self.url_list_lock.release()
# 		return nexturl
#
# 	def retrieve_url(self, nexturl):
# 		p = nexturl
# 		# page_id = p[0]
# 		# page_title = p[1]
# 		# url = 'https://ru.wikipedia.org/wiki/' + quote(page_title)
# 		scan_page(p)


# defining our worker and pass a counter and the semaphore to it
def worker_Semaphore(sema, p):
	scan_page(sema, p)
	# releasing the thread increments the sema value
	sema.release()


def do_work_threading_Semaphore():
	s = open_requests_session()
	list_pages_for_scan = db_get_list_pages_for_scan()
	# url_list_lock = threading.Lock()

	limit = 5
	pool_sema = threading.BoundedSemaphore(limit)
	threads = []
	for p in list_pages_for_scan:
		# pool_sema.acquire()
		# # page_id, page_title = p[0], p[1]
		# p = tuple(p)
		# t = threading.Thread(target=worker, args={p, pool_sema})
		# t.start()
		# threads.append(t)

		with pool_sema:
			# page_id, page_title = p[0], p[1]
			p = tuple(p)
			t = threading.Thread(target=worker, args={p, pool_sema})
			t.start()
			threads.append(t)
			download_and_scan_page(pool_sema, p)

		# try:
		# 	pool_sema.acquire()
		# 	t = threading.Thread(target=scan_page, args={p, pool_sema})
		# 	t.start()
		# 	threads.append(t)
		# # exit once the user hit CTRL+c
		# # or you can make the thead as daemon t.setdaemon(True)
		# except KeyboardInterrupt:
		# 	exit()
		pass
	pass


import queue


def worker(q, s):
	while True:
		item = q.get()
		if item is None:
			break
		download_and_scan_page(s, item)
		q.task_done()


def do_work_threading(s):
	list_pages_for_scan = db_get_list_pages_for_scan()
	q = queue.Queue()
	threads = []
	for i in range(3):
		t = threading.Thread(target=worker, args=(q, s,))
		t.start()
		threads.append(t)

	for item in list_pages_for_scan:
		q.put(item)

	# block until all tasks are done
	q.join()

	# stop workers
	for i in range(list_pages_for_scan):
		q.put(None)
	for t in threads:
		t.join()

# workerthreadlist = []
# for x in range(0, 3):
# 	newthread = WorkerThread(url_list, url_list_lock)
# 	workerthreadlist.append(newthread)
# 	newthread.start()
# for x in range(0, 3):
# 	workerthreadlist[x].join()
