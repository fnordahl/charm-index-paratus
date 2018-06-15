# Copyright 2018 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import mock
from unittest.mock import patch

# Mock out charmhelpers so that we can test without it.
import charms_openstack.test_mocks as ch
ch.mock_charmhelpers()

import charms.reactive  # noqa E402

# Mock out reactive decorators prior to importing reactive handler bits
dec_mock = mock.MagicMock()
dec_mock.return_value = lambda x: x
charms.reactive.hook = dec_mock
charms.reactive.when = dec_mock
charms.reactive.when_not = dec_mock

import reactive.index_paratus_handlers as handlers  # noqa E402
import unit_tests.test_utils  # noqa E402


class TestIndexParatusHandlers(unit_tests.test_utils.CharmTestCase):

    def setUp(self):
        super(TestIndexParatusHandlers, self).setUp()
        self.obj = handlers
        self.patches = [
            'pymysql',
        ]
        self.patch_all()

    def test_waiting(self):
        handlers.waiting()
        ch.charmhelpers.core.hookenv.status_set.assert_called_with(
            'waiting', 'Waiting for shared-db relation...')

    def test_configure_database(self):
        database = mock.MagicMock()
        handlers.configure_database(database)
        database.configure.assert_called_once_with('index-paratus',
                                                   'index-paratus')

    @patch.object(handlers, 'stop')
    @patch.object(handlers.reactive, 'is_flag_set')
    def test_probe_database(self, mock_is_flag_set, mock_stop):
        database = mock.MagicMock()
        mock_is_flag_set.return_value = False
        mock_stop.return_value = [False, False, True]
        handlers.probe_database(database)
        self.assertTrue(mock_is_flag_set.called)
        self.assertTrue(self.pymysql.connect.called)
