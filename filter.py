import re

from datetime import timedelta
from typing import Callable

from groupme import GroupMe

class MessageFilter:

    def __init__(self, 
                 username: str = None,
                 text: str = None,
                 date_on: str = None, 
                 date_before: str = None, 
                 date_after: str = None):

        self.groupme = GroupMe()

        self.username = username
        self.userid = None
        self.text = text
        self.date_on = date_on
        # Can't mix these filters with date_on
        self.date_before = date_before if self.date_on is None else None
        self.date_after = date_after if self.date_on is None else None


    def filter_lambda(self) -> Callable:
        """ Make a Callable filter to apply to returned messages. """
        return lambda messages : self.filter_messages(messages)


    def filter_messages(self, messages):
        # TODO: split each filter type into own function
        """ Filter messages by text, sender, date, etc. """

        filtered = []  # Messages to return to user

        if self.userid is None and self.username is not None:
            try:
                groupid = messages[0]['group_id']
                group_members = self.groupme.get_group_members(groupid=groupid)
                self.userid = self.groupme.get_user_id(group_members, name=self.username, nickname=self.username)
            except: # Direct Messages
               self.userid = None

        for message in messages:
            passes = True
            raw_time = message['created_at']
            timestamp = self.groupme.epoch_to_datetime(raw_time).date()

            # Filter user / user ID
            if self.userid:
                if 'sender_id' in message:
                    if message['sender_id'] != self.userid:
                        passes = False
                else:
                    passes = False

            elif self.username: # Direct Messages
                if 'name' in message:
                    if message['name'] != self.username:
                        passes = False
                else:
                    passes = False

            # Filter by text regex
            if self.text:
                if 'text' in message:
                    t = message['text']
                    if t is None: 
                        passes = False  # No text to filter.  Could be image, etc.
                    else:
                        search = re.search(self.text, t)
                        if search is None:
                            passes = False
                else:
                    passes = False

            # Filter by date
            if self.date_on:
                if timestamp != self.date_on:
                    passes = False

            elif self.date_before and self.date_after:
                if (self.date_before - timestamp) < timedelta() or (timestamp - self.date_after) < timedelta():
                    passes = False

            elif self.date_before:
                # either before OR on this date
                if (self.date_before - timestamp) < timedelta():
                    passes = False

            elif self.date_after:
                # either on OR after this date
                if (timestamp - self.date_after) < timedelta():
                    passes = False

            # Add to returned messages if it hasn't failed any filters
            if passes:
                filtered += [message]

        return filtered