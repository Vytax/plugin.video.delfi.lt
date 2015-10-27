#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import urllib

import xbmcgui
import xbmcplugin
import xbmcaddon

from libdelfi import Delfi
import time

settings = xbmcaddon.Addon(id='plugin.video.delfi.lt')

def getParameters(parameterString):
  commands = {}
  splitCommands = parameterString[parameterString.find('?') + 1:].split('&')
  for command in splitCommands:
    if (len(command) > 0):
      splitCommand = command.split('=')
      key = splitCommand[0]
      value = splitCommand[1]
      commands[key] = value
  return commands

def addListItem(title, url, thumb=None):
  
  cover = settings.getSetting('cover')
  
  listitem = xbmcgui.ListItem(title)
  listitem.setProperty('IsPlayable', 'false')
  if cover:
    listitem.setProperty('fanart_image', cover)
  if thumb:
    img = settings.getSetting(thumb)
    if img:
      listitem.setThumbnailImage(img)
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + url, listitem = listitem, isFolder = True, totalItems = 0)

def build_main_directory(): 
  
  addListItem('Naujausi įrašai', '?mode=1&page=1')
  addListItem('Transliacijos', '?mode=3')
  addListItem('Žinios', '?mode=100&page=1&channel=laidos%2F120s', 'laidos/120s')
  addListItem('Aktualijos', '?mode=100&page=1&channel=aktualijos', 'aktualijos')
  addListItem('Verslas', '?mode=100&page=1&channel=verslas', 'verslas')
  addListItem('Mokslas ir gamta', '?mode=100&page=1&channel=mokslas-ir-gamta', 'mokslas-ir-gamta')
  addListItem('Auto', '?mode=100&page=1&channel=auto', 'auto')
  addListItem('Sportas', '?mode=100&page=1&channel=sportas', 'sportas')
  addListItem('Pramogos', '?mode=100&page=1&channel=pramogos', 'pramogos')
  addListItem('Sveikatos TV', '?mode=100&page=1&channel=sveikata-tv', 'sveikata-tv')
  addListItem('Stilius', '?mode=100&page=1&channel=stilius', 'stilius') 
  addListItem('Laidos', '?mode=16&page=1')
  addListItem('Paieška', '?mode=10&page=1')
  
  xbmcplugin.setContent(int( sys.argv[1] ), 'tvshows')
  xbmc.executebuiltin('Container.SetViewMode(515)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def build_media_list(mode, page, channel):

  tvList = {}
  
  if mode == 1:
    tvList = delfi.getLatestVideos(page)
  elif mode == 4:
    tvList = delfi.getLiveUpcoming(page)
  elif mode == 5:
    tvList = delfi.getLiveArchive(page)
  elif mode == 6:
    tvList = delfi.getLive24()
  elif mode == 10:
    if not channel:
      dialog = xbmcgui.Dialog()
      channel = dialog.input('Vaizdo įrašo paieška', type=xbmcgui.INPUT_ALPHANUM)
    if channel:
      tvList = delfi.search(page, channel)
  elif mode == 100:
    tvList = delfi.getChannel(page, channel)
  else:
    return
  
  if 'data' in tvList:
    data = tvList['data']
  else:
    data = []
  
  for tv in data:
    listitem = xbmcgui.ListItem(tv['title'])
    listitem.setProperty('IsPlayable', 'true')
      
    info = { 'title': tv['title'], 'plot': tv['plot']}
    
    if 'aired' in tv:
        info['aired'] = tv['aired']
      
    if 'duration' in tv:	
      if tv['duration']:
	if hasattr(listitem, 'addStreamInfo'):
	  listitem.addStreamInfo('video', { 'duration': tv['duration'] })
	else:
	  info['duration'] = tv['duration']          
  
    listitem.setInfo(type = 'video', infoLabels = info )
      
    listitem.setThumbnailImage(tv['thumbnailURL'])
      
    u = {}
    u['mode'] = 2
    u['mediaId'] = tv['id']
      
    xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?' + urllib.urlencode(u), listitem = listitem, isFolder = False, totalItems = 0)
  
  if 'currentPage' in tvList and 'pageCount' in tvList:
    
    currentPage = tvList['currentPage']
    pageCount = tvList['pageCount']    
   
    if currentPage < pageCount:    
      listitem = xbmcgui.ListItem("[Daugiau... ] %d/%d" % (currentPage, pageCount))
      listitem.setProperty('IsPlayable', 'false')
      
      u = {}
      u['mode'] = mode
      u['page'] = page + 1
      if mode in [10, 100]:
	u['channel'] = channel
      
      xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?' + urllib.urlencode(u), listitem = listitem, isFolder = True, totalItems = 0)
  
  xbmcplugin.setContent(int( sys.argv[1] ), 'tvshows')
  xbmc.executebuiltin('Container.SetViewMode(503)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def build_live():
  
  addListItem('Anonsai', '?mode=4&page=1', 'transliacijos/anonsai')
  addListItem('Archyvas', '?mode=5&page=1')
  addListItem('24 val. transliacijos', '?mode=6', 'transliacijos/24-val-transliacijos')

  xbmcplugin.setContent(int( sys.argv[1] ), 'tvshows')
  xbmc.executebuiltin('Container.SetViewMode(515)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def build_tv_shows_list():
  
  addListItem('120s', '?mode=100&page=1&channel=laidos%2F120s', 'laidos/120s')
  addListItem('Pinigų karta', '?mode=100&page=1&channel=laidos%2Fpinigu-karta', 'laidos/pinigu-karta')
  addListItem('Mokslo ekspresas', '?mode=100&page=1&channel=laidos%2Fmokslo-ekspresas', 'laidos/mokslo-ekspresas')
  addListItem('Mano pergalės kelias', '?mode=100&page=1&channel=laidos%2Fmano-pergales-kelias', 'laidos/mano-pergales-kelias')
  addListItem('Kitas kampas', '?mode=100&page=1&channel=laidos%2Fkitas-kampas', 'laidos/kitas-kampas')
  addListItem('Boso valanda su S. Jovaišu', '?mode=100&page=1&channel=laidos%2Fboso-valanda-su-s-jovaisu', 'laidos/boso-valanda-su-s-jovaisu')
  addListItem('Grynas TV', '?mode=100&page=1&channel=laidos%2Fgrynas-tv', 'laidos/grynas-tv')
  addListItem('Pumpurėliai', '?mode=100&page=1&channel=laidos%2Fpumpureliai', 'laidos/pumpureliai')
  addListItem('1000receptų TV', '?mode=100&page=1&channel=laidos%2F1000-receptu-tv', 'laidos/1000-receptu-tv')
  addListItem('Mano namai TV', '?mode=100&page=1&channel=laidos%2Fmanonamai-tv', 'laidos/manonamai-tv')
  addListItem('Žinios rusų kalba', '?mode=100&page=1&channel=laidos%2Fzinios-rusu-kalba', 'laidos/zinios-rusu-kalba')
  addListItem('Dokumentika', '?mode=100&page=1&channel=laidos%2Fdokumentika', 'laidos/dokumentika')
  addListItem('Žinios anglų kalba', '?mode=100&page=1&channel=laidos%2Fzinios-anglu-kalba', 'laidos/zinios-anglu-kalba')
  addListItem('Balsuok', '?mode=100&page=1&channel=laidos%2Fbalsuok', 'laidos/balsuok')
  addListItem('LOGIN', '?mode=100&page=1&channel=laidos%2Flogin', 'laidos/login')
  addListItem('Judėk', '?mode=100&page=1&channel=laidos%2Fjudek', 'laidos/judek')
  addListItem('Radistai', '?mode=100&page=1&channel=laidos%2Fradistai', 'laidos/radistai')
  addListItem('Anekdotai', '?mode=100&page=1&channel=laidos%2Fanekdotai', 'laidos/anekdotai')
  addListItem('Karybos menas', '?mode=100&page=1&channel=laidos%2Fkarybos-menas', 'laidos/karybos-menas')
  addListItem('Trumpo metro filmai', '?mode=100&page=1&channel=laidos%2Ftrumpo-metro-filmai', 'laidos/trumpo-metro-filmai')
  addListItem('Animacija', '?mode=100&page=1&channel=laidos%2Fanimacija', 'laidos/animacija')

  xbmcplugin.setContent(int( sys.argv[1] ), 'tvshows')
  xbmc.executebuiltin('Container.SetViewMode(515)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def playVideo(mediaId):
  
  data = delfi.getArticle(mediaId)
  
  if 'videoURL' not in data:
    dialog = xbmcgui.Dialog()
    if 'error' in data:
      ok = dialog.ok( "DELFI TV" , data['error'] )
    else:
      ok = dialog.ok( "DELFI TV" , 'Nepavyko paleisti vaizdo įrašo!' )
    return
    
  listitem = xbmcgui.ListItem(label = data['title'])
  listitem.setPath(data['videoURL'])
  if 'thumbnailUrl' in data:
    listitem.setThumbnailImage(data['thumbnailUrl'])
  xbmcplugin.setResolvedUrl(handle = int(sys.argv[1]), succeeded = True, listitem = listitem)	

def setupPosters():
  
  postersUpdate = settings.getSetting('postersUpdate')
  if postersUpdate:
    
    if (int(time.time()) - 60*60*24*7) < int(postersUpdate):
      return
  
  posters = delfi.getPosters()
  if not posters:
    return  
    
  posters['postersUpdate'] = str(int(time.time()))
  
  for key, value in posters.iteritems():
    settings.setSetting(key, value)

# **************** main ****************

delfi = Delfi()

path = sys.argv[0]
params = getParameters(sys.argv[2])
mode = None
url = None
mediaId = None
page = None
channel = None

try:
	url = urllib.unquote_plus(params["url"])
except:
	pass
      
try:
	mode = int(params["mode"])
except:
	pass
      
try:
	mediaId = int(params["mediaId"])
except:
	pass
      
try:
	page = int(params["page"])
except:
	pass

try:
	channel = urllib.unquote_plus(params["channel"])
except:
	pass

setupPosters()

if mode == None:
  build_main_directory()
elif mode in [1, 4, 5, 6, 10, 100]:
  build_media_list(mode, page, channel)
elif mode == 2:
  playVideo(mediaId)
elif mode == 3:
  build_live()
elif mode == 16:
  build_tv_shows_list()
  