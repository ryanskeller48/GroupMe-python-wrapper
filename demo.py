import sys
from groupme import GroupMe
from datetime import datetime
import re
from optparse import OptionParser
import argparse

DATEON_HELP = "Filter messages by exact date e.g. --filter_dateOn='09/13/2019' " + \
              "[date must be in format DD/MM/YYYY with leading zeroes]"
DATEAFTER_HELP = "Filter messages on or after exact date e.g. --filter_dateAfter='09/13/2019' " + \
              "[date must be in format DD/MM/YYYY with leading zeroes]"
DATEBEFORE_HELP = "Filter messages on or before exact date e.g. --filter_dateBefore='09/13/2019' " + \
              "[date must be in format DD/MM/YYYY with leading zeroes]"

def main():

    g = GroupMe()
    
    usage = "usage: interact with GroupMe API -- list chats/DMs/messages, send messages, " + \
            "filter messages by text/sender/date"

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

    (options, _) = parser.parse_args()

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
        if options.filter_text: # seems to be working
            filters["text"] = rf"{options.filter_text}"
        if options.filter_dateOn: # TODO: test
            filters["dateOn"] = options.filter_dateOn
        else:
            if options.filter_dateBefore: # TODO: test
                filters["dateBefore"] = options.filter_dateBefore
            if options.filter_dateAfter: # TODO: test
                filters["dateAfter"] = options.filter_dateAfter
        if options.filter_user: # TODO: test
            filters["user"] = options.filter_user

        user_filter = g.filter_lambda(text=filters["text"], user=filters["user"], dateOn=filters["dateOn"],
                                      dateAfter=filters["dateAfter"], dateBefore=filters["dateBefore"])

        try:
            messages = g.get_all_messages(name=options.get_chat_messages, chat=True, filt=user_filter)
            for message in messages:
                print (message['text'])
        except:
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
        if options.filter_dateOn: # TODO: test
            filters["dateOn"] = options.filter_dateOn
        else:
            if options.filter_dateBefore: # TODO: test
                filters["dateBefore"] = options.filter_dateBefore
            if options.filter_dateAfter: # TODO: test
                filters["dateAfter"] = options.filter_dateAfter
        if options.filter_user: # TODO: test
            filters["user"] = options.filter_user

        user_filter = g.filter_lambda(text=filters["text"], user=filters["user"], dateOn=filters["dateOn"],
                                      dateAfter=filters["dateAfter"], dateBefore=filters["dateBefore"])

        try:
            messages = g.get_all_messages(name=options.get_group_messages, group=True, filt=user_filter)
            for message in messages:
                print (message['text'])
        except:
            print (f"\nNo group message with that name! (name: \"{options.get_group_messages}\")")

if __name__ == "__main__":
    main()
