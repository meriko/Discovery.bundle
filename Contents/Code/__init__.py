import urllib2

TITLE = 'Discovery'
ART   = 'art-default.jpg'
ICON  = 'icon-default.png'

ITEMS_PER_PAGE = 50

CHANNELS = []

CHANNEL          = {}
CHANNEL["title"] = 'Discovery Channel'
CHANNEL["url"]   = 'http://dsc.discovery.com'
CHANNEL["thumb"] = 'http://static.ddmcdn.com/en-us/dsc//images/default-still.jpg'
CHANNELS.append(CHANNEL)

CHANNEL          = {}
CHANNEL["title"] = 'Animal Planet'
CHANNEL["url"]   = 'http://animal.discovery.com'
CHANNEL["thumb"] = 'http://static.ddmcdn.com/en-us/apl//images/default-still.jpg'
CHANNELS.append(CHANNEL)

CHANNEL          = {}
CHANNEL["title"] = 'TLC'
CHANNEL["url"]   = 'http://www.tlc.com'
CHANNEL["thumb"] = 'http://static.ddmcdn.com/en-us/tlc//images/default-still.jpg'
CHANNELS.append(CHANNEL)

CHANNEL          = {}
CHANNEL["title"] = 'Investigation'
CHANNEL["url"]   = 'http://investigation.discovery.com'
CHANNEL["thumb"] = 'http://static.ddmcdn.com/en-us/ids//images/default-still.jpg'
CHANNELS.append(CHANNEL)

CHANNEL          = {}
CHANNEL["title"] = 'Science'
CHANNEL["url"]   = 'http://science.discovery.com'
CHANNEL["thumb"] = 'http://static.ddmcdn.com/en-us/sci//images/default-still.jpg'
CHANNELS.append(CHANNEL)

CHANNEL          = {}
CHANNEL["title"] = 'Destination America'
CHANNEL["url"]   = 'http://america.discovery.com'
CHANNEL["thumb"] = 'http://static.ddmcdn.com/en-us/dam//images/default-still.jpg'
CHANNELS.append(CHANNEL)

CHANNEL          = {}
CHANNEL["title"] = 'Military Channel'
CHANNEL["url"]   = 'http://military.discovery.com'
CHANNEL["thumb"] = 'http://static.ddmcdn.com/en-us/mil//images/default-still.jpg'
CHANNELS.append(CHANNEL)

CHANNEL          = {}
CHANNEL["title"] = 'Velocity'
CHANNEL["url"]   = 'http://velocity.discovery.com'
CHANNEL["thumb"] = 'http://static.ddmcdn.com/en-us/vel//images/default-still.jpg'
CHANNELS.append(CHANNEL)

##########################################################################################
def Start():
	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

	# Setup the default attributes for the ObjectContainer
	ObjectContainer.title1 = TITLE
	ObjectContainer.view_group = 'List'
	ObjectContainer.art = R(ART)

	# Setup the default attributes for the other objects
	DirectoryObject.thumb = R(ICON)
	DirectoryObject.art = R(ART)
	VideoClipObject.thumb = R(ICON)
	VideoClipObject.art = R(ART)

	HTTP.CacheTime = CACHE_1HOUR

##########################################################################################
@handler('/video/discovery', TITLE, art=ART, thumb=ICON)
def MainMenu():
	menu = ObjectContainer(title1 = TITLE)
	
	# Add all channels
	for channel in CHANNELS:
		menu.add(
			DirectoryObject(
				key = Callback(
						Shows, 
						title = channel["title"], 
						url = channel["url"], 
						thumb = channel["thumb"]), 
				title = channel["title"], 
				thumb = channel["thumb"]
			)
		)		
	
	# Add preference for video resolution
	menu.add(PrefsObject(title = "Settings..."))
	
	return menu

##########################################################################################
@route("/video/discovery/Shows")
def Shows(title, url, thumb):
	oc = ObjectContainer(title1 = title)
	
	# Add shows by parsing the site
	shows       = []
	pageElement = HTML.ElementFromURL(url + "/tv-shows")
	for item in pageElement.xpath("//div[contains(@class, 'show-badge')]"):
		show         = {}
		show["url"]  = url + item.xpath(".//a/@href")[0]
		show["name"] = ExtractNameFromURL(show["url"])
		show["img"]  = item.xpath(".//img/@src")[0]
		
		if not show in shows:
			shows.append(show)

	sortedShows = sorted(shows, key=lambda show: show["name"])
	for show in sortedShows:
		oc.add(
			DirectoryObject(
				key = Callback(
						Choice, 
						title = show["name"],
						base_url = url, 
						url = show["url"], 
						thumb = show["img"]), 
				title = show["name"], 
				thumb = show["img"]
			)
		)
								 
	return oc

##########################################################################################
@route("/video/discovery/Choice")
def Choice(title, base_url, url, thumb):
	oc = ObjectContainer(title1 = title)
	
	pageElement = HTML.ElementFromURL(url)
	
	try:
		serviceURI = pageElement.xpath("//section[contains(@id, 'all-videos')]//div/@data-service-uri")[0]
	except:
		Log.Error("Show without valid service url: " + title)
		return ObjectContainer(header="Sorry", message="A problem occured when retrieving data for this show.")
	
	pageElement = HTML.ElementFromURL(base_url + serviceURI + '?num=1&page=0&filter=fullepisode')
	
	totalFullEpisodes = 0
	for item in pageElement.xpath("//ul//li/text()"):
		if 'total' in item:
			totalFullEpisodes = int(item[item.find("total: ") + 7:])
			break
	
	if totalFullEpisodes > 0:
		oc.add(
			DirectoryObject(
				key = Callback(
						Videos, 
						title = title,
						base_url = base_url, 
						url = url, 
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
					thumb = thumb,
					episodeReq = False), 
			title = "Clips", 
			thumb = thumb
		)
	)

	return oc

##########################################################################################
@route("/video/discovery/Videos", episodeReq = bool, page = int)
def Videos(title, base_url, url, thumb, episodeReq, page = 0, ):
	dir = ObjectContainer(title2 = title)
	
	if episodeReq:
		optionString = "fullepisode"
	else:
		optionString = "clip"
		
	pageElement = HTML.ElementFromURL(url)
	serviceURI  = pageElement.xpath("//section[contains(@id, 'all-videos')]//div/@data-service-uri")[0]
	pageElement = HTML.ElementFromURL(base_url + serviceURI + '?num=' + str(ITEMS_PER_PAGE) + '&page=' + str(page) + '&filter=' + optionString + '&sort=date&order=desc&feedGroup=video&tpl=dds%2Fmodules%2Fvideo%2Fall_assets_grid.html')

	for item in pageElement.xpath("//div[contains(@class, 'item')]"):
		video         = {}
		video["url"]  = base_url + item.xpath(".//a/@href")[0]
		video["img"]  = item.xpath(".//img/@src")[0]
		video["name"] = item.xpath(".//h4//a/text()")[0]

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

		try:
			detailsPageElement = HTML.ElementFromURL(base_url + serviceURI + '?num=' + str(ITEMS_PER_PAGE) + '&page=' + str(page) + '&filter=clip%2Cfullepisode&sort=date&order=desc&feedGroup=video')
			Log(video["name"])
			Log("--------- New details")
			collectData = False
			for detailItem in detailsPageElement.xpath("//ul//li/text()"):
				if 'title' in detailItem and video["name"].lower() in detailItem.lower():
					collectData = True
			
				if 'date:' in detailItem and collectData:
					dateString = detailItem[detailItem.find("date: ") + 6:]
					video["date"] = Datetime.ParseDate(dateString).date()
					Log(video["date"])
				
				if 'duration raw:' in detailItem and collectData:
					video["duration"] = int(detailItem[detailItem.find("duration raw: ") + 14:]) * 1000
					break
		except:
			video["date"]     = None
			video["duration"] = None	
		
		if episodeReq:
			dir.add(
				EpisodeObject(
					url = video["url"],
					title = video['name'],
					thumb = video['img'],
					originally_available_at = video["date"],
					duration = video["duration"])
			)		
		else:
			dir.add(
				VideoClipObject(
					url = video["url"],
					title = video['name'],
					thumb = video['img'],
					originally_available_at = video["date"],
					duration = video["duration"])
        	)
    
	if len(dir) >= ITEMS_PER_PAGE:
		for item in pageElement.xpath("//div[contains(@class, 'pagination')]//ul//li"):
			try:
				if item.xpath(".//a/@href")[0]:   
					dir.add(
						NextPageObject(key = Callback(Videos, title = title, 
	 							                              base_url = base_url, 
     								                     	  url = url,
       								                     	  thumb = thumb,
       								                     	  episodeReq = episodeReq,
       		    						                      page = page + 1), 
						   		   	title = "More ...")
					)
					return dir
			except:
				pass
		
	return dir

##########################################################################################
def ExtractNameFromURL(url):
	if url.endswith("/"):
		url = url[:-1]
	if ".htm" in url:
		url = url[:url.find(".htm")]
	if "/video" in url:
		url = url[:url.find("/video")]
	return url[url.rfind("/") + 1 :].replace("-", " ").title()
