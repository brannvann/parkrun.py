# Заголовок запроса

На сайтах parkrun включена защита от скраппинга, поэтому в запросы надо подставить подходящий user-agent, притворившись браузером

<code>safe_headers = {
	'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0'}</code>

# country_url 
## url главной страницы забега
Для большинства национальных сайтов используется домен первого уровня, например parkrun.ru или parkrun.dk. Но это правило не является общим, поэтому формирование url вынесено в отдельную функцию  

```python
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
		(['us', 'usa', 'сша'],'https://www.parkrun.us')
	]
	for park in parks:
		if country in park[0]:
			return park[1]
	return 'https://www.parkrun.org'
```

# read_url
## чтение содержимого страницы

На сайтах parkrun включена защита от скраппинга, при слишком частых обращениях к сайту срабатывает блокировка по ip-адресу, поэтому перед каждым запросом посставлена случайная задержка от 2 до 4 секунд. Для ускорения работы добавлено кеширование: загруженная страница сохраняется на диске, и при следующем обращении,  если не выставлен флаг принудительного обновления, содержимое читается из файла. 

```python
def read_url(url, forceReload = False):
	cache_dir = 'urlcache'
	file_name = url.replace(':', '_').replace('/', '_').replace('=', '_').replace('?', '_')
	file_path = os.path.join(cache_dir, file_name)
	if (not forceReload ) and os.path.exists(file_path):
		if debug_print:
			print('reading ',url,' from cache')
		tmpfile = open(file_path, 'r')
		return tmpfile.read()
	sleep(0.05 * random.randint(40, 80))
	req = urllib.request.Request( url, data=None, headers=safe_headers)
	html = urlopen(req)
	page = str(html.read().decode('utf-8'))
	tmpfile = open(file_path, 'w')
	tmpfile.write(page)
	tmpfile.close()
	if debug_print:
		print('saving ',url,' to cache as ', file_name)
	return page
```
