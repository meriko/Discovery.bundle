TITLE = 'Discovery Networks'
ART   = 'art-default.jpg'
ICON  = 'icon-default.png'

ITEMS_PER_PAGE = 50

HTTP_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/536.26.17 (KHTML, like Gecko) Version/6.0.2 Safari/536.26.17"

CHANNELS = [ 
	{
		'title': 	'Discovery Channel',
		'id':		'Discovery',
		'url':		'http://dsc.discovery.com',
		'thumb':	'http://static.ddmcdn.com/en-us/dsc//images/default-still.jpg'
	},
	{
		'title': 	'Animal Planet',
		'id':		'apl',
		'url':		'http://animal.discovery.com',
		'thumb':	'http://static.ddmcdn.com/en-us/apl//images/default-still.jpg'
	},
	{
		'title': 	'TLC',
		'id':		'tlc',
		'url':		'http://www.tlc.com',
		'thumb':	'http://static.ddmcdn.com/en-us/tlc//images/default-still.jpg'
	},
	{
		'title': 	'Investigation Discovery',
		'id':		'investigation+discovery',
		'url':		'http://investigation.discovery.com',
		'thumb':	'http://static.ddmcdn.com/en-us/ids//images/default-still.jpg'
	},
	{
		'title': 	'Science',
		'id':		'science',
		'url':		'http://science.discovery.com',
		'thumb':	'http://static.ddmcdn.com/en-us/sci//images/default-still.jpg'
	},
	{
		'title': 	'Destination America',
		'id':		'dam',
		'url':		'http://america.discovery.com',
		'thumb':	'http://static.ddmcdn.com/en-us/dam//images/default-still.jpg'
	},
	{
		'title': 	'Military Channel',
		'id':		'military',
		'url':		'http://military.discovery.com',
		'thumb':	'http://static.ddmcdn.com/en-us/mil//images/default-still.jpg'
	},
	{
		'title': 	'Velocity',
		'id':		'velocity',
		'url':		'http://velocity.discovery.com',
		'thumb':	'http://static.ddmcdn.com/en-us/vel//images/default-still.jpg'
	}
]

##########################################################################################
def Start():
	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
	Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")

	# Setup the default attributes for the ObjectContainer
	ObjectContainer.title1     = TITLE
	ObjectContainer.view_group = "List"
	ObjectContainer.art        = R(ART)

	# Setup the default attributes for the other objects
	DirectoryObject.thumb = R(ICON)
	DirectoryObject.art   = R(ART)
	VideoClipObject.thumb = R(ICON)
	VideoClipObject.art   = R(ART)

	HTTP.CacheTime             = CACHE_1HOUR
	HTTP.Headers['User-agent'] = HTTP_USER_AGENT

##########################################################################################
@handler('/video/discovery', TITLE, art = ART, thumb = ICON)
def MainMenu():
	oc = ObjectContainer()
	
	# Add all channels
	for channel in CHANNELS:
		oc.add(
			DirectoryObject(
				key = Callback(
						ShowsChoice, 
						title = channel["title"], 
						url = channel["url"],
						id = channel["id"],
						thumb = channel["thumb"]), 
				title = channel["title"], 
				thumb = channel["thumb"]
			)
		)		
	
	# Add preference for video resolution
	oc.add(PrefsObject(title = "Settings..."))
	
	return oc

##########################################################################################
@route("/video/discovery/ShowsChoice")
def ShowsChoice(title, url, id, thumb):
	oc = ObjectContainer(title1 = title)
	
	pageElement = HTML.ElementFromURL(url + "/services/taxonomy/" + id + "/?feedGroup=video&filter=fullepisode&num=1")
	
	if GetTotalEpisodes(pageElement) > 0:
		oc.add(
			DirectoryObject(
				key = Callback(
						Shows, 
						title = title,
						url = url,
						thumb = thumb,
						fullEpisodesOnly = True), 
				title = "Shows With Full Episodes", 
				thumb = thumb
			)
		)				

		oc.add(
			DirectoryObject(
				key = Callback(
						Shows, 
						title = title,
						url = url,
						thumb = thumb,
						fullEpisodesOnly = False), 
				title = "All Shows", 
				thumb = thumb
			)
		)
		
		return oc
		
	else:
		oc.add(
			DirectoryObject(
				key = Callback(
						Shows, 
						title = title,
						url = url,
						thumb = thumb,
						fullEpisodesOnly = False), 
				title = "All Shows (clips only)", 
				thumb = thumb
			)
		)	
	
	return oc
	
##########################################################################################
@route("/video/discovery/Shows", fullEpisodesOnly = bool)
def Shows(title, url, thumb, fullEpisodesOnly):
	oc = ObjectContainer(title1 = title)
	
	# Add shows by parsing the site
	shows       = []
	showNames   = []
	pageElement = HTML.ElementFromURL(url + "/videos")
	
	for item in pageElement.xpath("//*[@class = 'show-badge']"):
		containsFullEpisodes = "full-episodes" in item.xpath(".//a/@data-module-name")[0] 
		
		if fullEpisodesOnly and not containsFullEpisodes:
			continue

		showUrl = item.xpath(".//a/@href")[0]
		
		if not showUrl:
			continue
		
		if not 'tv-shows/' in showUrl:
			continue

		show = {}
		
		if showUrl.startswith("http"):
			show["url"] = showUrl
		else:
			if not showUrl.startswith("/"):
				showUrl = "/" + showUrl
				
			show["url"] = url + showUrl

		show["img"]  = item.xpath(".//img/@src")[0]
		show["name"] = ExtractNameFromURL(show["url"])
		
		if not show["name"] in showNames:
			showNames.append(show["name"])
			shows.append(show)

	sortedShows = sorted(shows, key=lambda show: show["name"])
	for show in sortedShows:
		oc.add(
			DirectoryObject(
				key = Callback(
						VideosChoice, 
						title = show["name"],
						base_url = url, 
						url = show["url"], 
						thumb = show["img"]), 
				title = show["name"],
				thumb = show["img"]
			)
		)
	
	if len(oc) < 1:
		oc.header  = "Sorry"
		oc.message = "No shows found."
					 
	return oc

##########################################################################################
@route("/video/discovery/VideosChoice")
def VideosChoice(title, base_url, url, thumb):
	oc = ObjectContainer(title1 = title)
	
	pageElement = HTML.ElementFromURL(url)
	
	try:
		serviceURI  = pageElement.xpath("//section[contains(@id, 'all-videos')]//div/@data-service-uri")[0]
		pageElement = HTML.ElementFromURL(base_url + serviceURI + '?num=1&page=0&filter=fullepisode')
	except:
		try:
			# The serviceURI couldn't be retrieved
			# Known shows with this error:
			# - Backyard Oil
			# - Overhaulin when viewed from Discovery Channel(this is in fact a show in Velocity)
			serviceURI  = "/services/taxonomy/" + title.replace(" ", "+")
			
			if 'Overhaulin' in title:
				serviceURI = serviceURI + "'/"
				
			pageElement = HTML.ElementFromURL(base_url + serviceURI + '?num=1&page=0&filter=fullepisode')
		except:
			Log.Warn("Show without valid service url or no videos yet: " + title)
			oc.header  = "Sorry"
			oc.message = "No videos found."
			return oc
	
	if GetTotalEpisodes(pageElement) > 0:
		oc.add(
			DirectoryObject(
				key = Callback(
						Videos, 
						title = title,
						base_url = base_url, 
						url = url,
						serviceURI = serviceURI, 
						thumb = thumb,
						episodeReq = True), 
				title = "Full Episodes", 
				thumb = thumb
			)
		)				

		oc.add(
			DirectoryObject(
				key = Callback(
						Videos, 
						title = title,
						base_url = base_url, 
						url = url,
						serviceURI = serviceURI,
						thumb = thumb,
						episodeReq = False), 
				title = "Clips", 
				thumb = thumb
			)
		)
		
		return oc
	else:
		return Videos(
				title = title,
				base_url = base_url, 
				url = url,
				serviceURI = serviceURI,
				thumb = thumb,
				episodeReq = False)

##########################################################################################
@route("/video/discovery/Videos", episodeReq = bool, page = int)
def Videos(title, base_url, url, serviceURI, thumb, episodeReq, page = 0):
	oc            = ObjectContainer(title1 = title)
	oc.view_group = "InfoList"
	
	if episodeReq:
		optionString = "fullepisode"
	else:
		optionString = "clip"
		
	pageElement = HTML.ElementFromURL(base_url + serviceURI + '?num=' + str(ITEMS_PER_PAGE) + '&page=' + str(page) + '&filter=' + optionString + '&sort=date&order=desc&feedGroup=video&tpl=dds%2Fmodules%2Fvideo%2Fall_assets_list.html')

	for item in pageElement.xpath("//tr"):
		test = item.xpath(".//td")
		if len(test) < 1:
			continue
			
		videoUrl = item.xpath(".//a/@href")[0]
		
		if not videoUrl.startswith("http"):
			videoUrl = base_url + videoUrl

		video        = {}			
		video["url"] = videoUrl
		
		try:
			video["img"] = item.xpath(".//a//img/@src")[0]
		except:
			video["img"] = None
			
		try:
			video["name"] = item.xpath(".//h4//a/text()")[0]
		except:
			video["name"] = None
		
		try:
			video["summary"] = item.xpath(".//p/text()")[0]
		except:
			video["summary"] = None
			
		try:
			video["show"] = item.xpath(".//h5/text()")[0]
		except:
			video["show"] = None
		
		try:
			video["date"] = Datetime.ParseDate(item.xpath(".//div[contains(@class, 'date')]/text()")[0]).date()
		except:
			video["date"] = None
			
		try:
			length             = item.xpath(".//div[contains(@class, 'length')]/text()")[0]
			(minutes, seconds) = length.split(":")
			video["duration"]  = (int(minutes) * 60 + int(seconds)) * 1000
		except:
			video["duration"] = None
		
		if Prefs['qualitypreference'] == "Automatic":
			pass
		elif Prefs['qualitypreference'] == "High (720p)":
			video["url"] = video["url"] + "?resolution=720"
		elif Prefs['qualitypreference'] == "Normal (480p)":
			video["url"] = video["url"] + "?resolution=480"
		elif Prefs['qualitypreference'] == "Medium (360p)":
			video["url"] = video["url"] + "?resolution=360"
		else:
			video["url"] = video["url"] + "?resolution=270"
		
		oc.add(
			EpisodeObject(
				url = video["url"],
				title = video["name"],
				show = video["show"],
				summary = video["summary"],
				thumb = video["img"],
				originally_available_at = video["date"],
				duration = video["duration"]
			)
		)		
    
	if len(oc) >= ITEMS_PER_PAGE:
		for item in pageElement.xpath("//div[contains(@class, 'pagination')]//ul//li"):
			try:
				if item.xpath(".//a/@href")[0]:   
					oc.add(
						NextPageObject(
							key = Callback(
									Videos, 
									title = title, 
									base_url = base_url, 
									url = url,
									serviceURI = serviceURI,
									thumb = thumb,
									episodeReq = episodeReq,
									page = page + 1), 
							title = "More ...")
					)
					return oc
			except:
				pass
		
	return oc


##########################################################################################
def GetTotalEpisodes(pageElement):
	totalFullEpisodes = 0
	
	for item in pageElement.xpath("//ul//li/text()"):
		if 'total' in item.lower():
			m = Regex('.*total *: *([0-9]+).*', Regex.IGNORECASE|Regex.MULTILINE).search(item)
			if m is not None:
				totalFullEpisodes = int(m.groups()[0])
				break
	
	return totalFullEpisodes
			

##########################################################################################
def ExtractNameFromURL(url):
	if url.endswith("/"):
		url = url[:-1]
	if url.endswith("/videos"):
		url = url[:url.find("/videos")]
	url = url[url.rfind("/") + 1:]
	if ".htm" in url:
		url = url[:url.find(".htm")]
	if "-videos" in url:
		url = url.replace("-videos", "")
	return url.replace("-", " ").title()
