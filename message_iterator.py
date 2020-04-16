from groupme import GroupMe

class MessageIterator:

    def __init__(self, chat=False, group=False, name=None, filt=None, last=0):

        self.groupme = GroupMe()

        self.chatid = None
        self.groupid = None
        self.last_mess_id = last
        self.filt = filt
        
        if chat:
            self.chatid = self.groupme.get_chat_id(name)
        elif group:
            self.groupid = self.groupme.get_group_id(name)

    def next(self):

        if self.chatid:
            page = self.groupme.get_1page_messages(chatid=self.chatid, before=self.last_mess_id, chat=True)
            if page is not None and len(page) > 0:
                self.last_mess_id = page[-1]['id']
                return page

        elif self.groupid:
            page = self.groupme.get_1page_messages(groupid=self.groupid, before=self.last_mess_id, group=True)
            if page is not None and len(page) > 0:
                self.last_mess_id = page[-1]['id']
                return page

    def has_next(self):

        if self.chatid:
            page = self.groupme.get_1page_messages(chatid=self.chatid, before=self.last_mess_id, chat=True)
            if page is not None and len(page) > 0:
                return True
            else:
                return False

        if self.groupid:
            page = self.groupme.get_1page_messages(groupid=self.groupid, before=self.last_mess_id, group=True)
            if page is not None and len(page) > 0:
                return True
            else:
                return False


