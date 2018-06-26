#!/usr/bin/env python
# coding: utf-8
#
# author: https://github.com/vladiscripts
#
import time
import requests
from urllib.parse import quote
from scripts.db import db_session, Page, Ref, Timecheck, queryDB
from scripts.scan_refs_of_page import ScanRefsOfPage


def do_scan():
	"""Сканирование страниц на ошибки"""
	s = open_requests_session()

	for p in db_get_list_pages_for_scan():
		download_and_scan_page(s, p)


def download_and_scan_page(s, p):
	id, title = p[0], p[1]
	# if page_id != 273920:	continue  # For tests
	r = s.get('https://ru.wikipedia.org/wiki/' + quote(title))
	print(title + ':')
	# page = ScanRefsOfPage(page_id, page_title)
	page = ScanRefsOfPage(r.text)
	scan_page([id, title, page.err_refs])


def scan_page(p):
	"""Сканирование страниц на ошибки"""
	page_id, page_title, err_refs = p[0], p[1], p[2]
	db_session.rollback()

	# Очистка db от списка старых ошибок
	db_session.query(Ref).filter(Ref.page_id == page_id).delete()
	db_session.query(Timecheck).filter(Timecheck.page_id == page_id).delete()

	# Сканирование страниц на ошибки
	for ref in err_refs:
		db_session.add(Ref(page_id, ref['citeref'], ref['link_to_sfn'], ref['text']))

	time_current = time.strftime('%Y%m%d%H%M%S', time.gmtime())
	db_session.add(Timecheck(page_id, time_current))
	db_session.commit()


def db_get_list_pages_for_scan():
	return queryDB(db_session.query(Page.page_id, Page.title) \
				   .select_from(Page) \
				   .outerjoin(Timecheck, Page.page_id == Timecheck.page_id) \
				   .filter((Timecheck.timecheck.is_(None)) | (Page.timeedit > Timecheck.timecheck)))


def open_requests_session():
	s = requests.Session()
	s.headers.update({'User-Agent': 'user:textworkerBot'})
	s.params.update({"action": "render"})
	return s

# for test
# page = ScanRefsOfPage('2091672', 'Марк Фульвий Флакк (консул 125 года до н. э.)')
# pass
