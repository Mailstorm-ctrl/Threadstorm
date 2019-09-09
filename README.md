# Thread-Bot
An attempt to bring forum functionality to Discord.

# Commands:

| Command | Arguments| Description |
|:---:|:---:|:---|
| `.tmake` | N/A | This command will start the process of making a thread. Ask for a thread title and the body. Has a cooldown of 2 uses per hour. Takes no arguments.|
| `.tedit` | REQUIRED: body, title or image | Allows the author of the thread or a member with the manage_messages permissions to modify the threads original post. You may upload an image with the command to use your image, or provide a valid url. |
| `.tlock` | OPTIONAL: reason | Allows members with the manage_message permission to lock threads. This will go through and set the send_messages permission to False for every role that has access to the channel/thread. This is a moderation command. |
| `.tunlock` | N/A | Unlocks a thread. Returns to the channels original permission structure. |
| `.tcreate` | REQUIRED: category-name | Lets you create a custom category for your server. Must have the manage_channels permission to run this. |
| `.tdc` | N/A | Deletes a custom category. This command will delete all channels within the invoked category and finally the category itself. Will need to verify action before deletion occurs. |
|`.tprefix` | REQUIRED: prefix | Lets you set a custom guild prefix. Max allowed prefix length is 4 characters. |
| `.thelp` | N/A | Displays this help menu in Discord. |
| `.tim` | N/A | Sends an invite link for the bot to the channel command was invoked in. |

# Invite this bot to your server:

