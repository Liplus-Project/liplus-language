---
globs:
alwaysApply: true
layer: L4-operations
---

# Notifications API

PATCH  /notifications/threads/{id}   -> 205  read (stays in Inbox)
PUT    /notifications {"read":true}  -> 205  mark all read
DELETE /notifications/threads/{id}  -> 204  done (removed from Inbox)
GET    /notifications?all=false      -> 200  check inbox
scope = notifications (classic PAT)
