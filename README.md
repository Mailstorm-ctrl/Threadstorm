# Threadstorm [![Discord Bots](https://top.gg/api/widget/status/617376702187700224.svg)](https://top.gg/bot/617376702187700224)
An attempt to bring forum functionality to Discord. Including thread locking, category creation for organization and thread clean-up.

# Known issues:
Sometimes, the bot will not post a 24 hour warning if a thread is about to expire.

# Commands:

| Command | Arguments| Description |
|:---:|:---:|:---|
| `.tmake` | OPTIONAL: -t <title text>, -b <body text>, json attachment | Running this command with no argument or attachments will start the process of creating a thread. Alternativly, you may run this command with no argument but have a valid json file attached and the bot will use that file to create a thread. For an example of a valid json file, please see https://discohook.org/. Another option also exist which is using CLI-like arguments to create a thread.<br /> Example:<br /> `.tmake -t This is a title -b This is the body.`|
| `.tedit` | REQUIRED: body, title, image, json | Allows the author of the thread or a member with the manage_messages permissions to modify the threads original post. You may upload an image with the command to use your image, or provide a valid url.If the thread was created via a json file, you cannot use the body, title and image arguments. You must use the json argument and supply a valid json file to update the thread with.<br />Example:<br />`.tedit title The Super Shotty is an objectivly bad weapon. It is underpowered`|
| `.tkeep` | N/A | Allows you to "keep" a thread from being deleted due to inactivity. This is a toggle command. Run this command to toggle the delete flag on and off. You will need the `manage_channels` permission to run this.| 
| `.tlock` | OPTIONAL: reason | Allows members with the manage_message permission to lock threads. This will go through and set the send_messages permission to False for every role that has access to the channel/thread. This is a moderation command.<br />Example:<br />`.tlock The Super Shotty is fine. Get better.`|
| `.tunlock` | N/A | Unlocks a thread. Returns to the channels original permission structure. |
| `.tcreate` | REQUIRED: category-name | Lets you create a custom category for your server. Must have the manage_channels permission to run this.<br />Example:<br />`.tcreate Game Talk`|
| `.tdc` | N/A | Deletes a custom category. This command will delete all channels within the invoked category and finally the category itself. Will need to verify action before deletion occurs. |
|`.tprefix` | REQUIRED: prefix | Lets you set a custom guild prefix. Max allowed prefix length is 4 characters. |
|`.tttd` | REQUIRED: days | Sets your guilds thread activity time out. The default is 3 days. |
|`.troles` | OPTIONAL: [roles] | Running without arguments will toggle the flag that determines if users need a specific role in your guild to run `.tmake`. If you supply arguments, they must be mentions, ids, or the name of a role in your server. If a role is not found in the list, it is added. If it's already in the list, it is removed. <br />Example:<br />`.troles Staff Moderator` |
|`.taroles` | OPTIONAL: [roles] | Running without arguments will toggle the flag that determines if roles in this list can bypass the cooldown. If you supply arguments, they must be mentions, ids, or the name of a role in your server. If a role is not found in the list, it is added. If it's already in the list, it is removed. <br />Example:<br />`.taroles Staff Moderator` |
|`.tbypass` | N/A | The same as running `.taroles` without any arguments. |
|`.tclean` | N/A | Toggles the flag that determines if the bot "cleans up" messages used to make a thread. This will delete all messages used in the creation of a thread but leave the success message posted. |
| `.thelp` | N/A | Displays this help menu in Discord. |

##### Command Notes:
When using commands that create a text channel or a new category, the channel/category will have *the same permissions as the channel the command was invoked in*. So if your server requires a role to gain access to the rest of the server, the commands will handle this automatically to prevent bypassing your checkpoint. However, the initial category the bot makes is viewable publicly.

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
