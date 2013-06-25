from core.transport import nose_adapter
from stevedore import driver
import logging

log = logging.getLogger(__name__)

PLUGINS_NAMESPACE = 'plugins'


def get_transport(driver_name):
    log.info('GET TRANSPORT FOR - %s' % driver_name)
    # TODO remove nose hardcode from driver manager
    mgr = driver.DriverManager(PLUGINS_NAMESPACE,
                               driver_name,
                               invoke_on_load=True)
    return mgr.driver