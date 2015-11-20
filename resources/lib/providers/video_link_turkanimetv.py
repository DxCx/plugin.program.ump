import re
from unidecode import unidecode
			
domain="http://www.turkanime.tv/"
encoding="utf-8"


def return_links(name,url,fs):
	mpage=ump.get_page(url,encoding)
	iframe = re.findall("<iframe.+?src=\"(.+?)\"", mpage, re.DOTALL)
	if len(iframe) == 3:
		video_url = iframe[0]
	else:
		links = re.findall("<a\shref=\"([^\"]+?)\"\starget=\"_blank\"><img\ssrc=\"imajlar/kontrol.png\"\salt=\"\"></a>", mpage, re.DOTALL)
		if len(links) != 1:
			ump.add_log("unable to parse %s" % url)
			return None
		video_url = links[0]

	parts=[{"url": video_url}]
	prefix=""
	if not fs == "Varsayilan":
		prefix="[FS:%s]"%fs
	name="%s[HS:TR]%s" % (prefix,name)
	ump.add_mirror(parts,name)

def scrape_moviepage(url,fansub,name):
	pg=ump.get_page(domain+url,encoding)
	videos=re.findall("'#video','(.*?)','#video'.*?icon-play\"></i>(.*?)</a>",pg)
	for video in videos:
		url = domain+video[0]
		return_links(name, url, fansub)
		continue
		
def run(ump):
	globals()['ump'] = ump
	i=ump.info
	names=[i["tvshowtitle"]]
	if "tvshowalias" in i.keys():
		names.extend(i["tvshowalias"].split("|"))
	if "title" in i.keys() and not i["title"]=="":
		names.append(i["title"])
	is_movie=False
	url=None
	animes=re.findall('<a href="(.*?)" class="btn".*?title="(.*?)">',ump.get_page(domain+"/icerik/tamliste",encoding))
	for name in names:
		ump.add_log("turkanimetv is searching %s" % name)
		for anime in animes:
			if ump.is_same(anime[1],name):
				url=anime[0]
				break
		if not url is None:
			break

	if url is None:	
		ump.add_log("turkanimetv can't find any links for %s"%name)
		return None
	
	url=re.findall('"(icerik/bolumler.*?)"',ump.get_page(domain+url,encoding))[0]

	if not is_movie:
		bolumler=re.findall('<a href="(.*?)" class="btn".*?title=".*?([0-9]*?)\..*?">',ump.get_page(domain+url,encoding))
		url=None
		for bolum in bolumler:
			try:
				bid=int(bolum[1])
			except:
				continue
			if bid == i["absolute_number"]:
				ump.add_log("turkanimetv matched episode %dx%d:%s" % (i["season"],i["episode"],bid))
				url=bolum[0]
				break
	else:
		url=re.findall('<a href="(.*?)" class="btn"',ump.get_page(domain+url,encoding))
		if len(url)==1:
			url=url[0]
			ump.add_log("turkanimetv matched %s" % unidecode(anime[1]))
		else:
			url=None

	if url is None:	
		ump.add_log("turkanimetv can't find any links for %s"%name)
		return None

	fansubs=re.findall("'#video','(.*?)fansub=(.*?)&giris=OK','#video'",ump.get_page(domain+url,encoding))
	for fansub in fansubs:
		f=fansub[1]
		u=fansub[0]+"fansub="+fansub[1]+"&giris=OK"
		scrape_moviepage(u,f,i["title"])
	if len(fansubs)==0:
		scrape_moviepage(url,"Varsayilan",i["title"])
