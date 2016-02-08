from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
import os
from enigma import eTimer
#########

class LoopSyncMain(Screen):
	def __init__(self, session, args = None):
		Screen.__init__(self, session)
		self.session = session
		self.gotSession()

	def gotSession(self):
		self.ttype = "DVB"
		self.AVSyncTimer = eTimer()
		self.AVSyncTimer.callback.append(self.UpdateStatus)
		self.AVSyncTimer.start(10000, True)

	def UpdateStatus(self):
		frontendDataOrg = ""
		service1 = self.session.nav.getCurrentlyPlayingServiceOrGroup()
		if service1:
			service = self.session.nav.getCurrentService()
			if service:
				feinfo = service.frontendInfo()
				frontendDataOrg = feinfo and feinfo.getAll(True)
				if not len(frontendDataOrg): 
					self.ttype = "IPTV"
					self.AVSyncTimer.start(500, True)
					return
				if self.ttype == "IPTV": 
					self.ttype = "DVB"
					self.AVSyncTimer.start(100, True)
					return
		rst_status = 0
		try:
			f = open("/sys/class/tsync/reset_flag", "r")
			rst_status = int(f.read(),16)
			f.close()
		except Exception, e:
			print "[ReZap] Can't read class"
			self.AVSyncTimer.start(500, True)
			return
		if rst_status == 1 :
			print "[ReZap] DoReZap !!!"
			rst_status = 0
			self.AVSyncTimer.start(500, True)
			try:
				f_tmp = open("/sys/class/tsync/reset_flag", "w")
				f_tmp.write("0")
				f_tmp.close()
				self.session.open(DoReZap,service1)
			except Exception, e:
				print "[ReZap] Can't DoReZap"
			return
		self.AVSyncTimer.start(100, True)

###################################                
class DoReZap(Screen):
  
	skin = """
		<screen position="center,center" size="1920,1080" title="" >
		</screen>"""

	def __init__(self, session, xxx):
		Screen.__init__(self, session)

		try:
			f_tmp = open("/sys/class/video/blackout_policy", "w")
			f_tmp.write("0")
			f_tmp.close()
		except Exception, e:
			print "[ReZap] Can't change policy(0)"
		self.session.nav.stopService()
		self.session.nav.playService(xxx)
		try:
			f_tmp = open("/sys/class/video/blackout_policy", "w")
			f_tmp.write("1")
			f_tmp.close()
		except Exception, e:
			print "[ReZap] Can't change policy(1)"
		self.close()	


###################################                

def sessionstart(session, **kwargs):
	session.open(LoopSyncMain)
       
def Plugins(**kwargs):
	return [
		PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=sessionstart)
		]
