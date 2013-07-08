__author__ = 'ekonstantinov'
from json import loads, dumps


def main():
    with open('data/commands.json', 'rw+') as commands:
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