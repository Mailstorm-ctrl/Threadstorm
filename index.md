# Threadstorm
An attempt to bring forum functionality to Discord. Including thread locking, category creation for organization and thread clean-up.

# Commands:

| Command | Arguments| Description |
|:---:|:---:|:---|
| `.tmake` | N/A | This command will start the process of making a thread. Ask for a thread title and the body. Has a cooldown of 2 uses per hour. Takes no arguments.|
| `.tedit` | REQUIRED: body, title or image | Allows the author of the thread or a member with the manage_messages permissions to modify the threads original post. You may upload an image with the command to use your image, or provide a valid url.<br />Example:<br />`.tedit title The Super Shotty is an objectivly bad weapon. It is underpowered`|
| `.tkeep` | N/A | Allows you to "keep" a thread from being deleted due to inactivity. This is a toggle command. Run this command to toggle the delete flag on and off. You will need the `manage_channels` permission to run this.| 
| `.tlock` | OPTIONAL: reason | Allows members with the manage_message permission to lock threads. This will go through and set the send_messages permission to False for every role that has access to the channel/thread. This is a moderation command.<br />Example:<br />`.tlock The Super Shotty is fine. Get better.`|
| `.tunlock` | N/A | Unlocks a thread. Returns to the channels original permission structure. |
| `.tcreate` | REQUIRED: category-name | Lets you create a custom category for your server. Must have the manage_channels permission to run this.<br />Example:<br />`.tcreate Game Talk`|
| `.tdc` | N/A | Deletes a custom category. This command will delete all channels within the invoked category and finally the category itself. Will need to verify action before deletion occurs. |
|`.tprefix` | REQUIRED: prefix | Lets you set a custom guild prefix. Max allowed prefix length is 4 characters. |
| `.thelp` | N/A | Displays this help menu in Discord. |

##### Command Notes:
When using commands that create a text channel or a new category, the channel/category will have *the same permissions as the channel the command was invoked in*. So if your server requires a role to gain access to the rest of the server, the commands will handle this automatically to prevent bypassing your checkpoint.

# Invite this bot to your server:
[https://threadstorm.app/invite](https://threadstorm.app/invite)
##### Why it needs the permissions it request:
`Manage Channel`: This is needed so it can create channels. When you invite this bot to your server, it will create a category named "threads" which is the default location all threads will be put. This also allows the bot to lock/unlock threads. 

`Manage Messages`: When a thread is created, it will pin the original post (In the channel the bot makes). For custom categories, it will delete commands used to create threads to keep the channel clean.

`Manage Roles`: Needed to lock/unlock threads.

`View Audit Log`: SOON! This lets the bot attempt to auto-recover deleted categories.

# Support server
Join this server to report issues or get help with the bot. Alternatively, join to talk with other people.

[Threadstorm Support Server](https://discord.gg/M8DmU86)
