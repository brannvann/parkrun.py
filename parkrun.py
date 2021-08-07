#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup
from time import sleep
import random
import os.path

safe_headers = {
	'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0'
}

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
		print('reading ',url,' from cache')
		tmpfile = open(file_path, 'r')
		return tmpfile.read()
	sleep(0.05 * random.randint(100, 200))
	req = urllib.request.Request( url, data=None, headers=safe_headers)
	html = urlopen(req)
	page = str(html.read().decode('utf-8'))
	tmpfile = open(file_path, 'w')
	tmpfile.write(page)
	tmpfile.close()
	print('saving ',url,' to cache as ', file_name)
	return page

def get_all_parks(country, reloadHistory = False):
	records_url = country_url(country) + '/results/attendancerecords/'
	records_page = read_url(records_url, reloadHistory)
	bs = BeautifulSoup(records_page, 'html.parser')
	records_table = bs.tbody
	parks=[]
	rows = records_table.findAll('tr')
	for row in rows:
		refs = row.findAll('a')
		if len(refs) > 0:
			parkref = str(refs[0])
			parkname = (parkref.split('/'))[3]
			parks.append(parkname)
	return parks


def all_countries():
	countries = ['Россия', 'Германия', 'Норвегия', 'Англия', 'Австралия', 'Австрия', 
	'Канада','Дания','Финляндия','Франция', 'Италия','Ирландия', 'Япония','Малайзия', 
	'Нидерланды','Новая Зеландия', 'Польша','Сингапур', 'Южная Африка','Швеция', 'США', ]
	for country in countries:
		parks = get_all_parks(country)
		print(country, "\t", len(parks))	


def park_history(country, park, reloadHistory = False):
	parkurl = country_url(country) + "/" + park + '/results/eventhistory/'
	history_page = read_url(parkurl, reloadHistory)
	bs = BeautifulSoup(history_page, 'html.parser')
	history_table = bs.tbody
	events = []
	if history_table is None:
		print('cannot read tbody for ', park)
	else:
		rows = history_table.findAll('tr')
		for row in rows:
			event_num = row['data-parkrun']
			datefmt = row['data-date'].split('/')
			event_date = datefmt[2]+datefmt[1]+datefmt[0] 
			runners = row['data-finishers']
			volunteers = row['data-volunteers']
			events.append((event_date, event_num, runners, volunteers))
	return events
	
	
def country_history(country):
	events = []
	parks = get_all_parks(country)
	for parkname in parks:
		print(parkname)
		eventhistory = park_history(country, parkname)
		if len(eventhistory) > 0 : 
			events.append((parkname, len(eventhistory), eventhistory[-1][0], eventhistory[0][0]))
	return events
	
	
def parkrun_results(country, park, num):
	results = []
	event_date = '20210101'
	results_url = country_url(country) + "/" + park + "/results/weeklyresults/?runSeqNumber=" + str(num)
	bs = BeautifulSoup(read_url(results_url), 'html.parser')
	if bs.body.h3:
		title = bs.body.h3.findAll('span')
		if (title) and (len(title) > 0) and (len(title[0].contents) > 0):
			date_str = title[0].contents[0].split('/')
			event_date = date_str[2]+date_str[1]+date_str[0]
	
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
					if 'athleteNumber=' in refhref:
						runner_id = refhref.split('=')[1]
						break
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
					if 'Results-table-td--F' in field['class']:
						gender_str = 'F'
						gender_pos=field.findAll('div')[1].contents[0]
					if 'Results-table-td--M' in field['class']:
						gender_str = 'M' 
						gender_pos=field.findAll('div')[1].contents[0]
				if best_result == '':
					best_result = row.findAll('div')[-1].contents[-1]
				results.append((event_date, park, str(num), pos, 'A'+runner_id, name, time_str, gender_str, gender_pos, age_group, age_grade, best_result, data_runs))
	return results
	
	
def parkrun_results_by_date(country, park, event_date, reloadHistory = False):
	results = []
	events = park_history(country, park, reloadHistory)
	for info in events:
		if info[0] == event_date:
			results = parkrun_results(country, park, info[1])
			break
	return results

def print_country_history(country):
	events = country_history(country)
	for event in events:
		print(event[0], '\t',event[1], '\t',event[2], '\t',event[3]) 


def print_park_history(country, park):
	events = park_history(country, park)
	for event in events:
		print(event[0],'\t', park, '\t', event[1], '\t',event[2], '\t',event[3]) 

		
def print_parkrun_results(country, park, num):
	results = parkrun_results(country, park, num)
	for r in results:
		if len(r) == 5: 
			print(r[0],r[1],r[2],r[3],r[4],sep='\t')
		if len(r) == 13: 
			print(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9], r[10], r[11], r[12], sep='\t')


def print_parkrun_results_by_date(country, park, event_date):
	results = parkrun_results_by_date(country, park, event_date)
	for r in results:
		if len(r) == 5: 
			print(r[0],r[1],r[2],r[3],r[4],sep='\t')
		if len(r) == 13: 
			print(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9], r[10], r[11], r[12], sep='\t')
			

def results_to_string(results):
	outstr=''
	for result in results:
		for field in result:
			outstr = outstr + str(field) + '\t'
		outstr = outstr + '\n'
	return outstr 	 
	
			
def save_parkrun_results(country, park, reloadHistory = False):
	dir_name = country
	if not os.path.isdir(dir_name):
		print('create directory ', dir_name)
		os.mkdir(dir_name)
	if not os.path.isdir(dir_name):
		print('cannot access directory ', dir_name)
		return None
	filename = park + '_results.txt'
	file_path = os.path.join(dir_name, filename)
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
		#print_parkrun_results(country, park, num)
		resstr = results_to_string(parkrun_results(country, park, num))
		print('save results for ', park, num, ' in ', file_path)
		ofs.write(resstr)
		
def save_country_results(country, reloadHistory = False):
	parks = get_all_parks(country, reloadHistory)
	for park in parks:
		#print('save results for ', park)
		save_parkrun_results(country, park, reloadHistory)
		
def save_results_by_date(country, eventdate):
	dir_name = country
	if not os.path.isdir(dir_name):
		print('create directory ', dir_name)
		os.mkdir(dir_name)
	if not os.path.isdir(dir_name):
		print('cannot access directory ', dir_name)
		return None
	filename = str(eventdate) + '_' + country + '_results.txt'
	file_path = os.path.join(dir_name, filename)
	ofs = open(file_path, 'w')
	parks = get_all_parks(country, True)
	for park in parks :
		results = parkrun_results_by_date(country, park, eventdate)
		if not results:
			results = parkrun_results_by_date(country, park, eventdate, True)
		if results:
			print('save results ', park, eventdate)
			ofs.write(results_to_string(results))
	ofs.close()

print_country_history('ru')

#save_results_by_date('ru', '20210807')

#save_country_results('ru', True)

#save_parkrun_results('ru', 'bitsa')


	

