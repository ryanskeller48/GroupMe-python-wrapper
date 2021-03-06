# GroupMe-python-wrapper
Utility for interacting with GroupMe API -- view/send chats, direct messages, search by user/text/date

HOW TO USE:

prerequisites: python 3

1) register an "application" with GroupMe (https://dev.groupme.com/applications/new -- you can use dummy data) to receive a GroupMe API token.

2) in Terminal, `$ export groupme_token=<Groupme API Token from step 1>`

3) run actions from command line e.g. `$ python3 demo.py --get_dms=True` have fun!

---------------------

Options:

  -h, --help            
  
    show this help message and exit
  
  --get_dms=GET_DMS     
  
    List all user Direct Messages i.e. --get_groups=True
  
  --get_groups=GET_GROUPS
  
    List all user group chats i.e. --get_groups=True
                        
  --get_group_id=GET_GROUP_ID
                        
    Get internal id for group chat e.g. --get_group_id='Football Chat'
                        
  --get_chat_id=GET_CHAT_ID
  
    Get internal id for direct message e.g. --get_chat_id='Rob'
                        
  --get_group_members=GET_GROUP_MEMBERS
  
    List members of chosen group message e.g. --get_group_members='Football Chat'
                        
  --get_chat_messages=GET_CHAT_MESSAGES
  
    Get all messages from a direct messages e.g. --get_chat_messages='Rob'
                        
  --get_group_messages=GET_GROUP_MESSAGES
  
    Get all messages from a group message e.g. --get_group_messages='Football Chat'
                        
  --filter_text=FILTER_TEXT
  
    Filter messages by regex text e.g. --filter_text='^Hello!$'
                        
  --filter_user=FILTER_USER
  
    Filter messages by user who sent e.g. --filter_user='Rob'
                        
  --filter_dateOn=FILTER_DATEON
  
    Filter messages by exact date e.g. --filter_dateOn='09/13/2019' 
    [date must be in format DD/MM/YYYY with leading zeroes]
                        
  --filter_dateAfter=FILTER_DATEAFTER
  
    Filter messages on or after exact date e.g. --filter_dateAfter='09/13/2019' 
    [date must be in format DD/MM/YYYY with leading zeroes]
                        
  --filter_dateBefore=FILTER_DATEBEFORE
  
    Filter messages on or before exact date e.g. --filter_dateBefore='09/13/2019' 
    [date must be in format DD/MM/YYYY with leading zeroes]
                        
  --count=COUNT         
  
    return number of messages fitting criteria i.e. --count=True
  
  --send_message=SEND_MESSAGE
  
    Send message with provided text to chosen group/chat. Use --group_name='<GROUP NAME>' flag to send to a selected group. 
    Use --chat_name='<CHAT USER NAME>' flag to send to selected direct message. 
    e.g. python3 demo.py --send_message='Hello!' --group_name='Football Chat'
    
  --group_name=GROUP_NAME
  
    Specify group to send message to e.g. --group_name='Football Chat' 
    
  --chat_name=CHAT_NAME
  
    Specify user to send direct message to e.g. --chat_name='Rob'
    
  --group_rank_num_posts=GROUP_RANK_NUM_POSTS
  
    Get leaderboard of total messages sent per user in group chat e.g. --group_rank_num_posts='Football Chat'
    
  --group_rank_num_likes=GROUP_RANK_NUM_LIKES
  
    Get leaderboard of total likes received per user in group chat e.g.  --group_rank_num_likes='Football Chat'
    
  --group_rank_num_liked=GROUP_RANK_NUM_LIKED
  
    Get leaderboard of total likes given per user in group chat e.g.  --group_rank_num_liked='Football Chat'
    
  --group_rank_len_posts=GROUP_RANK_LEN_POSTS
  
    Tally total number of characters each user has sent in group and avg characters/post e.g. --group_rank_len_posts='Football Chat'
    
  --group_most_liked_post=GROUP_MOST_LIKED_POST
  
    Return the message(s) with the most likes in a group chat and its like count e.g. --group_most_liked_post='Football Chat'
