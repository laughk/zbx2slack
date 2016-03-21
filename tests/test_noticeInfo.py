import unittest
import json

try:
    import nose.tools
    nose.tools.assert_equal.__self__.maxDiff = None
except ImportError:
    from unittest import TestCase
    TestCase.maxDiff = None

zbx2slack = __import__('zbx2slack-alert-notify')


class argClass:
    pass


class testNoticeInfo(unittest.TestCase):


    def setUp(self):
        self.maxDiff = None

        self._args = argClass()
        self._args.slack_botname     = 'Zabbix Alert'
        self._args.zabbix_server_url = 'http://zabbix.example.com/zabbix'
        self._args.slack_incoming_webhook_url = 'https://hooks.slack.com/services/xxxxxxxxx/xxxxxxxxx/....'
        self._args.trigger_id        = '{TRIGGER.ID}'
        self._args.trigger_name      = '{TRIGGER.NAME}'
        self._args.trigger_status    = '{TRIGGER.STATUS}'
        self._args.trigger_severity  = '{TRIGGER.SEVERITY}'
        self._args.event_id          = '{EVENT.ID}'
        self._args.item              = [
            '{HOST.NAME1}|{ITEM.NAME1}|{ITEM.KEY1}|{ITEM.VALUE1}',
            '{HOST.NAME2}|{ITEM.NAME2}|{ITEM.KEY2}|{ITEM.VALUE2}',
            '*UNKNOWN*|*UNKNOWN*|*UNKNOWN*|*UNKNOWN*'
        ]

    def setDown(self):
        pass

    def test__gen_trigger(self):
        test_args = self._args
        _noticeInfo = zbx2slack.noticeInfo(test_args)

        expected = r'http://zabbix.example.com/zabbix/tr_events.php?triggerid={TRIGGER.ID}&eventid={EVENT.ID}'
        result = _noticeInfo._gen_trigger_url()
        self.assertEqual(result, expected)

    def test__gen_pretext(self):
        test_args = self._args

        test_case = {
            'PROBLEM': ':boom: A problem occured ',
            'OK': ':white_check_mark: A problem recovered :+1:',
            'other': ':ghost::ghost: UNKNOWN :ghost::ghost:'
        }

        for status in test_case.keys():
            test_args.trigger_status = status
            _noticeInfo = zbx2slack.noticeInfo(test_args)

            expected = test_case[status]
            result = _noticeInfo._gen_pretext()
            self.assertEqual(result, expected)


    def test__gen_attachment_color(self):
        test_args = self._args

        test_case = {
            'PROBLEM': 'danger',
            'OK': 'good',
            'other': 'warning'
        }

        for status in test_case.keys():
            test_args.trigger_status = status
            _noticeInfo = zbx2slack.noticeInfo(test_args)

            expected = test_case[status]
            result = _noticeInfo._gen_attachment_color()
            self.assertEqual(result, expected)


    def test__gen_attachment_fields(self):
        test_args = self._args
        _noticeInfo = zbx2slack.noticeInfo(test_args)

        expected = [
            {
                'title': r'{HOST.NAME1} - **{ITEM.NAME1}**',
                'value': r'"{ITEM.KEY1}" is "{ITEM.VALUE1}"'
            },
            {
                'title': r'{HOST.NAME2} - **{ITEM.NAME2}**',
                'value': r'"{ITEM.KEY2}" is "{ITEM.VALUE2}"'
            }
        ]
        result = _noticeInfo._gen_attachment_fields()
        self.assertEqual(result, expected)


    def test__gen_payload(self):
        """WIP"""
        test_args = self._args
        _noticeInfo = zbx2slack.noticeInfo(test_args)

        expected = {
                'username': 'Zabbix Alert',
                'attachments': [{
                    'color': 'warning',
                    'title': '{TRIGGER.NAME}',
                    'title_link': r'http://zabbix.example.com/zabbix/tr_events.php?triggerid={TRIGGER.ID}&eventid={EVENT.ID}',
                    'pretext': ':ghost::ghost: UNKNOWN :ghost::ghost:',
                    'fields': [
                            {
                                'title': r'{HOST.NAME1} - **{ITEM.NAME1}**',
                                'value': r'"{ITEM.KEY1}" is "{ITEM.VALUE1}"'
                            },
                            {   'title': r'{HOST.NAME2} - **{ITEM.NAME2}**',
                                'value': r'"{ITEM.KEY2}" is "{ITEM.VALUE2}"'
                            }
                        ]
                    }]
                }

        result = _noticeInfo.payload.decode('utf-8')
        result_dict = json.loads(result)
        self.assertDictEqual(result, expected)


    def test_payload(self):
        test_args = self._args
        _noticeInfo = zbx2slack.noticeInfo(test_args)
        result = _noticeInfo.payload

        self.assertTrue(isinstance(result, bytes))



if __name__ == '__main__':
    unittest.main(verbosity=3)

