import json
import re
import urlparse
			
domain="http://dizipub.com"
encoding="utf-8"


def crawl_movie_page(u, mpage=None):
	if mpage is None:
		mpage=ump.get_page(u,encoding)
	iframe = re.findall("<iframe.+?src=\"(.+?)\"", mpage, re.DOTALL)
	if len(iframe) != 4:
		ump.add_log("unable to parse %s" % u)
		return None
	return {"url": iframe[2]}

def return_links(name,part):
	parts=[part]
	mname="[HS:TR]%s" % (name,)
	ump.add_mirror(parts,mname)

def run(ump):
	globals()['ump'] = ump
	i=ump.info
	if not("tvshowtitle" in i.keys() and not i["tvshowtitle"]==""):
		return None
	names=[i["tvshowtitle"]]
	results=[]
	found=False
	if "tvshowalias" in i.keys():
		names.extend(i["tvshowalias"].split("|"))
	for name in names:
		ump.add_log("dizipub is searching %s" % name)
		q={"action":"ajax_search","fn":"get_ajax_search","terms":name}
		results=json.loads(ump.get_page(domain+"/wp-admin/admin-ajax.php",encoding,query=q))
		if len(results)==0 or len(results)==1 and "Arama kriterlerinize" in results[0]: 
			ump.add_log("dizipub can't find any links for %s"%name)
			continue
		for result in results:
			if ump.is_same(result["value"],name):
				found=True
				break
		if found:
			break
	
	if not found: return
	src=ump.get_page(result["url"],encoding)
	epis=re.findall('</div><h3> <a href="(.*?)">.*?([0-9]*?)\.S.*?([0-9]*?)\.B.*?</a></h3>',src)
	if len(epis)==0 and i["season"]==1:
		epis=re.findall('<h3> ?<a href="(.*?)">.*?([0-9]*?)\..*?</a></h3>',src)
		epis=[(x[0],1,x[1]) for x in epis]
	for epi in epis:
		u,s,e = epi
		s=int(s)
		e=int(e)
		if s==i["season"] and e==i["episode"]:
			ename="%s %dx%d %s" % (result["value"],s,e,i["title"])
			ump.add_log("dizipub matched %s " % (ename,))
			mpage=ump.get_page(u,encoding)
			part=crawl_movie_page(u, mpage)
			if not part is None:
				return_links(ename,part)
			alts=re.findall('><a href="(.*?)"><span class="listed-item">',mpage)
			for alt in alts:
				part=crawl_movie_page(alt)
				if not part is None:
					return_links(ename,part)
