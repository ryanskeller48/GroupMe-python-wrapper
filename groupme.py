import logging
import json
import os
import re
import requests

from datetime import datetime, date, timedelta
from math import ceil
from random import randint
from typing import Callable, Dict, List


logging.basicConfig(level=logging.INFO)
logging.getLogger(__name__)

# TODO: typing
class APIAuthException(Exception):

    def __init__(self, message="User is not authorized.  " +
                               "Set the GROUPME_TOKEN environment variable with a valid token and try again."):
        self.message = message
        super().__init__(self.message)


class BadNameException(Exception):

    def __init__(self, 
                 message="Could not find the group/user associated with the name '%s' provided.  " +
                         "Check spelling and try again.",
                 username=""):
        self.message = message % username 
        super().__init__(self.message)


class BadMessageException(Exception):

    def __init__(self, message="Could not send message, there may be forbidden characters."):
        self.message = message
        super().__init__(self.message)


class BadDateStringException(Exception):

    def __init__(self, message="Invalid date string entered.  " +
                 "Valid format: DD/MM/YYYY (use leading zeroes for single digits)."):
        self.message = message
        super().__init__(self.message)


class GroupMe:

    def __init__(self, api_token=os.getenv('GROUPME_TOKEN')):
        self.api_url = "https://api.groupme.com/v3"
        if api_token is None:
            raise APIAuthException("No auth token provided, please set the GROUPME_TOKEN environment variable.")
        self.api_token = api_token


    def _api_request(self, endpoint, params=None):
        """ Helper to do API GET calls. """
        
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
        elif code >= 400:
            raise APIAuthException
        else:
            logging.error(f"ERROR: Bad API call: {self.api_url}/{endpoint} | {code}")


    def _api_request_post(self, endpoint, data, headers=None):
        """ Helper to do API POST calls. """

        all_headers = {"Content-Type": "application/json"}

        if headers:  # Add additional headers to the default
            for header in headers:
                all_headers[header] = headers[header]

        response = requests.post(url=f"{self.api_url}/{endpoint}", headers=all_headers, data=data)
        code = response.status_code
        logging.debug(f"API POST call: {self.api_url}/{endpoint} | {code}")
        if 200 <= code < 300:
            raw = response.content
            return json.loads(raw)
        elif code > 400:
            raise APIAuthException
        elif code == 400:
            raise BadMessageException
        else:
            logging.error(f"ERROR: Bad API POST call: {self.api_url}/{endpoint} | {code}")


    def epoch_to_datetime(self, epoch):
        """ Make datetime object out of seconds from epoch time. """

        return datetime.fromtimestamp(int(epoch))


    def get_groups(self):
        """ Get all groups the signed-in user is subscribed to. """

        all_groups = []

        params = {"token": self.api_token, "per_page": 10}
        tick = 1
        params['page'] = tick
  
        response = self._api_request("groups", params=params)

        while response['response'] is not None and response['response'] != []:
            all_groups += response['response']
            tick += 1  # get next page of groups
            params['page'] = tick
            response = self._api_request("groups", params=params)

        return all_groups


    def get_group_id(self, name):
        """ Get internal ID for group chat with given `name`. """

        groups = self.get_groups()
        for group in groups:
            if group['name'] == name:
                return group['id']
        raise BadNameException(username=name)  # We've parsed all group names and didn't find a match


    def get_chat_id(self, username):
        """ Get internal ID for direct message with given user `username`. """

        chats = self.get_chats()
        for chat in chats:
            if chat['other_user']['name'] == username:
                return chat['other_user']['id']
        raise BadNameException(username=username)  # We've parsed all group names and didn't find a match


    def get_group_members(self, name=None, groupid=None):
        """ Get list of members for a given group via group `name` or internal `groupid`. """

        if name or groupid:
            groups = self.get_groups()
            for group in groups:
                if group['name'] == name or group['id'] == groupid:
                    return group['members']
        raise BadNameException(username=name)  # We've parsed all group names and didn't find a match
            

    def get_user_id(self, members, name=None, nickname=None):
        """ Given a list of group members, turn name/nickname into uuid that is consistent across all GroupMe chats. """

        if name or nickname:
            for member in members:
                if member['name'] == name or member['nickname'] == nickname:
                    return member['user_id']


    def filter_response(self, response, filt: Callable = None):
        """ Helper to filter responses as the same code is used a couple times. """

        if response is not None and response != []:

            resp_content = response['response']['direct_messages'] if 'direct_messages' in response['response'] \
                           else response['response']['messages']
            if resp_content == []:
                return None
            if filt:
                return filt(resp_content)
            else:
                return resp_content
        

    def get_1page_group(self, groupid: int, before: int = 0, filt: Callable = None) -> List[str]:
        """ Method for getting 1 page of messages from a group message. """

        # Set params for API GET call based on input
        params = {"token": self.api_token, "limit": 100}
        if before:
            params["before_id"] = before

        response = self._api_request(f"groups/{groupid}/messages", params=params)
        return self.filter_response(response, filt=filt)


    def get_1page_chat(self, chatid: int, before: int = 0, filt: Callable = None) -> List[str]:
        """ Method for getting 1 page of messages from a direct message. """

        # Set params for API GET call based on input
        params = {"token": self.api_token, "limit": 100}
        if before:
            params["before_id"] = before
        params["other_user_id"] = chatid

        response = self._api_request(f"direct_messages", params=params)
        return self.filter_response(response, filt=filt)

    
    def get_1page_messages(self,
                           name=None,
                           groupid=None,
                           chatid=None,
                           before=0,
                           group=False,
                           chat=False,
                           filt=None) -> List[str]:
        """ By default, messages return 20 at a time, so need to paginate to get all messages. """

        # Need a group/user `name` or ID in order to get messages
        if not name and not groupid and not chatid:
            raise BadNameException(message="Must provide the name of a group message / direct message!")

        # Convert string group/user `name` to internal ID for ease of use
        if group:
            if name and not groupid and group:
                groupid = self.get_group_id(name)
            return self.get_1page_group(groupid, before=before, filt=filt)
        elif chat:
            if name and not chatid and chat:
                chatid = self.get_chat_id(name)
            return self.get_1page_chat(chatid, before=before, filt=filt)


    def get_all_messages(self, name=None, groupid=None, chatid=None, group=False, chat=False, filt=None):
        """ Helper to paginate messages -- paginates on id of last message """

        # Need a group/user `name` or ID in order to get messages
        if not name and not groupid and not chatid:
            raise BadNameException(message="Must provide the name of a group message / direct message!")

        # Convert string group/user `name` to internal ID for ease of use
        if name and not groupid and group:
            groupid = self.get_group_id(name)
        if name and not chatid and chat:
            chatid = self.get_chat_id(name)

        all_messages = []
        some_messages = self.get_1page_messages(name=name, groupid=groupid, chatid=chatid, group=group, chat=chat)

        while some_messages is not None and len(some_messages) > 0:

            # Grab this before we filter out any messages so we don't poll the same messages twice
            last_id = some_messages[-1]['id']

            if filt:
                some_messages = filt(some_messages)
            all_messages += some_messages
            # Get next page of messages based on the ID we grabbed
            some_messages = self.get_1page_messages(name=name, groupid=groupid, chatid=chatid, before=last_id, group=group, chat=chat)

        return all_messages


    def get_chats(self):
        """ Get all direct messages for signed-in user. """

        all_chats = []

        params = {"token": self.api_token, "per_page": 10}
        tick = 1
        params['page'] = tick

        # Paginate responses
        response = self._api_request("chats", params=params)
        while response['response'] is not None and response['response'] != []:
            all_chats += response['response']
            tick += 1
            params['page'] = tick
            response = self._api_request("chats", params=params)

        return all_chats


    def send_dm(self, text: str, name: str) -> Dict:
        """ Helper to send a message to a DM. """

        chatid = self.get_chat_id(name)
        data = {
            "direct_message": {
                "source_guid": f"{randint(1, 9999)}",
                "recipient_id": chatid,
                "text": text
            }
        }
        
        return self._api_request_post(f"direct_messages?token={self.api_token}", json.dumps(data))


    def send_group_message(self, text: str, name: str) -> Dict:
        """ Helper to send a message to a group. """

        groupid = self.get_group_id(name)
        data = {
            "message": {
                "source_guid": f"{randint(1, 9999)}",
                "text": text
            }
        }

        return self._api_request_post(f"groups/{groupid}/messages?token={self.api_token}", json.dumps(data))

    
    def send_message(self, text, name=None, groupid=None, chatid=None, group=False, chat=False):
        """ Send message to specified group/chat. """
        # TODO: split into group/chat functions

        # If message is >1000chars, split into manageable chunks and call send_message() recursively on chunks.
        if len(text) > 1000:
            messages = self.split_message(text)
            for m in messages:
                self.send_message(m, name=name, groupid=groupid, chatid=chatid, group=group, chat=chat)
            return

        # Need a group/user `name` or ID in order to send message
        if not group and not chat:
            return

        elif group:
            # return self.send_group_message(data, groupid)

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
            

            response = self._api_request_post(f"groups/{groupid}/messages?token={self.api_token}", json.dumps(data))
            return response

        elif chat:
            # return self.send_dm(data, groupid)

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
            

            response = self._api_request_post(f"direct_messages?token={self.api_token}", json.dumps(data))
            return response


    def split_message(self, m):
        # TODO: comment / make more readable
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
