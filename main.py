# -*- coding: utf-8 -*-
'''
Created on 04/27/2017.
@author: Ryububuck
'''

import sys
import os, time
import melon, dc, dc_api
import schedule, threading
import requests, json, random, re
import logging, logging.handlers
import win32gui, win32api
import pyperclip
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtGui, uic

global Melhwnd
Melhwnd=0

global result_dict
url = 'https://raw.githubusercontent.com/Ryububuck/sminghae/master/sminghae.json'
res = requests.get(url).text
result_dict = json.loads(res)


# GUI 및 멜론
class gui:
	form_class = uic.loadUiType("main.ui")[0]
	class MyWindow(QMainWindow, form_class):
		def __init__(self):
			super(gui.MyWindow, self).__init__()
			self.setupUi(self)
			self.smingListTable.hide()
			self.clickable(self.imgControl).connect(self.btn_Melon_Play)

			self.gall = 'lovelyz'
			ver = '1.0'
			if ver < result_dict['min_ver']:
				QMessageBox.about(self, "안내", "<b>%s</b>" % (result_dict['update_memo']))
				os.system('explorer "' + result_dict['update_url'] + '"')
				sys.exit()
			try:	QMessageBox.about(self, "안내", "<b>%s</b>" % (result_dict['notice']))
			except:	pass

		#총공 클릭 시(sming_clicked)
		def btn_Get_DC(self, article_no):
			tmp_init = mel.set_init()
			if (tmp_init is not True):
				QMessageBox.about(self, "Melon Init Error", tmp_init)
				return 0

			global attackList
			attackList = dcinside.get_gall_sming_lists(article_no)
			i = 0

			self.smingListTable.show()
			self.tableWidget.hide()
			self.smingListTable.setRowCount(len(attackList))

			row = 0
			for item in attackList:
				self.smingListTable.setItem(row, 0, QTableWidgetItem(item['time']))
				self.smingListTable.setItem(row, 1, QTableWidgetItem(item['song_name']))
				self.smingListTable.setItem(row, 2, QTableWidgetItem(item['subject']))
				row += 1

			dat = []
			for items in attackList:
				if items['sids'][0] == '88888888':    continue
				dat.append(mel.get_json(items['sids'][0]))
			dat.reverse()
			#지금, 우리 추가
			#dat.append(mel.get_json('30395923'))
			mel.write_alst(dat)

			i = 0
			for item in attackList:
				schedule.every().day.at(item['time']).do(Postingjob, i)
				i += 1
			t = threading.Thread(target=Posting_Set)
			t.start()

			self.btn_Melon_Play()
			return 0

		#멜론 실행, 재생
		def btn_Melon_Play(self):
			tmp_init = mel.set_init()
			if (tmp_init is not True):
				QMessageBox.about(self, "Melon Init Error", tmp_init)
				return 0


			mel.start()
			# Melon Handle 얻기
			while(Melhwnd == 0):
				win32gui.EnumWindows(self.GetMelHwnd, None)
				time.sleep(1)

			while(win32gui.GetWindowText(Melhwnd) == ''): time.sleep(1)
			try:
				print("%X %s" % (Melhwnd, win32gui.GetWindowText(Melhwnd)))
			except:
				QMessageBox.about(self, "About This", """<b>Error Code: 03</b>
					멜론 프로세서를 찾을 수 없어요.
					위에 있는 초록색 버튼을 눌러 다시 멜론을 실행해보세요!""")
				return 0

			# 중복 스트리밍
			Checkhwnd = win32gui.FindWindow(0, '중복 스트리밍 알림')
			while (Checkhwnd != 0):
				try:
					win32api.SendMessage(btnYesHnd, 245, 0, 0)
					btnYesHnd = win32gui.FindWindowEx(Checkhwnd, 0, "Button", "예")
				except:
					break

			time.sleep(2)
			#재생
			tmpPause = win32gui.FindWindowEx(Melhwnd, 0, "Button", u"일시정지")
			while(tmpPause == 0):
				btnHnd = win32gui.FindWindowEx(Melhwnd, 0, "Button", u"재생")
				win32api.SendMessage(btnHnd, 245, 0, 0)
				time.sleep(0.5)
				tmpPause = win32gui.FindWindowEx(Melhwnd, 0, "Button", u"일시정지")

			MelonCapture = CaptureProcess(name=Melhwnd)
			MelonCapture.start()

		#총공 선택
		def slotItemClicked(self, y, x):
			#QMessageBox.information(self,"Row: " + str(item) + " |Column: " + str(item2))
			if x == 0:
				os.system('explorer http://gall.dcinside.com/' + dc_gall + '/' + self.tableWidget.item(y, 0).text())
				return 0
			self.btn_Get_DC(self.tableWidget.item(y, 0).text())

		#멜론 메인 핸들 찾기
		def GetMelHwnd(self, hwnd, lParam):
			if win32gui.IsWindowVisible(hwnd):
				if 'Melon' == win32gui.GetWindowText(hwnd):
					global Melhwnd
					Melhwnd = hwnd

		#디시 로그인
		def btn_dc_login(self):
			global dc_id, dc_pw, dcinside, dc_sess, dc_no, dc_gall
			dc_id = self.inputid.text()
			dc_pw = self.inputpw.text()
			dc_gall = self.lineEdit.text()
			dc_no = 1 #1 유동(기본), 2 고닉

			if len(dc_id) < 1 or len(dc_pw) < 1 :
				QMessageBox.about(self, "Login Fail", "<b>아이디 또는 비밀번호를 입력</b>해주세요")
				return 0

			hangul = re.compile('[ ㄱ-ㅣ가-힣]+')
			result = hangul.findall(dc_pw)
			if(len(result) != 0):
				QMessageBox.about(self, "Login Fail", "비밀번호에 <b>한글</b>이 있어요")
				return 0

			if dc_gall == '': dc_gall = 'lovelyz'

			dcinside = dc.dc(dc_id, dc_pw, dc_gall)

			if self.chk.isChecked() is False:
				self.pushButton.setEnabled(False)
				dc_sess = dcinside.login()
				if dc_sess == 1:
					QMessageBox.about(self, "Login Fail", "로그인 실패")
					self.pushButton.setEnabled(True)
					return 0
				dc_no = 2

			print("Login Success")
			try:
				resultData = dc_api.get_sming(dc_gall, 2)
			except Exception as e:
				print(e)
				QMessageBox.about(self, "Load Fail", "<b>총공을 가져오는데 실패</b>했어요 8ㅅ8 <br> 갤러리명을 다시 확인해주세요!")
				self.pushButton.setEnabled(True)
				return 0
			self.tableWidget.setRowCount(int(len(resultData)))

			row = 0
			for item in resultData:
				self.tableWidget.setItem(row, 0, QTableWidgetItem(item['no']))
				self.tableWidget.setItem(row, 1, QTableWidgetItem(item['nickname']))
				self.tableWidget.setItem(row, 2, QTableWidgetItem(item['subject']))
				row += 1
			self.resize(460, 500)
			self.inputid.setEnabled(False)
			self.inputpw.setEnabled(False)
			self.lineEdit.setEnabled(False)
			self.pushButton.setEnabled(False)

		#수동 총공(직접 글쓰기, 지각 글쓰기)
		def sming_clicked(self, y, x):
			if x == 2:
				os.system('explorer http://gall.dcinside.com/' + attackList[y]['gall'])
				pyperclip.copy(attackList[y]['subject'])
				return 0
			if x == 0: Postingjob(y, 1)

		# 이미지(캡쳐 시작)가 클릭에 대응하도록
		def clickable(self, widget):
			class Filter(QObject):
				clicked = pyqtSignal()

				def eventFilter(self, obj, event):
					if obj == widget:
						if event.type() == QEvent.MouseButtonRelease:
							if obj.rect().contains(event.pos()):
								self.clicked.emit()
								# The developer can opt for .emit(obj) to get the object within the slot.
								return True
					return False

			filter = Filter(widget)
			widget.installEventFilter(filter)
			return filter.clicked

# 캡쳐 프로세스
class CaptureProcess(threading.Thread):
	# 캡쳐 실행
	def run(self):
		MelHwnd = int(threading.currentThread().getName())
		while(1):
			now = time.time()
			now_playing = win32gui.GetWindowText(MelHwnd)
			if(now_playing == 'Melon' or ''):
				time.sleep(0.5)
				continue

			logger.info('Playing : ' + now_playing)
			self.mel_init(MelHwnd)
			try:
				chkHeart = win32gui.FindWindowEx(MelHwnd, 0, "Static", u"선택시 좋아요 반영")
			except:
				logger.info('CaptureProcess End. Err Code: NOT_MELON')
				return 0

			while (1):
				a = win32gui.GetWindowText(MelHwnd)
				if a != now_playing:    break
				time.sleep(0.5)

			song_name = now_playing.split(' - ')[0]
			song_artist = now_playing.split(' - ')[1].split(' - ')[0]
			mel.make_img2(mel.search(song_name, song_artist), chkHeart, now)
		return 0

	#멜론 곡마다 좋아요
	def mel_init(self, hwnd):
		#중복 스트리밍
		Checkhwnd = win32gui.FindWindow(0, '중복 스트리밍 알림')
		if Checkhwnd != 0:
			while (1):
				time.sleep(0.5)
				try:
					btnYesHnd = win32gui.FindWindowEx(Checkhwnd, 0, "Button", "예")
					win32api.PostMessage(btnYesHnd, 513, 0, 0)
					win32api.PostMessage(btnYesHnd, 514, 0, 0)
				except: break

		#좋아요
		try:
			btnHnd = win32gui.FindWindowEx(hwnd, 0, "Static", "선택시 좋아요 반영")
			win32api.PostMessage(btnHnd, 513, 0, 0)
			time.sleep(0.3)
			btnHnd = win32gui.FindWindowEx(hwnd, 0, "Static", "선택시 좋아요 반영")
		except:	print('Like Click Fail')

		#확인
		try:
			Mel_ok = win32gui.FindWindow(0, 'Melon')
			btnHnd = win32gui.FindWindowEx(Mel_ok, 0, "Button", "확인")
			win32api.PostMessage(btnHnd, 513, 0, 0)
			time.sleep(0.4)
			win32api.PostMessage(btnHnd, 514, 0, 0)
		except: pass
		return 0

# 20초마다 총공타임인지 확인
def Posting_Set():
	while (1):
		schedule.run_pending()
		time.sleep(20)
	return 0

# 글쓰기(i는 총공순서, late=1이면 지각으로 글올리기)
def Postingjob(i, late=0):
	# 스밍짤 찾기, fname은 멜론 SID
	def searchSmingImg(fname):
		today = time.localtime()
		today = "17%02d%02d" % (today.tm_mon, today.tm_mday)
		dirname = "sming\\" + today
		filenames = os.listdir(dirname)
		for filename in filenames:
			full_filename = os.path.join(dirname, filename)
			if full_filename.find(fname) != -1:
				a = full_filename
		return a

	replaceSpecialString = '♥' + str(random.randrange(1,99))

	subject = attackList[i]['subject']

	#지각이면 제목 변경
	if late == 1:
		subject = re.sub("\(?특문\)?", '', subject)
		subject = re.sub("\(?설리.*총대\)?", '', subject)  # 설리>총대
		subject = re.sub("\(?설.*?총.*?\)?", '', subject)  # 설총
		subject = re.sub("\(?설리.*?첫글\)?", '', subject)  # 설리>첫글
		subject = re.sub("\(?설.*?첫.*?\)?", '', subject)  # 설첫
		subject = re.sub("\(?설리[xX]\)?", '', subject)  # 설리x

	try:
		f = open("res/tail.txt", 'r')
		arr = {
			'memo': f.readline() + result_dict['memo'],  # + '<font style=\"color:#fff\">' + str(random.random())
			'subject': subject.replace('특문', replaceSpecialString),
			'gall': attackList[i]['gall']
		}
		f.close()
	except:
		logger.info('Error Code: NW | 자동 글쓰기를 사용하지 않습니다. res/tail.txt 로드 실패')
		return 0

	msid = searchSmingImg(str(attackList[i]['sids'][0]))
	img = dcinside.upload_img(msid, arr)
	if dc_no == 2:
		dcinside.user_write(dc_sess, img, arr)
	else:
		dcinside.non_write(img, arr)

	'''
	try:
		msid = searchSmingImg(str(attackList[i]['sids'][0]))
		img = dcinside.upload_img(msid, arr)
		if dc_no == 2:
			dcinside.user_write(dc_sess, img, arr)
		else:
			dcinside.non_write(img, arr)
		#os.remove(msid)
	except Exception as e:
		logger.info('Error Code A1: 글 쓰기 에러, 스밍짤이 없어요')
		logger.error(e)
	'''


def log_set():
	today = time.localtime()
	todaystr = "17%02d%02d" % (today.tm_mon, today.tm_mday)

	global logger
	logger = logging.getLogger('mylogger')
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

def main():
	log_set()
	global mel
	mel = melon.melon()

	app = QApplication(sys.argv)
	myWindow = gui.MyWindow()
	myWindow.show()
	sys.exit(app.exec_())

if __name__ == '__main__': main()