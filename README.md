HipChat status plugin for Buildbot
==================================

This Buildbot plugin sends messages to a HipChat room when each build finishes with a handy link to the build results.

This plugin was created by the dev team at http://www.pricingassistant.com/ ; Contributions are welcome!


Install
=======

Copy hipchat.py next to your master.cfg file

Then in your master.cfg, add the following:

```
import hipchat
c['status'].append(hipchat.HipChatStatusPush("YOUR_HIPCHAT_TOKEN", "HIPCHAT_ROOM_ID"))
```

If you Buildbot web frontend doesn't know its public address it will use "localhost" in its links. You can change this:

```
import hipchat
c['status'].append(hipchat.HipChatStatusPush("YOUR_HIPCHAT_TOKEN", "HIPCHAT_ROOM_ID", localhost_replace="buildbot.mycompany.com"))
```

Enjoy!