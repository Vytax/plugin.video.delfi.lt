#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import urllib
import sys
import sqlite3
from datetime import datetime, timedelta

DELFI_TV = 'http://www.delfi.lt/'
DELFI_TV_URL = DELFI_TV + 'video/'
DELFI_TV_ARCHIVE = DELFI_TV_URL + 'archive/?fromd=%s&tod=%s&page=%d'
DELFI_TV_ARTICLE = 'http://m.delfi.lt/video/article.php?id=%d'

DELFI_ALT_TITLES = {
  '1000-receptu' : '1000 receptų TV',
  'Cosmopolitan' : 'Cosmopolitan TV',
  'Manonamai'    : 'Mano Namai TV',
  'Perpasauli TV': 'Per pasaulį TV',
  'SportoTV'     : 'Sporto TV'
  }

reload(sys) 
sys.setdefaultencoding('utf8')

class Delfi(object):
  def __init__(self, sqlfilename):
    self._db = sqlite3.connect(sqlfilename)
  
    cursor = self._db.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS videos (mid INTEGER PRIMARY KEY, videoURL TEXT, plot TEXT, aired TEXT, title TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS badVideos (mid INTEGER PRIMARY KEY, accessTime TEXT)')
  
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
  
  def getSportsTVReports(self, page):
    
    now = datetime.now()
    last = now - timedelta(days=500)
    
    url = DELFI_TV_ARCHIVE % (last.strftime('%d.%m.%Y'), now.strftime('%d.%m.%Y'), page)
    
    return self.getInfo(url + '&category=65179417')
  
  def getInfo(self, url):
  
    result = {}
  
    html = self.getURL(url)
    
    videoItems = re.findall('<div class="headline">(.*?)<div class="cb">', html, re.DOTALL)
    
    if not videoItems:
      return result    
 
    videos = []
    
    for item in videoItems:
      
      video = {}
      
      thumb = re.findall('<img class="img-responsive" src="([^"]*)"', item, re.DOTALL)
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
	
      pubtime = re.findall('<div class="headline-pubtime">(\d+) (val|d).</div>', item, re.DOTALL)
      if pubtime:
	pubtime = pubtime[0]
	t = datetime.now()
	if pubtime[1] == 'd':
	  t = t - timedelta(days=int(pubtime[0]))
	elif pubtime[1] == 'val':
	  t = t - timedelta(hours=int(pubtime[0]))
	else:
	  t = None
	  
	if t:
	  video['aired'] = t.strftime('%Y.%m.%d.')
      
      videos.append(video)
    
    result['data'] = videos
    
    pages = self.getPageCount(html)
    result.update(pages)
    
    return result

  def getArticle(self, mid):
    
    result = {}
    
    html = self.getURL(DELFI_TV_ARTICLE % mid)
    
    data_id = re.findall('data-provider="dvideo" data-id="([^"]*)">', html, re.DOTALL)
    data_title = re.findall('<h1>(.*?)<\/h1>', html, re.DOTALL)
    data_published = re.findall('<div class="articleDateSource[^>]*>([^<]*)<\/div>', html, re.DOTALL)
    data_description = re.findall('<p itemprop="description"[^>]*>(.*?)<\/p>', html, re.DOTALL)
    
    if not data_id:
      print 'klaida: ' + str(mid)
      self.badVideo(mid)
      return result
    data_id = data_id[0]
    
    result['data_id'] = data_id
    result['videoURL'] = 'http://g.dcdn.lt/vs/videos/%s/%s/v480.mp4' % (data_id [0],  data_id)
    
    if data_description:
      description = re.sub(r'<[^>]*?>', '', data_description[0])
      result['plot'] = description.replace('\t','').strip()
    else:
      result['plot'] = ''
      
    if data_published:
      result['aired'] = self.longDateToShort(data_published[0])
    else:
      result['aired'] = ''
      
    if data_title:
      result['title'] = data_title[0].replace('\t','').strip()
    else:
      result['title'] = ''

    return result

  def getArticleCached(self, mid):
    
    cursor = self._db.cursor()
    
    cursor.execute('SELECT videoURL, plot, aired, title FROM videos WHERE mid=?', (mid,))
    row = cursor.fetchone()
    
    if row:      
      result = {}
      result['videoURL'] = row[0]
      result['plot'] = row[1]
      result['aired'] = row[2]
      result['title'] = row[3]
      return result
    
    else:
      if self.isBadVideo(mid):
	return {}
      
      data = self.getArticle(mid)
      print data
      if data: 
	cursor.execute('INSERT INTO videos (mid, videoURL, plot, aired, title) VALUES (?,?,?,?,?)', (mid, data['videoURL'].decode('utf-8'), data['plot'].decode('utf-8'), data['aired'].decode('utf-8'), data['title'].decode('utf-8')))
      
	self._db.commit()
      
      return data

  def longDateToShort(self, longDate):
    
    parts = re.findall('(\d+)\s*m.\s*([a-zA-Zžėščū]+)\s*(\d+)\s*d\.', longDate, re.UNICODE)
    
    if not parts:
      return ''
    
    parts = parts[0]
    
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
    
    if not parts[1] in months:
      return ''
    
    return parts[0] + '-' + str(months[parts[1]]).zfill(2) + '-' + parts[2].zfill(2)
  
  def badVideo(self, mid):
    cursor = self._db.cursor()
    cursor.execute("REPLACE INTO badVideos (mid, accessTime) VALUES (?, DateTime('now'))", (mid,))
    self._db.commit()
    
  def isBadVideo(self, mid):
    cursor = self._db.cursor()
    cursor.execute("DELETE FROM badVideos WHERE accessTime < DateTime('now', '-2 hours')")
    self._db.commit()
    
    cursor.execute('SELECT * FROM badVideos WHERE mid=?', (mid,))
    row = cursor.fetchone()
    
    if row:
      return True
    else:
      return False
    
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
    
   

if __name__ == '__main__':
  
  delfi = Delfi('test.sql')
  
  delfi.getLatestVideos(1)
