# for localized messages  	 
from . import _
#
#  RmLocale - Plugin E2
#
#  by ims (c) 2013-2017
#
VERSION = 1.05
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

from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.config import ConfigSubsection, ConfigSelection, ConfigYesNo, ConfigDirectory, getConfigListEntry, NoSave, config
from Components.ConfigList import ConfigListScreen, ConfigList
from Components.Language import language
from Tools.Directories import resolveFilename, fileExists, pathExists, SCOPE_LANGUAGE, SCOPE_PLUGINS
import os

TEMP = "/tmp/"
STARTDIR = "/media/hdd/"
if not pathExists(STARTDIR):
	STARTDIR = TEMP

config.plugins.RmLocale = ConfigSubsection()
choicelist = []
from Components.Language import language
languages = language.getLanguageList()
default_language = language.getActiveLanguage()
for lng in languages:
	choicelist.append((lng[0],lng[1][0]))
config.plugins.RmLocale.usedlang = NoSave(ConfigSelection(default = default_language, choices = choicelist))
config.plugins.RmLocale.target = NoSave(ConfigDirectory(STARTDIR))
config.plugins.RmLocale.enigma = NoSave(ConfigSelection(default = "no", choices = [("no", _("nothing")), (("delete", _("delete"))), (("move", _("move")))]))
config.plugins.RmLocale.plugins = NoSave(ConfigYesNo(default = False))
config.plugins.RmLocale.python = NoSave(ConfigYesNo(default = False))
config.plugins.RmLocale.skin = NoSave(ConfigYesNo(default = False))
cfg = config.plugins.RmLocale


if not pathExists(cfg.target.value):
	cfg.target.value = TEMP

ENIGMA = resolveFilename(SCOPE_LANGUAGE).rstrip("/po/")
PLUGINS = resolveFilename(SCOPE_PLUGINS)

class RemoveLocale(Screen, ConfigListScreen):
	y_size = 200
	skin = """
		<screen name="RmLocale" position="center,center" size="560,%d" backgroundColor="#31000000" title="RmLocale">
			<ePixmap name="red"    position="0,0"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
			<ePixmap name="green"  position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
			<ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />
			<ePixmap name="blue"   position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />
			<widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
			<widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
			<widget name="key_blue" position="420,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
			<widget name="config" position="10,40" size="540,125" zPosition="1" transparent="0" scrollbarMode="showOnDemand" />
			<ePixmap pixmap="skin_default/div-h.png" position="0,%d" zPosition="1" size="560,2" />
			<ePixmap alphatest="on" pixmap="skin_default/icons/clock.png" position="480,%d" size="14,14" zPosition="3"/>
			<widget font="Regular;18" halign="right" position="495,%d" render="Label" size="55,20" source="global.CurrentTime" transparent="1" valign="center" zPosition="3">
				<convert type="ClockToText">Default</convert>
			</widget>
			<widget name="statusbar" position="10,%d" size="480,20" font="Regular;18" zPosition="2" transparent="0" foregroundColor="white" />
		</screen>""" % (y_size, y_size-25, y_size-19, y_size-22, y_size-20)

	def __init__(self, session):
		self.skin = RemoveLocale.skin
		self.session = session
		Screen.__init__(self, session)

		self["actions"] = ActionMap(['ColorActions', 'SetupActions'],
		{
			"cancel": self.close,
			"red": self.close,
			"green": self.runRemove,
			"blue": self.selectTarget
		})

		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("Run"))
		self["key_blue"] = Label()

		self["statusbar"] = Label()

		self.inhibitDirs = ["/autofs", "/bin", "/boot", "/dev", "/etc", "/lib", "/proc", "/sbin", "/sys", "/tmp", "/usr", "/media/net"]

		self.removeLocaleCfglist = []
		self.removeLocaleCfglist.append(getConfigListEntry(_("Primary language"), cfg.usedlang))
		self.removeLocaleCfglist.append(getConfigListEntry(_("Remove unused plugin's language files"), cfg.plugins))
		self.removeLocaleCfglist.append(getConfigListEntry(_("What make with Enigma2 language files"), cfg.enigma))
		self.removeLocaleCfglist.append(getConfigListEntry(_("Remove python2.7's .py"), cfg.python))
		self.removeLocaleCfglist.append(getConfigListEntry(_("Remove FullNightHD"), cfg.skin))

		self.onChangedEntry = []
		ConfigListScreen.__init__(self, self.removeLocaleCfglist, session, on_change = self.changedEntry)

	def changedEntry(self):
		if cfg.enigma.value == "move":
			self["key_blue"].setText(_("Path"))
			self["statusbar"].setText(_("Move to %s") % cfg.target.value)
		else:
			self["key_blue"].setText("")
			self["statusbar"].setText("")	

	def runRemove(self):
		self["statusbar"].setText(_("Working..."))
		language = cfg.usedlang.value # primary language
		if cfg.plugins.value:
			dirs = self.lookDirs(PLUGINS, "locale", language)
			self.removeFiles(dirs, "locale", language)
		if cfg.enigma.value in ("delete", "move"):
			dirs = self.lookDirs(ENIGMA, "po", language)
			if cfg.enigma.value == "delete":
				self["statusbar"].setText(_("Deleting..."))
				self.removeFiles(dirs, "po", language)
			elif cfg.enigma.value == "move":
				self["statusbar"].setText(_("Moving..."))
				self.moveEnigmaFiles(dirs,language)
		if cfg.python.value:
			self.removePythonsPy()
		if cfg.skin.value:
			self.removeSkin()
		self["statusbar"].setText(_("Done"))

	def lookDirs(self, path, directory, language):
		locales = []
		lang = "%s/%s" % (directory, self.getName(language, directory))
		lastdir = directory + "/"
		for path, dirs, files in os.walk(path):
			if path.find(lastdir) != -1 and path.find("LC_MESSAGES") == -1 and path.find(lang) == -1:
				locales.append(path)
		return locales

	def getName(self, language, directory):
		if language.find("pt_BR") != -1 and directory == "po": # Brasilian for enigma2
			return language
		return language.split("_")[0]

	def removeFiles(self, dirs, typ, language):
		for path in dirs:
			if typ == "po":
				try:
					path += "/LC_MESSAGES/enigma2.mo"
					self.osSystem("rm -R %s" % (path))
					target = "".join((ENIGMA,"/po/",self.getName(language,typ),"/LC_MESSAGES/enigma2.mo"))
					self.osSystem("ln -s %s %s" % (target, path))
				except:
					print("[RemoveLocale] error", path)
			else:
				try:
					self.osSystem("rm -R %s" % (path))
				except:
					print("[RemoveLocale] error", path)
		self["statusbar"].setText(_("Removed"))

	def removePythonsPy(self):
		self.osSystem("find /usr/lib/python2.7/ -name '*.py' | xargs rm -f")
		self.osSystem("find /usr/lib/python2.7/ -name '*.egg-info' | xargs rm -r")
		
	def removeSkin(self):
		self.osSystem("rm /usr/share/enigma2/PLi-FullNightHD -r")

	def moveEnigmaFiles(self, dirs, language):
		newPath = cfg.target.value + "po"
		if not os.path.exists(newPath):
			os.makedirs(newPath)
		for path in dirs:
			try:
				subDir = "".join((newPath,"/",path.split("/")[-1],"/LC_MESSAGES"))
				# CREATE FOLDERS
				if not os.path.exists(subDir):
					os.makedirs(subDir)
				# MOVE
				path += "/LC_MESSAGES/enigma2.mo"
				self.osSystem("mv %s %s" % (path, subDir))
				# CREATE LINKS
				subDir += "/enigma2.mo"
				self.osSystem("ln -s %s %s" % (subDir, path))
			except:
				print("[RemoveLocale] error", path)
		self["statusbar"].setText(_("Moved"))

	def osSystem(self, cmd):
#		print(">>>", cmd)
		os.system(cmd)

	def selectTarget(self):
		if cfg.enigma.value is not "move":
			return
		from Screens.LocationBox import LocationBox
		txt = _("Language files will be moved to")
		self.session.openWithCallback(self.targetDirSelected, LocationBox, text=txt, currDir=cfg.target.value,
						autoAdd=False, editDir=True,
						inhibitDirs=self.inhibitDirs, minFree=10 )

	def targetDirSelected(self, res):
		if res is not None:
			cfg.target.value = res
			self["statusbar"].setText("%s" % res)

