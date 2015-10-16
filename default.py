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
  
  xbmcplugin.setContent(int( sys.argv[1] ), 'tvshows')
  xbmc.executebuiltin('Container.SetViewMode(515)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def build_media_list(page):

  tvList = delfi.getLatestVideos(page)
  
  for tv in tvList:
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
    
  listitem = xbmcgui.ListItem("[Daugiau... ]")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=1&page=' + str(page + 1), listitem = listitem, isFolder = True, totalItems = 0)
  
  xbmcplugin.setContent(int( sys.argv[1] ), 'tvshows')
  xbmc.executebuiltin('Container.SetViewMode(503)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def playVideo(mediaId, thumbnailURL):
  
  data = delfi.getArticleCached(mediaId)
  
  if not data:
    dialog = xbmcgui.Dialog()
    ok = dialog.ok( "DELFI" , 'Nepavyko paleisti vaizdo įrašo!' )
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
elif mode == 1:
  build_media_list(page)
elif mode == 2:
  playVideo(mediaId, thumbnailURL)
  