OSTF 0.1 Release Notes

OSTF (OpenStack Test Framework) version 0.1 provides possibilities to unify the ways of testing OpenStack and also a way to integrate OpenStack tests running with Fuel.

Release date: 7/Jun/2013

Release source code:
ssh://gerrit.mirantis.com:29418/openstack-test-framework/testing-adapter
BRANCH: release/demo-0.1

Release content:
Features implemented (short names and JIRAs):
POST host/<test_service>?job=<job_name>
test_service - name of abstract procedure e.g post_deployment
job_name - name of the job in jenkins
Will invoke build in jenkins and collect results of that build
If no job provided will invoke build for predefined job

GET host/<test_service>?job=<job_name>
Will return results of the build, in json format: e.g
{<test_service>: {<job_name>: {status: ‘FAILURE’}}}
if there any test results beside of the build info, they will be included in xunit format
If no job provided - all results that correspond to <test_service> will be returned

DELETE host/<test_service>?job=<job_name>
For now just deletes info in storage
Will stop builds later


Known issues and limitations:
1. Does not store any history info, e.g previous builds
2. Could not stop builds
3. As test runner uses jenkins
4. Only rest api transport service is provided
5. No product installation
6. Configuration must be done manually


Short guidelines on the release installation / integration:
To use testing-adapter you need:
1. Install jenkins and attach jobs which you will call later
Jenkins url should be configured in testing-adapter/core/wsgi/config
2. Install redis on localhost
3. Start wsgi server at testing-adapter/bin/adapter-api.py
By default app will be started on 8777 port