TITLE = 'Discovery Networks'
ART   = 'art-default.jpg'
ICON  = 'icon-default.png'

PREFIX = '/video/discovery'
ITEMS_PER_PAGE = 50

HTTP_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/536.26.17 (KHTML, like Gecko) Version/6.0.2 Safari/536.26.17"

CHANNELS = [ 
    {
        'title':    'Discovery Channel',
        'desc':     'Science, History, Space, Tech, Sharks, News!',
        'id':       'Discovery',
        'url':      'http://dsc.discovery.com',
        'thumb':    'http://static.ddmcdn.com/en-us/dsc//images/default-still.jpg'
    },
    {
        'title':    'Animal Planet',
        'desc':     'Animal Planet lets you explore cat breeds, dog breeds, wild animals and pets.',
        'id':       'apl',
        'url':      'http://animal.discovery.com',
        'thumb':    'http://static.ddmcdn.com/en-us/apl//images/default-still.jpg'
    },
    {
        'title':    'Animal Planet LIVE',
        'desc':     'Animal Planet LIVE, featuring live HD cams for chicks, puppies, ants, cockroaches, penguins, kittens and many more.',
        'id':       'apltv',
        'url':      'http://www.apl.tv',
        'thumb':    'http://static.ddmcdn.com/en-us/apltv/img/body-bg-2.jpg'
    },
    {
        'title':    'TLC',
        'desc':     'TLC TV network opens doors to extraordinary lives.',
        'id':       'tlc',
        'url':      'http://www.tlc.com',
        'thumb':    'http://static.ddmcdn.com/en-us/tlc//images/default-still.jpg'
    },
    {
        'title':    'Investigation Discovery',
        'desc':     'Hollywood crimes, murder and forensic investigations. Investigation Discovery gives you insight into true stories that piece together puzzles of human nature.',
        'id':       'investigation+discovery',
        'url':      'http://investigationdiscovery.com',
        'thumb':    'http://static.ddmcdn.com/en-us/ids//images/default-still.jpg'
    },
    {
        'title':    'Destination America',
        'desc':     'Destination America.',
        'id':       'dam',
        'url':      'http://america.discovery.com',
        'thumb':    'http://static.ddmcdn.com/en-us/dam//images/default-still.jpg'
    },
    {
        'title':    'Velocity',
        'desc':     'Get ready for Velocity!  Velocity brings the best of car programming with diverse new original series and specials.',
        'id':       'velocity',
        'url':      'http://velocity.discovery.com',
        'thumb':    'http://static.ddmcdn.com/en-us/vel//images/default-still.jpg'
    }
]

##########################################################################################
def Start():
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")

    # Setup the default attributes for the ObjectContainer
    ObjectContainer.title1     = TITLE
    ObjectContainer.view_group = "InfoList"
    ObjectContainer.art        = R(ART)

    # Setup the default attributes for the other objects
    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art   = R(ART)
    EpisodeObject.thumb   = R(ICON)
    EpisodeObject.art     = R(ART)

    HTTP.CacheTime             = CACHE_1HOUR
    HTTP.Headers['User-agent'] = HTTP_USER_AGENT

##########################################################################################
@handler(PREFIX, TITLE, art = ART, thumb = ICON)
def MainMenu():
    oc = ObjectContainer()
    
    # Add all channels
    for channel in CHANNELS:
        if channel["title"] == 'Animal Planet LIVE':
            oc.add(
                DirectoryObject(
                    key = Callback(
                            LiveStreams, 
                            title = channel["title"], 
                            url = channel["url"],
                            thumb = channel["thumb"]), 
                    title = channel["title"],
                    summary = channel["desc"],
                    thumb = channel["thumb"]
                )
            )
        else:
            oc.add(
                DirectoryObject(
                    key = Callback(
                            ShowsChoice, 
                            title = channel["title"], 
                            url = channel["url"],
                            id = channel["id"],
                            thumb = channel["thumb"]), 
                    title = channel["title"],
                    summary = channel["desc"],
                    thumb = channel["thumb"]
                )
            )       
    
    return oc

##########################################################################################
@route(PREFIX + "/Episodes")
def Episodes(url, thumb, title):
    oc = ObjectContainer(title2 = title)   
    
    pageElement = HTML.ElementFromURL(url + "/videos")
    
    for item in pageElement.xpath("//*[@data-item-index]"):
        if True:
            fullEpisode = item.xpath("./@data-item-type")[0] == "fullepisode"
            
            if not fullEpisode:
                continue
        else:
            continue
        
        url = item.xpath(".//a/@href")[0].strip() 
        title = item.xpath(".//img/@alt")[0].strip()
        
        try:
            thumb = item.xpath(".//img/@src")[0].strip()
        except:
            thumb = R(ICON)
            
        try:
            show = item.xpath(".//*[contains(@class,'show-title')]/text()")[0].strip()
        except:
            show = None
            
        try:
            summary = item.xpath(".//*[contains(@class,'description')]/text()")[0].strip()
        except:
            summary = None
            
        try:
            durationString = item.xpath(".//*[contains(@class,'extra')]/text()")[0].strip()
            duration = ((int(durationString.split(':')[0]) * 60) + int(durationString.split(':')[1])) * 1000
        except:
            duration = None
            
        oc.add(
            EpisodeObject(
                url = url,
                title = title,
                thumb = thumb,
                show = show,
                summary = summary,
                duration = duration
            )
        )
    
    if len(oc) < 1:
        oc.header = "Sorry"
        oc.message = "Couldn't find any episodes"
    
    return oc

##########################################################################################
@route(PREFIX + "/ShowsChoice")
def ShowsChoice(title, url, id, thumb):
    oc = ObjectContainer(title2 = title)
    
    try:
        fullEpisodesURL = url + "/services/taxonomy/" + id + "/?feedGroup=video&filter=fullepisode&num=200"
        pageElement     = HTML.ElementFromURL(fullEpisodesURL)
    except:
        return Episodes(url = url, thumb = thumb, title = title)
    
    if GetTotalEpisodes(pageElement) > 0:
        oc.add(
            DirectoryObject(
                key = Callback(
                        Shows, 
                        title = title,
                        url = url,
                        thumb = thumb,
                        fullEpisodesOnly = True,
                        fullEpisodesURL = fullEpisodesURL), 
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
@route(PREFIX + "/Shows", fullEpisodesOnly = bool)
def Shows(title, url, thumb, fullEpisodesOnly, fullEpisodesURL = None):
    oc = ObjectContainer(title1 = title)
    
    # Add shows by parsing the site
    shows       = []
    showNames   = []
    pageElement = HTML.ElementFromURL(url + "/videos")
    
    for item in pageElement.xpath("//*[@id='masc']//*[@class='item']//a"):
        showUrl = item.xpath("./@href")[0]
        
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
            
        try:
            show["img"] = item.xpath(".//img/@data-original")[0]
        except:
            show["img"] = thumb
        
        show["name"] = ExtractNameFromURL(show["url"])
    
        if fullEpisodesOnly:
            fullEpisodesElement = HTML.ElementFromURL(fullEpisodesURL)
            if not ShowInFullEpisodesList(fullEpisodesElement, show["name"]):
                continue
        
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
@route(PREFIX + "/VideosChoice")
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
                        episodeReq = False), 
                title = "Clips", 
                thumb = thumb
            )
        )

        episode_oc = Videos(
            title = title,
            base_url = base_url, 
            url = url,
            serviceURI = serviceURI, 
            thumb = thumb,
            episodeReq = True        
        )
        
        for episode in episode_oc.objects:
            oc.add(episode)
        
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
@route(PREFIX + "/Videos", episodeReq = bool, page = int)
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
@route(PREFIX + "/LiveStreams")
def LiveStreams(title, url, thumb):
    oc            = ObjectContainer(title1 = title)
    oc.view_group = "InfoList"
    
    pageElement = HTML.ElementFromURL(url)

    for item in pageElement.xpath("//div[contains(@class, 'slider')]//div"):
        test = item.xpath(".//td")
            
        video        = {}           
        video["url"] = item.xpath(".//a/@href")[0]
        
        try:
            video["img"] = item.xpath(".//a//img/@src")[0]
        except:
            video["img"] = None
            
        try:
            video["name"] = item.xpath(".//h3/text()")[0]
        except:
            video["name"] = None

        oc.add(
            EpisodeObject(
                url = video["url"],
                title = video["name"],
                thumb = video["img"]
            )
        )       
        
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
def ShowInFullEpisodesList(pageElement, showName):
    for item in pageElement.xpath("//ul//li/text()"):
        if 'title' in item.lower():
            if showName.lower() in item.lower():
                return True
    
    return False

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
