from message_iterator import MessageIterator
from groupme import GroupMe

GM_INSTANCE = GroupMe()

def group_rank_num_posts(name):
    """ leaderboard of total messages sent by user in group chat """

    it = MessageIterator(name=name, group=True)
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

    out = "\nNumber of posts by user:\n"
    for player in score_sort:
         out += f"    {player[1]} - {player[0]}\n"

    return out

def group_rank_num_likes(name):
    """ leaderboard of total likes received by user in group chat """

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

def group_rank_len_posts(name): # TODO: implement
    """ tally total number of characters each user has sent in group and avg characters/post"""

    return

def most_liked_message(groupname): # TODO: implement
    """ return the message(s) with the most likes in a group chat and its like count """

    return

def orphaned_users(groupname): # TODO: implement
    """ return list of users who have left a group chat """

    return

