# Copyright 2004 Daniel Henninger <jadestorm@nc.rr.com>
# Licensed for distribution under the GPL version 2, check COPYING for details

from twisted.web import microdom
from twisted.protocols import oscar
import groupchat
import icqt
import config
import debug

# The name of the transport
name = "ICQ Transport"

# The transport's version
version = "0.2"

# This should be set to the identity of the gateway
id = "icq"

# This should be set to the identity of the conference gateway, blank if none
confid = ""

# Set to True if spool directory entries need to be mangled @ -> %
mangle = True

# This should be set to the name space roster entries are in in the spool
namespace = "jabber:iq:register"

# This function should return an xml element as it should exist in the spool
def formRegEntry(username, password, nickname):
	reginfo = microdom.Element("query")
	reginfo.namespace = "jabber:iq:register"

	userEl = microdom.Element("username")
	userEl.appendChild(microdom.Text(username))
	reginfo.appendChild(userEl)

	passEl = microdom.Element("password")
	passEl.appendChild(microdom.Text(password))
	reginfo.appendChild(passEl)

	nickEl = microdom.Element("nick")
	nickEl.appendChild(microdom.Text(nickname))
	reginfo.appendChild(nickEl)

	return reginfo

# This function should, given a spool xml entry, pull the username, password,
# and nickname out of it and return them
def getAttributes(base):
	username = ""
	password = ""
	nickname = ""
	for child in base.childNodes:
		try:
			if(child.tagName == "username"):
				username = child.firstChild().value
			elif(child.tagName == "password"):
				password = child.firstChild().value
			elif(child.tagName == "nick"):
				nickname = child.firstChild().value
		except AttributeError:
			continue

	return username, password, nickname

# This function should return true if the JID is a group JID, false otherwise
def isGroupJID(jid):
	if (0):
		return True
	else:
		return False

# This function translates an ICQ screen name to a JID
def icq2jid(icqid):
	retstr = icqid.replace(' ', '')
	return retstr.replace('@', '%') + "@" + config.jid

# This function translates a JID to an ICQ screen name
def jid2icq(jid):
	return unicode(jid[:jid.find('@')].replace('%', '@'))

# This function is called to handle legacy id translation to a JID
translateAccount = icq2jid

# This class handles groupchats with the legacy protocol
class LegacyGroupchat(groupchat.BaseGroupchat):
	def __init__(self, session, resource, ID=None, existing=False, switchboardSession=None):
		pass
	
	def removeMe(self):
		pass

	def sendLegacyMessage(self, message):
		pass
	
	def sendContactInvite(self, contactJID):
		pass

# This class handles most interaction with the legacy protocol
class LegacyConnection(icqt.ICQConnection):
	""" A glue class that connects to the legacy network """
	def __init__(self, username, password, session):
		self.session = session
		icqt.ICQConnection.__init__(self, username, password)
		self.session.ready = True
		debug.log("LegacyConnection: __init__")
	
	def removeMe(self):
		debug.log("LegacyConnection: removeMe")
		icqt.ICQConnection.removeMe(self)
	
	def sendMessage(self, dest, body):
		debug.log("LegacyConnection: sendMessage %s %s" % (dest, body))
		icqt.ICQConnection.sendMessage(self, dest, body)

	def newResourceOnline(self, resource):
		debug.log("LegacyConnection: newResourceOnline %s" % (resource))
		icqt.ICQConnection.resendBuddies(self, resource)
	
 	def setStatus(self, show, friendly):
		debug.log("LegacyConnection: setStatus %s %s" % (show, friendly))
		if (show in ["online", None]):
			icqt.ICQConnection.setAway(self)
		else:
			icqt.ICQConnection.setAway(self, friendly)

        def buildFriendly(self, status):
		friendly = self.jabberID[:self.jabberID.find('@')]
		if(status and len(status) > 0):
			friendly += " - "
			friendly += status
		if(len(friendly) > 127):
			friendly = friendly[:124] + "..."
		debug.log("Session: buildFriendly(%s) returning \"%s\"" % (self.jabberID, friendly))
		return friendly
	
	def jabberSubscriptionReceived(self, source, subtype):
		debug.log("LegacyConnection: jabberSubscriptionReceived %s %s" % (source, subtype))
		icqt.ICQConnection.jabberSubscriptionReceived(self, source, subtype)
