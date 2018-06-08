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
import signal

import charmhelpers.core as ch_core
import charms.reactive as reactive
import pymysql


def timeout_handler(signum, frame):
    raise TimeoutError


@reactive.when_not('shared-db.connected')
@reactive.when_not('shared-db.available')
@reactive.when_not('update-status')
def waiting():
    ch_core.hookenv.status_set('waiting', 'Waiting for shared-db relation...')


@reactive.when('shared-db.connected')
def configure_database(database):
    ch_core.hookenv.status_set('maintenance', 'Initializing database...')
    database.configure('index-paratus', 'index-paratus')
    reactive.clear_flag('shared-db.connected')


@reactive.when('shared-db.available')
@reactive.when_not('index-paratus.probed')
def probe_database(database):
    if reactive.is_flag_set('index-paratus.probed'):
        return
    reactive.set_flag('index-paratus.probed')
    ch_core.hookenv.status_set('maintenance', 'Connecting to database...')
    ch_core.hookenv.log(
        'Connecting to database pymysql.connect(host="{}", '
        'user="{}", '
        'password="xXx", '
        'database="{}")'
        .format(database.db_host(), database.username(),
                database.database()),
        level=ch_core.hookenv.INFO,
    )
    timeout = 600
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    try:
        conn = pymysql.connect(host=database.db_host(),
                               user=database.username(),
                               password=database.password(),
                               database=database.database())
        cur = conn.cursor()
        ch_core.hookenv.status_set('maintenance', 'Probing...')

        i = 0
        s = 0
        spinner = ['\\', '|', '/', '-']
        while True:
            cur.execute("SELECT 1")
            i += 1
            if not i % 20000:
                s += 1
                if s >= len(spinner):
                    s = 0
                throbber = spinner[s]
                ch_core.hookenv.status_set('maintenance',
                                           'Probing ({})...'
                                           .format(throbber))
        cur.close()
        conn.close()
    except (ConnectionRefusedError, pymysql.err.InternalError,
            pymysql.err.OperationalError) as e:
        ch_core.hookenv.status_set('blocked', e.args[1])
    except (TimeoutError):
        ch_core.hookenv.log('Probe stopped after running successfully for {}s'
                            .format(timeout), level=ch_core.hookenv.INFO)
        ch_core.hookenv.status_set('active', 'Unit ready, probe successfull!')
