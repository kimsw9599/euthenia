# -*- encoding: utf-8 -*-


from slack import WebClient
import os
from slack import RTMClient
from slack.errors import SlackApiError


class SlackUtil:
    def __init__(self):
        self.slack_token = self.get_slack_token()
        self.slack_m = self.set_slack(self.slack_token)

    def set_slacker(self, token):
        #    slack_m = Slacker(token)
        slack_m = WebClient(token)
        return slack_m

    def get_slack_token(self):
        f = open("./slack_token", 'r')
        token = f.readline()
        print(token)
        f.close()

        return token.strip()

    def send_slack_alart_mesg(self, channel_name, current_usd, last_usd):
        if self.slack_m is not None:
            message = "<@sunfun>  Last $1:{} => Current $1:{}".format(str(last_usd), str(current_usd))
            attachments = [{
                "color": "#ff0000",
                "title": "Check Currency",
                "text": message
            }]
            #        msg=slack_m.chat.post_message(channel_name, message, username="QuantSun")
            msg = self.slack_m.chat_postMessage(
                                   channel=channel_name
                                   , username=user_name
                                   , icon_emoji=":dart:"
                                   , attachments=attachments)
            print("---------")
            print(msg)
        else:
            print("??????")

    def send_slack_info_mesg(self, channel_name, current_usd, last_usd):
        if self.slack_m is not None:
            message = "Last $1:{} => Current $1:{}".format(str(last_usd), str(current_usd))
            msg = self.slack_m.chat_postMessage(
                                   channel=channel_name,
                                   username=user_name, icon_emoji=":dart:", text=message)
            # msg = slack_m.chat.post_message(channel_name, message, username="QuantSun")
            print(msg)
        else:
            print("??????")


class RTMSlackUtil:
    def __init__(self):
        self.rtm_client = RTMClient(token=self.get_slack_token(), connect_method='rtm.start')

    def get_slack_token(self):
        f = open("./slack_token", 'r')
        token = f.readline()
        print(token)
        f.close()

        return token.strip()

    def start(self):
        self.rtm_client.start()


