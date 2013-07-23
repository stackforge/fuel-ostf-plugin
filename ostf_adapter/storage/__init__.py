#    Copyright 2013 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from ostf_adapter.storage import sql_storage
import logging
from pecan import conf

log = logging.getLogger(__name__)


DEFAULT_DBPATH = 'postgresql+psycopg2://postgres:demo@localhost/testing_adapter'

def get_storage(dbpath=None):
    log.info('GET STORAGE FOR - %s' % conf.get('dbpath', '') or DEFAULT_DBPATH)
    return sql_storage.SqlStorage(conf.get('dbpath', '') or DEFAULT_DBPATH)