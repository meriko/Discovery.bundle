TITLE = 'Discovery Networks'
ART   = 'art-default.jpg'
ICON  = 'icon-default.png'
PREFIX = '/video/discovery'
HTTP_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/536.26.17 (KHTML, like Gecko) Version/6.0.2 Safari/536.26.17"

CHANNELS = [ 
    {
        'title':    'Discovery Channel',
        'desc':     'Science, History, Space, Tech, Sharks, News!',
        'url':      'http://dsc.discovery.com',
        'thumb':    'http://static.ddmcdn.com/en-us/dsc//images/default-still.jpg'
    },
    {
        'title':    'Animal Planet',
        'desc':     'Animal Planet lets you explore cat breeds, dog breeds, wild animals and pets.',
        'url':      'http://animal.discovery.com',
        'thumb':    'http://static.ddmcdn.com/en-us/apl//images/default-still.jpg'
    },
    {
        'title':    'Animal Planet LIVE',
        'desc':     'Animal Planet LIVE, featuring live HD cams for chicks, puppies, ants, cockroaches, penguins, kittens and many more.',
        'url':      'http://www.apl.tv',
        'thumb':    'http://static.ddmcdn.com/en-us/apltv/img/body-bg-2.jpg'
    },
    {
        'title':    'TLC',
        'desc':     'TLC TV network opens doors to extraordinary lives.',
        'url':      'http://www.tlc.com',
        'thumb':    'http://static.ddmcdn.com/en-us/tlc//images/default-still.jpg'
    },
    {
        'title':    'Investigation Discovery',
        'desc':     'Hollywood crimes, murder and forensic investigations. Investigation Discovery gives you insight into true stories that piece together puzzles of human nature.',
        'url':      'http://investigationdiscovery.com',
        'thumb':    'http://static.ddmcdn.com/en-us/ids//images/default-still.jpg'
    },
    {
        'title':    'Destination America',
        'desc':     'Destination America.',
        'url':      'http://america.discovery.com',
        'thumb':    'http://static.ddmcdn.com/en-us/dam//images/default-still.jpg'
    },
    {
        'title':    'Velocity',
        'desc':     'Get ready for Velocity!  Velocity brings the best of car programming with diverse new original series and specials.',
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

    HTTP.CacheTime  = CACHE_1HOUR
    HTTP.User_Agent = HTTP_USER_AGENT

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
                        thumb = channel["thumb"]
                    ), 
                    title = channel["title"],
                    summary = channel["desc"],
                    thumb = channel["thumb"]
                )
            )
        else:
            oc.add(
                DirectoryObject(
                    key = Callback(
                        Episodes,
                        url = channel["url"],
                        thumb = channel["thumb"],
                        channel_title = channel["title"]
                    ), 
                    title = channel["title"],
                    summary = channel["desc"],
                    thumb = channel["thumb"]
                )
            )       
    
    return oc

##########################################################################################
@route(PREFIX + "/Episodes")
def Episodes(url, thumb, channel_title):
    oc = ObjectContainer(title2 = channel_title)   
    
    pageElement = HTML.ElementFromURL(url + "/videos")
    
    for item in pageElement.xpath("//*[@data-item-index]"):
        try:
            fullEpisode = item.xpath("./@data-item-type")[0] == "fullepisode"
            
            if not fullEpisode:
                continue
        except:
            continue
        
        url = item.xpath(".//a/@href")[0].strip() 
        title = item.xpath(".//*[@class='item-title']/text()")[0].strip()
        
        try:
            thumb = item.xpath(".//a/@style")[0].split("(")[1].split(")")[0]
        except:
            thumb = R(ICON)
            
        try:
            show = item.xpath(".//*[contains(@class,'show')]/text()")[0].strip()
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
                duration = duration,
                source_title = channel_title
            )
        )
    
    if len(oc) < 1:
        oc.header = "Sorry"
        oc.message = "Couldn't find any episodes"
    
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

