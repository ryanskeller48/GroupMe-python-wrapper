from message_iterator import MessageIterator
from groupme import GroupMe

GM_INSTANCE = GroupMe()

def group_rank_num_posts(name, filt=None, filtstr=None):
    """ leaderboard of total messages sent per user in group chat """

    it = MessageIterator(name=name, group=True, filt=filt)
    members = GM_INSTANCE.get_group_members(name=name)
    scoreboard = {}

    for member in members:
        scoreboard[member['user_id']] = 0

    page = it.next()
    while (page != None):
        for message in page:
            if 'sender_id' in message and message['sender_id'] != "system" and message['sender_id'] in scoreboard:
                scoreboard[message['sender_id']] += 1
        page = it.next()

    score_format = []
    for user_id in scoreboard:
        for member in members:
            if user_id == member['user_id']:
                score_format += [(scoreboard[user_id], member['name'])]
                break

    score_sort = sorted(score_format)
    score_sort.reverse()
    
    if filtstr:
        out = f"\nNumber of posts by user {filtstr}:\n"
    else:
        out = "\nNumber of posts by user:\n"
    for player in score_sort:
         out += f"    {player[1]} - {player[0]}\n"

    return out

def group_rank_num_likes(name):
    """ leaderboard of total likes received per user in group chat """

    it = MessageIterator(name=name, group=True)
    members = GM_INSTANCE.get_group_members(name=name)
    scoreboard = {}

    for member in members:
        scoreboard[member['user_id']] = 0

    page = it.next()
    while (page != None):
        for message in page:
            if 'sender_id' in message and message['sender_id'] != "system" and message['sender_id'] in scoreboard and \
                'favorited_by' in message:
                num_likes = len(message['favorited_by'])
                scoreboard[message['sender_id']] += num_likes
        page = it.next()

    score_format = []
    for user_id in scoreboard:
        for member in members:
            if user_id == member['user_id']:
                score_format += [(scoreboard[user_id], member['name'])]
                break

    score_sort = sorted(score_format)
    score_sort.reverse()

    out = "\nTotal number of likes on posts by user:\n"
    for player in score_sort:
        out += f"    {player[1]} - {player[0]}\n"

    return out

def group_rank_num_liked(name):
    """ leaderboard of total likes given by user in group chat """

    it = MessageIterator(name=name, group=True)
    members = GM_INSTANCE.get_group_members(name=name)
    scoreboard = {}

    for member in members:
        scoreboard[member['user_id']] = 0

    page = it.next()
    while (page != None):
        for message in page:
            if 'sender_id' in message and message['sender_id'] != "system":
                likes = message['favorited_by']
                for like in likes:
                    if like in scoreboard:
                        scoreboard[like] += 1
        page = it.next()

    score_format = []
    for user_id in scoreboard:
        for member in members:
            if user_id == member['user_id']:
                score_format += [(scoreboard[user_id], member['name'])]
                break

    score_sort = sorted(score_format)
    score_sort.reverse()

    out = "\nTotal number of liked posts by user:\n"
    for player in score_sort:
        out += f"    {player[1]} - {player[0]}\n"

    return out

def group_rank_len_posts(name):
    """ tally total number of characters each user has sent in group and avg characters/post """

    it = MessageIterator(name=name, group=True)
    members = GM_INSTANCE.get_group_members(name=name)
    scoreboard = {}

    for member in members:
        scoreboard[member['user_id']] = [0, 0] # [# of characters sent, # of posts]

    page = it.next()
    while (page != None):
        for message in page:
            if 'sender_id' in message and message['sender_id'] != "system" and message['sender_id'] in scoreboard:
                if message['text'] is not None:
                    len_text = len(message['text'])
                    scoreboard[message['sender_id']][0] += len_text
                    scoreboard[message['sender_id']][1] += 1
        page = it.next()

    score_format = []
    for user_id in scoreboard:
        for member in members:
            if user_id == member['user_id']:
                len_posts = scoreboard[user_id][0]
                num_posts = scoreboard[user_id][1]
                if num_posts == 0:
                    score_format += [(len_posts, float(0), member['name'])]
                else:
                    score_format += [(len_posts, len_posts/float(num_posts), member['name'])]
                break

    score_sort = sorted(score_format)
    score_sort.reverse()

    out = "\nTotal number of characters of text sent by user (avg characters per message):\n"
    for player in score_sort:
        n = player[2]
        count = f"{player[0]:,}"
        av = float(f"{player[1]:.2f}")
        av = f"{av:,}"
        out += f"    {n} - {count} ({av})\n"

    return out

def group_most_liked_post(name):
    """ return the message(s) with the most likes in a group chat and its like count """
    
    it = MessageIterator(name=name, group=True)
    members = GM_INSTANCE.get_group_members(name=name)
    ids = [member['user_id'] for member in members]
    scoreboard = {}

    top_likes = 0
    top_posts = []

    page = it.next()
    while (page != None):
        for message in page:
            if 'favorited_by' in message and message['favorited_by'] is not None and message['sender_id'] != "system" \
                and message['sender_id'] in ids:
                num_likes = len(message['favorited_by'])
                if num_likes > top_likes:
                    top_posts = [message]
                    top_likes = num_likes
                elif num_likes == top_likes:
                    top_posts += [message]
        page = it.next()
    
    out = f"\nMost-liked post(s) in group ({top_likes} likes):\n\n"
    for post in top_posts:
        user_name = None
        user_id = post['sender_id']
        posttime = GM_INSTANCE.epoch_to_datetime(post['created_at'])
        attachments = post['attachments']
        for member in members:
            if user_id == member['user_id']:
                user_name = member['name']
        out += f"Sender: {user_name} | Date: {posttime}\n"
        out += f"    Text: {post['text']}\n"
        if attachments is not None and len(attachments) > 0:
            for attachment in attachments:
                try:
                    out += f"    Attachment: {attachment['url']} ({attachment['type']})\n"
                except:
                    pass
        out += "\n"

    return out

def orphaned_users(groupname):
    """ return list of users who have left a group chat """

    it = MessageIterator(name=groupname, group=True)
    current_members = GM_INSTANCE.get_group_members(name=groupname)
    current_ids = [member['user_id'] for member in current_members]
    orphan_ids = {}

    page = it.next()
    while (page != None):
        for message in page:
            if message['sender_id'] != "system" and message['sender_id'] != "calendar" and \
                message['sender_id'] not in current_ids and (message['sender_id'] not in orphan_ids or \
                (message['sender_id'] in orphan_ids and orphan_ids[message['sender_id']] is None) ):
                    if 'name' in message and message['name'] is not None:
                        orphan_ids[message['sender_id']] = message['name']
                    else:
                        orphan_ids[message['sender_id']] = None
        page = it.next()

    out = f"\nUsers that have left group '{groupname}':\n"
    for orphan_id in orphan_ids:
        out += f"    Name: {orphan_ids[orphan_id]} | GroupMe ID #: {orphan_id}\n"
    out += "\n"

    return out

