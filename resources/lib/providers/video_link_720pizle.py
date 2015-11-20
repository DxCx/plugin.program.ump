import json
import re
			
domain="http://720pizle.com"
encoding="iso-8859-9"
player_code_page="/js/ayarlar.min.js?v=0.8"

def parse_player_urls():
	parsers = globals().get('parsers', None)
	if parsers is None:
		mpage = ump.get_page(domain+player_code_page,encoding)
		url_funcs = re.findall("function\s(\w+?)\(id,div\)\s+\{.+?<iframe\ssrc=\"(.+?)\".+?\}", mpage, re.DOTALL)
		parsers = dict([(i[0], i[1].replace("'+id+'", "%s")) for i in url_funcs])
		globals()["parsers"] = parsers
	return parsers

def extract_url(mpage):
	# Try plusplayer first.
	video_hash=re.findall("class=\"plusplayer\".*>(.*)<",mpage)
	if len(video_hash) > 0:
		return "http://720pizle.com/player/plusplayer.asp?v=%s" % video_hash[0]

	# Try the javascript ones
	scripts=re.findall("<script>(\w+?)\('(.+?)','(.+?)'\);<\/script>", mpage, re.DOTALL)
	if not len(scripts):
		return None

	url_parsers = parse_player_urls()
	video_func, video_hash, video_div = scripts[0]
	if video_func not in url_parsers.keys():
		return None
	return url_parsers[video_func] % video_hash

def crawl_movie_page(mpage,url):
	url = domain+url

	video_url = extract_url(mpage)
	if video_url is None:
		ump.add_log("unable to parse %s" % url)
		return None
	
	if domain in video_url:
		innerplayer = ump.get_page(video_url, encoding)
		iframe = re.findall("<iframe.+?src='(.+?)'", innerplayer, re.DOTALL)
		if len(iframe):
			video_url = iframe[0]

	res=re.findall('class="a oval">(.*?)<',mpage)
	if len(res)>0:
		res=res[0]
	else:
		res="HD"

	return {"url": video_url, "resolution": res}

def return_links(name,type,part):
	if part:
		dub=["","[D:TR]"][type=="dub"]
		sub=["","[HS:TR]"][type=="sub"]
		mname="%s%s%s" % (dub,sub,name)

		ump.add_mirror([part],mname)

def run(ump):
	globals()['ump'] = ump
	i=ump.info
	if "tvshowtitle" in i.keys() and not i["tvshowtitle"]=="":
		return None
	ump.add_log("720pizle is searching %s" % i["title"])
	results=json.loads(ump.get_page(domain+"/api/autocompletesearch.asp",encoding,query={"limit":"10","q":i["title"]}))
	if len(results)==0 or len(results)==1 and "orgfilmadi" in results[0].keys() and "Bulunamad" in results[0]["orgfilmadi"] : 
		ump.add_log("720pizle can't find any links for %s"%i["title"])
		return None
	matches=[]
	max_match=3
	imdbmatch=False

	for result in results:
		if i["code"].startswith("tt") and result["imdbid"]==i["code"]:
			ump.add_log("720pizle matched %s with %s" % (i["title"],i["code"]))
			matches=[result["url"]]
			imdbmatch=True
			break

	for result in results:
		if not imdbmatch and len(matches)<=max_match and ump.is_same(result["orgfilmadi"],i["title"]):
			ump.add_log("720pizle matched %s" % i["title"])
			matches.append(result["url"])

	for match in matches:
		src=ump.get_page(domain+match,encoding)
		movie_pages=re.findall('href="(/izle/.*?)" title=""',src)
		count=len(movie_pages)
		for movie_page in movie_pages:
			movie_page_type=["dub","sub"][movie_page.split("/")[2]=="altyazi"]
			src=ump.get_page(domain+movie_page,encoding)
			part=crawl_movie_page(src,movie_page)
                        return_links(i["title"],movie_page_type,part)
			alts=[]
			urls = re.findall('href="(/izle/.*?)" rel="nofollow"(.*?)</a>',src)
			alts=[x[0] for x in urls if not "tlb_isik" in x[1] ]
			count+=len(alts)
			ump.add_log("720pizle found %d mirrors for Turkish %s %s" % (len(alts),movie_page_type,i["title"]))
			for alt in alts:
				src=ump.get_page(domain+alt,encoding)
				#ump.add_log("720pizle is crawling %s" % alt)
				part=crawl_movie_page(src,alt)
                                return_links(i["title"],movie_page_type,part)
		ump.add_log("720pizle finished crawling %d mirrors"%count)
		return None
	
	if len(matches)<1:ump.add_log("720pizle cant find any match from %d results"%len(results))
	return None
