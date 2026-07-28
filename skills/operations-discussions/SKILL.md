---
name: operations-discussions
description: Invoke when a Discussions reference is being handled / an external user enters the project / a bot-created issue originating from Discussions is being processed. Defines Discussions as the external entry point with a bot stationed (issue create and read only, no commit).
layer: L4-operations
---

<discussions>

# Discussions

<purpose>

## Purpose

Discussions = external user entry point.
A bot is stationed in Discussions.
Bot capabilities: issue creation, issue reading.
Bot does not commit or modify code.

External users interact via Discussions -> bot creates issue -> AI implements from issue.

</purpose>

</discussions>
