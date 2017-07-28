# for localized messages  	 
from . import _
#
#  RmLocale - OpenPLi E2 Plugin
#
#  by ims (c) 2013
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
from Plugins.Plugin import PluginDescriptor

def main(session,**kwargs):
	import ui
	session.open(ui.RemoveLocale)

def Plugins(path,**kwargs):
	return [PluginDescriptor(name="RemoveLocale", description=_("removing unwanted e2 and plugin's locale directories"), where = PluginDescriptor.WHERE_PLUGINMENU, icon = "plugin.png", fnc=main)]


