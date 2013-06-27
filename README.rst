SETUP:

1. System packages:
    1.1. Postgres server
    1.2. libpq-dev
2. Install pip-requirements
    2.1. python setup.py develop
        Will install python dependencies, and two scripts
        ostf-server
        ostf-db
3. Migrate postgres database
        ostf-db --config-file /etc/testing_adapter.conf upgrade head
     TO REMOVE APPLIED MIGRATION USE:
        ostf-db --config-file /etc/testing_adapter.conf downgrade -1
4. ostf-server --config-file /etc/testing_adapter.conf
     config-file should be in format of ./etc/testing_adapter.conf.sample
     where database_connection just usual sqlalchemy url

-------------------------------------------------------------------------------------------------------------------------------------------------

USE:

working_directory - absolute path of the tests

1. curl -H "Content-Type: application/json" -X POST -d  http://localhost:8777/v1/tests
RESPONSE: {"type": "tests", "id": 7}

Application expecting working_directory of tests that should be runed
2. curl -X GET http://localhost:8777/v1/tests?test_run_id=7
RESPONSE:
{"tests": {"test_for_adapter.TestSimple.test_first_sleep": {"taken": 0.9953169822692871, "type": "success", "name": "test_for_adapter.TestSimple.test_first_sleep"},
"test_for_adapter.TestSimple.test_first_without_sleep": {"taken": 8.893013000488281e-05, "type": "success", "name": "test_for_adapter.TestSimple.test_first_without_sleep"}},
"type": "tests", "id": 7}

3. curl -X DELETE http://localhost:8777/v1/tests?test_run_id=7
Will kill test run