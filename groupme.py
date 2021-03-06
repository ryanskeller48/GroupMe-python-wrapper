import logging
import json
import os
import requests
from datetime import datetime, date, timedelta
from random import randint
import re
from math import ceil

class APIAuthException(Exception):
    pass

class BadNameException(Exception):
    pass

class BadMessageException(Exception):
    pass

logging.basicConfig(level=logging.DEBUG)
logging.getLogger(__name__)


class GroupMe:

    def __init__(self, api_token=os.environ['groupme_token']):
        self.api_url = "https://api.groupme.com/v3"
        self.api_token = api_token

    def _api_request(self, endpoint, params=None):
        """ helper to do API GET calls """
        
        if params:
            response = requests.get(url=f"{self.api_url}/{endpoint}", params=params)
        else:
            response = requests.get(url=f"{self.api_url}/{endpoint}")
        code = response.status_code
        if 200 <= code < 300:
            logging.debug(f"API call: {self.api_url}/{endpoint} | {code}")
            encoding = response.encoding
            raw = response.content
            return json.loads(raw.decode(encoding))
        elif code >= 500:
            raise APIAuthException
        else:
            logging.error(f"ERROR: Bad API call: {self.api_url}/{endpoint} | {code}")

    def _api_request_post(self, endpoint, data, headers=None):
        """ helper to do API POST calls """

        all_headers = {"Content-Type": "application/json"}

        if headers:
            for header in headers:
                all_headers[header] = headers[header]

        response = requests.post(url=f"{self.api_url}/{endpoint}", headers=all_headers, data=data)
        code = response.status_code
        if 200 <= code < 300:
            logging.debug(f"API POST call: {self.api_url}/{endpoint} | {code}")
            raw = response.content
            return json.loads(raw)
        elif code >= 500:
            raise APIAuthException
        elif code == 400:
            raise BadMessageException
        else:
            logging.error(f"ERROR: Bad API POST call: {self.api_url}/{endpoint} | {code}")

    def epoch_to_datetime(self, epoch):
        """ make datetime object out of seconds from epoch time """

        return datetime.fromtimestamp(int(epoch))

    def get_groups(self):
        """ get all groups the signed-in user is subscribed to """

        all_groups = []

        params = {"token": self.api_token, "per_page": 10}
        tick = 1
        params['page'] = tick
  
        response = self._api_request("groups", params=params)

        while response['response'] is not None and response['response'] != []:
            all_groups += response['response']
            tick += 1
            params['page'] = tick
            response = self._api_request("groups", params=params)

        return all_groups

    def get_group_id(self, name):

        groups = self.get_groups()
        for group in groups:
            if group['name'] == name:
                return group['id']
        raise BadNameException

    def get_chat_id(self, name):

        chats = self.get_chats()
        for chat in chats:
            if chat['other_user']['name'] == name:
                return chat['other_user']['id']
        raise BadNameException

    def get_group_members(self, name=None, groupid=None):
        """ get list of members for a group """

        if name or groupid:
            groups = self.get_groups()
            for group in groups:
                if group['name'] == name or group['id'] == groupid:
                    return group['members']

    def get_user_id(self, members, name=None, nickname=None):
        """ given a list of group members, turn name/nickname into uuid that is consistent across all GroupMe chats """

        if name or nickname:
            for member in members:
                if member['name'] == name or member['nickname'] == nickname:
                    return member['user_id']

    def get_1page_messages(self, name=None, groupid=None, chatid=None, before=0, group=False, chat=False, filt=None):
        """ by default, messages return 20 at a time, so need to paginate to get all """

        if not name and not groupid and not chatid: return

        elif name and not groupid and group:
            groupid = self.get_group_id(name)

        elif name and not chatid and chat:
            chatid = self.get_chat_id(name)

        params = {"token": self.api_token, "limit": 100}
        
        if before:
            params["before_id"] = before
        
        if group:
            response = self._api_request(f"groups/{groupid}/messages", params=params)
        elif chat:
            if chatid:
                params["other_user_id"] = chatid
            response = self._api_request(f"direct_messages", params=params)
        else:
            return None

        if response is not None and response != []:
                
            if chat:
                if filt:
                    return filt(response['response']['direct_messages'])
                else:
                    return response['response']['direct_messages']
            else:
                if filt:
                    return filt(response['response']['direct_messages'])
                else:
                    return response['response']['messages']

    def get_all_messages(self, name=None, groupid=None, chatid=None, group=False, chat=False, filt=None):
        """ helper to paginate messages -- paginates on id of last message """

        if not name and not groupid and not chatid: return

        elif name and not groupid and group:
            groupid = self.get_group_id(name)

        elif name and not chatid and chat:
            chatid = self.get_chat_id(name)

        params = {"token": self.api_token, "limit": 100}
        all_messages = []

        some_messages = self.get_1page_messages(name=name, groupid=groupid, chatid=chatid, group=group, chat=chat)

        while some_messages is not None and len(some_messages) > 0:

            last_id = some_messages[-1]['id']

            if filt:
                some_messages = filt(some_messages)

            all_messages += some_messages
            some_messages = self.get_1page_messages(name=name, groupid=groupid, chatid=chatid, before=last_id, group=group, chat=chat)

        return all_messages

    def get_chats(self):
        """ get all direct messages for signed-in user """

        all_chats = []

        params = {"token": self.api_token, "per_page": 10}
        tick = 1
        params['page'] = tick

        response = self._api_request("chats", params=params)

        while response['response'] is not None and response['response'] != []:
            all_chats += response['response']
            tick += 1
            params['page'] = tick
            response = self._api_request("chats", params=params)

        return all_chats

    def filter_lambda(self, user=None, userid=None, text=None, dateOn=None, dateBefore=None, dateAfter=None):
        return lambda messages : self.filter_messages(messages, user=user, userid=userid, text=text, dateOn=dateOn,
                                                      dateBefore=dateBefore, dateAfter=dateAfter)

    def filter_string(self, user=None, userid=None, text=None, dateOn=None, dateBefore=None, dateAfter=None):
        outstr = "{Filter ="
        if user:
            outstr += f" user:{user}"
        if userid:
            outstr += f" userid:{userid}"
        if text:
            outstr += f" text:'{text}'"
        if dateOn:
            outstr += f" dateOn:{dateOn}"
        if dateAfter:
            outstr += f" dateAfter:{dateAfter}"
        if dateBefore:
            outstr += f" dateBefore:{dateBefore}"
        outstr += "}"
        return outstr

    def filter_messages(self, messages, user=None, userid=None, text=None, dateOn=None, dateBefore=None, dateAfter=None):
        """ filter messages by text, sender, date, etc. """

        filtered = []

        if userid is None and user is not None:
            try:
                groupid = messages[0]['group_id']
                group_members = self.get_group_members(groupid=groupid)
                userid = self.get_user_id(group_members, name=user, nickname=user)
            except: # Direct Messages
                userid = None

        for message in messages:
            passes = True
            raw_time = message['created_at']
            timestamp = self.epoch_to_datetime(raw_time).date()

            if userid:
                if 'sender_id' in message:
                    if message['sender_id'] != userid:
                        passes = False
                else:
                    passes = False

            elif user: # Direct Messages
                if 'name' in message:
                    if message['name'] != user:
                        passes = False
                else:
                    passes = False

            if text:
                if 'text' in message:
                    t = message['text']
                    if t is None: 
                        passes = False
                    else:
                        search = re.search(text, t)
                        if search is None:
                            passes = False
                else:
                    passes = False

            if dateOn:
                if timestamp != dateOn:
                    passes = False

            elif dateBefore and dateAfter:
                if (dateBefore - timestamp) < timedelta() or (timestamp - dateAfter) < timedelta():
                    passes = False

            elif dateBefore:
                # either before OR on this date
                if (dateBefore - timestamp) < timedelta():
                    passes = False

            elif dateAfter:
                # either on OR after this date
                if (timestamp - dateAfter) < timedelta():
                    passes = False

            if passes:
                filtered += [message]

        return filtered

    def send_message(self, text, name=None, groupid=None, chatid=None, group=False, chat=False):
        """ send message to specified group/chat """

        if len(text) > 1000:
            messages = self.split_message(text)
            for m in messages:
                self.send_message(m, name=name, groupid=groupid, chatid=chatid, group=group, chat=chat)
            return

        if not group and not chat:
            return

        elif group:

            data = {
                "message": {
                    "source_guid": f"{randint(1, 9999)}",
                    "text": text
                }
            }

            if not name and not groupid:
                return
            elif not groupid and name:
                groupid = self.get_group_id(name)

            try:
                response = self._api_request_post(f"groups/{groupid}/messages?token={self.api_token}", json.dumps(data))
                return response
            except BadMessageException:
                logging.error("GroupMe won't accept that message -- it may be too long or contain forbidden characters")

        elif chat:

            if not chatid and not name:
                return
            elif not chatid and name:
                chatid = self.get_chat_id(name)

            data = {
                "direct_message": {
                    "source_guid": f"{randint(1, 9999)}",
                    "recipient_id": chatid,
                    "text": text
                }
            }

            try:
                response = self._api_request_post(f"direct_messages?token={self.api_token}", json.dumps(data))
                return response
            except BadMessageException:
                logging.error("GroupMe won't accept that message -- it may be too long or contain forbidden characters")

    def split_message(self, m):
        """ split message into chunks if too long for GroupMe (max message len=1000 characters)"""
        
        maxlen = 920 # lets set this low because we'll re-add newlines and spaces that are cut
        out = []
        if "\n" in m:
            segments = m.split("\n")
            goodstr = ""
            for segment in segments:
                if len(segment) > maxlen:
                    segments2 = self.split_message(segment)
                    if len(goodstr) != 0:
                        out += [goodstr]
                    else:
                        for s in segments2:
                            out += [s]
                else:
                    if len(segment) + len(goodstr) <= maxlen:
                        goodstr += "\n" + segment
                    else:
                        out += [goodstr]
                        goodstr = ""
        else:
            if " " in m:
                segments = m.split(" ")
                goodstr = ""
                for segment in segments:
                    if len(segment) > maxlen:
                        segments2 = self.split_message(segment)
                        if len(goodstr) != 0:
                            out += [goodstr]
                        else:
                            for s in segments2:
                                out += [s]
                    else:
                        if len(segment) + len(goodstr) <= maxlen:
                            goodstr += " " + segment
                        else:
                            out += [goodstr]
                            goodstr = ""
            else:
                mlen = len(m)
                num_segs = ceil(mlen/1000.)
                start = 0
                end = 999
                tick = 0
                while tick < num_segs:
                    seg = m[start:end]
                    start += 999
                    end += 999
                    tick += 1
                    out += [seg]
        return out

