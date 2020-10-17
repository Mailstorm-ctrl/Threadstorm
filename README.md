# Threadstorm [![Discord Bots](https://top.gg/api/widget/status/617376702187700224.svg)](https://top.gg/bot/617376702187700224)
An attempt to bring forum functionality to Discord. Including thread locking, category creation for organization and thread clean-up.

# Usage example:
![](https://threadstorm.app/assets/DEMO.gif)

# Invite this bot to your server:
https://threadstorm.app/invite
##### Why it needs the permissions it request:
`Manage Channel`: This is needed so it can create channels. When you invite this bot to your server, it will create a category named "threads" which is the default location all threads will be put. This also allows the bot to lock/unlock threads. 

`Manage Messages`: When a thread is created, it will pin the original post (In the channel the bot makes). For custom categories, it will delete commands used to create threads to keep the channel clean.

`Manage Roles`: Needed to lock/unlock threads.

`View Audit Log`: The bot will attempt to move channels/threads back into their respective channels if they weren't deleted properly.

# Support server
Join this server to report issues or get help with the bot. Alternatively, join to talk with other people.

https://threadstorm.app/support

## Known issues:
Sometimes, the bot will not post a 24 hour warning if a thread is about to expire.
