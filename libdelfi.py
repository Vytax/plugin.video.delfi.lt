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

  def getChannels(self):
  
    html = self.getURL(DELFI_TV_URL)
    urls = re.findall('<li class="(?:nav-0-(active|live) |)nav"><a href="http:\/\/www\.delfi\.lt\/video\/([A-Za-z0-9-]+)[/]*">(.*?)</a></li>', html, re.DOTALL)
  
    channelsList = []
  
    for url in urls:
    
      channel = {}
    
      mType = url[0]
      if mType != 'live':
	mType = 'standart'
    
      channel['type'] = mType
    
      channel['url'] = 'http://www.delfi.lt/video/' + url[1]
    
      title = url[2]
    
      img = re.findall('<img src="[^"]*" alt="([^"]*)" />', title, re.DOTALL)
      if img:
	alt = img[0]
	if alt in DELFI_ALT_TITLES:
	  title = DELFI_ALT_TITLES[alt]
	else:
	  title = alt
    
      channel['title'] = title
    
      channelsList.append(channel)
    
    return channelsList

  def str_duration_to_int(self, duration):
    
    parts = duration.split(':')
    if not parts:
      return 0
    
    return int(parts[0])*60+int(parts[1])

  def getLatestVideos(self, page):
    
    videos = []
    
    now = datetime.now()
    last = now - timedelta(days=180)
    
    url = DELFI_TV_ARCHIVE % (last.strftime('%d.%m.%Y'), now.strftime('%d.%m.%Y'), page)
    
    html = self.getURL(url)
    
    body = re.findall('<div class="dblock-wrapper">(.*?)<div class="archive-paging">', html, re.DOTALL)
    
    if not body:
      return videos
    
    videoItems = re.findall('<div class="block-224.*?<img src="([^"]*)".*?<span class="block-length"><i>\s*(\d+:\d+)\s*</i>.*?<h3 class="video-title">.*?id=(\d+)">([^<]*)</a', body[0], re.DOTALL)
      
    for item in videoItems:
      
      video = {}
      video['thumbnailURL'] = item[0]
      video['duration'] = self.str_duration_to_int(item[1])
      video['id'] = item[2]
      video['title'] = item[3].replace('\t','').strip()
      
      extraData = self.getArticleCached(int(video['id']))
      if not extraData:
	continue
	
      video['plot'] = extraData['plot']
      video['aired'] = extraData['aired']
	
      videos.append(video)
      
    return videos

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
    
    parts = re.findall('(\d+) m. (\w+) (\d+) d\.', longDate)
    
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

if __name__ == '__main__':
  
  delfi = Delfi('test.sql')
  
  print delfi.getArticleCached(69290496)
  delfi.isBadVideo(100)
 # print longDateToShort('2015 m. spalio 9 d. 20:00')
