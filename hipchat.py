from buildbot.status.base import StatusReceiverMultiService
from buildbot.status.builder import Results, SUCCESS
import os, urllib


class HipChatStatusPush(StatusReceiverMultiService):

  def __init__(self, api_token, room_id, localhost_replace=False, **kwargs):
    StatusReceiverMultiService.__init__(self)

    self.api_token = api_token
    self.room_id = room_id
    self.localhost_replace = localhost_replace
    self.watched = []

  def setServiceParent(self, parent):
    StatusReceiverMultiService.setServiceParent(self, parent)
    self.master_status = self.parent
    self.master_status.subscribe(self)
    self.master = self.master_status.master

  def disownServiceParent(self):
    self.master_status.unsubscribe(self)
    self.master_status = None
    for w in self.watched:
      w.unsubscribe(self)
    return StatusReceiverMultiService.disownServiceParent(self)

  def builderAdded(self, name, builder):
    self.watched.append(builder)
    return self  # subscribe to this builder

  def buildFinished(self, builderName, build, result):
    url = self.master_status.getURLForThing(build)
    if self.localhost_replace:
      url = url.replace("//localhost", "//%s" % self.localhost_replace)

    message = urllib.quote("<a href='%s'>%s</a> %s" % (url, builderName, Results[result].upper()))
    if result == SUCCESS:
      color = "green"
      notify = "0"
    else:
      color = "red"
      notify = "1"

    # Yes, we are in Twisted and shouldn't do os.system :)
    os.system('curl -d "room_id=%s&from=Buildbot&message=%s&color=%s&notify=%s" https://api.hipchat.com/v1/rooms/message?auth_token=%s&format=json' % (self.room_id, message, color, notify, self.api_token))
