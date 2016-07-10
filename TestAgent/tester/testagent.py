from __future__ import absolute_import
from datetime import datetime,timedelta
import logging
import sys
from volttron.platform.vip.agent import Agent,Core
from volttron.platform.agent import utils
import time
from volttron.platform.jsonrpc import RemoteError
import random

utils.setup_logging()
_log = logging.getLogger(__name__)
topic = 'campus/building/bacnet1/dmpr_pos_1'
topic2 = 'campus/building/modbus/flap_override'
topic3 = 'campus/building/modbus/flap_position'

PLATFORM_ACTUATOR = 'platform.actuator'
PLATFORM_BACNET = 'platform.bacnet_proxy'
REQUEST_NEW_SCHEDULE = 'request_new_schedule'

class TestAgent(Agent):
    def __init__(self,config_path,**kwargs):
        super(TestAgent,self).__init__(**kwargs)
        
    @Core.receiver('onstart')
    def onStart(self ,sender, **kwargs):
        agent_id = 'testagent'
        taskid = str(random.random())
        start = str(datetime.now())
        end = str(datetime.now() + timedelta(seconds=10))
        msg = [['campus/building/modbus', start, end]]
        result = self.vip.rpc.call(PLATFORM_ACTUATOR,REQUEST_NEW_SCHEDULE,agent_id,taskid,'HIGH',msg).get(timeout=10)
        _log.info('Agent Status:'+str(result))
        result = self.vip.rpc.call(PLATFORM_ACTUATOR,'set_point',agent_id,topic2,'ON').get(timeout=10)
        result = self.vip.rpc.call(PLATFORM_ACTUATOR,'set_point',agent_id,topic3,10).get(timeout=10)
        _log.info('RESULT:'+str(result))
        _log.info('RESULT:'+str(result))




def main(argv=sys.argv):
    try:
        utils.vip_main(TestAgent)
    except Exception as e:
        _log.exception(e)

if __name__ == '__main__':
    sys.exit(main())
