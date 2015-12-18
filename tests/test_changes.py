from cliquet.tests.support import unittest

from . import BaseWebTest


SAMPLE_RECORD = {'data': {'dev-edition': True}}


class UpdateChangesTest(BaseWebTest, unittest.TestCase):
    changes_uri = '/buckets/monitor/collections/changes/records'
    records_uri = '/buckets/blocklists/collections/certificates/records'

    def setUp(self):
        super(UpdateChangesTest, self).setUp()
        # XXX: should happen during Listener instanciation or includeme()
        self.app.post_json(self.records_uri,
                           SAMPLE_RECORD,
                           headers=self.headers)

    def test_a_change_record_is_updated_per_bucket_collection(self):
        resp = self.app.get(self.changes_uri, headers=self.headers)
        change_record = resp.json['data'][0]

        self.app.post_json(self.records_uri, SAMPLE_RECORD,
                           headers=self.headers)

        resp = self.app.get(self.changes_uri, headers=self.headers)
        after = resp.json['data'][0]
        self.assertEqual(change_record['id'], after['id'])
        self.assertNotEqual(change_record['last_modified'],
                            after['last_modified'])

    def test_changes_bucket_and_collection_are_created_automatically(self):
        self.app.delete('/buckets/monitor', headers=self.headers)
        self.app.post_json(self.records_uri, SAMPLE_RECORD,
                           headers=self.headers)
        self.app.get(self.changes_uri, headers=self.headers, status=200)

    def test_only_collections_specified_in_settings_are_monitored(self):
        resp = self.app.get(self.changes_uri, headers=self.headers)
        change_record = resp.json['data'][0]
        records_uri = '/buckets/default/collections/certificates/records'

        self.app.post_json(records_uri, SAMPLE_RECORD,
                           headers=self.headers)

        resp = self.app.get(self.changes_uri, headers=self.headers)
        after = resp.json['data'][0]
        self.assertEqual(change_record['id'], after['id'])
        self.assertEqual(change_record['last_modified'],
                         after['last_modified'])

    def test_changes_bucket_last_modified_is_not_updated(self):
        resp = self.app.get('/buckets/monitor', headers=self.headers)
        before = resp.json['data']['last_modified']

        self.app.post_json(self.records_uri, SAMPLE_RECORD,
                           headers=self.headers)

        resp = self.app.get('/buckets/monitor', headers=self.headers)
        after = resp.json['data']['last_modified']
        self.assertEqual(before, after)

    def test_changes_collection_last_modified_is_not_updated(self):
        resp = self.app.get('/buckets/monitor/collections/changes',
                            headers=self.headers)
        before = resp.json['data']['last_modified']

        self.app.post_json(self.records_uri, SAMPLE_RECORD,
                           headers=self.headers)

        resp = self.app.get('/buckets/monitor/collections/changes',
                            headers=self.headers)
        after = resp.json['data']['last_modified']
        self.assertEqual(before, after)

    def test_change_record_has_last_modified_of_collection_of_records(self):
        resp = self.app.post_json(self.records_uri, SAMPLE_RECORD,
                                  headers=self.headers)
        last_modified = resp.json['data']['last_modified']
        resp = self.app.get(self.changes_uri, headers=self.headers)
        change_last_modified = resp.json['data'][0]['last_modified']
        self.assertEqual(last_modified, change_last_modified)

    def test_record_with_old_timestamp_does_update_changes(self):
        resp = self.app.post_json(self.records_uri, SAMPLE_RECORD,
                                  headers=self.headers)
        old_record = SAMPLE_RECORD.copy()
        old_record['data']['last_modified'] = 42
        self.app.post_json(self.records_uri, old_record, headers=self.headers)

        resp = self.app.get(self.changes_uri, headers=self.headers)
        change_last_modified = resp.json['data'][0]['last_modified']
        self.assertNotEqual(change_last_modified, 42)

    def test_change_record_has_server_host_attribute(self):
        self.app.post_json(self.records_uri, SAMPLE_RECORD,
                           headers=self.headers)

        resp = self.app.get(self.changes_uri, headers=self.headers)
        change = resp.json['data'][0]
        self.assertEqual(change['host'], 'www.kinto-storage.org')

    def test_change_record_has_bucket_and_collection_attributes(self):
        self.app.post_json(self.records_uri, SAMPLE_RECORD,
                           headers=self.headers)

        resp = self.app.get(self.changes_uri, headers=self.headers)
        change = resp.json['data'][0]
        self.assertEqual(change['bucket'], 'blocklists')
        self.assertEqual(change['collection'], 'certificates')


class UpdateConfiguredChangesTest(BaseWebTest, unittest.TestCase):
    config = 'mozilla.ini'
    changes_uri = '/buckets/mozilla/collections/updates/records'
    records_uri = '/buckets/blocklists/collections/certificates/records'

    def setUp(self):
        super(UpdateConfiguredChangesTest, self).setUp()
        # XXX: should happen during Listener instanciation or includeme()
        self.app.post_json(self.records_uri,
                           SAMPLE_RECORD,
                           headers=self.headers)

    def test_changes_bucket_and_collection_can_be_specified_in_settings(self):
        resp = self.app.get(self.changes_uri, headers=self.headers)
        self.assertEquals(len(resp.json['data']), 1)

    def test_changes_records_permissions_can_be_specified_in_settings(self):
        resp = self.app.get('/buckets/mozilla/collections/updates',
                            headers=self.headers)
        self.assertIn('user:natim', resp.json['permissions']['read'])