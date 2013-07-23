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

__author__ = 'ekonstantinov'
from json import loads, dumps


def main():
    with open('ostf_adapter/commands.json', 'rw+') as commands:
        data = loads(commands.read())
        for item in data:
            if data[item].get('argv'):
                if "--with-xunit" not in data[item]['argv']:
                    data[item]['argv'].append("--with-xunit")
            else:
                data[item]['argv'] = ["--with-xunit", ]
        test_apps = {"plugin-general": {"test_path": "tests/functional/dummy_tests/general_test.py", "driver": "nose"},
                     "plugin-stopped": {"test_path": "tests/functional/dummy_tests/stopped_test.py", "driver": "nose"}}
        data.update(test_apps)
        commands.seek(0)
        commands.write(dumps(data))
        commands.truncate()

if __name__ == '__main__':
    main()