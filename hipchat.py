from buildbot.status.base import StatusReceiverMultiService
from buildbot.status.builder import Results, SUCCESS
import os, urllib, json, requests


class HipChatStatusPush(StatusReceiverMultiService):

  def __init__(self, api_token, room_id, localhost_replace=False, **kwargs):
      StatusReceiverMultiService.__init__(self)

      self.api_token = api_token
      self.room_id = room_id
      self.localhost_replace = localhost_replace

  def sendNotification(self, message, color, notify):
    client = requests.session()
    client.headers = { "Authorization": "Bearer {api_token}".format(api_token=self.api_token),
                       "Content-Type": "application/json" }
    client.post('https://api.hipchat.com/v2/room/{room_id}/notification'.format(room_id=self.room_id),
                params={"format": "json"},
                data=json.dumps({"notify": notify, "message": message, "color": color}))

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
    return self  # subscribe to this builder

  def buildFinished(self, builderName, build, result):
    url = self.master_status.getURLForThing(build)
    if self.localhost_replace:
      url = url.replace("//localhost", "//%s" % self.localhost_replace)

    message = "<a href='%s'>%s</a> %s" % (url, builderName, Results[result].upper())

    # Valid values: yellow, green, red, purple, gray, random.
    if result == SUCCESS:
      color = "green"
      notify = False
    else:
      color = "red"
      notify = True

    # Yes, we are in Twisted and shouldn't do os.system :)
    self.sendNotification(message, color, notify)
