from stevedore import driver
from core.transport import jenkins_adapter

TRANSPORT_NAMESPACE = 'core.transport'


def get_transport(conf):
    return jenkins_adapter.JenkinsClient(conf.jenkins_url)