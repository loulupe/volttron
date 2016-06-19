from __future__ import absolute_import
from datetime import datetime,timedelta
import logging
import sys
from volttron.platform.vip.agent import Agent,Core
from volttron.platform.agent import utils
import time
from volttron.platform.jsonrpc import RemoteError

utils.setup_logging()
_log = logging.getLogger(__name__)
topic = 'devices/motiondetect_device/IsMotionDetect'
PLATFORM_ACTUATOR = 'platform.actuator'
REQUEST_NEW_SCHEDULE = 'request_new_schedule'

class TestAgent(Agent):
    def __init__(self,config_path,**kwargs):
        super(TestAgent,self).__init__(**kwargs)


    def scheduleDevice(self):
        point = 'campus/motiondetect_device'
        start = str(datetime.now())
        end = str(datetime.now() + timedelta(seconds=1))
        msg = [[point, start, end]]
        agent_id = 'master_driver'
        result = self.vip.rpc.call(
                PLATFORM_ACTUATOR,
                REQUEST_NEW_SCHEDULE,
                agent_id,
                'taskSuccess',
                'HIGH',
                msg).get(timeout=10)
        _log.info(str(result['result']))
        
    @Core.periodic(3)
    def publish_heartbeat(self):
       _log.info('Agent Starting')
       result = self.vip.rpc.call(
                PLATFORM_ACTUATOR,  # Target agent
                'get_point',  # Method
                'campus/motiondetect_device/IsMotionDetect'  # point
                ).get(timeout=10)
       _log.info('RESULT:'+str(result))



def main(argv=sys.argv):
    try:
        utils.vip_main(TestAgent)
    except Exception as e:
        _log.exception(e)

if __name__ == '__main__':
    sys.exit(main())
