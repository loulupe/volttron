#This code has been developed for the 1st PNNL Connected Building Challenge
#by the team "Ventilation Scheduler"
#All our development is based on opensource contributions
#It is intended to be distributed for the building automation communities for research and educational purposes
#Copyrights and license is to be determined
#This work is being funded by the Department of Energy Program - BIRD Building Integration Research and Developed Innovators Program
#and NSF-I-Corps - Rochester Institute of Technology.
#None of the team members, entities that had collaborated or funded to this project has legal liability 
#or responsibility for any outcome
#The views and opinions of any team member or collaborator do not reflect those of any agencyentity.
#_Project Team: Lourdes Gutierrez and Priyank Kapadia
#_Contact info: lmg4630@rit.edu, plk8075@rit.edu
#_Created: 2016-06-19

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
