import sys
from groupme import GroupMe, BadNameException
from datetime import datetime
import re
from optparse import OptionParser
import argparse
from group_stats import *

class BadDateException(Exception):
        pass

DATEON_HELP = "Filter messages by exact date e.g. --filter_dateOn='09/13/2019' " + \
              "[date must be in format DD/MM/YYYY with leading zeroes]"
DATEAFTER_HELP = "Filter messages on or after exact date e.g. --filter_dateAfter='09/13/2019' " + \
              "[date must be in format DD/MM/YYYY with leading zeroes]"
DATEBEFORE_HELP = "Filter messages on or before exact date e.g. --filter_dateBefore='09/13/2019' " + \
              "[date must be in format DD/MM/YYYY with leading zeroes]"
SEND_HELP = "Send message with provided text to chosen group/chat.  Use --group_name='<GROUP NAME>' flag to send to" + \
            " a selected group.  Use --chat_name='<CHAT USER NAME>' flag to send to selected direct message. " + \
            "e.g. python3 demo.py --send_message='Hello!' --group_name='Football Chat'"

def parse_input_date(d):
    try:
        d = d.split('/')
        month = int(d[0])
        day = int(d[1])
        year = int(d[2])
        return datetime(year, month, day).date()
    except:
        print ("Bad date! Date must be in format DD/MM/YYYY with leading zeroes")
        raise BadDateException

def main():

    # create a GroupMe API wrapper instance
    g = GroupMe()
    
    usage = "usage: interact with GroupMe API -- list chats/DMs/messages, send messages, " + \
            "filter messages by text/sender/date"

    # set up command line options
    parser = OptionParser(usage)

    parser.add_option("--get_dms", action="store", dest="get_dms", default=None,
                      help="List all user Direct Messages i.e. --get_groups=True")
    parser.add_option("--get_groups", action="store", dest="get_groups", default=None,
                      help="List all user group chats i.e. --get_groups=True")
    parser.add_option("--get_group_id", action="store", dest="get_group_id", default=None,
                      help="Get internal id for group chat e.g. --get_group_id='Football Chat'")
    parser.add_option("--get_chat_id", action="store", dest="get_chat_id", default=None,
                      help="Get internal id for direct message e.g. --get_chat_id='Rob'")
    parser.add_option("--get_group_members", action="store", dest="get_group_members", default=None,
                      help="List members of chosen group message e.g. --get_group_members='Football Chat'")
    parser.add_option("--get_chat_messages", action="store", dest="get_chat_messages", default=None,
                      help="Get all messages from a direct messages e.g. --get_chat_messages='Rob'")
    parser.add_option("--get_group_messages", action="store", dest="get_group_messages", default=None,
                      help="Get all messages from a group message e.g. --get_group_messages='Football Chat'")
    parser.add_option("--filter_text", action="store", dest="filter_text", default=None,
                      help="Filter messages by regex text e.g. --filter_text='^Hello!$'")
    parser.add_option("--filter_user", action="store", dest="filter_user", default=None,
                      help="Filter messages by user who sent e.g. --filter_user='Rob'")
    parser.add_option("--filter_dateOn", action="store", dest="filter_dateOn", default=None, help=DATEON_HELP)
    parser.add_option("--filter_dateAfter", action="store", dest="filter_dateAfter", default=None, help=DATEAFTER_HELP)
    parser.add_option("--filter_dateBefore", action="store", dest="filter_dateBefore", default=None, help=DATEBEFORE_HELP)
    parser.add_option("--count", action="store", dest="count", default=None, 
                      help="return number of messages fitting criteria i.e. --count=True")
    parser.add_option("--send_message", action="store", dest="send_message", default=None, help=SEND_HELP)
    parser.add_option("--group_name", action="store", dest="group_name", default=None, 
                      help="Specify group to send message to e.g. --group_name='Football Chat'")
    parser.add_option("--chat_name", action="store", dest="chat_name", default=None, 
                      help="Specify user to send direct message to e.g. --chat_name='Rob'")
    # group_stats stuff
    parser.add_option("--group_rank_num_posts", action="store", dest="group_rank_num_posts", default=None,
                      help="Get leaderboard of total messages sent per user in group chat e.g." + \
                           " --group_rank_num_posts='Football Chat'")
    parser.add_option("--group_rank_num_likes", action="store", dest="group_rank_num_likes", default=None,
                      help="Get leaderboard of total likes received per user in group chat e.g. " + \
                           " --group_rank_num_likes='Football Chat'")
    parser.add_option("--group_rank_num_liked", action="store", dest="group_rank_num_liked", default=None,
                      help="Get leaderboard of total likes given per user in group chat e.g. " + \
                           " --group_rank_num_liked='Football Chat'")
    parser.add_option("--group_rank_len_posts", action="store", dest="group_rank_len_posts", default=None,
                      help="Tally total number of characters each user has sent in group and avg characters/post " + \
                           "e.g. --group_rank_len_posts='Football Chat'")
    parser.add_option("--group_most_liked_post", action="store", dest="group_most_liked_post", default=None,
                      help="Return the message(s) with the most likes in a group chat and its like count " + \
                           "e.g. --group_most_liked_post='Football Chat'")
    parser.add_option("--orphaned_users", action="store", dest="orphaned_users", default=None,
                      help="Find users that have left a group and list their usernames/GroupMe ID #s " + \
                           "e.g. --orphaned_users='Football Chat'")

    # TODO: add orphaned_users option when finished with that method

    # grab input from command line
    (options, _) = parser.parse_args()

    # carry out specified action
    if options.get_dms:
        dms = g.get_chats()
        print ("\nUser direct messages:")
        for dm in dms:
            print ("    " + dm['other_user']['name'])

    elif options.get_groups:
        dms = g.get_groups()
        print ("\nUser group messages:")
        for dm in dms:
            print ("    " + dm['name'])

    elif options.get_group_id:
        gid = g.get_group_id(options.get_group_id)
        if gid:
            print (f"\nGroup ID for group name \"{options.get_group_id}\": {gid}")
        else:
            print (f"\nNo group by that name! (name: \"{options.get_group_id}\")")

    elif options.get_chat_id:
        cid = g.get_chat_id(options.get_chat_id)
        if cid:
            print (f"\nGroup ID for chat with user \"{options.get_chat_id}\": {cid}")
        else:
            print (f"\nNo direct message with that user! (name: \"{options.get_chat_id}\")")

    elif options.get_group_members:
        members = g.get_group_members(name=options.get_group_members, groupid=options.get_group_members)
        if members:
            print (f"\nGroup members for group \"{options.get_group_members}\":")
            for member in members:
                print (f"    Name: \"{member['name']}\" | Nickname: \"{member['nickname']}\"")
        else:
            print (f"\nNo group by that name! (name: \"{options.get_group_members}\")")

    elif options.get_chat_messages:
        filters = {
            "text": None,
            "user": None,
            "dateOn": None,
            "dateAfter": None,
            "dateBefore": None,
        }
        if options.filter_text:
            filters["text"] = rf"{options.filter_text}"
        if options.filter_dateOn:
            filters["dateOn"] = parse_input_date(options.filter_dateOn)
        else:
            if options.filter_dateBefore:
                filters["dateBefore"] = parse_input_date(options.filter_dateBefore)
            if options.filter_dateAfter:
                filters["dateAfter"] = parse_input_date(options.filter_dateAfter)
        if options.filter_user:
            filters["user"] = options.filter_user

        user_filter = g.filter_lambda(text=filters["text"], user=filters["user"], dateOn=filters["dateOn"],
                                      dateAfter=filters["dateAfter"], dateBefore=filters["dateBefore"])

        try:
            messages = g.get_all_messages(name=options.get_chat_messages, chat=True, filt=user_filter)
            if not messages:
                print ("No messages match filter")
                return

            if options.count:
                print (f"\n# messages matching filter: {len(messages)}")
            else:
                print ("")
                if not messages:
                    print ("No messages match filter")
                    return
                for message in messages:
                    message_meta = f"Sender: {message['name']} | " + \
                                   f"Date: {g.epoch_to_datetime(message['created_at']).date()}"
                    print (message_meta)
                    print (f"    Text: {message['text']}\n")
        except BadNameException:
            print (f"\nNo direct message with that user! (name: \"{options.get_chat_messages}\")")

    elif options.get_group_messages:
        filters = {
            "text": None,
            "user": None,
            "dateOn": None,
            "dateAfter": None,
            "dateBefore": None,
        }
        if options.filter_text: 
            filters["text"] = rf"{options.filter_text}"
        if options.filter_dateOn:
            filters["dateOn"] = parse_input_date(options.filter_dateOn)
        else:
            if options.filter_dateBefore:
                filters["dateBefore"] = parse_input_date(options.filter_dateBefore)
            if options.filter_dateAfter:
                filters["dateAfter"] = parse_input_date(options.filter_dateAfter)
        if options.filter_user:
            filters["user"] = options.filter_user

        user_filter = g.filter_lambda(text=filters["text"], user=filters["user"], dateOn=filters["dateOn"],
                                      dateAfter=filters["dateAfter"], dateBefore=filters["dateBefore"])

        try:
            messages = g.get_all_messages(name=options.get_group_messages, group=True, filt=user_filter)
            if not messages:
                print ("No messages match filter")
                return

            groupid = messages[0]['group_id']
            members = g.get_group_members(groupid=groupid)

            if options.count:
                print (f"\n# messages matching filter: {len(messages)}")
            else:
                print ("")
                for message in messages:
                    for member in members:
                        if member['user_id'] == message['sender_id']:
                            sender = member
                    sender_name = sender['nickname']
                    sender_nickname = sender['name']
                    message_meta = f"Sender: {sender_nickname} ({sender_name}) | " + \
                                   f"Date: {g.epoch_to_datetime(message['created_at']).date()}"

                    print (message_meta)
                    print (f"    Text: {message['text']}\n")
        except BadNameException:
            print (f"\nNo group message with that name! (name: \"{options.get_group_messages}\")")

    elif options.send_message: 
        if options.group_name:
            sent = g.send_message(options.send_message, name=options.group_name, group=True)
            print (sent)
        elif options.chat_name:
            sent = g.send_message(options.send_message, name=options.chat_name, chat=True)
            print (sent)
        else:
            print ("Provide a --chat_name or --group_name! Try --help")

    # group_stats stuff
    elif options.group_rank_num_posts:
        print (group_rank_num_posts(options.group_rank_num_posts))
        
    elif options.group_rank_num_likes:
        print (group_rank_num_likes(options.group_rank_num_likes))

    elif options.group_rank_num_liked:
        print (group_rank_num_liked(options.group_rank_num_liked))

    elif options.group_rank_len_posts:
        print (group_rank_len_posts(options.group_rank_len_posts))

    elif options.group_most_liked_post:
        print (group_most_liked_post(options.group_most_liked_post))

    elif options.orphaned_users:
        print (orphaned_users(options.orphaned_users))

    else: # no input
        print ("Provide an action! Try --help")

if __name__ == "__main__":
    main()
