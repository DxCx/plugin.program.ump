import re
import json
from urllib2 import HTTPError

encoding="utf-8"
domain = 'http://sezonlukdizi.com'


def run(ump):
	globals()['ump'] = ump
	i=ump.info
	is_serie,names=ump.get_vidnames()
	found=False
	if not i["code"][:2]=="tt" or not is_serie:
		return None

	page=ump.get_page(domain+"/hakkimizda.html",encoding)
	series=re.findall('<li><a href="'+domain+'/diziler(/.*?/).*?" title="(.*?) Sezon ([0-9]*?)"',page)
	for name in names:
		ump.add_log("sezonlukdizi is searching %s"%name)	
		for serie in series:
			l,t,s=serie
			if ump.is_same(t,name) and int(i["season"])==int(s):
				url=domain+l+str(i["season"])+"-sezon-"+str(i["episode"])+"-bolum"
				try:
					epage=ump.get_page(url+".html",encoding)
				except HTTPError, err:
					if err.code == 404:
						epage=ump.get_page(url+"-sezon-finali.html",encoding)
				ump.add_log("sezonlukdizi matched %s %dx%d %s"%(i["tvshowtitle"],i["season"],i["episode"],i["title"]))
				video_id = re.findall('video_id  \= "([0-9]*?)"',epage)[0]
				part_name = re.findall('var part_name \= "(.*?)"',epage)[0]
				vurl=domain+"/service/get_video_part"
				vpage=ump.get_page(vurl,encoding,data={"video_id":video_id,"part_name":part_name,"page":0},header={"X-Requested-With":"XMLHttpRequest"})
				js=json.loads(vpage)
				glink=re.findall('<script src="(.*?)"',js["part"]["code"])
				oklink=re.findall('<iframe src="(.*?)"',js["part"]["code"])
                                part_list=[]
				if len(glink)>0:
					script=ump.get_page(glink[0],encoding,referer=domain)
                                        links=re.findall('file:\s"(.*?)",\s*label:\s"(.*?)",\s*type:\s"mp4"',script, re.MULTILINE)
					part_list=[]
					for link in links:
                                            url = ump.get_page(link[0], encoding, referer=domain, head=True)
                                            part_list.append({"url": url.geturl(), "resolution": link[1]})
				elif len(oklink)>0:
					oksrc=ump.get_page(oklink[0],encoding,referer=domain)
					links=re.findall('file:"(.*?)", label:"(.*?)"',oksrc)
					for link in links:
                                            part_list.append({"url": link[0], "resolution": link[1]})
                                for part in part_list:
					ump.add_mirror([part],"%s %dx%d %s" % (i["tvshowtitle"],i["season"],i["episode"],i["title"]))				
				return None
	ump.add_log("sezonlukdizi can't match %s %dx%d %s"%(i["tvshowtitle"],i["season"],i["episode"],i["title"]))
