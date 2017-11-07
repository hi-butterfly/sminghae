import requests, json, sys, time
from pprint import pprint
from hashlib import sha256
from base64 import b64encode
from requests_toolbelt.multipart.encoder import MultipartEncoder


def get_app_id():
	global s
	s = requests.session()
	s.headers['User-Agent'] = 'dcinside.app'
	s.headers['Referer'] = 'http://www.dcinside.com'
	s.headers['Content-Type'] = 'application/x-www-form-urlencoded'

	t = time.localtime()
	app_key = 'dcArdchk_' + '%04d%02d%02d%02d' % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour)
	app_key = sha256(app_key.encode('ascii')).hexdigest()

	url = 'https://dcid.dcinside.com/join/mobile_app_key_verification_3rd.php'
	tmp = s.post(url, data="value_token=" + app_key + "&signature=ReOo4u96nnv8Njd7707KpYiIVYQ3FlcKHDJE046Pg6s=&pkg=com.dcinside.app&vCode=10808&vName=1.8.8")

	global app_id
	app_id = json.loads(tmp.text)
	app_id = app_id[0]['app_id']

	print('app_id: ', app_id)
	return app_id

def redirect(s):
	hash = b64encode(bytes(s.encode("utf8")))
	url = 'http://m.dcinside.com/api/redirect.php?hash=' + hash.decode('utf8')
	return url

class article:
	def get_info(gall, no):
		url = 'http://m.dcinside.com/api/gall_view.php?id=' + gall + '&page=1&no=' + str(no) + '&app_id=' + app_id
		tmp = s.get(url)
		json_data = json.loads(tmp.text)
		return json_data

	def read(gall, no):
		hash = str('http://m.dcinside.com/api/view2.php?id=' + gall + '&page=1&confirm_id=1234&no=' + str(no) + '&app_id=' + app_id)
		tmp = s.get(redirect(hash))
		json_data = json.loads(tmp.text)
		return json_data

	def write(gall, subject, memo, user):
		url = 'http://upload.dcinside.com/_app_write_api.php'
		fields = {
			'app_id': app_id,
			'id': gall,
			'mode': 'write',
			'subject': subject,
			'name': user['name'],
			'memo_block[0]': memo
		}

		if user['stype'] == 'C':	fields['password'] = user['password']
		elif user['stype'] == 'A': fields['user_id'] = user['user_id']

		multipart_data = MultipartEncoder(fields)
		#name="app_id"\n\n" + this.appid + "\n--e6e6d3aa-603d-4cdd-9e6b-a83420e04aed\nContent-Disposition: form-data; name=\"mode\"\n\nwrite\n--e6e6d3aa-603d-4cdd-9e6b-a83420e04aed\nContent-Disposition: form-data; name=\"subject\"\n\n" + this.myListView1.Items[index1].SubItems[3].Text + "\n--e6e6d3aa-603d-4cdd-9e6b-a83420e04aed\nContent-Disposition: form-data; name=\"user_id\"\n\n" + Form2.user_id + "\n--e6e6d3aa-603d-4cdd-9e6b-a83420e04aed\n";
		res = s.post(url, data=multipart_data, headers={'Content-Type': multipart_data.content_type})
		print(res.text)

def login(id, pw):
	url = 'https://dcid.dcinside.com/join/mobile_app_login.php'
	tmpHead = {'Host': 'dcid.dcinside.com'}
	tmp = s.post(url, data="user_id=" + id + "&user_pw=" + pw, headers=tmpHead)
	json_data = json.loads(tmp.text)
	return json_data[0]

#목록 가져오기
def get_list(gall, page):
	hash = 'http://m.dcinside.com/api/gall_list.php?id=' + gall + '&page=' + str(page) + '&app_id=' + app_id
	tmp = s.get(redirect(hash))
	json_data = json.loads(tmp.text)
	return json_data

#내용 검색하기
def dc_search(gall, page, content):
	hash = 'http://m.dcinside.com/api/gall_list.php?id=' + gall + '&page=' + str(page) + '&app_id=' + app_id + '&s_type=memo&serVal=' + content
	tmp = s.get(redirect(hash))
	json_data = json.loads(tmp.text)
	return json_data

def get_sming(gall, max_pages):
	page = 1
	lists = []
	while page < max_pages:
		hash = 'http://m.dcinside.com/api/gall_list.php?id=' + gall + '&page=' + str(page) + '&app_id=' + app_id + '&s_type=memo&serVal=SID+M%3A'
		tmp = s.get(redirect(hash))
		json_data = json.loads(tmp.text)

		for a in json_data[0]['gall_list']:
			link = a['no']
			nickname = a['name']
			subject = a['subject']
			date = a['date_time']
			lists.append({'no': link, 'subject': subject, 'date': date, 'nickname': nickname})
		page += 1
	return lists

app_id = get_app_id()

def main():
	gall = 'lovelyz'
	no = '3788'

	user = login('kinghappy', 'gina9629')
	pprint(get_sming(gall, 2))
	#pprint(dc_search(gall, 1, 'SID%20M%3A'))
	#user = {'name': 'ㅇㅇ', 'password': 'tagall', 'stype': 'C'}
	#article.write(gall, 'test', 'testing..', user)

if __name__ == '__main__': main()