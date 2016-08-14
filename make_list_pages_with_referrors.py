# -*- coding: utf-8  -*-
#
# author: https://github.com/vladiscripts
#
# import wikiapi
# from lxml import cssselect
from config import *


class make_listpage_referrors:
	list_transcludes = []
	pages_with_referrors = {}

	def __init__(self, tpls_like_sfns_names, filename_tpls_transcludes):
		from wikiapi import get_list_transcludes_of_tpls
		self.make_list_transcludes(tpls_like_sfns_names, filename_tpls_transcludes)
		self.make_listpages_with_referrors()
		pass

	def make_list_transcludes(self, tpls_like_sfns_names, filename_tpls_transcludes):
		global get_transcludes_from

		if get_transcludes_from == 1:  # from connect
			self.list_transcludes = get_list_transcludes_of_tpls(tpls_like_sfns_names)
			file_savelines(filename_tpls_transcludes, self.list_transcludes)

		# Тесты
		elif get_transcludes_from == 2:  # from file
			self.list_transcludes = file_readlines_in_set(filename_tpls_transcludes)

		elif get_transcludes_from == 3:  # from manual
			global test_pages
			self.list_transcludes = test_pages

	def make_listpages_with_referrors(self):
		pages_count = len(self.list_transcludes)
		print('Всего страниц: {}.'.format(pages_count))
		p_count_cur = pages_count

		for title in self.list_transcludes:
			print(title)
			page = find_cites_on_page(title, p_count_cur)
			self.pages_with_referrors[title] = page.full_errrefs
			# self.collect_refs(title, p_count_cur)
			p_count_cur -= 1


class find_cites_on_page:
	title = ''
	parsed_html = ''
	pages_count_cur = 0
	list_sfns = set()
	list_refs = set()
	ref_calls = dict()
	full_errrefs = dict()

	def __init__(self, title, pages_count_cur):
		from wikiapi import page_html_parse, page_get_html
		self.title = title
		self.pages_count_cur = pages_count_cur
		self.parsed_html = page_html_parse(self.title)  # html из url
		# parsed_html = html.fromstring(file_textread('test_html.html'))  # html из файла для тестов
		self.find_sfns_on_page()
		self.find_refs_on_page()
		self.compare_refs()

		self.list_sfns.clear()
		self.list_refs.clear()
		self.ref_calls.clear()

	def find_sfns_on_page(self):
		p_ref_list = self.parsed_html.xpath("//ol[@class='references']/li")
		for li in p_ref_list:
			span = li.xpath("./span[@class='reference-text']")[0]
			a_list = span.xpath("./descendant::a[contains(@href,'CITEREF')]")
			for a in a_list:
				href = ''
				text = ''
				link_to_sfn = ''
				href = a.attrib['href']  # href = span.xpath("*/a[contains(@href,'CITEREF')]/@href")
				text = a.text
				link_to_sfn = li.attrib['id']  # li.xpath("./@id")

				href_cut = self.find_href_cut(a.attrib['href'])
				self.list_sfns.add(href_cut)
				self.ref_calls[href_cut] = {'text': a.text, 'link_to_sfn': str(li.attrib['id'])}
				pass

			# from lxml import cssselect
			# # for li in parsed_html.cssselect('li[href*="CITEREF"]'):
			# for eref in self.parsed_html.cssselect('span.reference-text a[href*="CITEREF"]'):
			# 	href = eref.get('href')
			# 	pos = href.find('CITEREF')
			# 	if pos >= 0:
			# 		href_cut = href[pos:]
			# 		self.list_sfns.add(href_cut)
			# 		# link_to_sfn ссылка на sfn-сноску
			# 		# print(href)
			# 		try:
			# 			link_to_sfn = self.parsed_html.xpath(
			# 					"//li[@id]/span/a[@href='{href}']/ancestor::li[contains(@id,'{link_to_sfn}')][1]/@id".format(
			# 							href=href, link_to_sfn='cite_note'))[0]
			# 		except IndexError:
			# 			try:
			# 				link_to_sfn = self.parsed_html.xpath(
			# 						"//li[@id]/span/cite/a[@href='{href}']/ancestor::li[contains(@id,'{link_to_sfn}')][1]/@id".format(
			# 								href=href, link_to_sfn='cite_note'))[0]
			# 			except IndexError:
			# 				link_to_sfn = '#Примечания'
			#
			# 		self.ref_calls[href_cut] = {'text': eref.text, 'link_to_sfn': str(link_to_sfn)}

	def find_href_cut(self, href):
		pos = href.find('CITEREF')
		if pos >= 0:
			return href[pos:]
		return False

	def find_refs_on_page(self):
		for xpath in ['//span[@class="citation"]/@id', '//cite/@id']:
			self.find_refs_on_page_(xpath)

	def find_refs_on_page_(self, xpath):
		for href in self.parsed_html.xpath(xpath):
			href_cut = self.find_href_cut(href)
			self.list_refs.add(href_cut)

	def compare_refs(self):
		# Отлов красных ошибок как в ст.  "Казаки" не получается
		# for undefined_ref in parsed_html.cssselect('li span.mw-ext-cite-error'):
		# for undefined_ref in parsed_html.cssselect('span.error'):
		# for undefined_ref in parsed_html.cssselect('span').text:
		# t = [undefined_ref for undefined_ref in parsed_html.xpath('//li[@id=cite_note-sol5_2_3-35]')]
		# t = parsed_html.cssselect('li')
		# t = [undefined_ref for undefined_ref in parsed_html.cssselect('li#cite_note-sol5_2_3-35')]
		# t = [undefined_ref for undefined_ref in parsed_html.xpath('//span/text')]
		# for undefined_ref in parsed_html.xpath('//span').text:
		# if 'Ошибка в сносках' in undefined_ref.text

		# сравнение списков сносок и примечаний
		err_refs = self.list_sfns - self.list_refs
		# Если в статье есть некорректные сноски без целевых примечаний
		if err_refs:
			self.full_errrefs = {}
			for citeref in err_refs:
				self.full_errrefs[citeref] = self.ref_calls[citeref]
			# self.list_pages_with_referrors[self.title] = self.full_errrefs

			global print_log
			if print_log:
				print(u'Страница № {}: {}'.format(self.pages_count_cur, self.title))
				# print(u'Ошибочные сноски типа sfn без связи с ref: {}'.format(self.list_pages_with_referrors[self.title]))
				print(u'Ошибочные сноски типа sfn без связи с ref: {}'.format(self.full_errrefs))
