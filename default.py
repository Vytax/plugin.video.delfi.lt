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
  
  listitem = xbmcgui.ListItem("Sporto TV")
  listitem.setProperty('IsPlayable', 'false')
  listitem.setThumbnailImage('http://g4.dcdn.lt/vd/i/sporto-tv/logo.png')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=3', listitem = listitem, isFolder = True, totalItems = 0)
  
  xbmcplugin.setContent(int( sys.argv[1] ), 'tvshows')
  xbmc.executebuiltin('Container.SetViewMode(515)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def build_media_list(mode, page):

  tvList = {}
  
  if mode == 1:
    tvList = delfi.getLatestVideos(page)
  elif mode == 4:
    tvList = delfi.getSportsTVReports(page)
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
    u['thumbnailURL'] = tv['thumbnailURL']
      
    xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?' + urllib.urlencode(u), listitem = listitem, isFolder = False, totalItems = 0)
  
  if 'currentPage' in tvList and 'pageCount' in tvList:
    
    currentPage = tvList['currentPage']
    pageCount = tvList['pageCount']
    
    print currentPage
    print pageCount
    
    if currentPage < pageCount:    
      listitem = xbmcgui.ListItem("[Daugiau... ] %d/%d" % (currentPage, pageCount))
      listitem.setProperty('IsPlayable', 'false')
      xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=' + str(mode) + '&page=' + str(page + 1), listitem = listitem, isFolder = True, totalItems = 0)
  
  xbmcplugin.setContent(int( sys.argv[1] ), 'tvshows')
  xbmc.executebuiltin('Container.SetViewMode(503)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def build_sporto_tv():
  
  listitem = xbmcgui.ListItem("Reportažai")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=4&page=1', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem("Rungtynių įrašai")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=5&page=1', listitem = listitem, isFolder = True, totalItems = 0)
  
  xbmcplugin.setContent(int( sys.argv[1] ), 'tvshows')
  xbmc.executebuiltin('Container.SetViewMode(515)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def playVideo(mediaId, thumbnailURL):
  
  data = delfi.getArticle(mediaId)
  
  if 'data_id' not in data:
    dialog = xbmcgui.Dialog()
    if 'error' in data:
      ok = dialog.ok( "DELFI TV" , data['error'] )
    else:
      ok = dialog.ok( "DELFI TV" , 'Nepavyko paleisti vaizdo įrašo!' )
    return
    
  listitem = xbmcgui.ListItem(label = data['title'])
  listitem.setPath(data['videoURL'])
  listitem.setThumbnailImage(thumbnailURL)
  xbmcplugin.setResolvedUrl(handle = int(sys.argv[1]), succeeded = True, listitem = listitem)	
  

# **************** main ****************
tmpdir = os.path.join(settings.getAddonInfo( 'path' ), 'tmp');

if not os.path.exists(tmpdir):
    os.makedirs(tmpdir)

delfi = Delfi(os.path.join(tmpdir,'cache.sql'))

path = sys.argv[0]
params = getParameters(sys.argv[2])
mode = None
url = None
thumbnailURL = None
mediaId = None
page = None

try:
	url = urllib.unquote_plus(params["url"])
except:
	pass
      
try:
	mode = int(params["mode"])
except:
	pass
      
try:
	thumbnailURL = urllib.unquote_plus(params["thumbnailURL"])
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

if mode == None:
  build_main_directory()
elif mode in [1, 4]:
  build_media_list(mode, page)
elif mode == 2:
  playVideo(mediaId, thumbnailURL)
elif mode == 3:
  build_sporto_tv()
  