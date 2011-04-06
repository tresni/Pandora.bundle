NAMESPACES = {'pandora':'http://www.pandora.com/rss/1.0/modules/pandora/'}
ART = 'art-default.jpg'
ICON = 'icon-default.jpg'
ICON_PREFS = 'icon-prefs.png'
ICON_SEARCH = 'icon-search.png'

FEED_URL = 'http://feeds.pandora.com/feeds/people/%s/%s.xml'

####################################################################################################
def Start():
    # Current artwork.jpg free for personal use only - http://squaresailor.deviantart.com/art/Apple-Desktop-52188810
    Plugin.AddPrefixHandler('/music/pandora', MainMenu, 'Pandora', ICON, ART)
    Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')
    Plugin.AddViewGroup('List', viewMode='List', mediaType='items')

    MediaContainer.title1 = 'Pandora'
    MediaContainer.art = R(ART)
    MediaContainer.viewGroup = 'List'

    DirectoryItem.thumb = R(ICON)
    WebVideoItem.thumb = R(ICON)

    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_7; en-us) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27'

####################################################################################################  
def WebnameFromEmail(email, authenticate=False):
    jsonUrl = 'http://feeds.pandora.com/services/ajax/?method=authenticate.emailToWebname&email=' + email

    if authenticate:
        values = {'loginform': '',
                  'login_username': Prefs['pan_user'],
                  'login_password': Prefs['pan_pass']}
        dict = JSON.ObjectFromURL(jsonUrl, values=values)
    else:
        dict = JSON.ObjectFromURL(jsonUrl)

    if dict['stat'] == 'ok':
        return dict['result']['webname']
    else:
        return False

####################################################################################################  
def MainMenu():
    dir = MediaContainer(noCache=True)

    if not Prefs['pan_user'] or not Prefs['pan_pass']:
        dir.Append(PrefsItem(title='Set your Pandora Preferences', thumb=R(ICON_PREFS)))
    elif not WebnameFromEmail(Prefs['pan_user']):
        dir.Append(PrefsItem(title='Set your Pandora Preferences', thumb=R(ICON_PREFS)))
        dir.header = "Couldn't find your account"
        dir.message = "Please check your settings"
    else:
        webname = WebnameFromEmail(Prefs['pan_user'], True)

        dir.Append(Function(DirectoryItem(Bookmarks, title='Your Stations'), webname=webname, feed='stations'))
        dir.Append(Function(DirectoryItem(Bookmarks, title='Your Bookmarked Songs'), webname=webname, feed='favorites'))
        dir.Append(Function(DirectoryItem(Bookmarks, title='Your Bookmarked Artists'), webname=webname, feed='favoriteartists'))

        dir.Append(Function(InputDirectoryItem(ArtistSearch, title='Search Station by Artist', prompt='Search Station by Artist', thumb=R(ICON_SEARCH))))
        dir.Append(Function(InputDirectoryItem(EmailSearch, title='Search for User Stations by Email', prompt='Search for User Stations by Email', thumb=R(ICON_SEARCH))))
        dir.Append(Function(InputDirectoryItem(WebnameSearch, title='Search for User Stations by ID', prompt='Search for User Stations by ID', thumb=R(ICON_SEARCH))))
        dir.Append(PrefsItem(title='Change your Pandora Preferences', thumb=R(ICON_PREFS)))

    return dir

####################################################################################################  
def Bookmarks(sender, webname, feed):
    dir = MediaContainer(title2=sender.itemTitle)
    url = FEED_URL % (webname, feed)

    for item in XML.ElementFromURL(url, errors='ignore').xpath('//item'):
        title = item.xpath('./title')[0].text
        link = item.xpath('./link')[0].text
        desc = item.xpath('./description')[0].text

        try:
            if feed == 'stations':
                thumb = item.xpath('./pandora:stationAlbumArtImageUrl', namespaces=NAMESPACES)[0].text
            elif feed == 'favorites':
                thumb = item.xpath('./pandora:albumArtUrl', namespaces=NAMESPACES)[0].text
            elif feed == 'favoriteartists':
                thumb = item.xpath('./pandora:artistPhotoUrl', namespaces=NAMESPACES)[0].text
        except:
            thumb = None

        dir.Append(WebVideoItem(link, title=title, summary=desc, thumb=Function(GetThumb, url=thumb)))

    return dir
        
####################################################################################################  
def ArtistSearch(sender, query):
    dir = MediaContainer(title2=sender.itemTitle)
    content = HTML.ElementFromURL('http://www.pandora.com/backstage?type=all&q=' + query).xpath('//table[@id="tbl_artist_search_results"]/tbody/tr')

    for artist in content:
        thumb = artist.xpath('./td/a/img')[0].get('src')
        a = artist.xpath('./td/a')
        href = a[1].get('href')
        url = 'http://www.pandora.com/?search=' + href[href.rfind('/')+1:]
        title = a[1].text
        dir.Append(WebVideoItem(url, title=title, thumb=Function(GetThumb, url=thumb)))

    return dir

####################################################################################################  
def EmailSearch(sender, query):
    dir = MediaContainer(title2=sender.itemTitle)

    if WebnameFromEmail(query):
        dir = Bookmarks(sender, query, 'stations')
        return dir
    else:
        return MessageContainer('Invalid Email', 'Search for User Stations by Email')

####################################################################################################  
def WebnameSearch(sender, query):
    dir = MediaContainer(title2=sender.itemTitle)

    try:
        dir = Bookmarks(sender, query, 'stations')
        return dir
    except:
        return MessageContainer('Invalid Webname', 'Search for User Stations by Webname')

####################################################################################################  
def GetThumb(url):
    if url:
        try:
            data = HTTP.Request(url, cacheTime=CACHE_1MONTH).content
            return DataObject(data, 'image/jpeg')
        except:
            pass

    return Redirect(R(ICON))
