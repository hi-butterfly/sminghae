# -*- coding: utf-8 -*-
'''
Created on 05/07/2017
@author: Ryububuck
'''

import json, codecs, os, glob
import winreg
import requests
from PIL import Image, ImageDraw, ImageFont
import time
from io import BytesIO
from random import randrange
import win32process
import pprint
import sys
import logging
import logging.handlers

# 로그 세팅
def log_set():
	today = time.localtime()
	todaystr = "17%02d%02d" % (today.tm_mon, today.tm_mday)

	global logger
	logger = logging.getLogger('mel-logger')
	fomatter = logging.Formatter('[%(asctime)s][%(filename)s:%(lineno)s] ▶ %(message)s')
	logging.basicConfig(level=logging.INFO)

	# 스트림과 파일로 로그를 출력하는 핸들러를 각각 만든다.
	filepath = 'log\\'
	if not os.path.exists(filepath): os.makedirs(filepath)
	fileHandler = logging.FileHandler('log\\' + todaystr + '.log')
	streamHandler = logging.StreamHandler()
	fileHandler.setFormatter(fomatter)
	streamHandler.setFormatter(fomatter)
	logger.addHandler(fileHandler)
	logger.addHandler(streamHandler)

log_set()

class melon:
	def __init__(self):
		fontsFolder = 'res'
		self.nanum12 = ImageFont.truetype(os.path.join(fontsFolder, 'NanumBarunGothic.ttf'), 12)
		self.nanum15 = ImageFont.truetype(os.path.join(fontsFolder, 'NanumBarunGothic.ttf'), 15)
		#self.yeon15 = ImageFont.truetype(os.path.join(fontsFolder, 'BMYEONSUNG_ttf.ttf'), 17)
		self.nanum18 = ImageFont.truetype(os.path.join(fontsFolder, 'NanumBarunGothic.ttf'), 18)
		self.nanum50 = ImageFont.truetype(os.path.join(fontsFolder, 'NanumBarunGothic.ttf'), 50)

		self.nanum24 = ImageFont.truetype(os.path.join(fontsFolder, 'NanumB.ttf'), 24)
		self.nanum25 = ImageFont.truetype(os.path.join(fontsFolder, 'NanumBarunGothic.ttf'), 25)
		self.nanum30 = ImageFont.truetype(os.path.join(fontsFolder, 'NanumBarunGothic.ttf'), 30)
		self.nanumb30 = ImageFont.truetype(os.path.join(fontsFolder, 'NanumB.ttf'), 30)
		self.nanum36 = ImageFont.truetype(os.path.join(fontsFolder, 'NanumB.ttf'), 36)
		self.nbb30 = ImageFont.truetype(os.path.join(fontsFolder, 'NBB.ttf'), 30)
		#self.yeon34 = ImageFont.truetype(os.path.join(fontsFolder, 'BMYEONSUNG_ttf.ttf'), 34)

		today = time.localtime()
		self.today = "17%02d%02d" % (today.tm_mon, today.tm_mday)

	def set_init(self):
		try: self.MelonPath = regkey_value(r"HKEY_CURRENT_USER\SOFTWARE\Melon40", "InstallPath")  # Melon_Dir
		except:		return 'Error 11: 멜론 로드 실패, 멜론 재설치가 필요해요!'

		try:
			autoLogin = regkey_value(r"HKEY_CURRENT_USER\SOFTWARE\Melon40\Main", "auto_login")
			if autoLogin != 1:	raise ValueError
		except:		return 'Error NL: 멜론 자동 로그인 설정이 필요해요!'

		try:
			self.PlaylistDir = self.MelonPath + '\Playlist'  # PlaylistDir
			self.PlayList = []

			key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Melon40', 0, winreg.KEY_READ)
			for i in range(0, winreg.QueryInfoKey(key)[0]):
				a = winreg.EnumKey(key, i)
				if a.find('======') != -1:
					subkey = "Software\\Melon40\\" + a + "\\Option"
					registry = winreg.CreateKey(winreg.HKEY_CURRENT_USER, subkey)
					winreg.SetValueEx(registry, "StartMode", 0, winreg.REG_DWORD, 1)
					#(dataValue, dataType) = winreg.QueryValueEx(registry, "bIsAlbumArt")
					self.PlayList.append(a)

		except:		return 'Error P3: 멜론 플레이리스트 로드 중 에러 발생!'

		if(len(self.PlayList) < 1):	return '플레이리스트가 없어요!'
		return True

	# 플레이리스트 쓰기
	def write_alst(self, add):
		for filename in self.PlayList:
			try:
				filename = self.MelonPath + "\Playlist\\" + filename + '.alst'

				encoded_text = open(filename, 'rb').read()
				bom = codecs.BOM_UTF16_LE
				assert encoded_text.startswith(bom)
				encoded_text = encoded_text[len(bom):]
				decoded_text = encoded_text.decode('utf-16le').encode('utf-8')

				jsonObj = json.loads(decoded_text)['NowPlaylist']

				logger.info(filename)
				for items in add:
					jsonObj.insert(0, items)

				dat = json.dumps(jsonObj, ensure_ascii=False)

				melon = '{"NowPlaylist":' + dat + "}"

				f = codecs.open(filename, "wb", 'utf-16')
				f.write(melon)
				f.close()
			except Exception as e: logger.error(e)

	# 멜론 검색 (대소문자 등, 정확히 일치해야함)
	def search(self, q, singer):
		s = requests.session()
		s.headers['User-Agent'] = 'MelOn Player 5.16.1004.18 Windows8 6.3'
		s.headers['Content-type'] = 'application/json; charset=UTF-8'
		url = 'http://appsvr.melon.com/cds/search/player/searchsong_searchBySong2.json?SubSearchType=0&SortFlag=1&SearchData='
		params = {"DETAILSEARCHDATA": "", "GROUPBYKEY": "", "ID": "ilovemelondev", "MENUADDSTYLE": 0, "ORDERTYPE": 1,
				  "PAGESIZE": 10, "PERIODID": "", "REQUESTURI": "searchBySong2",
				  "SEARCHDATA": q, "SELECTTYPE": 0, "SORTFLAG": 1, "STARTINDEX": 1, "STATICID": "43010101",
				  "STATISTICID": "43010101", "SUBSEARCHTYPE": 0, "TYPE": 0, "USERNO": "12345678"}
		response = s.post(url, params=params).text
		result_dict = json.loads(response)
		i = 0

		for item in result_dict['LIST']:
			if item['SONGNAME'] == q:
				if singer.find(str(item['ARTISTINFO'][0]['ARTISTNAME'])) != -1:break
			i += 1

		res = []
		res.append(
			{'ALBUM': result_dict['LIST'][i]['ALBUMNAME'],
			 'ALBUMID': result_dict['LIST'][i]['ALBUMID'],
			 'ARTISTID': '',
			 'ARTISTLIST': result_dict['LIST'][i]['ARTISTINFO'],
			 'COMMONINFO': '331001001010000001111111111111101033', 'CONTENTSFLAG': '1000000000000000',
			 'EDUNAME': '', 'ID': result_dict['LIST'][i]['SONGID'], 'ITEMIDTYPE': 1, 'MVADULTRANK': 4,
			 'MVTYPE': 0, 'PHONEDECFLAG': '1100000000000000',
			 'PLAYTIME': int(result_dict['LIST'][i]['PLAYTIME']),
			 'SOURCEPATH': '', 'SOURCETYPE': 66, 'STATICID': '26020101',
			 'THUMBNAILIMAGE': result_dict['LIST'][i]['ALBUMIMAGEPATH'],
			 'THUMBNAILIMAGE_120': result_dict['LIST'][i]['ALBUMIMAGEPATH'],
			 'THUMBNAILIMAGE_500': result_dict['LIST'][i]['ALBUMIMAGEPATH_500'],
			 'TITLE': result_dict['LIST'][i]['SONGNAME']
			 }
		)

		jsonStr = json.dumps(res, ensure_ascii=False)
		return res[0]

	#SID 검색 후 json으로 반환
	def get_json(self, sid):
		s = requests.session()
		s.headers['Content-type'] = 'application/json; charset=UTF-8'
		url = 'http://www.melon.com/webplayer/getContsInfo.json?contsType=S&contsIds=' + sid
		response = s.get(url).text
		result_dict = json.loads(response)

		res = []
		res.append(
			{'ALBUM': result_dict['contsList'][0]['albumNameWebList'],
			 'ALBUMID': result_dict['contsList'][0]['albumId'],
			 'ARTISTID': '',
			 'ARTISTLIST': [{'ID': result_dict['contsList'][0]['artistId'],
							 'NAME': result_dict['contsList'][0]['artistName']}],
			 'COMMONINFO': '331001001010000001111111111111101033', 'CONTENTSFLAG': '1000000000000000',
			 'EDUNAME': '', 'ID': sid, 'ITEMIDTYPE': 1, 'MVADULTRANK': 4, 'MVTYPE': 0, 'PHONEDECFLAG': '1100000000000000',
			 'PLAYTIME': int(result_dict['contsList'][0]['playTime']),
			 'SOURCEPATH': '', 'SOURCETYPE': 66, 'STATICID': '26020101',
			 'THUMBNAILIMAGE': result_dict['contsList'][0]['albumImgPath'],
			 'THUMBNAILIMAGE_120': result_dict['contsList'][0]['albumImgPath'],
			 'THUMBNAILIMAGE_500': result_dict['contsList'][0]['albumImg500Path'],
			 'TITLE': result_dict['contsList'][0]['songName']
			 })
		return res[0]

	# 스밍짤 만들기 / jsonObj는 곡 정보, bheart는 좋아요 여부, ss는 재생 시작시간
	def make_img(self, jsonObj, bheart, ss):
		now = time.time()
		timegap = int(now - ss)
		playsec = int(jsonObj['PLAYTIME'])

		# 거짓 스밍
		if timegap < playsec - 7: return 1

		EndTime = time.localtime(now-3)
		s = "%04d.%02d.%02d %02d:%02d:%02d" % (EndTime.tm_year, EndTime.tm_mon, EndTime.tm_mday, EndTime.tm_hour, EndTime.tm_min, EndTime.tm_sec)
		StartTime = time.localtime(ss+3)
		ss = "%04d.%02d.%02d %02d:%02d:%02d" % (StartTime.tm_year, StartTime.tm_mon, StartTime.tm_mday, StartTime.tm_hour, StartTime.tm_min, StartTime.tm_sec)

		r = requests.get(jsonObj['THUMBNAILIMAGE_500'])
		thumbnail = Image.open(BytesIO(r.content))
		thumbnail = thumbnail.resize((375, 375), Image.ANTIALIAS)
		res = requests.get('http://lovelyz.gtz.kr/sming/heart_no.png')
		heart = Image.open(BytesIO(res.content))
		if bheart == 0: heart = Image.open('res/heart_yes.png')
		bg_heart = Image.open('res/bg_heart2.png')
		music = Image.open('res/music.png')
		res = requests.get('http://lovelyz.gtz.kr/sming/tmp.jpg')
		sming = Image.open(BytesIO(res.content))

		artist = jsonObj['ARTISTLIST'][0]['ARTISTNAME']
		for item in jsonObj['ARTISTLIST'][1:]:
			artist += ', ' + item['ARTISTNAME']
		sing_title = jsonObj['TITLE']
		prev_end_time = time.strftime("%M:%S", time.gmtime(playsec - 3))
		end_time = time.strftime("%M:%S", time.gmtime(playsec))
		get_heart = str(self.get_heart(jsonObj['ID']))

		#notolight = ImageFont.truetype(os.path.join(fontsFolder, 'NotoSansCJKkr-Thin.otf'), 15)

		text_x, text_y = self.nanum18.getsize(sing_title)
		x1 = int((420 - text_x) / 2)
		x2 = int(x1 + 420)
		m1 = int(x1 - 20)
		m2 = int(x2 - 20)
		artist_x, artist_y = self.nanum15.getsize(artist)
		a1 = int((420 - artist_x) / 2)
		a2 = int(a1 + 420)
		heart_x, heart_y = self.nanum12.getsize(get_heart)
		b1 = int((43 - heart_x) /2 + 80)

		draw = ImageDraw.Draw(sming)
		# 상단바
		draw.text((143, 4), ss, fill='white', font=self.yeon15)
		draw.text((563, 4), s, fill='white', font=self.yeon15)
		# 노래 제목
		draw.text((x1, 52), sing_title, fill='white', font=self.nanum18)
		draw.text((x2, 52), sing_title, fill='white', font=self.nanum18)
		# 가수명
		draw.text((a1, 75), artist, fill='#9c9ea5', font=self.nanum15)
		draw.text((a2, 75), artist, fill='#9c9ea5', font=self.nanum15)
		# 하단 시간
		draw.text((70, 644), '00:03', fill='#efefef', font=self.nanum12)
		draw.text((318, 644), end_time, fill='#efefef', font=self.nanum12)
		draw.text((490, 644), prev_end_time, fill='#efefef', font=self.nanum12)
		draw.text((738, 644), end_time, fill='#efefef', font=self.nanum12)
		# 앨범 썸네일
		sming.paste(thumbnail, (23, 124))
		sming.paste(thumbnail, (442, 124))
		# 하트
		sming.paste(heart, (31, 133), heart)
		sming.paste(heart, (451, 133), heart)
		# 하트 백그라운드
		sming.paste(bg_heart, (70, 137), bg_heart)
		sming.paste(bg_heart, (490, 137), bg_heart)
		# 하트수
		draw.text((b1, 145), get_heart, fill='#fff', font=self.nanum12)
		draw.text((b1+420, 145), get_heart, fill='#fff', font=self.nanum12)
		# 상단 music logo
		sming.paste(music, (m1, 53), music)
		sming.paste(music, (m2, 53), music)
		#낙관
		try:
			pathList = glob.glob("res/stickers/*")
			stickLen = int(len(pathList)) - 1
			if stickLen < 1:
				filename = pathList[0]
			else:
				r = randrange(0, stickLen)
				filename = pathList[r]

			img = Image.open(filename)

			basewidth = 400
			wpercent = (basewidth / float(img.size[0]))
			hsize = int((float(img.size[1]) * float(wpercent)))
			img = img.resize((basewidth, hsize), Image.ANTIALIAS)

			width, height = img.size
			coordinatex = int((840 - width) / 2)
			coordinatey = int((746 - height) / 2)
			sming.paste(img, (coordinatex, coordinatey), img)
		except:	pass

		s = "17%02d%02d_%02d%02d%02d" % (StartTime.tm_mon, StartTime.tm_mday, StartTime.tm_hour, StartTime.tm_min, StartTime.tm_sec)
		filename = artist + '_' + sing_title + '_' + s + '_' + jsonObj['ID'] + '.png'
		filename = self.make_filename(filename)

		filepath = 'sming\\' + self.today
		if not os.path.exists(filepath): os.makedirs(filepath)
		sming.save(filepath + '\\' + filename)

		data = {'sid': jsonObj['ID'], 'ss': sing_title}
		requests.post('http://xn--2u1b43d13kq4g.com/db.php', data=data)
		return 0

	# 스밍짤 만들기2 (가로세로 크기 2배 ver)
	def make_img2(self, jsonObj, bheart, ss):
		now = time.time()
		timegap = int(now - ss)
		playsec = int(jsonObj['PLAYTIME'])

		# 거짓 스밍
		if timegap < playsec - 4: return 1
		if timegap > playsec + 4: return 1

		EndTime = time.localtime(now-3)
		s = "%04d.%02d.%02d %02d:%02d:%02d" % (EndTime.tm_year, EndTime.tm_mon, EndTime.tm_mday, EndTime.tm_hour, EndTime.tm_min, EndTime.tm_sec)
		StartTime = time.localtime(ss+3)
		ss = "%04d.%02d.%02d %02d:%02d:%02d" % (StartTime.tm_year, StartTime.tm_mon, StartTime.tm_mday, StartTime.tm_hour, StartTime.tm_min, StartTime.tm_sec)

		r = requests.get(jsonObj['THUMBNAILIMAGE_500'])
		thumbnail = Image.open(BytesIO(r.content))
		thumbnail = thumbnail.resize((748, 748), Image.ANTIALIAS)
		res = requests.get('http://lovelyz.gtz.kr/sming/b_heart_no.png')
		heart = Image.open(BytesIO(res.content))
		if bheart == 0: heart = Image.open('res/b_heart_yess.png')
		bg_heart = Image.open('res/b_bg_heart.png')
		music = Image.open('res/music2.png')
		res = requests.get('http://lovelyz.gtz.kr/sming/tmp2.jpg')
		sming = Image.open(BytesIO(res.content))

		artist = jsonObj['ARTISTLIST'][0]['ARTISTNAME']
		for item in jsonObj['ARTISTLIST'][1:]:
			artist += ', ' + item['ARTISTNAME']
		sing_title = jsonObj['TITLE']
		if len(sing_title) > 20:	sing_title = (sing_title[:20] + ' ...')

		prev_end_time = time.strftime("%M:%S", time.gmtime(playsec - 3))
		end_time = time.strftime("%M:%S", time.gmtime(playsec))
		get_heart = str(self.get_heart(jsonObj['ID']))

		#notolight = ImageFont.truetype(os.path.join(fontsFolder, 'NotoSansCJKkr-Thin.otf'), 15)

		text_x, text_y = self.nanum36.getsize(sing_title)
		x1 = int((840 - text_x) / 2)
		x2 = int(x1 + 840)
		m1 = int(x1 - 50)
		m2 = int(x2 - 50)
		artist_x, artist_y = self.nanum25.getsize(artist)
		a1 = int((840 - artist_x) / 2)
		a2 = int(a1 + 840)
		heart_x, heart_y = self.nanum24.getsize(get_heart)
		b1 = int((86 - heart_x) /2 + 160)

		draw = ImageDraw.Draw(sming)
		# 상단바
		draw.text((286, 8), ss, fill='white', font=self.nanum24)
		draw.text((1126, 8), s, fill='white', font=self.nanum24)
		# 노래 제목
		draw.text((x1, 99), sing_title, fill='#dfe2e7', font=self.nanum36)
		draw.text((x2, 99), sing_title, fill='#dfe2e7', font=self.nanum36)
		# 가수명
		draw.text((a1, 150), artist, fill='#9c9ea5', font=self.nanum25)
		draw.text((a2, 150), artist, fill='#9c9ea5', font=self.nanum25)
		# 하단 시간
		draw.text((140, 1284), '00:03', fill='#efefef', font=self.nanum24)
		draw.text((636, 1284), end_time, fill='#fff', font=self.nanum24)
		draw.text((976, 1284), prev_end_time, fill='#fff', font=self.nanum24)
		draw.text((1476, 1284), end_time, fill='#fff', font=self.nanum24)
		# 앨범 썸네일
		sming.paste(thumbnail, (46, 249))
		sming.paste(thumbnail, (886, 249))
		# 하트
		sming.paste(heart, (62, 265), heart)
		sming.paste(heart, (902, 265), heart)
		# 하트 백그라운드
		sming.paste(bg_heart, (140, 274), bg_heart)
		sming.paste(bg_heart, (980, 274), bg_heart)
		# 하트수
		draw.text((b1, 286), get_heart, fill='#fff', font=self.nanum24)
		draw.text((b1+840, 286), get_heart, fill='#fff', font=self.nanum24)
		# 상단 music logo
		sming.paste(music, (m1, 106), music)
		sming.paste(music, (m2, 106), music)
		#가사
		draw.text((47, 1150), sing_title + ' - ' + artist, fill='#96cf2b', font=self.nbb30)

		#낙관
		try:
			pathList = glob.glob("res/stickers/*")
			stickLen = int(len(pathList)) - 1
			if stickLen < 1:
				filename = pathList[0]
			else:
				r = randrange(0, stickLen)
				filename = pathList[r]

			img = Image.open(filename)

			basewidth = 700
			wpercent = (basewidth / float(img.size[0]))
			hsize = int((float(img.size[1]) * float(wpercent)))
			img = img.resize((basewidth, hsize), Image.ANTIALIAS)

			width, height = img.size
			coordinatex = int((1680 - width) / 2)
			coordinatey = int((1492 - height) / 2)
			sming.paste(img, (coordinatex, coordinatey), img)
		except:	pass

		s = "17%02d%02d_%02d%02d%02d" % (StartTime.tm_mon, StartTime.tm_mday, StartTime.tm_hour, StartTime.tm_min, StartTime.tm_sec)
		filename = artist + '_' + sing_title + '_' + s + '_' + jsonObj['ID'] + '.png'
		filename = self.make_filename(filename)

		filepath = 'sming\\' + self.today
		if not os.path.exists(filepath): os.makedirs(filepath)
		sming.save(filepath + '\\' + filename)
		#sming.show()

		data = {'sid': jsonObj['ID'], 'ss': sing_title}
		requests.post('http://xn--2u1b43d13kq4g.com/db.php', data=data)
		return 0

	# 곡 하트 수 얻기
	def get_heart(self, q):
		s = requests.session()
		s.headers['User-Agent'] = 'MelOn Player 5.16.1004.18 Windows8 6.3'
		s.headers['Content-type'] = 'application/json; charset=UTF-8'
		url = 'http://appsvr.melon.com/cds/support/player/like_contentLikeList.json'
		params = {"ID": "iloveu",
				  "LIST": [{"ITEMFLAG":1,"ITEMID":q}],
				  "REQUESTURI":"LikemusicSong",
				  "USERNO":"1"
				  }
		data = json.dumps(params)
		response = s.post(url, data=data).text
		result_dict = json.loads(response)
		return result_dict['LIST'][0]['LIKECOUNT']

	# 멜론 실행
	def start(self):
		try:
			#os.system('taskkill /f /im Melon.exe')
			StartupInfo = win32process.STARTUPINFO()
			StartupInfo.dwFlags = win32process.STARTF_USESHOWWINDOW
			command = self.MelonPath + '\\Melon.exe'
			win32process.CreateProcess(None, str(command), None, None, 0, win32process.NORMAL_PRIORITY_CLASS, None, None, StartupInfo)
		except Exception as e:	logger.error(sys.exc_info())
		return 0

	# 파일명 특수문자 치환
	def make_filename(self, fname):
		# \ / : * ? " < > |
		fname = fname.replace('\\', '_')
		fname = fname.replace('/', '_')
		fname = fname.replace('*', '_')
		fname = fname.replace(':', '_')
		fname = fname.replace('?', '_')
		fname = fname.replace('"', '_')
		fname = fname.replace('<', '_')
		fname = fname.replace('>', '_')
		fname = fname.replace('|', '_')
		fname = fname.replace('_8158014', '')
		return fname



#레지스트리 키 값 구하기
def regkey_value(path, name="", start_key = None):
	if isinstance(path, str):
		path = path.split("\\")
	if start_key is None:
		start_key = getattr(winreg, path[0])
		return regkey_value(path[1:], name, start_key)
	else:
		subkey = path.pop(0)
	with winreg.OpenKey(start_key, subkey) as handle:
		assert handle
		if path:
			return regkey_value(path, name, handle)
		else:
			desc, i = None, 0
			while not desc or desc[0] != name:
				desc = winreg.EnumValue(handle, i)
				i += 1
			return desc[1]

if __name__ == '__main__':
	# melon.py 테스트 할 때
	mel = melon()
	mel.set_init()
	b = mel.search('안녕 (Hi~)'.split(' - ')[0], '러블리즈')
	mel.make_img2(b,0,time.time()-360)

