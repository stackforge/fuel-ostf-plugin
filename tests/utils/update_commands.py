__author__ = 'ekonstantinov'
from json import loads, dumps


def main():
    with open('data/commands.json', 'rw+') as file:
        data = loads(file.read())
        for item in data:
            data[item]['argv'].appent("--with-xunit")
        test_apps = {"plugin-general": {"test_path": "tests/functional/dummy_tests/general_test.py", "driver": "nose"},
                     "plugin-stopped": {"test_path": "tests/functional/dummy_tests/stopped_test.py", "driver": "nose"}}
        data.update(test_apps)
        file.seek(0)
        file.write(dumps(data))
        file.truncate()

if __name__ == '__main__':
    main()