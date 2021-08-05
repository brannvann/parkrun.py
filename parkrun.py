#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup
from time import sleep
import random

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

def read_url(url):
	sleep(0.02 * random.randint(1, 10))
	req = urllib.request.Request( url, data=None, headers=safe_headers)
	html = urlopen(req)
	return str(html.read().decode('utf-8'))

def get_all_parks(country):
	records_url = country_url(country) + '/results/attendancerecords/'
	records_page = read_url(records_url)
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


def park_history(country, park):
	parkurl = country_url(country) + "/" + park + '/results/eventhistory/'
	isFile=False
	history_page = ''
	if isFile:
		tmpfile = open(r'eventhistory.html', 'r')
		history_page = tmpfile.read()
	else:
		history_page = read_url(parkurl)
		tmpfile = open(r'eventhistory.html', 'w')
		tmpfile.write(history_page)
		tmpfile.close()
	#print(history_page)
	bs = BeautifulSoup(history_page, 'html.parser')
	history_table = bs.tbody
	events = []
	rows = history_table.findAll('tr')
	for row in rows:
		event_num = row['data-parkrun']
		datefmt = row['data-date'].split('/')
		event_date = datefmt[2]+datefmt[1]+datefmt[0] 
		runners = row['data-finishers']
		volunteers = row['data-volunteers']
		#print(event_date,'\t', park, '\t', event_num, '\t', runners, '\t', volunteers)
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


allevents = country_history('ru')
for event in allevents:
	print(event) 
	#print(parkname, len(eventhistory), eventhistory[-1][0], eventhistory[0][0],)


if False:
	parks = get_all_parks('pl')
	for park in parks:
		print(park)


