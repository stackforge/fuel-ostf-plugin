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


BY DEFAULT database connection will be:
postgresql+psycopg2://adapter:demo@localhost/testing_adapter

If you want logging to file : 
ostf-server --log_file testing.log

After installation hook
ostf-server --after-initialization-environment-hook --dbpath=postgresql+psycopg2://postgres:demo@localhost/testing_adapter
-------------------------------------------------------------------------------------------------------------------------------------

USE:

Design of OSTF REST API entities, urls and output format
Testset
GET /v1/testsets
Response:
[
 {id: "testset-nova-1", name: "Tests for nova"},
 {id: "testset-keystone-222", name: "Tests for keystone"},
 ...
]
Test
GET /v1/tests
Response:
[
 {id: "test_for_adapter.TestSimple.test_first_without_sleep_1", name: "Some test #1", testset: "testset-nova-1"},
 {id: "test_for_adapter.TestSimple.test_first_without_sleep_2", name: "Some test #2", testset: "testset-nova-1"},
 {id: "test_for_keystone.TestSimple.fgsfds", name: "Another test", testset: "testset-keystone-222"},
 ...
]
Testrun (history entry)
GET /v1/testruns
Response:
[
 {id: <autoincrement>, testset: "testset-keystone-222", metadata: {...}, tests: [
  {id: "test_for_adapter.TestSimple.test_first_without_sleep_1", status: "running/success/error", message: "error message if error"},
  ...
 ]},
 ...
]

GET /v1/testruns/last/<cluster_id>
Response format is the same, but response contains only last entries filtered by cluster_id

POST /v1/testruns (run the tests)
Request:
[
 {testset: "testset-keystone-222", metadata: {...}},
 ...
]
Response format is like GET reponse format (i.e. with status and id)

PUT /v1/testruns (stop the tests)
Request:
[
 {id: <autoincrement>, status: "stopped"},
 ...
]
