from buildbot.status.base import StatusReceiverMultiService
from buildbot.status.builder import Results, SUCCESS, WARNINGS, FAILURE
import os, urllib, json, requests


class HipChatStatusPush(StatusReceiverMultiService):

  def __init__(self, api_token, room_id, localhost_replace=False, mode='all', **kwargs):
      StatusReceiverMultiService.__init__(self)

      self.api_token = api_token
      self.room_id = room_id
      self.localhost_replace = localhost_replace
      if isinstance(mode, basestring):
          if mode == "all":
              mode = ("failing", "passing", "warnings", "exception")
          elif mode == "warnings":
              mode = ("failing", "warnings")
          else:
              mode = (mode,)
      self.mode = mode

  def sendNotification(self, message, color, notify):
    print("Send HipChat message " + message)
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

  def isNotfificationNeeded(self, build, result):
    if "failing" in self.mode and result == FAILURE:
        return True
    if "passing" in self.mode and result == SUCCESS:
        return True
    if "warnings" in self.mode and result == WARNINGS:
        return True
    if "exception" in self.mode and result == EXCEPTION:
        return True

    return False

  def buildFinished(self, builderName, build, result):
    if not self.isNotfificationNeeded(build, result):
      return
    url = self.master_status.getURLForThing(build)
    if self.localhost_replace:
      url = url.replace("//localhost", "//%s" % self.localhost_replace)

    message = "<a href='%s'>%s</a> %s" % (url, builderName, Results[result].upper())

    # Valid values: yellow, green, red, purple, gray, random.
    if result == SUCCESS:
      color = "green"
      notify = False
    elif result == WARNINGS:
      color = "orange"
      notify = False
    else:
      color = "red"
      notify = True

    # Yes, we are in Twisted and shouldn't do os.system :)
    self.sendNotification(message, color, notify)
