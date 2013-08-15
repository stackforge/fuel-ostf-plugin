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


from sqlalchemy.orm import object_mapper

from ostf_adapter.storage import models

def copy_test(test, test_run, predefined_tests):
        new_test = models.Test()
        mapper = object_mapper(test)
        primary_keys = set([col.key for col in mapper.primary_key])
        for column in mapper.iterate_properties:
            if column.key not in primary_keys:
                setattr(new_test, column.key, getattr(test, column.key))
        new_test.test_run_id = test_run.id
        if predefined_tests and new_test.name not in predefined_tests:
            new_test.status = 'disabled'
        else:
            new_test.status = 'wait_running'
        return new_test
