# GroupMe-python-wrapper
Utility for interacting with GroupMe API -- view/send chats, direct messages, search by user/text/date, and more!

HOW TO USE:

Prerequisites: Python 3

1) Register an "application" with GroupMe (https://dev.groupme.com/applications/new -- you can use dummy data) to receive a GroupMe API token.

2) In Terminal, `$ export GROUPME_TOKEN=<Groupme API Token from step 1>`

3) Run actions from command line e.g. `$ python3 demo.py --get_dms=True` have fun!

---------------------
---------------------

**Options:**

  `-h`, `--help`            
  
  **Show this help message and exit.**
  
  `--get_dms=<bool>`     

  **List all user Direct Messages.**
    
  ```
  python3 demo.py --get_groups=True

  User direct messages:
     Brian
     Rob
     Isabella
     Alex
     GröuрMе Suррört
     Liam
     Dave
     Jen
     Burl
     Mike
     Connor
  ```

  `--get_groups=<bool>`   

  **List all user group chats.** 

  ```
  python3 demo.py --get_groups=True

  User group messages:
     Settle Squad
     Online Catan
     Video Games
     Dave’s Bachelor
  ```
                        
  `--get_group_id=GROUP_NAME`
                        
  **Get internal id for a group chat.**

    python3 demo.py --get_group_id='Football Chat'

    Group ID for group name "Football Chat": 19501457
                        
  `--get_chat_id=CHAT_NAME`
  
  **Get internal id for direct message.**

    python3 demo.py --get_chat_id='Rob'

    Group ID for chat with user "Rob": 15011625
                        
  `--get_group_members=GROUP_NAME`
  
  **List members of chosen group message.**
  
    python3 demo.py --get_group_members='Football Chat'

    Group members for group "Football Chat":
      Name: "Connor" | Nickname: "Bill Russell"
      Name: "Ryan Keller" | Nickname: "2nd Highest Paid QB Fan"
                        
  `--get_chat_messages=CHAT_NAME`
  
  **Get all messages from a direct messages.**
  
    python3 demo.py --get_chat_messages='Rob'
                        
  `--get_group_messages=GROUP_NAME`
  
  **Get all messages from a group message.**

    python3 demo.py --get_group_messages='Football Chat'
                        
  `--filter_text=FILTER_TEXT`
  
  **Filter messages by regex text.** Use with flag that returns messages e.g. `--get_group_messages`.
  
    python3 demo.py --get_group_messages='Football Chat' --filter_text='^Hello!$'
                        
  `--filter_user=USER_NAME`
  
  **Filter messages by user who sent the message.** Use with flag that returns messages e.g. `--get_group_messages`.
  
    python3 demo.py --get_group_messages='Football Chat' --filter_user='Rob'
                        
  `--filter_dateOn=FILTER_DATE`
  
  **Filter messages by exact date.** Use with flag that returns messages e.g. `--get_group_messages`.

    python3 demo.py --get_group_messages='Football Chat' --filter_dateOn='09/13/2019' 
    [date must be in format DD/MM/YYYY with leading zeroes]
                        
  `--filter_dateAfter=FILTER_DATE`
  
  **Filter messages on or after exact date.** Use with flag that returns messages e.g. `--get_group_messages`.
  
    python3 demo.py --get_group_messages='Football Chat' --filter_dateAfter='09/13/2019' 
    [date must be in format DD/MM/YYYY with leading zeroes]
                        
  `--filter_dateBefore=FILTER_DATE`
  
  **Filter messages on or before exact date.** Use with flag that returns messages e.g. `--get_group_messages`.
    
    python3 demo.py --get_group_messages='Football Chat' --filter_dateBefore='09/13/2019' 
    [date must be in format DD/MM/YYYY with leading zeroes]
                        
  `--count=<bool>`       
  
  **Return number of messages fitting criteria.** Use with flag that returns messages e.g. `--get_group_messages`.
  
    python3 demo.py --get_chat_messages="Brian" --count=True

    # messages matching filter: 7
  
  `--send_message=MESSAGE`
  
  **Send message with provided text to chosen group/chat.** Use `--group_name=GROUP_NAME` flag to send to a selected group. Use `--chat_name=CHAT_NAME` flag to send to selected direct message.

    python3 demo.py --send_message='Hello!' --group_name='Football Chat'
    
  `--group_name=GROUP_NAME`
  
  **Specify group to which to send message.** Use with flag `--send_message`.

    python3 demo.py --send_message='Hello!' --group_name='Football Chat'
    
  `--chat_name=CHAT_NAME`
  
  **Specify user to whom to send direct message.** Use with flag `--send_message`.
    
    python3 demo.py --send_message='Hello!' --chat_name='Rob'
    
  `--group_rank_num_posts=GROUP_NAME`
  
  **Get leaderboard of total messages sent per user in group chat.** 
  
    python3 demo.py --group_rank_num_posts='Football Chat'

    Number of posts by user:
      Corey - 264
      Ryan Keller - 178
      Alec - 149
    
  `--group_rank_num_likes=GROUP_NAME`
  
  **Get leaderboard of total likes received per user in group chat.** 
  
    python3 demo.py --group_rank_num_likes='Football Chat'

    Total number of likes on posts by user:
      Nick - 215
      Ryan Keller - 206
      Alec - 195
    
  `--group_rank_num_liked=GROUP_NAME`
  
  **Get leaderboard of total likes given per user in group chat.**
  
    python3 demo.py --group_rank_num_liked='Football Chat'

    Total number of liked posts by user:
      Corey - 332
      Burl - 235
      Nick - 187
    
  `--group_rank_len_posts=GROUP_NAME`
  
  **Tally total number of characters each user has sent in group and avg characters/post.**
  
    python3 demo.py --group_rank_len_posts='Football Chat'

    Total number of characters of text sent by user (avg characters per message):
      Corey - 8,396 (32.17)
      Burl - 7,959 (31.84)
      Nick - 7,020 (35.82)
    
  `--group_most_liked_post=GROUP_NAME`
  
  **Return the message(s) with the most likes in a group chat and its like count.**
  
    python3 demo.py --group_most_liked_post='Football Chat'

    Most-liked post(s) in group (5 likes):

    Sender: Alec | Date: 2017-06-25 16:13:30
      Text: Go Birds!
      Attachment: https://i.groupme.com/810x1440.jpeg.asdasdasd (image)

    Sender: Ryan Keller | Date: 2017-04-04 00:19:57
      Text: Eagles Rule!
