from stevedore import driver
from core.transport import jenkins_adapter, simple

TRANSPORT_NAMESPACE = 'core.transport'


def get_transport():
    return simple