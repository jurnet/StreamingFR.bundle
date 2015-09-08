#SITE : http://www.lookiz.me
# coding: utf-8
TITLE = 'Streaming FR'

####################################################################################################
def Start():

	ObjectContainer.title1 = TITLE
	DirectoryObject.thumb = R('icon-default.jpg')
	HTTP.CacheTime = 1
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36'

####################################################################################################
def ValidatePrefs():

	try:
		test = HTTP.Request(Prefs['site_url'], cacheTime=0).content
	except:
		return ObjectContainer(header='Invalid URL', message='Please input a valid and existing URL, including http://')

####################################################################################################
@handler('/video/lookiz', TITLE)
def MainMenu():

	oc = ObjectContainer()

	oc.add(DirectoryObject(key=Callback(Section, title='Videos', type='movies'), title='Videos'))
	oc.add(DirectoryObject(key=Callback(Section, title='Series', type='tv'), title='Series'))
	oc.add(DirectoryObject(key=Callback(Section, title='Rechercher', type='search'), title='Rechercher'))
	oc.add(PrefsObject(title='Preferences'))
	oc.add(InputDirectoryObject(key=Callback(Search, type=type), title='Search', prompt='Search', thumb=R('search.png')))


	return oc

####################################################################################################
@route('/video/lookiz/section')
def Section(title, type='movies'):

	if type == 'tv':
		rel_url = 'series?sort=%s'
	else:
		rel_url = 'movies?sort=%s'

	oc = ObjectContainer(title2=title)
	if type == 'search':
		oc.add(DirectoryObject(key=Callback(Media, title='Rechercher une video', rel_url="movies?t=", title='Rechercher une video'))
	else:
		oc.add(DirectoryObject(key=Callback(Media, title='Tous', rel_url=rel_url % ('created&direction=desc')), title='Tous'))
		oc.add(DirectoryObject(key=Callback(Media, title='Derniers Ajouts', rel_url=rel_url % ('created&direction=desc')), title='Derniers Ajouts'))
		oc.add(DirectoryObject(key=Callback(Media, title='Meilleurs Notes', rel_url=rel_url % ('vote&direction=desc')), title='Meilleurs Notes'))
		oc.add(DirectoryObject(key=Callback(Media, title='Plus Populaires', rel_url=rel_url % ('views&direction=desc')), title='Plus Populaires'))
		oc.add(DirectoryObject(key=Callback(Media, title='Plus Vus', rel_url=rel_url % ('likes&direction=desc')), title='Plus Vus'))

	oc.add(InputDirectoryObject(key=Callback(Search, type=type), title='Search', prompt='Search', thumb=R('search.png')))

	return oc

####################################################################################################
@route('/video/lookiz/media', page=int)
def Media(title, rel_url, page=1):

	url = '%s/%s&page=%d' % (Prefs['site_url'].rstrip('/'), rel_url, page)
	html = HTML.ElementFromURL(url, encoding='utf-8', errors='ignore')

	oc = ObjectContainer(title2=title)
	
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

	return oc

####################################################################################################
@route('/video/lookiz/media/seasons')
def MediaSeasons(url, title, thumb):

	if not url.startswith('http'):
		url = '%s%s' % (Prefs['site_url'].rstrip('/'), url)

	html = HTML.ElementFromURL(url, encoding='utf-8', errors='ignore')

	oc = ObjectContainer(title2=title)

	for season in html.xpath('//*[@id="contenu"]/div[3]/table/tbody/tr/td/h3/text()'):

		oc.add(DirectoryObject(
			key = Callback(MediaEpisodes, url=url, title=season, thumb=thumb),
			title = season,
			thumb = thumb
		))

	return oc

####################################################################################################
@route('/video/lookiz/media/episodes')
def MediaEpisodes(url, title, thumb):

	if not url.startswith('http'):
		url = '%s%s' % (Prefs['site_url'].rstrip('/'), url)

	html = HTML.ElementFromURL(url, encoding='utf-8', errors='ignore')

	oc = ObjectContainer(title2=title)

	for item in html.xpath('//h3[text()[contains(.,"'+title+'")]]/../../following-sibling::tr[1]/td/a[@class="num_episode"]'):

		item_title = 'Episode %s' % (item.xpath('./text()')[0])
		item_url = item.xpath('./@href')[0]

		oc.add(DirectoryObject(
			key = Callback(MediaVersions, url=item_url, title=item_title, thumb=thumb),
			title = item_title,
			thumb = thumb
		))

	return oc

####################################################################################################
@route('/video/lookiz/media/versions')
def MediaVersions(url, title, thumb):

	if not url.startswith('http'):
		url = '%s%s' % (Prefs['site_url'].rstrip('/'), url)

	html = HTML.ElementFromURL(url, encoding='utf-8', errors='ignore')
	summary = html.xpath('//div[@class="resume"]/text()')
	#Log("Résumé = "+summary[0])

	oc = ObjectContainer(title2=title)

	for ext_url in html.xpath('//div[@class="tab-pane"]//iframe/@src'):

		url = ext_url
		host = url
		source = Regex('(?:https?:\/\/)?(?:www\.)?(.*?)\/').search(host).group(1)

		oc.add(DirectoryObject(
			key = Callback(MediaPlayback, url=url, title=title, summary=summary[0], thumb=thumb, source=source),
			title = u'%s - %s' % (host, title),
			summary = summary[0],
			thumb = thumb
		))

	#if len(oc) < 1:
		#return ObjectContainer(header='No Sources', message='No compatible sources found')
	#else:
	return oc

####################################################################################################
@route('/video/lookiz/media/playback')
def MediaPlayback(url, title, summary, thumb, source):

	oc = ObjectContainer()
	fichier = ""

	if source == 'allvid.ch':
		page = HTTP.Request(url).content
		fichier = Regex('file:\"(.*?)\"').search(page).group(1)
	elif source == 'thevideo.me':
		page = HTTP.Request(url).content
		fichier = Regex("\'360p\', \'file\' : \'(.*?)\'").search(page).group(1)
		Log(fichier)
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
		#Log(page)
		Log(post_values)
		search_page_file_mp4 = Regex('file: \"(.*?)\"').search(page)
		if search_page_file_mp4:
			fichier = search_page_file_mp4.group(1)
		else:
			cpt = 0
			while fichier == "" or cpt<5:
				time.sleep(2)
				Log(page)
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
	elif source == 'youwatch.org':
		import time
		id_film = Regex("-(.*?)-").search(url).group(1)
		url = "http://youwatch.org/"+id_film
		youwatch = HTTP.Request(url).content
		val_hash = Regex('hash\" value=\"(.*)\"').search(youwatch).group(1)
		val_fname = Regex('fname\" value=\"(.*)\"').search(youwatch).group(1)
		post_values = {}
		post_values["op"] = "download1"
		post_values["usr_login"] = ""
		post_values["id"] = id_film
		post_values["fname"] = val_fname
		post_values["referer"] = "youwatch.org%2F"+id_film
		post_values["hash"] = val_hash
		post_values["imhuman"] = "Slow+Download"
		HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'
		HTTP.Headers['Upgrade'] = '1'
		HTTP.Headers['Referer'] = url
		HTTP.Headers['Origin'] = "http://youwatch.org"
		HTTP.Headers['Cookie'] = "lang=french;aff=26595;__utmt=1"
		time.sleep(10)
		page = HTTP.Request(url, values=post_values, method='POST').content
		Log("RECHERCHER")
		Log(page)
		search_page_file_mp4 = Regex('file=(.*)&amp\;provider').search(page)
		Log(search_page_file_mp4)
		if search_page_file_mp4:
			fichier = search_page_file_mp4.group(1)
	else:
		return ObjectContainer(header='Pas de Source', message='Aucune source compatible')

	if fichier:
		oc.add(CreateVideoClipObject(
			url = fichier,
			title = title,
			summary = summary
		))

	return oc
	
####################################################################################################
def CreateVideoClipObject(url, title, summary, include_container=False):

	videoclip_obj = VideoClipObject(
		key = Callback(CreateVideoClipObject, url=url, title=title, summary=summary, include_container=True),
		rating_key = url,
		title = title,
		summary = summary,
		items = [
			MediaObject(
				parts = [
					PartObject(key=url)
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
@route('/video/lookiz/media/search')
def Search(type='movies', query=''):

	if type == 'tv':
		rel_url = 'index.php?tv=&search_keywords=%s' % (String.Quote(query, usePlus=True).lower())
	else:
		rel_url = 'index.php?search_keywords=%s' % (String.Quote(query, usePlus=True).lower())

	return Media(title=query, rel_url=rel_url)
