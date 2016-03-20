#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''rst

zbx2slack-alert-notify.py
================================

Zabbix Alert Notification Script for Slack. by pure python.

- Can use by "Remote command". But can't use by "Media type".
- if use by python2.6- (like CentOS6.x), install ``argparse`` module.  ex, 

  .. sourcecode:: sh

     $  sudo yum install python-argparse


Install
-----------------------

(TBC)


set this script your zabbix server.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

put file and add mode to execute.


Usage
-----------------------


In the WebUI of your zabbix server.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. [Configureation]
2. [Action]
3. Choose 'Trigger' at Event source and Create Action.
4. if "Recovery message" checked, Uncheck the checkbox.
5. At [Conditions] tab, add ``Trigger value = OK`` to Conditions.
    - ``Trigger value = OK`` and ``Trigger value = PROBLEM`` are in Conditions.
6. At [Operations] tab, add ``Remote Command``
    - Operation type : Remote Command
    - Targeta list   : any host (ex. Current host)
    - Type           : Custom script
    - Execute on     : Zabbix server
    - Commands:

      .. sourcecode:: sh

        /path/to/zbx2slack-alert-notify.py \
          --zabbix-server-url "http://zabbix.example.com/zabbix" \
          --slack-botname "Zabbix Alert" \
          --slack-incoming-webhook-url "https://hooks.slack.com/services/xxxxxxxxx/xxxxxxxxx/...." \
          --trigger-id "{TRIGGER.ID}" \
          --trigger-name "{TRIGGER.NAME}" \
          --trigger-status "{TRIGER.STATUS}" \
          --trigger-severity "{TRIGGER.SEVERITY}" \
          --triger-url "{TRIGGER.URL}" \
          --event-id "{EVENT.ID}" \
          --item "{HOST.NAME1}|{ITEM.NAME1}|{ITEM.KEY1}|{ITEM.VALUE1}" \
          --item "{HOST.NAME2}|{ITEM.NAME2}|{ITEM.KEY2}|{ITEM.VALUE2}" \
          --item "{HOST.NAME3}|{ITEM.NAME3}|{ITEM.KEY3}|{ITEM.VALUE3}"


LICENSE
------------------------

MIT


AUTHOR
------------------------
Kei Iwasaki <me@laughk.org>


'''

import os, sys
import re
import argparse

try:
    '''for python3.x'''
    from urllib import request
except ImportError:
    '''for python2.x'''
    import urllib2 as request

try:
    import json
except ImportError:
    '''for python2.4'''
    import simplejson as json


class noticeInfo(object):
    def __init__(self, args):
        self.slack_botname     = args.slack_botname
        self.zabbix_server_url = args.zabbix_server_url

        self.trigger_id        = args.trigger_id
        self.trigger_name      = args.trigger_name
        self.trigger_status    = args.trigger_status
        self.trigger_severity  = args.trigger_severity
        self.event_id          = args.event_id
        self._items            = args.item

        self.trigger_url       = self._gen_trigger_url()
        self.attachment_color  = self._gen_attachment_color()
        self.pretext           = self._gen_pretext()
        self.attachment_fields = self._gen_attachment_fields()
        self.graph_url         = self._gen_graph_url()

        self._payload = self._gen_payload()

    def _gen_trigger_url(self):
        '''
         generate and return url of Alert Tigger infomation.

         ex.
            http://zabbix.example.com/zabbix/tr_events.php?triggerid=00000&eventid=00

        '''
        _trigger_url = '{0}/tr_events.php?triggerid={1}&eventid={2}'.format(
                self.zabbix_server_url,
                self.trigger_id,
                self.event_id)
        return _trigger_url

    def _gen_pretext(self):
        '''
        generate and return string for alert pretext, by the state.
        '''

        if self.trigger_status == 'PROBLEM':
            return ':boom: A problem occured '
        elif self.trigger_status == 'OK':
            return ':white_check_mark: A problem recovered :+1:'
        else:
            return ':ghost::ghost: UNKNOWN :ghost::ghost:'

    def _gen_attachment_color(self):
        '''
        generate and return attchment color by the state.
        ref. https://api.slack.com/docs/attachments#color
        '''
        if self.trigger_status == 'PROBLEM':
            return 'danger'
        elif self.trigger_status == 'OK':
            return 'good'
        else:
            return 'warning'

    def _gen_attachment_fields(self):

        '''
        generate and return attchment color by the state.
        ref. https://api.slack.com/docs/attachments#color
        '''
        _fileds = []

        for _item in self._items:

            _item_list = _item.split('|')

            if _item_list[0] == r'*UNKNOWN*':
                continue

            _fileds.append({
                    'title': '{0} - **{1}**'.format(*_item_list),
                    'value': '"{2}" is "{3}"'.format(*_item_list)
                    })

        return _fileds


    def _gen_payload(self):
        '''
        generate and return attchment fields by the state.
        ref. https://api.slack.com/docs/attachments#fields
        '''

        _payload = json.dumps({
            'username': self.slack_botname,
            'attachments': [{
                'color': self.attachment_color,
                'fields': self.attachment_fields,
                'title': self.trigger_name,
                'title_link': self.trigger_url,
                'pretext': self.pretext,
                'image_url': self.graph_url
            }]
        })

        if isinstance(_payload, str):
            return _payload.encode('utf-8')

        return _payload

    @property
    def payload(self):
        return self._payload


def alert_to_slack(payload, slack_incoming_webhook):

    request_header = {'Content-Type': 'application/json'}
    req = request.Request(
            slack_incoming_webhook,
            payload,
            request_header)
    request.urlopen(req)


def script_versoin():
    return '{0} 0.0.1'.format(sys.argv[0])


def main():


    '''
    Environment Check and merge to SCRIPT_ENV
    -------------------------------

    {{{
    '''
    SCRIPT_ENV = {
        'ZABBIX_SERVER_URL': '',
        'INCOMING_WEBHOOK_URL': ''
    }

    for env in SCRIPT_ENV.keys():
        if env in os.environ.keys():
            SCRIPT_ENV[env] = os.environ[env]
    '''
    ------------------------------
    }}}
    '''


    '''
    Analyze options
    -------------------------------

    ex.

        $ zbx2slack-alert-notify.py \
            --zabbix-server-url "http://zabbix.example.com/zabbix" \
            --slack-botname "Zabbix Alert" \
            --slack-incoming-webhook-url "https://hooks.slack.com/services/xxxxxxxxx/xxxxxxxxx/...." \
            --trigger-id "{TRIGGER.ID}" \
            --trigger-name "{TRIGGER.NAME}" \
            --trigger-status "{TRIGGER.STATUS}" \
            --trigger-severity "{TRIGGER.SEVERITY}" \
            --event-id "{EVENT.ID}" \
            --item "{HOST.NAME1}|{ITEM.NAME1}|{ITEM.KEY1}|{ITEM.VALUE1}" \
            --item "{HOST.NAME2}|{ITEM.NAME2}|{ITEM.KEY2}|{ITEM.VALUE2}" \
            --item "{HOST.NAME3}|{ITEM.NAME3}|{ITEM.KEY3}|{ITEM.VALUE3}"

    {{{

    '''

    parser = argparse.ArgumentParser(
            description='Zabbix Alert Notification Script for Slack.')

    parser.add_argument('--zabbix-server-url',
            default=SCRIPT_ENV['ZABBIX_SERVER_URL'],
            help='Your Zabbix server URL (Default: "")'.format(SCRIPT_ENV['ZABBIX_SERVER_URL']),
            type=str)

    parser.add_argument('--slack-botname', default='Zabbix Alert',
            type=str, help='Slack Bot name (Default: "Zabbix Alert")')
    parser.add_argument('--slack-incoming-webhook-url',
            default=SCRIPT_ENV['INCOMING_WEBHOOK_URL'],
            help='Slack Bot name (Default: "{0}")'.format(SCRIPT_ENV['INCOMING_WEBHOOK_URL']),
            type=str)

    parser.add_argument('--trigger-id',
            type=int, help='Set Zabbix Macro "{TRIGGER.ID}"')
    parser.add_argument('--trigger-name',
            type=str, help='Set Zabbix Macro "{TRIGGER.NAME}"')
    parser.add_argument('--trigger-status',
            type=str, help='Set Zabbix Macro "{TRIGGER.STATUS}"' )
    parser.add_argument('--trigger-severity',
            type=str, help='Set Zabbix Macro "{TRIGGER.SEVERITY}"')
    parser.add_argument('--event-id',
            type=int, help='Set Zabbix Macro "{EVENT.ID}"')
    parser.add_argument('--item', action='append',
            type=str, help='Set Zabbix Macro formated by'
                           '"{HOST.NAME1}|{ITEM.NAME1}|{ITEM.KEY1}|{ITEM.VALUE1}"')

    parser.add_argument('--version', action='version',
            version=script_versoin())

    args = parser.parse_args()

    '''
    --------------------------------
    }}}
    '''

    notice = noticeInfo(args)
    alert_to_slack(
            notice.payload,
            args.slack_incoming_webhook_url)


if __name__ == '__main__':
    main()