# -*- coding: utf-8 -*-
import time
import re
import json
from urllib2 import HTTPError
from xml.dom import minidom

encoding="utf-8"
domain = 'http://dizilab.com'


def run(ump):
	globals()['ump'] = ump
	i=ump.info
	is_serie,names=ump.get_vidnames()
	found=False
	if not i["code"][:2]=="tt" or not is_serie:
		return None
	ump.add_log("dizilab is searching %s"%names[0])
	page=ump.get_page(domain+"/diziler.xml",None)
	res=minidom.parseString(page)
	series=res.getElementsByTagName("dizi")
	for serie in series:
		if i["code"]==serie.getElementsByTagName("imdb")[0].lastChild.data:
			url=serie.getElementsByTagName("url")[0].lastChild.data+"/sezon-"+str(i["season"])+"/bolum-"+str(i["episode"])
			epage=ump.get_page(url,encoding)
			if "<title>Sayfa Bulunamad" in epage:
				continue
			ump.add_log("dizilab matched %s %dx%d %s"%(i["tvshowtitle"],i["season"],i["episode"],i["title"]))
			links=re.findall('file: "(.*?)",\s*label: "(.*?)",\s*type:\s"mp4"',epage,re.DOTALL | re.MULTILINE)
			mname="%s %dx%d %s" % (i["tvshowtitle"],i["season"],i["episode"],i["title"])
			if len(links)>0:
				for link in links:
				    part = {"url": link[0], "resolution": link[1]}
				    ump.add_mirror([part],mname)				
			return None
	ump.add_log("dizilab can't match %s %dx%d %s"%(i["tvshowtitle"],i["season"],i["episode"],i["title"]))
