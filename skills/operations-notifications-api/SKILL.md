---
name: operations-notifications-api
description: Invoke when the GitHub notifications API is about to be called directly (PATCH, PUT, DELETE or GET on notification threads). Reference for endpoint behavior, response codes, and the required PAT scope.
layer: L4-operations
---

<notifications-api>

# Notifications API

PATCH  /notifications/threads/{id}   -> 205  read (stays in Inbox)
PUT    /notifications {"read":true}  -> 205  mark all read
DELETE /notifications/threads/{id}  -> 204  done (removed from Inbox)
GET    /notifications?all=false      -> 200  check inbox
scope = notifications (classic PAT)

</notifications-api>
