#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup
from time import sleep
import random
import os.path
from urllib.error import HTTPError
import argparse
import random
import json

import requests
from requests.auth import HTTPProxyAuth


proxies = []

safe_headers = {
	'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0'
}

debug_print = True

parser_settings = { 'last_park' : {}, 'percentage' : {} }
settings_filename = 'settings.json'

# загрузить текущие настройки из файла
def load_settings():
	global parser_settings
	try:
		with open(settings_filename, "r") as ifs:
			parser_settings = json.load(ifs)
		if 'last_park' not in parser_settings.keys():
			parser_settings['last_park'] = {}
		if 'percentage' not in parser_settings.keys():
			parser_settings['percentage'] = {}
	except:
		print(f"cannot read data from {settings_filename}")
	return    

# сохранить текущие настройки в файл
def save_settings(country:str, park:str, percentage:float=0.0):
	parser_settings['last_park'][country] = park
	parser_settings['percentage'][country] = round(percentage,2)
	with open(settings_filename, "w") as ofs:
		json.dump(parser_settings, ofs)
	return

# последний обработанный парк в текущий или прошлый запуск
def latest_processed_park(country:str)->str:
	if country in parser_settings['last_park'].keys():
		return parser_settings['last_park'][country]
	return None

def country_url(country):
	country = country.lower()
	parks = [ 
		(['ru', 'russia', 'рф', 'россия'], 'https://www.parkrun.ru'),
		(['de', 'germany', 'deutschland', 'германия'], 'https://www.parkrun.com.de'),
		(['no', 'norway', 'norge', 'норвегия'],'https://www.parkrun.no'),
		(['uk', 'england', 'англия'],'https://www.parkrun.org.uk'),
		(['au', 'australia', 'австралия'],'https://www.parkrun.com.au'),
		(['at', 'austria', 'австрия'],'https://www.parkrun.co.at'),
		(['ca', 'canada', 'канада'],'https://www.parkrun.ca'),
		(['dk', 'denmark', 'дания'],'https://www.parkrun.dk'),
		(['fi', 'finland', 'suomi', 'финляндия'],'https://www.parkrun.fi'),
		(['fr', 'france', 'франция'],'https://www.parkrun.fr'),
		(['it', 'italy', 'италия'],'https://www.parkrun.it'),
		(['ie', 'ireland', 'ирландия'],'https://www.parkrun.ie'),
		(['jp', 'japan', 'япония'],'https://www.parkrun.jp'),
		(['my', 'malaysia', 'малайзия'],'http://www.parkrun.my'),
		(['nl', 'netherlands', 'нидерланды'],'https://www.parkrun.co.nl'),
		(['nz', 'new zealand', 'новая зеландия'],'https://www.parkrun.co.nz'),
		(['pl', 'poland', 'польша'],'https://www.parkrun.pl'),
		(['sg', 'singapore', 'сингапур'],'https://www.parkrun.sg'),
		(['za', 'south africa', 'южная африка'],'https://www.parkrun.co.za'),
		(['se', 'sweden', 'швеция'],'https://www.parkrun.se'),
		(['us', 'usa', 'сша'],'https://www.parkrun.us'),
		(['lt', 'lithuania', 'литва'],'https://www.parkrun.lt')
	]
	for park in parks:
		if country in park[0]:
			return park[1]
	return 'https://www.parkrun.org'


def read_url(url, forceReload = False):
	cache_dir = 'urlcache'
	file_name = url.replace(':', '_').replace('/', '_').replace('=', '_').replace('?', '_')
	file_path = os.path.join(cache_dir, file_name)
	if (not forceReload ) and os.path.exists(file_path):
		if debug_print:
			print('reading ',url,' from cache')
		tmpfile = open(file_path, 'r')
		return tmpfile.read()
	sleep(0.05 * random.randint(60, 100))
	req = urllib.request.Request( url, data=None, headers=safe_headers)
	try:
		html = urlopen(req)
	except HTTPError as err:
		print('catch exception in urlopen error code = ' + str(err.code))
		return None 
	page = str(html.read().decode('utf-8'))
	
	# proxy_data = random.choice(proxies) if proxies else None
	# proxy = {
	# 	'http' : f"http://{proxy_data['ip']}:{proxy_data['port']}",
	# 	'https' : f"http://{proxy_data['ip']}:{proxy_data['port']}"
	# }
	# auth = HTTPProxyAuth(proxy_data['username'], proxy_data['password'])
	# s = requests.Session()
	# s.proxies = proxy
	# s.auth = auth
	# s.headers = safe_headers
	# try:
	# 	r = s.get(url=url.replace('https:', 'http:'))
	# 	page2 = str(r.text.decode('utf-8'))
	# 	print(page2)
	# except Exception as ex:
	# 	print(str(ex))
	# pass

	tmpfile = open(file_path, 'w')
	tmpfile.write(page)
	tmpfile.close()
	if debug_print:
		print('saving ',url,' to cache as ', file_name)
	return page


def get_all_parks(country, latest = False, reloadHistory = False):
	park_url = country_url(country) + '/special-events/'
	park_page = read_url(park_url, reloadHistory)
	bs = BeautifulSoup(park_page, 'html.parser')
	parks=[]
	if records_table := bs.find_all(id='results'):
		rows = records_table[0].find_all('tr')
		for row in rows:
			refs = row.find_all('a')
			if len(refs) > 0:
				parkref = str(refs[0])
				parkname = (parkref.split('/'))[3]
				parks.append(parkname)
			pass
		pass
	pass
	return parks
	

def all_countries():
	countries = [
#	'ru', 
	'it','de', 'no', 'au', 'at', 'se',
	'ca','dk','fi','fr','jp','my', 
	'nl','nz', 'pl','sg', 'za', 'us','uk','ie','lt' ]
	return countries 
	
		
def all_parks():
	parks = []
	for country in all_countries:
		parks = parks + get_all_parks(country)
	return parks


def park_history(country, park, reloadHistory = False):
	parkurl = country_url(country) + "/" + park + '/results/eventhistory/'
	history_page = read_url(parkurl, reloadHistory)
	if not history_page:
		return []
	bs = BeautifulSoup(history_page, 'html.parser')
	history_table = bs.tbody
	events = []
	if history_table is None:
		print('cannot read tbody for ', park)
	else:
		rows = history_table.findAll('tr')
		for row in rows:
			if not row.attrs:
				return []
			event_num = row['data-parkrun']
			datefmt = row['data-date'].split('-')
			event_date = datefmt[0]+datefmt[1]+datefmt[2] 
			runners = row['data-finishers']
			volunteers = row['data-volunteers']
			events.append((event_date, event_num, runners, volunteers))
		pass
	return events
	
def parkrun_news(country, park, year):
	news = []
	news_url = country_url(country) + "/" + park + "/news/" + str(year)
	bs = BeautifulSoup(read_url(news_url), 'html.parser')
	atricles = bs.findAll('article')
	for article in atricles:
		entries = article.findAll(class_ = 'entry-content')
		for entry in entries:  
			print(entry) 
			print('-----------------------------------------------------------')
	return news	
	
	
def country_history(country):
	events = []
	parks = get_all_parks(country)
	for parkname in parks:
		if debug_print:
			print(parkname)
		eventhistory = park_history(country, parkname)
		if len(eventhistory) > 0 : 
			events.append((parkname, len(eventhistory), eventhistory[-1][0], eventhistory[0][0]))
	return events
	
	
def parkrun_results(country, park, num, reloadResults=False):
	results = []
	try:
		event_date = '19761220'
		results_url = country_url(country) + "/" + park + "/results/" + str(num)
		bs = BeautifulSoup(read_url(results_url, reloadResults), 'html.parser')
		if (bs is None) or (bs.body is None) or (bs.body.h3 is None):
			print('cannot read results for ', park, '№', num, ' object is None')
			return results
		pass
		if bs.body.h3:
			title = bs.body.h3.findAll('span')
			if (title) and (len(title) > 0) and (len(title[0].contents) > 0):
				date_str = title[0].contents[0].split('/')
				event_date = date_str[2]+date_str[1]+date_str[0]
			pass
		pass
		results_table = bs.tbody
		if results_table is None:
			print('cannot read results for ', park, '№', num)
		else:
			rows = results_table.findAll('tr')
			for row in rows:
				pos = row['data-position']
				name = row['data-name']
				age_group = row['data-agegroup']
				age_grade = row['data-agegrade']
				best_result = row['data-achievement']
				data_runs = row['data-runs']
				if ( len(data_runs)==0 ) or (data_runs=='0'):
					results.append((event_date, park, str(num), pos, name))
				else:
					runner_id=''
					refs=row.findAll('a')
					for ref in refs:
						refhref = ref['href']
						if 'parkrunner' in refhref:
							runner_id = refhref.split('/')[-1]
							break
						pass
						if 'athleteNumber=' in refhref:				# 
							runner_id = refhref.split('=')[1]		# старый формат
							break
						pass
					pass									#
					fields = row.findAll('td')
					time_str = ''
					gender_str = ''
					gender_pos = ''
					for field in fields:
						if 'Results-table-td--time' in field['class']:
							if field.contents[0] and field.contents[0].contents:
								time_str = field.contents[0].contents[0]
								timebuf = time_str.split(':')
								if len(timebuf) == 3:
									minutes = int(timebuf[0])*60 + int(timebuf[1])
									time_str = str(minutes)+':'+timebuf[2]
								pass
							pass
						if 'Results-table-td--F' in field['class']:
							gender_str = 'F'
							gender_pos=field.findAll('div')[1].contents[0]
						pass
						if 'Results-table-td--M' in field['class']:
							gender_str = 'M' 
							gender_pos=field.findAll('div')[1].contents[0]
						pass
					if best_result == '':
						best_result = row.findAll('div')[-1].contents[-1]
					results.append((event_date, park, str(num), pos, 'A'+runner_id, name, time_str, gender_str, gender_pos, age_group, age_grade, best_result, data_runs))
				pass
			pass
		pass
	except Exception as e:
		print(f"exeption: {str(e)}")	
	return results
	
def parkrun_volunteers(country, park, num, reloadVolunteers=False):
	volunteers = []
	try:
		event_date = '19761220'
		results_url = country_url(country) + "/" + park + "/results/" + str(num)
		bs = BeautifulSoup(read_url(results_url, reloadVolunteers), 'html.parser')
		if bs.body.h3:
			title = bs.body.h3.findAll('span')
			if (title) and (len(title) > 0) and (len(title[0].contents) > 0):
				date_str = title[0].contents[0].split('/')
				event_date = date_str[2]+date_str[1]+date_str[0]
		ptags = bs.find_all(name='p')
		for ptag in ptags:
			classarrt = ptag.get('class')
			if not classarrt or ( not 'paddedb' in classarrt ):
				continue
			pass
			if refs := ptag.findAll('a'):
				for ref in refs:
					refhref = ref['href']
					if 'parkrunner' in refhref:
						runner_id = 'A'+refhref.split('/')[-1]
						runner_name = ref.text
						volunteers.append((event_date, park, str(num), runner_id, runner_name))
					pass
				pass
			pass
		pass
	except Exception as e:
		print(f"exeption: {str(e)}")	
	return volunteers 
	
	
def parkrun_results_by_date(country, park, event_date, reloadHistory = False):
	results = []
	events = park_history(country, park, reloadHistory)
	for info in events:
		if info[0] == event_date:
			results = parkrun_results(country, park, info[1])
			if not results:
				results = parkrun_results(country, park, info[1], True)
			break
	return results

	
def parkrun_volonteers_by_date(country, park, event_date, reloadHistory = False):
	volonteers = []
	events = park_history(country, park, reloadHistory)
	for info in events:
		if info[0] == event_date:
			volonteers = parkrun_volunteers(country, park, info[1])
			break
	return volonteers


def print_country_history(country):
	events = country_history(country)
	for event in events:
		print(event[0], '\t',event[1], '\t',event[2], '\t',event[3]) 


def print_park_history(country, park):
	events = park_history(country, park)
	for event in events:
		print(event[0],'\t', park, '\t', event[1], '\t',event[2], '\t',event[3]) 

		
def print_parkrun_results(country, park, num):
	for result in parkrun_results(country, park, num):
		outstr = ''
		for field in result:
			outstr = outstr + str(field) + '\t'
		print(outstr)

def print_parkrun_results_by_date(country, park, event_date):
	for result in parkrun_results_by_date(country, park, event_date):
		outstr = ''
		for field in result:
			outstr = outstr + str(field) + '\t'
		print(outstr)		

def results_to_string(results):
	outstr=''
	for result in results:
		for field in result:
			outstr = outstr + str(field) + '\t'
		outstr = outstr + '\n'
	return outstr 	 
	
	
def create_country_dir(country, subdirname=None):
	dir_name = 'countries'
	if not os.path.isdir(dir_name):
		print('create directory ', dir_name)
		os.mkdir(dir_name)
	if not os.path.isdir(dir_name):
		print('cannot access directory ', dir_name)
		return None
	dir_name = dir_name = os.path.join(dir_name, country)
	if not os.path.isdir(dir_name):
		print('create directory ', dir_name)
		os.mkdir(dir_name)
	if not os.path.isdir(dir_name):
		print('cannot access directory ', dir_name)
		return None
	if subdirname:
		dir_name = os.path.join(dir_name, subdirname)
		if not os.path.isdir(dir_name):
			print('create directory ', dir_name)
			os.mkdir(dir_name)
		if not os.path.isdir(dir_name):
			print('cannot access directory ', dir_name)
			return None	
	return dir_name
	

def create_date_dir(country):
	return create_country_dir(country, 'date')
	

def create_volunteers_dir(country):
	return create_country_dir(country, 'volunteers')

			
def save_parkrun_results(country, park, reloadHistory = False):
	dir_name = create_country_dir(country)
	if not dir_name:
		return None
	filename = park + '_results.txt'
	file_path = os.path.join(dir_name, filename)
	if debug_print:
		print('results filename:', file_path)
	ofs = open(file_path, 'a+')
	ofs.seek(0)
	saved_results = ofs.read()
	#print('saved results:\n', saved_results, '\n') 
	events = park_history(country, park, reloadHistory)
	events_num = len(events)
	print('save ', events_num, 'results for ', park)
	for num in range(1, events_num+1):
		test_str = park + '\t' + str(num) + '\t1'
		if test_str in saved_results:
			print('results for ', park, num, ' already saved in ', file_path)
			continue
		resstr = results_to_string(parkrun_results(country, park, num))
		if not resstr:
			resstr = results_to_string(parkrun_results(country, park, num, True))
		print('save results for ', park, num, ' in ', file_path)
		ofs.write(resstr)
		
		
def save_parkrun_volunteers(country, park, reloadHistory = False, reloadVolunteers=False):
	dir_name = create_volunteers_dir(country)
	if not dir_name:
		return None
	filename = park + '_volunteers.txt'
	file_path = os.path.join(dir_name, filename)
	if debug_print:
		print('volunteer filename:', file_path)
	ofs = open(file_path, 'a+')
	ofs.seek(0)
	saved_volunteers = ofs.read()
	events = park_history(country, park, reloadHistory)
	events_num = len(events)
	print('save ', events_num, 'volunteers for ', park)
	for num in range(1, events_num+1):
		test_str = park + '\t' + str(num) + '\tA'
		if test_str in saved_volunteers:
			print('volunteers for ', park, num, ' already saved in ', file_path)
			continue
		resstr = results_to_string(parkrun_volunteers(country, park, num))
		if not resstr:
			if reloadVolunteers:
				resstr = results_to_string(parkrun_volunteers(country, park, num, True)) 
		if debug_print:
			if resstr:
				print('save volunteers for ', park, num, ' in ', file_path)
			else:
				print('no volunteers for ', park, num)
		ofs.write(resstr)			
		
		
def save_country_results(country, reloadHistory = False, reloadVolunteers=False, eventdate = None, continue_parsing=False):
	parks = get_all_parks(country, False, reloadHistory)
	parks_count = len(parks)
	last_park = latest_processed_park(country)
	for (indx, park) in enumerate(parks):
		if continue_parsing and last_park and (park < last_park):
			continue
		skip_park = False
		if 'juniors' in park:
			print(f"skip juniors event {park}")
			skip_park = True
		if (not skip_park) and eventdate and is_results_saved(country, park, eventdate):
			print(f"result for {eventdate} is already saved in {park} ")
			skip_park = True
		if not skip_park:
			save_parkrun_results(country, park, reloadHistory)
		pass
		save_settings(country=country, park=park, percentage=(indx / parks_count) if (parks_count != 0) else 0)
		#save_parkrun_volunteers(country, park, reloadHistory, reloadVolunteers)
	return
	
		
def save_results_by_date(country, eventdate, latest=False, skipNoResults=False):
	dir_name = create_date_dir(country)
	filename = str(eventdate) + '_' + country + '_results.txt'
	file_path = os.path.join(dir_name, filename)
	ofs = open(file_path, 'a+')
	ofs.seek(0)
	saved_results = ofs.read()
	parks = get_all_parks(country, latest, latest)
	for park in parks :
		test_str = str(eventdate) + '\t' + park
		if test_str in saved_results:
			print('results for ', park, eventdate, ' already saved in ', file_path)
			continue
		results = parkrun_results_by_date(country, park, eventdate)
		if (not results) and (not skipNoResults):
			results = parkrun_results_by_date(country, park, eventdate, True)
		if results:
			print('save results ', park, eventdate)
			ofs.write(results_to_string(results))
		else:
			print('no results for ', park, eventdate)
	ofs.close()

def remove_results_from_park(country, park, eventdate):
	dir_name = create_country_dir(country)
	if not dir_name:
		return None
	filename = park + '_results.txt'
	file_path = os.path.join(dir_name, filename)
	if debug_print:
		print('results filename:', file_path)
	ifs = open(file_path, 'r')
	results = []
	for row in ifs:
		if eventdate not in row:
			results.append(row)
	ifs.close()
	ofs = open(file_path, 'w')
	for result in results:
		ofs.write(result)
	ofs.close()
	
def remove_results_from_country(country, eventdate):
	parks = get_all_parks(country)
	for park in parks:
		remove_results_from_park(country, park, eventdate)
	dir_name = create_date_dir(country)
	filename = str(eventdate) + '_' + country + '_results.txt'
	file_path = os.path.join(dir_name, filename)
	ofs = open(file_path, 'w')
	ofs.write('')
	
def remove_results_by_date(eventdate):
	for country in all_countries():
		remove_results_from_country(country, eventdate)

def is_results_saved(country, park, eventdate):
	dir_name = create_country_dir(country)
	filename = park + '_results.txt'
	file_path = os.path.join(dir_name, filename)
	if os.path.exists(file_path):
		ifs = open(file_path)
		saved_results = ifs.read()
		test_str = str(eventdate) + '\t' + park
		if test_str in saved_results:
			return True	
	return False

def load_proxies(filename:str):
	if ifs := open(filename, 'r'):
		for row in ifs:
			data_flds = row.split(':')
			if data_flds and len(data_flds) > 3:
				proxies.append({
					'ip'  : data_flds[0],
					'port' : data_flds[1],
					'username' : data_flds[2],
					'password' : data_flds[3].replace('\n', '')
				})
			pass
		pass
	else:
		print(f"cannot load proxies from file {filename}")
	return

def main(args):
	argparser = argparse.ArgumentParser(description="download parkrun results")
	argparser.add_argument("--country", help="country results")
	argparser.add_argument("--date", help="results by date")
	argparser.add_argument("--proxylist", help="file with proxies")
	argparser.add_argument("-c", "--continue_parsing", help="continue previous task", action="store_true")
	args = argparser.parse_args()
	country_results = args.country if args.country else None
	event_date = args.date if args.date else None
	continue_parsing = args.continue_parsing
	proxyfile = args.proxylist if args.proxylist else 'proxies.txt'
	load_proxies(filename=proxyfile)
	load_settings()
	print(f"country={country_results}, date={event_date}")
	for country in all_countries():
		if (not country_results) or (country_results == country):
			save_country_results(country, True, True, eventdate=event_date, continue_parsing=continue_parsing)
		pass
	pass

	# last_event_date='20230923'
	
	# for event_date in [last_event_date]:
	# 	for country in all_countries():
	# 		save_results_by_date(country, event_date, True) 
	
	#for country in all_countries():
	#	save_country_results(country, True, True)
	
	#parkrun_news('uk', 'bushy', 2019)
	return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
	

