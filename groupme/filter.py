import re

from datetime import timedelta
from typing import Callable

from groupme.groupme import GroupMe

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


    def filter_user(self, message):
        """ Return message if it was sent by selected user, otherwise discard. """

        if self.userid:
            if 'sender_id' in message:
                if message['sender_id'] != self.userid:
                    return None
            else:
                return None

        elif self.username: # Direct Messages
            if 'name' in message:
                if message['name'] != self.username:
                    return None
            else:
                return None
        return message


    def filter_date(self, message):
        """ Return message if it was sent in selected date range, otherwise discard. """

        raw_time = message['created_at']
        timestamp = self.groupme.epoch_to_datetime(raw_time).date()

        if self.date_on:
            if timestamp != self.date_on:
                return None

        elif self.date_before and self.date_after:
            if (self.date_before - timestamp) < timedelta() or (timestamp - self.date_after) < timedelta():
                return None

        elif self.date_before:
            # Either before OR on this date
            if (self.date_before - timestamp) < timedelta():
                return None

        elif self.date_after:
            # Either on OR after this date
            if (timestamp - self.date_after) < timedelta():
                return None
        return message


    def filter_text(self, message):
        """ Return message if it contains selected text, otherwise discard. """

        if self.text:
            if 'text' in message:
                t = message['text']
                if t is None: 
                    return None  # No text to filter.  Could be image, etc.
                else:
                    search = re.search(self.text, t)
                    if search is None:
                        return None
            else:
                return None
        return message

    
    def filter_messages(self, messages):
        """ Filter messages by text, sender, date, etc. """

        filtered = []  # Messages to return to user

        # Set up user data if not done already
        if self.userid is None and self.username is not None:
            try:
                groupid = messages[0]['group_id']
                group_members = self.groupme.get_group_members(groupid=groupid)
                self.userid = self.groupme.get_user_id(group_members, name=self.username, nickname=self.username)
            except: # Direct Messages
               self.userid = None

        # Apply filters
        for message in messages:
            message = self.filter_user(message)
            if message:  # We can probably save some computation by not checking filters if it already failed
                message = self.filter_date(message)
            if message:
                message = self.filter_text(message)
            if message:  # Add to returned messages if it hasn't failed any filters
                filtered += [message]

        return filtered