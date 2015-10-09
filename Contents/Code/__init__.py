# coding: utf-8
TITLE = 'StreamingFR'
## FICHIER DE LOG : tail -f /Library/Logs/PMS\ Plugin\ Logs/com.plexapp.plugins.streamingfr.log
## REPERTOIRE DE TRAVAIL : ~/Library/Application\ Support/Plex\ Media\ Server/Plug-ins/StreamingFR.bundle/
## Kill Plex
## Reglage -> Lecteur -> Desactivé "Lecture Directe"
## Installer phantomjs
PHANTOMJS_URL = "/usr/local/Cellar/phantomjs/2.0.0/bin/phantomjs"
LIST_COMPATIBLE = ["allvid.ch","thevideo.me","watching.com","openload.co","speedvideo.com","speedvideo.net","ok.ru","exashare.com","youwatch.org"]

####################################################################################################
def Start():

	ObjectContainer.title1 = TITLE
	DirectoryObject.thumb = R('icon-default.jpg')
	HTTP.CacheTime = 0#CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36'

####################################################################################################
def ValidatePrefs():

	try:
		test = HTTP.Request(Prefs['site_url'], cacheTime=0).content
	except:
		return ObjectContainer(header='URL Invalide', message='Inclure http://')

####################################################################################################
@handler('/video/streaming', TITLE)
@route('/video/streaming')
def MainMenu():

	oc = ObjectContainer()

	oc.add(DirectoryObject(key=Callback(Section, title='Videos', type='movies'), title='Videos'))
	oc.add(DirectoryObject(key=Callback(Section, title='Series', type='tv'), title='Series'))
	oc.add(PrefsObject(title='Preferences'))

	#url1 = 'http://fs35.youwatch.org:8777/slvpz4afosoax3ptx3nift52u4sp73jynewnh2ouhnjwak3l6jagi72xse/video.mp4'
	#url2 = 'http://techslides.com/demos/sample-videos/small.mp4'
	#url3 = 'http://fs23.exashare.com:8777/7wxkdvwnzym56odwtyi6jw7svh7fn3zabx2jlpxz7ujsr6qrnetrcf6ge7la/v.mp4'
	#url4 = "http://c7.vkcache.com/sec/p_urGIcT13_wTFqCDkBFEg/1442264400/hls-vod-s5/flv/api/files/videos/2015/09/07/144163487495d8c.mp4.m3u8"
	#url5 = "http://www.jurnet.fr/144320852928d2b.mp4.m3u8"
	'''
	oc.add(CreateVideoClipObject(
			url = url5,
			title = "title",
			summary = "summary"
		))
	'''
	return oc

####################################################################################################
@route('/video/streaming/section')
def Section(title, type='movies'):

	oc = ObjectContainer(title2=title)

	# SITE = http://lookiz.me
	if Prefs['site_url'] == "http://lookiz.me":

		if type == 'tv':
			rel_url = 'series?sort=%s'
			oc.add(InputDirectoryObject(key=Callback(Search, type=type), title=u'Rechercher une série', thumb=R('icon-search.png'), prompt=u"Rechercher une série"))

		else:
			rel_url = 'movies?sort=%s'
			oc.add(InputDirectoryObject(key=Callback(Search, type=type), title=u'Rechercher une vidéo', thumb=R('icon-search.png'), prompt=u"Rechercher une vidéo"))

		oc.add(DirectoryObject(key=Callback(Media, title='Derniers Ajouts', rel_url=rel_url % ('created&direction=desc')), title='Derniers Ajouts'))
		oc.add(DirectoryObject(key=Callback(Media, title='Meilleurs Notes', rel_url=rel_url % ('vote&direction=desc')), title='Meilleurs Notes'))
		oc.add(DirectoryObject(key=Callback(Media, title=u'Derniers Modifiés', rel_url=rel_url % ('modified&direction=desc')), title=u'Derniers Modifiés'))
		oc.add(DirectoryObject(key=Callback(Media, title='Plus Vus', rel_url=rel_url % ('likes&direction=desc')), title='Plus Vus'))

	# SITE = http://www.streamog.fr
	elif Prefs['site_url'] == "http://www.streamog.fr":

		if type == 'tv':
			rel_url = 'series-streaming'
			
		else:
			rel_url = 'films-streaming'

		oc.add(DirectoryObject(key=Callback(Media, title='Derniers Ajouts', rel_url=rel_url), title='Derniers Ajouts'))
		oc.add(InputDirectoryObject(key=Callback(Search, type=type), title=u'Rechercher', thumb=R('icon-search.png'), prompt=u"Rechercher"))

	# SITE = http://full-stream.me
	elif Prefs['site_url'] == "http://full-stream.me":

		if type == 'tv':
			rel_url = 'seriestv/'
			oc.add(InputDirectoryObject(key=Callback(Search, type=type), title=u'Rechercher une série', thumb=R('icon-search.png'), prompt=u"Rechercher une série"))

		else:
			rel_url = 'movie/'
			oc.add(InputDirectoryObject(key=Callback(Search, type=type), title=u'Rechercher une vidéo', thumb=R('icon-search.png'), prompt=u"Rechercher une vidéo"))

		oc.add(DirectoryObject(key=Callback(Media, title='Tops', rel_url=rel_url), title='Tops'))
		oc.add(DirectoryObject(key=Callback(Media, title=u'Derniers Ajouts (Films et Séries)', rel_url="lastnews"), title=u'Derniers Ajouts (Films et Séries)'))
		
	return oc

####################################################################################################
@route('/video/streaming/media', page=int)
def Media(title, rel_url, page=1):

	oc = ObjectContainer(title2=title)

	# SITE = http://lookiz.me
	if Prefs['site_url'] == "http://lookiz.me":
		url = '%s/%s&page=%d' % (Prefs['site_url'].rstrip('/'), rel_url, page)
		html = HTML.ElementFromURL(url, encoding='utf-8', errors='ignore')
	
		for item in html.xpath('//div[@class="film boxed film_mosaique"]//a[contains(@class, "affiche_lien")]'):

			item_url = item.xpath('./@href')[0]
			item_title = item.xpath('./img/@alt')[0]
			item_thumb = item.xpath('./img/@src')[0]
			

			if item_thumb.startswith('//'):
				item_thumb = 'http:%s' % (item_thumb)
			elif item_thumb.startswith('/'):
				item_thumb = 'http://%s%s' % (url.split('/')[2], item_thumb)

			if 'series' in url:
				oc.add(DirectoryObject(
					key = Callback(MediaSeasons, url=item_url, title=item_title, thumb=item_thumb),
					title = item_title,
					thumb = item_thumb
				))
			else:
				oc.add(DirectoryObject(
					key = Callback(MediaVersions, url=item_url, title=item_title, thumb=item_thumb),
					title = item_title,
					thumb = item_thumb
				))

		next_check = html.xpath('//ul[@class="pagination"]/li[last()]/a[@rel="next"]/@href')

		if len(next_check) > 0:

			next_check = next_check[0].split('page=')[-1].split('&')[0]

			if int(next_check) > page:

				oc.add(NextPageObject(
					key = Callback(Media, title=title, rel_url=rel_url, page=page+1),
					title = 'Plus...'
				))

	# SITE = http://www.streamog.fr
	elif Prefs['site_url'] == "http://www.streamog.fr":
		url = '%s/%s/page/%d' % (Prefs['site_url'].rstrip('/'), rel_url, page)
		html = HTML.ElementFromURL(url, encoding='utf-8', errors='ignore')
		for item in html.xpath('//div[@class="moviefilm"]//a[img]'):

			item_url = item.xpath('./@href')[0]
			item_title = item.xpath('./img/@alt')[0]
			item_thumb = item.xpath('./img/@src')[0]

			if 'series' in url:
				oc.add(DirectoryObject(
					key = Callback(MediaSeasons, url=item_url, title=item_title, thumb=item_thumb),
					title = item_title,
					thumb = item_thumb
				))
			else:
				oc.add(DirectoryObject(
					key = Callback(MediaVersions, url=item_url, title=item_title, thumb=item_thumb),
					title = item_title,
					thumb = item_thumb
				))

		next_check = html.xpath('//a[@class="nextpostslink"]/@href')

		if len(next_check) > 0:

			next_check = next_check[0].split('page/')[-1]

			if int(next_check) > page:

				oc.add(NextPageObject(
					key = Callback(Media, title=title, rel_url=rel_url, page=page+1),
					title = 'Plus...'
				))

	# SITE = http://full-stream.me
	elif Prefs['site_url'] == "http://full-stream.me":
		import urlparse
		import urllib
		import urllib2
		from lxml import html
		type = rel_url.split("/")[0] 
		url = '%s/%s/page/%d' % (Prefs['site_url'].rstrip('/'), type, page)
		payload = {}
		headers = {
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
			'Content-Type': 'form-data',
			}
		params = urllib.urlencode(payload)
		req = urllib2.Request(url, params, headers)
		response = urllib2.urlopen(req)
		html = html.fromstring(response.read())
		for item in html.xpath('//div[@id="dle-content"]//div[@class="fullstream fullstreaming"]'):

			item_url = item.xpath('./div[@class="fullmask"]//a[@class="fullinfo"]/@href')[0]
			item_title = item.xpath('./img/@alt')[0]
			item_thumb = Prefs['site_url']+item.xpath('./img/@src')[0]
			is_un_film = item.xpath('./i')
			if is_un_film:
				oc.add(DirectoryObject(
					key = Callback(MediaVersions, url=item_url, title=item_title, thumb=item_thumb),
					title = item_title,
					thumb = item_thumb
				))
			else:
				oc.add(DirectoryObject(
					key = Callback(MediaSeasons, url=item_url, title=item_title, thumb=item_thumb),
					title = item_title,
					thumb = item_thumb
				))

		next_check = html.xpath('//div[@class="navigation ignore-select"]/a[last()]/@href')

		if len(next_check) > 0:

			next_check = next_check[0].split('page/')[-1].rstrip('/')
			if int(next_check) > page:

				oc.add(NextPageObject(
					key = Callback(Media, title=title, rel_url=rel_url, page=page+1),
					title = 'Plus...'
				))

	return oc

####################################################################################################
@route('/video/streaming/media/seasons')
def MediaSeasons(url, title, thumb):

	if not url.startswith('http'):
		url = '%s%s' % (Prefs['site_url'].rstrip('/'), url)

	html = HTML.ElementFromURL(url, encoding='utf-8', errors='ignore')
	oc = ObjectContainer(title2=title)

	# SITE = http://lookiz.me
	if Prefs['site_url'] == "http://lookiz.me":
		for season in html.xpath('//*[@id="contenu"]/div[3]/table/tbody/tr/td/h3/text()'):

			oc.add(DirectoryObject(
				key = Callback(MediaEpisodes, url=url, title=season, thumb=thumb),
				title = season,
				thumb = thumb
			))

	# SITE = http://www.streamog.fr
	elif Prefs['site_url'] == "http://www.streamog.fr":
		for season in html.xpath('//div[@class="filmicerik"]/div[@align="center"]/img/@alt'):

			oc.add(DirectoryObject(
				key = Callback(MediaEpisodes, url=url, title=season, thumb=thumb),
				title = season,
				thumb = thumb
			))

	# SITE = http://full-stream.me
	elif Prefs['site_url'] == "http://full-stream.me":
			oc.add(DirectoryObject(
				key = Callback(MediaEpisodes, url=url, title="VOSTFR", thumb=thumb),
				title = "VOSTFR",
				thumb = thumb
			))
			oc.add(DirectoryObject(
				key = Callback(MediaEpisodes, url=url, title="VF", thumb=thumb),
				title = "VF",
				thumb = thumb
			))

	return oc

####################################################################################################
@route('/video/streaming/media/episodes')
def MediaEpisodes(url, title, thumb):

	if not url.startswith('http'):
		url = '%s%s' % (Prefs['site_url'].rstrip('/'), url)

	html = HTML.ElementFromURL(url, encoding='utf-8', errors='ignore')
	oc = ObjectContainer(title2=title)


	# SITE = http://lookiz.me
	if Prefs['site_url'] == "http://lookiz.me":
		for item in html.xpath('//h3[text()[contains(.,"'+title+'")]]/../../following-sibling::tr[1]/td/a[@class="num_episode"]'):

			item_title = 'Episode %s' % (item.xpath('./text()')[0])
			item_url = item.xpath('./@href')[0]

			oc.add(DirectoryObject(
				key = Callback(MediaVersions, url=item_url, title=item_title, thumb=thumb),
				title = item_title,
				thumb = thumb
			))

	# SITE = http://www.streamog.fr
	elif Prefs['site_url'] == "http://www.streamog.fr":
		for item in html.xpath('//img[@alt="'+title+'"]/../following-sibling::div[1]/ul/li'):
			
			x = item.xpath('./a/text()')[0]
			item_title = 'Episode %s' % (x)
			item_url = item.xpath('../../div/iframe/@src')
			summary = html.xpath('//div[@class="filmaltiaciklama"]/p[3]/text()')
			version = html.xpath('//div[@class="filmaltiaciklama"]/p[1]/a/text()')[0]
			source = GetSourceFromURL(item_url[0])

			oc.add(DirectoryObject(
					key = Callback(MediaPlayback, url=item_url[0], title=item_title, summary=summary[0], thumb=thumb, source=source),
					title = u'%s - %s - %s' % (version, title, source),
					summary = summary[0],
					thumb = thumb
				))  

	# SITE = http://full-stream.me
	elif Prefs['site_url'] == "http://full-stream.me":
		if title == "VOSTFR":
			sibling = '//div[@class="VOSTFR-tab"]/following::div[1]/a'
		else:
			sibling = '//div[@class="VF-tab"]/following::div[1]/a'

		for item in html.xpath(sibling):
			item_title = item.xpath('./@title')[0]
			Log("item_title")
			Log(item_title)
			if item.xpath('./@href')[0]=="#":
				item_url = url+"|"+item.xpath('./@data-rel')[0]
				oc.add(DirectoryObject(
					key = Callback(MediaVersions, url=item_url, title=item_title, thumb=thumb),
					title = item_title,
					thumb = thumb
				))
			else:
				title = item.xpath('./@title')[0]
				url = item.xpath('./@href')[0]
				summary = html.xpath('//div[@class="music-details"]/ul/text()')
				version = html.xpath('//div[@class="music-details"]/ul/h4/text()')[0]
				host = GetSourceFromURL(url)
				supported = GetSupportedFromHost(host)
				oc.add(DirectoryObject(
					key = Callback(MediaPlayback, url=url, title=title, summary=summary, thumb=thumb),
					title = u'%s - %s - %s - %s' % (version, title, host, supported),
					summary = summary[0],
					thumb = thumb
				))
				
	# Si vide de oc alors : return ObjectContainer(header=u'Aucun épisode', message=u'Aucun épisode')
	return oc

####################################################################################################
@route('/video/streaming/media/versions')
def MediaVersions(url, title, thumb):

	# SITE = http://lookiz.me
	if Prefs['site_url'] == "http://lookiz.me":
		if not url.startswith('http'):
			url = '%s%s' % (Prefs['site_url'].rstrip('/'), url)

		html = HTML.ElementFromURL(url, encoding='utf-8', errors='ignore')
		oc = ObjectContainer(title2=title)
		summary = html.xpath('//div[@class="resume"]/text()')
		version = html.xpath('//li[@role="presentation"]/a/text()')

		for ext_url in html.xpath('//div[@role="tabpanel"]//iframe'):

			url = ext_url.xpath('./@src')[0]
			host = url
			source = Regex('(?:https?:\/\/)?(?:www\.)?(.*?)\/').search(host).group(1)
			version = ext_url.xpath('./ancestor::div[@role="tabpanel"][1]/@id')[0].upper()

			oc.add(DirectoryObject(
				key = Callback(MediaPlayback, url=url, title=title, summary=summary[0], thumb=thumb, source=source),
				title = u'%s - %s - %s' % (version, title, host),
				summary = summary[0],
				thumb = thumb
			))
	
	# SITE = http://www.streamog.fr
	elif Prefs['site_url'] == "http://www.streamog.fr":
		import time
		import urllib
		import urllib2
		import re
		if not url.startswith('http'):
			url = '%s%s' % (Prefs['site_url'].rstrip('/'), url)

		html = HTML.ElementFromURL(url, encoding='utf-8', errors='ignore')
		oc = ObjectContainer(title2=title)
		summary = html.xpath('//div[@class="filmaltiaciklama"]/p[6]/text()')
		version = html.xpath('//div[@class="filmaltiaciklama"]/p[4]/text()')[0].split(': ')[-1]

		for ext_url in html.xpath('//div[@class="keremiya_part"]/a'):
			time.sleep(1)
			url = ext_url.xpath('./@href')[0]
			host = ext_url.xpath('./span/text()')[0]

			payload = { 
				"hash":""
				}

			headers = {
				'origin': "http://www.streamog.fr/"
				}

			params = urllib.urlencode(payload)
			req = urllib2.Request(url, params, headers)
			handle = urllib2.urlopen(req)
			page = handle.read()

			list_url = re.findall("<iframe.*src=[\"']((?:.(?![\"']?\s+(?:\S+)=|[>\"']))+.)[\"']",page,re.I)

			for match_url in list_url:
				if match_url.startswith( 'http://ok.ru' ) or match_url.startswith( 'http://videoapi.my.mail.ru' ) or match_url.startswith( 'http://hqq.tv' ) or match_url.startswith( 'http://youwatch.org' ) or match_url.startswith( 'http://exashare.com' ) or match_url.startswith( 'http://videomega.tv' ) or match_url.startswith( 'http://speedvideo.net' ) or match_url.startswith( 'http://watching.to' ) or match_url.startswith( 'https://openload.co' ):
					url = match_url
					source = GetSourceFromHost(host)

					if source=="netu.tv":
						supported = "NON SUPPORTE"
					elif source=="allvid.ch" or source=="thevideo.me" or source=="watching.com" or source=="openload.co" or source=="speedvideo.com" or source=="ok.ru" or source=="exashare.com" or source=="youwatch.org":
						supported = "SUPPORTE"
					else:
						supported = "PAS ENCORE SUPPORTE"
						
					oc.add(DirectoryObject(
						key = Callback(MediaPlayback, url=url, title=title, summary=summary[0], thumb=thumb, source=source),
						title = u'%s - %s - %s - %s' % (version, title, host, supported),
						summary = summary[0],
						thumb = thumb
					))

	# SITE = http://full-stream.me
	elif Prefs['site_url'] == "http://full-stream.me":
		Log(url)
		if url.startswith('http'):
			#Si c'est une serie
			if "|" in url: 
				episode = url.split("|")[1]
				url = url.split("|")[0]
				html = HTML.ElementFromURL(url, encoding='utf-8', errors='ignore')
				oc = ObjectContainer(title2=title)
				summary = html.xpath('//div[@class="music-details"]/ul/text()')
				version = html.xpath('//div[@class="music-details"]/ul/h4/text()')[0]
				for ext_url in html.xpath('//div[@id="'+episode+'"]//li/a'):
					url = ext_url.xpath('./@href')[0]
					host = GetSourceFromURL(url)
					supported = GetSupportedFromHost(host)
					
					oc.add(DirectoryObject(
						key = Callback(MediaPlayback, url=url, title=title, summary=summary, thumb=thumb),
						title = u'%s - %s - %s - %s' % (version, title, host, supported),
						summary = summary[0],
						thumb = thumb
					))
			#Si c'est un film
			else:
				html = HTML.ElementFromURL(url, encoding='utf-8', errors='ignore')
				oc = ObjectContainer(title2=title)
				summary = html.xpath('//div[@id="player"]/text()[last()]')[0]
				version = html.xpath('//div[@id="player"]/text()[preceding::strong][6]')[0].split(': ')[-1].rsplit(')')[0]
				for ext_url in html.xpath('//div[@class="filmelink"]/a'):
					url = ext_url.xpath('./@href')[0]
					host = GetSourceFromURL(url)
					supported = GetSupportedFromHost(host)
					
					oc.add(DirectoryObject(
						key = Callback(MediaPlayback, url=url, title=title, summary=summary, thumb=thumb),
						title = u'%s - %s - %s - %s' % (version, title, host, supported),
						summary = summary[0],
						thumb = thumb
					))
			


	#if len(oc) < 1:
		#return ObjectContainer(header='No Sources', message='No compatible sources found')
	#else:
	return oc

####################################################################################################
@route('/video/streaming/media/playback')
def MediaPlayback(url, title, summary, thumb):

	oc = ObjectContainer()
	source = GetSourceFromURL(url)
	fichier = ""
	if "xxxxx" in url :
		fichier = ""
	else:
		if source == 'allvid.ch':
			page = HTTP.Request(url).content
			search_page_file_mp4 = Regex('file:\"(.*?)\"').search(page)
			if search_page_file_mp4:
				fichier = search_page_file_mp4.group(1)
			else:
				fichier = ""
		elif source == 'thevideo.me':
			page = HTTP.Request(url).content
			search_page_file_mp4 = Regex("\'360p\', \'file\' : \'(.*?)\'").search(page)
			if search_page_file_mp4:
				fichier = search_page_file_mp4.group(1)
			else:
				fichier = ""
		elif source == 'watching.com':
			page = HTTP.Request(url).content
			search_page_file_mp4 = Regex("file: [\"']((?:.(?![\"']?\s+(?:\S+)=|[>\"']))+.mp4)").search(page)
			if search_page_file_mp4:
				fichier = search_page_file_mp4.group(1)
			else:
				fichier = ""
		elif source == 'openload.co':
			from selenium import webdriver
			driver = webdriver.PhantomJS(executable_path=PHANTOMJS_URL)
			driver.get(url)
			content = driver.page_source
			search_page_file_mp4 = Regex('type="video\/mp4" src="(.+)">').search(content)
			if search_page_file_mp4:
				fichier = search_page_file_mp4.group(1)
			else:
				fichier = ""
		elif source == 'ok.ru':
			page = HTTP.Request(url).content
			search_page_file_mp4 = Regex("data-id1=\"(\d+)\"").search(page)
			if search_page_file_mp4:
				fichier = search_page_file_mp4.group(1)
				page = HTTP.Request("http://m.ok.ru/video/"+fichier).content
				fichier = Regex("videoSrc&quot;:&quot;(.*)&quot;,&quot;movie").search(page).group(1)
				fichier = fichier.replace('\u0026','&')
				fichier = fichier.replace('\u003d','=')
			else:
				fichier = ""
		elif source == 'speedvideo.com' or source == 'speedvideo.net':
			from selenium import webdriver
			driver = webdriver.PhantomJS(executable_path=PHANTOMJS_URL)
			driver.get(url)
			content = driver.page_source
			linkfile = Regex("linkfile =\"(.*)\"").search(content).group(1)
			base64_code = Regex("base64_decode\(linkfile, (.*)\)").search(content).group(1)
			val_base64_code = Regex("var "+base64_code+" = (.*);").search(content).group(1)
			fichier = driver.execute_script('function base64_decode(linkfile,password){var _4=linkfile.substr(0,password);var _5=linkfile.substr(password+10);linkfile=_4+_5;var _6="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";var _7,_8,_9,_a,_b,_c,_d,_e,_f=0,_10=0,_11="",_12=[];if(!linkfile){return linkfile}linkfile+="";do{_a=_6.indexOf(linkfile.charAt(_f++));_b=_6.indexOf(linkfile.charAt(_f++));_c=_6.indexOf(linkfile.charAt(_f++));_d=_6.indexOf(linkfile.charAt(_f++));_e=_a<<18|_b<<12|_c<<6|_d;_7=_e>>16&0xff;_8=_e>>8&0xff;_9=_e&0xff;if(_c==64){_12[_10++]=String.fromCharCode(_7)}else{if(_d==64){_12[_10++]=String.fromCharCode(_7,_8)}else{_12[_10++]=String.fromCharCode(_7,_8,_9)}}}while(_f<linkfile.length){_11=_12.join("")}return decodeURIComponent(escape(_11.replace("/+$/","")))}return base64_decode("'+linkfile+'", '+val_base64_code+');')
		elif source == 'exashare.com':
			import time
			id_film = Regex("-(.*?)-").search(url).group(1)
			url = "http://exashare.com/"+id_film
			exashare = HTTP.Request(url).content
			val_hash = Regex('hash\" value=\"(.*)\"').search(exashare).group(1)
			val_fname = Regex('fname\" value=\"(.*)\"').search(exashare).group(1)
			val_usrlogin = Regex('usr_login\" value=\"(.*)\"').search(exashare).group(1)
			val_id = Regex('id\" value=\"(.*)\"').search(exashare).group(1)
			val_referer = Regex('referer\" value=\"(.*)\"').search(exashare).group(1)
			post_values = {}
			post_values["op"] = "download1"
			post_values["usr_login"] = val_usrlogin
			post_values["id"] = val_id
			post_values["fname"] = val_fname
			post_values["referer"] = val_referer
			post_values["hash"] = val_hash
			post_values["imhuman"] = "Proceed+to+video"
			page = HTTP.Request(url, values=post_values, method='POST').content
			search_page_file_mp4 = Regex('file: \"(.*?)\"').search(page)
			if search_page_file_mp4:
				fichier = search_page_file_mp4.group(1)
			else:
				cpt = 0
				while fichier == "" or cpt<5:
					time.sleep(2)
					val_hash = Regex('hash\" value=\"(.*)\"').search(exashare).group(1)
					val_fname = Regex('fname\" value=\"(.*)\"').search(exashare).group(1)
					val_usrlogin = Regex('usr_login\" value=\"(.*)\"').search(exashare).group(1)
					val_id = Regex('id\" value=\"(.*)\"').search(exashare).group(1)
					val_referer = Regex('referer\" value=\"(.*)\"').search(exashare).group(1)
					post_values = {}
					post_values["op"] = "download1"
					post_values["usr_login"] = val_usrlogin
					post_values["id"] = val_id
					post_values["fname"] = val_fname
					post_values["referer"] = val_referer
					post_values["hash"] = val_hash
					post_values["imhuman"] = "Proceed+to+video"
					page = HTTP.Request(url, values=post_values, method='POST').content
					search_page_file_mp4 = Regex('file: \"(.*?)\"').search(page)
					cpt += 1
					if search_page_file_mp4:
						fichier = search_page_file_mp4.group(1)
					else:
						fichier = ""
		elif source == 'youwatch.org':
			import time
			import urllib
			import urllib2
			import jsunpack

			id_film = Regex("-(.*?)-").search(url).group(1)
			url = "http://youwatch.org/"+id_film
			youwatch = HTTP.Request(url).content
			val_hash = Regex('hash\" value=\"(.*)\"').search(youwatch).group(1)
			val_fname = Regex('fname\" value=\"(.*)\"').search(youwatch).group(1)

			time.sleep(6)

			payload = { 
				"hash":val_hash,
				"imhuman":"Slow+Download",
				"usr_login":"",
				"referer":"youwatch.org",
				"fname":val_fname,
				"id":id_film,
				"op":"download1"
				}
			headers = {
				'origin': "http//youwatch.org"
				}

			time.sleep(4)

			params = urllib.urlencode(payload)
			req = urllib2.Request(url, params, headers)
			handle = urllib2.urlopen(req)
			page = handle.read()
			code_obfuscated = Regex(">(eval.*)").search(page).group(1)
			unpacked = jsunpack.unpack(code_obfuscated)
			search_page_file_mp4 = Regex('file:\"(.+.mp4)\",').search(unpacked)
			if search_page_file_mp4:
				fichier = search_page_file_mp4.group(1)
			else:
				fichier = ""

		else:
			return ObjectContainer(header='Pas de Source', message='Aucune source compatible')

	if fichier:
		oc.add(CreateVideoClipObject(
			url = fichier,
			title = title,
			summary = summary
		))
	else:
		return ObjectContainer(header='Aucune Source', message='Non disponible')

	return oc
	
####################################################################################################
#@route('/video/streaming/media/playback/watch')
def CreateVideoClipObject(url, title, summary, include_container=False):
	
	Log(url)
	videoclip_obj = VideoClipObject(
		key = Callback(CreateVideoClipObject, url=url, title=title, summary=summary, include_container=True),
		rating_key = url,
		title = title,
		summary = summary,
		items = [
			MediaObject(
				parts = [
					PartObject(key=HTTPLiveStreamURL(url=url))
				],
				container = Container.MP4,
				video_codec = VideoCodec.H264,
				video_resolution = '544',
				audio_codec = AudioCodec.AAC,
				audio_channels = 2,
				optimized_for_streaming = True
			)
		]
	)

	if include_container:
		return ObjectContainer(objects=[videoclip_obj])
	else:
		return videoclip_obj
	

####################################################################################################
@route('/video/streaming/media/search')
def Search(type='movies', query=''):
	Log("RECHERCHE")
	# SITE = http://lookiz.me
	if Prefs['site_url'] == "http://lookiz.me":
		if type == 'tv':
			rel_url = 'series?t=%s' % (String.Quote(query, usePlus=True).lower())
		else:
			rel_url = 'movies?t=%s' % (String.Quote(query, usePlus=True).lower())

	# SITE = http://www.streamog.fr
	elif Prefs['site_url'] == "http://www.streamog.fr":
		if type == 'tv':
			rel_url = 'series?t=%s' % (String.Quote(query, usePlus=True).lower())
		else:
			rel_url = 'movies?t=%s' % (String.Quote(query, usePlus=True).lower())

	# SITE = http://full-stream.me
	elif Prefs['site_url'] == "http://full-stream.me":
		if type == 'tv':
			rel_url = 'index.php?do=search&subaction=search&story=%s&catlist[]=2' % (String.Quote(query, usePlus=True).lower())
		else:
			rel_url = 'index.php?do=search&subaction=search&story=%s&catlist[]=1' % (String.Quote(query, usePlus=True).lower())

	return Media(title=query, rel_url=rel_url)

####################################################################################################
def GetSourceFromHost(host):

	host = host.upper()
	if host == 'NETU':
		return 'netu.tv'
	elif host == 'YOUWATCH':
		return 'youwatch.org'
	elif host == 'EXASHARE':
		return 'exashare.com'
	elif host == 'VIDEOMEGA':
		return 'videomega.com'
	elif host == 'SPEEDVIDEO':
		return 'speedvideo.com'
	elif host == 'WATCHING':
		return 'watching.com'
	elif host == 'OK.RU':
		return 'ok.ru'
	elif host == 'MAIL.RU':
		return 'mail.ru'
	elif host == 'OPENLOAD':
		return 'openload.co'	
	else:
		return None

####################################################################################################
def GetSourceFromURL(url):
	import urlparse
	return urlparse.urljoin(url.lower(), '/').rsplit('/')[2]

####################################################################################################
def GetSupportedFromHost(host):
	if host in LIST_COMPATIBLE:
		return u"SUPPORTÉ"
	else:
		return u"NON SUPPORTÉ"

####################################################################################################
