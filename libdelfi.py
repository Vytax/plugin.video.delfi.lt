#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import urllib
import sys
from datetime import datetime, timedelta
import simplejson as json

DELFI_TV = 'http://www.delfi.lt/'
DELFI_TV_URL = DELFI_TV + 'video/'
DELFI_TV_ARCHIVE = DELFI_TV_URL + 'archive/?fromd=%s&tod=%s&page=%d'
DELFI_TV_ARTICLE = DELFI_TV_URL + 'article.php?id=%d'
DELFI_VIDEO_DATA = 'http://g.dcdn.lt/vfe/data.php?video_id=%s'
DELFI_TV_LIVE_UPCOMING = DELFI_TV_URL + 'transliacijos/anonsai/?page=%d'
DELFI_TV_LIVE_ARCHIVE = DELFI_TV_URL + 'transliacijos/archyvas/?page=%d'
DELFI_TV_LIVE_24 = DELFI_TV_URL + 'transliacijos/24-val-transliacijos/'
DELFI_TV_CHANNEL = DELFI_TV_URL + '%s/?page=%d'
DELFI_TV_SEARCH = DELFI_TV_URL + 'archive/?fromd=00.00.0000&tod=%s&query=%s&page=%d'

reload(sys) 
sys.setdefaultencoding('utf8')

class Delfi(object):
  def __init__(self):
    pass
  
  def getURL(self, url):
  
    res = urllib.urlopen(url)
    return res.read()

  def str_duration_to_int(self, duration):
    
    parts = duration.split(':')
    if not parts:
      return 0
    
    return int(parts[0])*60+int(parts[1])

  def getLatestVideos(self, page):    
       
    now = datetime.now()
    last = now - timedelta(days=180)
    
    url = DELFI_TV_ARCHIVE % (last.strftime('%d.%m.%Y'), now.strftime('%d.%m.%Y'), page)
    
    return self.getInfo(url)
  
  def getLiveUpcoming(self, page):
    
    return self.getInfo(DELFI_TV_LIVE_UPCOMING % (page - 1))
  
  def getLiveArchive(self, page):
    
    return self.getInfo(DELFI_TV_LIVE_ARCHIVE % (page - 1))
  
  def getLive24(self):
    
    return self.getInfo(DELFI_TV_LIVE_24)
  
  def getChannel(self, page, channel):
    
    return self.getInfo(DELFI_TV_CHANNEL % (channel, page))
  
  def search(self, page, key):
    
    key = urllib.quote_plus(key.strip())    
    tod = datetime.now().strftime('%d.%m.%Y')
    return self.getInfo(DELFI_TV_SEARCH % (tod, key, page))
  
  def getInfo(self, url):
  
    result = {}
  
    html = self.getURL(url)
    
    videoItems = re.findall('<div class="headline">(.*?)<div class="cb">', html, re.DOTALL)
    
    if not videoItems:
      return result    
 
    videos = []
    
    for item in videoItems:
      
      video = {}
      
      thumb = re.findall('<img class="img-responsive"[^<>]*data-src2x="([^"]*)"', item, re.DOTALL)
      if thumb:	    
	video['thumbnailURL'] = thumb[0]
      else:
	video['thumbnailURL'] = ''
      
      mId = re.findall('\?id=(\d*)', item, re.DOTALL)      
      if mId:
	video['id'] = mId[0]
      else:
	continue
      
      title = re.findall('<h3 class="headline-title">\s*<a[^>]*>(.*?)<\/a>', item, re.DOTALL) 
      if title:
	video['title'] = title[0].replace('\t','').strip()
      else:
	continue      
      
      plot = re.findall('<div class="headline-lead hidden-xs">\s*<a[^>]*>(.*?)<\/a><\/div>', item, re.DOTALL)
      if plot:
	plot =  re.sub(r'<[^>]*?>', '', plot[0])
	video['plot'] = plot.replace('\t','').strip()
      else:
	video['plot'] = ''
	
      pubtime = re.findall('<div class="headline-pubtime">([^<]*)</div>', item, re.DOTALL)
      
      if pubtime:
	t = self.parseDate(pubtime[0])	  
	if t:
	  video['aired'] = t
      
      videos.append(video)
    
    result['data'] = videos
    
    pages = self.getPageCount(html)
    if pages:
      result.update(pages)
    
    return result
  
  def parseDate(self, dstr):
    dstr = dstr.strip()
    
    pubtime = re.findall('^(?:prieš |)(\d+) (val|d|min).$', dstr)
    if pubtime:
      pubtime = pubtime[0]
      t = datetime.now()
      if pubtime[1] == 'd':
	t = t - timedelta(days=int(pubtime[0]))
      elif pubtime[1] == 'val':
	t = t - timedelta(hours=int(pubtime[0]))
      elif pubtime[1] == 'min':
	t = t - timedelta(minutes=int(pubtime[0]))
      else:
	t = None
	  
      if t:
	return t.strftime('%Y.%m.%d')
	
    pubtime = re.findall('^(\d+)\s*([a-zA-Zžėščū]+)\s*mėn\.\s*(\d+)\s*d\.\s*\d+:\d+$', dstr, re.UNICODE)

    if pubtime:
      pubtime = pubtime[0]

      months = {
	'sausio' : 1,
	'vasario' : 2,
	'kovo' : 3,
	'balandžio': 4,
	'gegužės' : 5,
	'birželio': 6,
	'liepos' : 7,
	'rugpjūčio' : 8,
	'rugsėjo' : 9,
	'spalio' : 10,
	'lapkričio' : 11,
	'gruodžio' : 12     
      }

      if pubtime[1] in months:
	return pubtime[0] + '.' + str(months[pubtime[1]]).zfill(2) + '.' + pubtime[2].zfill(2)
    
    return None
  
  def arrayToHash(self, arr):
    
    result = {}
    
    for item in arr:
      result[item[0]] = item[1]
      
    return result
  
  def getVideoData(self, vid):
    
    jsonData = self.getURL(DELFI_VIDEO_DATA % vid)
    response = json.loads(jsonData)['data']
    
    result = {}
    
    if 'abr_playlist' in response:
      url = response['abr_playlist']
      if url.startswith('//'):
	url = 'http:' + url
      result['videoURL'] = url
      
    elif 'versions' in response:
	versions = response['versions']
	
	version = None
	if 'HD' in versions:
	  version = versions['HD']
	elif 'SD' in versions:
	  version = versions['HD']
	  
	if version:
	  for video in version:
	    if video['type'] == 'application/x-mpegurl':
	      result['videoURL'] = video['src']
    
    return result

  def getArticle(self, mid):
    
    result = {}
    
    html = self.getURL(DELFI_TV_ARTICLE % mid)
    
    data_id = re.findall('data-provider="dvideo" data-id="([^"]*)">', html, re.DOTALL)
    
    metaItems = re.findall('<meta\s+(?:itemprop|property)\s*=\s*"([^"]*)"\s*content\s*=\s*"([^"]*)"\s*\/>', html, re.DOTALL)
    meta = self.arrayToHash(metaItems)
    
    if data_id:
      data_id = data_id[0]    
      result['data_id'] = data_id
      
      videoData = self.getVideoData(data_id)
      
      if 'videoURL' in videoData:
	result['videoURL'] = videoData['videoURL']
      elif 'contentUrl' in meta:
	result['videoURL'] = meta['contentUrl']
      else:    
	result['videoURL'] = 'http://g.dcdn.lt/vs/videos/%s/%s/v480.mp4' % (data_id [0],  data_id)
    
    else:
      data_hls = re.findall('data-hls="([^"]+)"', html, re.DOTALL)
      if data_hls:
	result['videoURL'] = data_hls[0]
	
      else:
	youtube = re.findall('<div id="youtube-([^"]+)"', html, re.DOTALL)
	if youtube:
	  result['videoURL'] = 'plugin://plugin.video.youtube/play/?video_id=' + youtube[0]
	  
	else:
	  err = re.findall('div class="time-overlay">(.*?)<\/div>', html, re.DOTALL)	
	  if err:
	    err = re.sub(r'<[^>]*?>', '', err[0])
	    result['error'] = err.replace('\t','').strip()
	    
	  print 'klaida: ' + str(mid)
	  return result
    
    if 'description' in meta:
      result['plot'] = meta['description'].replace('\t',' ').strip()
    else:
      result['plot'] = ''
      
    if 'datePublished' in meta:
      result['aired'] = meta['datePublished'].split('T')[0].replace('-','.')
    else:
      result['aired'] = ''
      
    if 'name' in meta:
      result['title'] = meta['name'].replace('\t','').strip()
    else:
      result['title'] = ''
      
    if 'thumbnailUrl' in meta:
      result['thumbnailUrl'] = meta['thumbnailUrl']

    return result
   
  def getPageCount(self, html):
    
    paging = re.findall('<div class="paging">(.*?)</div>', html, re.DOTALL)
    
    if not paging:
      return False
           
    pages = re.findall('<a class="item item-num( item-active|)[^>]*>(\d*)<\/a>', paging[0], re.DOTALL)
    
    currentPage = 1
    for page in pages:
      if page[0]:
	currentPage = int(page[1])
	break
      
    pageCount = int(pages[-1][1])  
    return { 'currentPage' : currentPage, 'pageCount' : pageCount }
    
  def getPosters(self):
    
    html = self.getURL(DELFI_TV_URL)
    
    cover = re.findall('<div id="cover".*?data-image="([^"]+)"', html, re.DOTALL)
    posters = re.findall('<div class="level-2-item "><a href="http:\/\/www\.delfi\.lt\/video\/([^"]+)".*?url\(([^\)]+)\)', html, re.DOTALL)
    
    result = {}
    if posters:
      result = self.arrayToHash(posters)
    if cover:
      result['cover'] = cover[0]

    return result

if __name__ == '__main__':
  
  delfi = Delfi()  
