# -*- coding: utf-8 -*-
'''
Created on 05/07/2017
@author: Ryububuck
'''

from bs4 import BeautifulSoup as bs
import re
import requests
import json
from requests_toolbelt.multipart.encoder import MultipartEncoder
import time
import pprint
import os
import sys

class dc:
	def __init__(self, id='ㅇㅇ', pw='test123', gall='lovelyz'):
		self.gall = str(gall)
		self.id = str(id)
		self.pw = str(pw)

	def remove_html_tags(self, data):
		p = re.compile(r'<.*?>')
		return p.sub('\n', data)

	# 총공 정보 가져오기 lists 반환
	def get_gall_sming_lists(self, article_no):
		url = "http://m.dcinside.com/view.php?id=" + self.gall + "&no=" + str(article_no)
		session = requests.session()
		session.headers['X-Requested-With'] = 'XMLHttpRequest'
		session.headers['User-Agent'] = 'Mozilla/5.0 (Linux; U; Android 1.5; de-; sdk Build/CUPCAKE) AppleWebkit/528.5+'
		html = session.get(url).text
		soup = bs(html, 'lxml')

		content = soup.find("table", {"style": "table-layout: fixed; width: 100%"})
		bodies = self.remove_html_tags(str(content))
		bodies = bodies.split('\n')

		smings = []

		for body in bodies:
			if body.find('http://gall.dcinside.com') != -1:
				smings.append(body)
				continue
			if body.find('스밍 :') != -1:
				song_name = body.split('스밍 :')[1]
				if body.find('youtu'):    song_name = song_name.split('https://youtu.be')[0]
				smings.append(song_name.strip())
				continue
			if body.find('총공명 :') != -1:
				smings.append(body)
				continue
			if body.find('갤]') != -1 or body.find('갤)') != -1:
				smings.append(body)
				continue
			if body.find('SID M:') != -1:
				smings.append(body)
				continue
			if body.find(':') != -1:
				body = body.strip(' ')
				if body.replace(':', '').isdigit():    smings.append(body)

		i = 0
		lists = []
		endi = int(len(smings) / 5)

		if endi < 1: return 1

		for item in range(0, endi):
			time = smings[i].replace('24:', '00:')
			gall = smings[i + 1].split('?id=')[1]
			if smings[i+2].find('총공명 :') != -1:
				subject = smings[i+2].split('총공명 :')[1]
				subject = subject.strip()
				song_name = smings[i + 3]
			elif smings[i+2].find('갤]') != -1 or smings[i+2].find('갤)') != -1:
				subject = smings[i+2]
				song_name = smings[i+3]
			else:
				subject = smings[i+3]
				song_name = smings[i+2]
			try:
				sids = smings[i + 4]
				tmp1 = sids.split('SID M:')[1]
				tmp2 = re.split('\W+', tmp1)
				i = i + 5
			except:
				#tmp2 = ['8158014', 'g', '85121813', 'b', '4587284'] #Melon만 Moonrise 문라이즈
				tmp2 = ['88888888', 'g', '88888888', 'b', '88888888']
				i = i + 4
			tmpb = {'time': time, 'gall': gall, 'song_name': song_name, 'subject': subject, 'sids': tmp2}
			lists.append(tmpb)

		try:
			time = smings[i].replace('24:', '00:')
			gall = smings[i + 1].split('?id=')[1]
			if smings[i + 2].find('총공명 :') != -1:
				subject = smings[i + 2].split('총공명 :')[1]
				subject = subject.strip()
				song_name = smings[i + 3]
			elif smings[i + 2].find('갤]') != -1 or smings[i + 2].find('갤)') != -1:
				subject = smings[i + 2]
				song_name = smings[i + 3]
			else:
				subject = smings[i + 3]
				song_name = smings[i + 2]
			try:
				sids = smings[i + 4]
				tmp1 = sids.split('SID M:')[1]
				tmp2 = re.split('\W+', tmp1)
				i = i + 5
			except:
				tmp2 = ['8158014', 'g', '85121813', 'b', '4587284']  # Melon만 Moonrise 문라이즈
				i = i + 4
			lists.append({'time': time, 'gall': gall, 'song_name': song_name, 'subject': subject, 'sids': tmp2})
		except: pass
		return lists

	# 총공 게시물들 검색
	def search_sming(self, max_pages):
		page = 1
		lists = []
		url = 'http://gall.dcinside.com/board/lists/?id=' + self.gall + '&s_type=search_all&s_keyword=SID%20M%3A'
		while page < max_pages:
			data = requests.get(url).text
			soup = bs(data, 'lxml')
			table = soup.find(style="table-layout:fixed;")
			try:
				trs = table.tbody.find_all('tr')
			except:
				url = 'http://gall.dcinside.com/mgallery/board/lists/?id=' + self.gall + '&page=' + str(page) + '&search_pos=&s_type=search_all&s_keyword=SID%20M%3A'
				data = requests.get(url).text
				soup = bs(data, 'lxml')
				table = soup.find(summary="마이너갤러리 리스트로 번호,제목,글쓴이,날짜,조회,추천을 제공")
				trs = table.tbody.find_all('tr')

			for tr in trs:
				tds = tr.find_all('td')
				if tds[0].string == '공지':  continue

				link = tds[1].a['href']
				link = link.split('no=')[1].split('&page')[0]

				try: nickname = tds[2].span.string
				except: nickname = 'Err'
				subject = tds[1].a.string
				date = tds[3].string
				lists.append({'no': link, 'subject': subject, 'date': date, 'nickname': nickname})

			content = soup.find("a", "b_next")
			try:    url = 'http://gall.dcinside.com' + content.get('href')
			except: break
			page += 1

		return lists

	# 로그인
	def login(self):
		with requests.session() as s:
			s.headers['X-Requested-With'] = 'XMLHttpRequest'
			s.headers['Referer'] = 'http://m.dcinside.com/login.php?r_url=m.dcinside.com%2Flist.php%3Fid%3Dlovelyz'
			s.headers['User-Agent'] = 'Mozilla/5.0 (Linux; U; Android 2.1-update1; ko-kr; Nexus One Build/ERE27)'

			for i in range(0, 3):
				res = s.get('http://m.dcinside.com/login.php?r_url=m.dcinside.com%2Flist.php%3Fid%3Dlovelyz').text
				soup = bs(res, 'lxml')
				con_key = soup.find('input', {'name': 'con_key'})['value']

				time.sleep(2.5)
				data = {'token_verify': 'login', 'con_key': con_key}
				res = s.post('http://m.dcinside.com/_access_token.php', data=data).text
				result_dict = json.loads(res)
				con_key = result_dict['data']

				data = {'user_id': self.id, 'user_pw': self.pw, 'id_chk': 'on',
						'mode': '', 'id': '', 'r_url': 'm.dcinside.com%252Flist.php%253Fid%253Dlovelyz',
						'con_key': con_key}
				res = s.post('https://dcid.dcinside.com/join/mobile_login_ok.php', data=data)

				if res.text.find('http://m.dcinside.com%2Flist.php%3Fid%3Dlovelyz') != -1:
					return s
				time.sleep(0.5)
		return 1

	#유동 글쓰기
	def non_write(self, img, arr):
		s = requests.session()
		s.headers['X-Requested-With'] = 'XMLHttpRequest'
		s.headers['Referer'] = 'http://m.dcinside.com%2Flist.php%3Fid%3Dlovelyz'
		s.headers['User-Agent'] = 'Mozilla/5.0 (Linux; U; Android 2.1-update1; ko-kr; Nexus One Build/ERE27)'

		url = 'http://m.dcinside.com/write.php?id=' + arr['gall'] + '&mode=write'
		res = s.get(url).text
		soup = bs(res, 'lxml')
		code = soup.find('input', {'name': 'code'})['value']

		data = {
			'id': arr['gall'],
			'w_subject': arr['subject'],
			'w_memo': arr['memo'],
			'w_filter': '1',
			'mode': 'write_verify'
		}
		res = s.post('http://m.dcinside.com/_option_write.php', data=data).text
		result_dict = json.loads(res)
		block_key = result_dict['data']

		multipart_data = MultipartEncoder(
			fields={
				# 'file': ('file.py', open('file.py', 'rb'), 'text/plain')
				'name': self.id,
				'password': self.pw,
				'subject': arr['subject'],
				'memo': arr['memo'],
				'user_id': '',
				'page': '',
				'mode': 'write',
				'id': arr['gall'],
				'code': code,
				'no': '',
				'mobile_key': 'mobile_nomember',
				't_ch2': '',
				'FL_DATA': img + '^@^',
				'OFL_DATA': '1.png^@^',
				'delcheck': '',
				'Block_key': block_key,
				'filter': '1',
				'wikiTag': ''
			}
		)

		res = s.post('http://upload.dcinside.com/g_write.php', data=multipart_data,
					 headers={'Content-Type': multipart_data.content_type})

		if res.text.find('refresh') != -1:
			tmpUrl = res.text.split('url=')[1].split('">')[0]
			data = {'gall': self.gall, 'gall_url': tmpUrl}
			print(data)
			#requests.post('http://xn--2u1b43d13kq4g.com/sminghae/db_dc.php', data=data)
			return tmpUrl
		else:	return 'err'

	#user 글쓰기
	def user_write(self, s, img, writeArr):
		url = str('http://m.dcinside.com/write.php?id=' + writeArr['gall'] + '&mode=write')
		res = s.get(url).text
		soup = bs(res, 'lxml')
		code = soup.find('input', {'name': 'code'})['value']
		mobile_key = soup.find('input', {'name': 'mobile_key'})['value']

		data = {
			'id': writeArr['gall'],
			'w_subject': writeArr['subject'],
			'w_memo': writeArr['memo'],
			'w_filter': '1',
			'mode': 'write_verify'
		}
		res = s.post('http://m.dcinside.com/_option_write.php', data=data).text
		result_dict = json.loads(res)
		block_key = result_dict['data']

		multipart_data = MultipartEncoder(
			fields={
				# 'file': ('file.py', open('file.py', 'rb'), 'text/plain')
				'name': 'test',
				'password': 'tagall',
				'subject': writeArr['subject'],
				'memo': writeArr['memo'],
				'user_id': self.id,
				'page': '',
				'mode': 'write',
				'id': writeArr['gall'],
				'code': code,
				'no': '',
				'mobile_key': mobile_key,
				't_ch2': '',
				'FL_DATA': img + '^@^',
				'OFL_DATA': '1.png^@^',
				'delcheck': '',
				'Block_key': block_key,
				'filter': '1',
				'wikiTag': ''
			}
		)

		res = s.post('http://upload.dcinside.com/g_write.php', data=multipart_data,
					 headers={'Content-Type': multipart_data.content_type})

		if res.text.find('refresh') != -1:
			tmpUrl = res.text.split('url=')[1].split('">')[0]
			data = {'gall': self.gall, 'gall_url': tmpUrl}
			print(data)
			#requests.post('http://xn--2u1b43d13kq4g.com/sminghae/db_dc.php', data=data)
			return tmpUrl
		else:   return 'err'

	#이미지 업로드
	def upload_img(self, imgname, arr):
		with requests.session() as s:
			s.headers['X-Requested-With'] = 'XMLHttpRequest'
			s.headers['Referer'] = 'http://m.dcinside.com/write.php?id=' + arr['gall'] +'&mode=write'
			s.headers['User-Agent'] = 'Mozilla/5.0 (Linux; U; Android 2.1-update1; ko-kr; Nexus One Build/ERE27)'

			multipart_data = MultipartEncoder(
				fields={
					'upload[0]': ('sminghae.png', open(imgname, 'rb').read(), 'image/png'),
					'imgId': arr['gall'], 'mode': 'write', 'img_num': '21'
				}
			)

			res = s.post('http://upload.dcinside.com/upload_imgfree_mobile.php', data=multipart_data,
						 headers={'Content-Type': multipart_data.content_type})
			a = res.text.split('\'FL_DATA\').value = \'')[1]
			a = a.split('^@^')[0]
		return a

if __name__ == '__main__':
	# dc.py 테스트
	dc = dc('kinghappy','gina9629','lovelyz')
	dc_sess = dc.login()

	if dc_sess == 1:
		print('err@@@@@@@@@@@')
		sys.exit()
	dc_no = 2
	arr = {
		'memo': 'ㅌㅅㅌ',
		'subject': '테스트',
		'gall': 'lvlz8'
	}
	print("Login Success!")
	dc.search_sming(10)
	#img = dc.upload_img('res/_stickers/1.gif', arr)
	#dc.non_write(img,arr)
	#dc.user_write(dc_sess, img, arr)

	#dc.get_gall_sming_lists(2827059)