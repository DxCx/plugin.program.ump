import re
import json
from urllib2 import HTTPError

encoding="utf-8"
domain = 'http://www.koreanturk.com'


def run(ump):
	globals()['ump'] = ump
	i=ump.info
	is_serie,names=ump.get_vidnames()
	found=False
	if not is_serie:
		return None
	return None # Still have lots of work to do here...
	for name in names:
		ump.add_log("koreanturk is searching %s"%name)
		data={"action":"ajaxy_sf","sf_value":name,"search":"false"}
		page=ump.get_page(domain+"/wp-admin/admin-ajax.php",encoding,data=data,referer=domain,header={"X-Requested-With":"XMLHttpRequest"})
		print page
		js=json.loads(page)
		try:
			series=js["diziler"][0]["all"]
		except TypeError:
			continue
		for serie in series:
			t=serie["post_title"]
			l=domain+"/"+serie["post_link"].split("/")[-1]+"-%d-bolum"%i["episode"]
			if 	i["season"]  in (0,1) and ump.is_same(t,name) or not i["season"]  in (0,1) and ump.is_same(t,"%s %d"%(name,i["season"])):
				try:
				    url = l+"-izle.html"
				    epage=ump.get_page(url,encoding)
				except HTTPError, err:
					if err.code == 404:
						try:
						    url = l+"-final-izle.html"
						    epage=ump.get_page(url,encoding)
						except HTTPError, err:
						    if err.code == 404:
							break
				ump.add_log("koreanturk matched %s %dx%d %s"%(i["tvshowtitle"],i["season"],i["episode"],i["title"]))
				lang=re.findall('<img src="(.*?)" width="20" height="20" alt="Dil Se',epage)
				videos=re.findall('div class="tab-pane" id="(.*?)"><iframe.*?src="(.*?)"',epage)
				
				if "altyazi.png" in lang[0]:
					prefix="[D:KR][HS:TR]"
				elif "orjinal.png" in lang[0]:
					prefix="[D:KR]"
				else:
					prefix=""

				dmparts={}
				for video in videos:
					found=False
					print "Hagai"
					print video
					continue
					up,link=video
					if up == "ok":
						upname="okru"
						mirrors=link.split("/")[-1]
						found=True
					elif up=="vk":
						upname="vkext"
						mirrors=link
						found=True
					elif up=="mr":
						upname="mailru"
						mirrors=link.split("mail/")[-1]
						found=True
					elif up[:4]=="part":
						dmparts[int(up[4:])]=link.split("/")[-1]
					if found:
						parts=[{"url_provider_name":upname, "url_provider_hash":mirrors}]				
						ump.add_mirror(parts,"%s%s %dx%d %s" % (prefix,i["tvshowtitle"],i["season"],i["episode"],i["title"]))
				
				if len(dmparts.keys())>0:
					parts=[]
					for k,v in sorted(dmparts.iteritems()):
						parts.append({"url_provider_name":"dailymotion", "url_provider_hash":v})
					ump.add_mirror(parts,"%s%s %dx%d %s" % (prefix,i["tvshowtitle"],i["season"],i["episode"],i["title"]))
				return None
	ump.add_log("koreanturk couldn't find %s %dx%d %s"%(i["tvshowtitle"],i["season"],i["episode"],i["title"]))
	return None
