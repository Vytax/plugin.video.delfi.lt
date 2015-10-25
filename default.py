#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import urllib

import xbmcgui
import xbmcplugin
import xbmcaddon

from libdelfi import Delfi

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

def build_main_directory(): 
  
  listitem = xbmcgui.ListItem("Naujausi įrašai")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=1&page=1', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem("Transliacijos")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=3', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem("Žinios")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=laidos%2F120s', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem("Aktualijos")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=aktualijos', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem("Verslas")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=verslas', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem("Mokslas ir gamta")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=mokslas-ir-gamta', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem("Auto")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=auto', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem("Sportas")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=sportas', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem("Pramogos")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=pramogos', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem("Sveikatos TV")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=sveikata-tv', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem("Stilius")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=stilius', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem("Laidos")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=16&page=1', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem("Paieška")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=10&page=1', listitem = listitem, isFolder = True, totalItems = 0)
  
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
  
  listitem = xbmcgui.ListItem("Anonsai")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=4&page=1', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem("Archyvas")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=5&page=1', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem("24 val. transliacijos")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=6', listitem = listitem, isFolder = True, totalItems = 0)
  
  xbmcplugin.setContent(int( sys.argv[1] ), 'tvshows')
  xbmc.executebuiltin('Container.SetViewMode(515)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def build_tv_shows_list():
  
  listitem = xbmcgui.ListItem("120s")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=laidos%2F120s', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem("Pinigų karta")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=laidos%2Fpinigu-karta', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem("Mokslo ekspresas")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=laidos%2Fmokslo-ekspresas', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem("Mano pergalės kelias")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=laidos%2Fmano-pergales-kelias', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem("Kitas kampas")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=laidos%2Fkitas-kampas', listitem = listitem, isFolder = True, totalItems = 0)

  listitem = xbmcgui.ListItem("Boso valanda su S. Jovaišu")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=laidos%2Fboso-valanda-su-s-jovaisu', listitem = listitem, isFolder = True, totalItems = 0)

  listitem = xbmcgui.ListItem("Grynas TV")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=laidos%2Fgrynas-tv', listitem = listitem, isFolder = True, totalItems = 0)

  listitem = xbmcgui.ListItem("Pumpurėliai")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=laidos%2Fpumpureliai', listitem = listitem, isFolder = True, totalItems = 0)

  listitem = xbmcgui.ListItem("1000receptų TV")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=laidos%2F1000-receptu-tv', listitem = listitem, isFolder = True, totalItems = 0)

  listitem = xbmcgui.ListItem("Mano namai TV")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=laidos%2Fmanonamai-tv', listitem = listitem, isFolder = True, totalItems = 0)

  listitem = xbmcgui.ListItem("Žinios rusų kalba")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=laidos%2Fzinios-rusu-kalba', listitem = listitem, isFolder = True, totalItems = 0)

  listitem = xbmcgui.ListItem("Dokumentika")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=laidos%2Fdokumentika', listitem = listitem, isFolder = True, totalItems = 0)

  listitem = xbmcgui.ListItem("Žinios anglų kalba")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=laidos%2Fzinios-anglu-kalba', listitem = listitem, isFolder = True, totalItems = 0)

  listitem = xbmcgui.ListItem("Balsuok")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=laidos%2Fbalsuok', listitem = listitem, isFolder = True, totalItems = 0)

  listitem = xbmcgui.ListItem("LOGIN")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=laidos%2Flogin', listitem = listitem, isFolder = True, totalItems = 0)

  listitem = xbmcgui.ListItem("Judėk")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=laidos%2Fjudek', listitem = listitem, isFolder = True, totalItems = 0)

  listitem = xbmcgui.ListItem("Radistai")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=laidos%2Fradistai', listitem = listitem, isFolder = True, totalItems = 0)

  listitem = xbmcgui.ListItem("Anekdotai")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=laidos%2Fanekdotai', listitem = listitem, isFolder = True, totalItems = 0)

  listitem = xbmcgui.ListItem("Karybos menas")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=laidos%2Fkarybos-menas', listitem = listitem, isFolder = True, totalItems = 0)

  listitem = xbmcgui.ListItem("Trumpo metro filmai")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=laidos%2Ftrumpo-metro-filmai', listitem = listitem, isFolder = True, totalItems = 0)

  listitem = xbmcgui.ListItem("Animacija")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=100&page=1&channel=laidos%2Fanimacija', listitem = listitem, isFolder = True, totalItems = 0)
  
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
  