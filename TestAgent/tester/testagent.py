from __future__ import absolute_import
from datetime import datetime,timedelta
import logging
import sys
from volttron.platform.vip.agent import Agent,Core,PubSub
from volttron.platform.agent import utils
import time
from volttron.platform.jsonrpc import RemoteError
import random
import os
import sqlite3
from tester.data import ClassData
from volttron.platform.messaging import topics
import json
import hashlib
import pickle

utils.setup_logging()
_log = logging.getLogger(__name__)
topic = 'campus/building/bacnet1/dmpr_pos_1'
topic2 = 'campus/building/modbus/flap_override'
topic3 = 'campus/building/modbus/flap_position'

PLATFORM_ACTUATOR = 'platform.actuator'
PLATFORM_BACNET = 'platform.bacnet_proxy'
REQUEST_NEW_SCHEDULE = 'request_new_schedule'
DATABASE = 'db.sqlite3'
SQLITE_PATH = '/home/priyankkapadia/website/ventos'
vav_schedule ='devices/actuators/schedule/announce/campus/building/modbus/'

class TestAgent(Agent):
    def __init__(self,config_path,**kwargs):
        super(TestAgent,self).__init__(**kwargs)
        self.path = os.path.join(SQLITE_PATH,DATABASE)

    @Core.periodic(10)
    def DataListener(self):
        print self.path
        with ClassData(litePath = self.path) as self.data:
            self.schedules = self.data.getAllActiveSchedules()
            _log.info("LENGTH DICT"+str(len(self.schedules)))
            count = 0
            if (len(self.schedules)) > 1:
                    #data = {
                    #    'start' : str(datetime.now()),
                    #    'end' : str(datetime.now() + timedelta(seconds=60)),
                    #    'facility':'a',
                    #    'vav':'b',
                    #    'default':'0',
                    #    'pos':'87'
                    #    }
                    #key = hashlib.sha1(json.dumps(data,sort_keys=True)).hexdigest()
                    #self.schedules[key] = data
                    pickle.dump(self.schedules,open(SQLITE_PATH+"/save.p","wb"))
            for key in self.schedules:
                data = self.schedules[key]
                _log.info("#######SCHEDULIN######")
                headers = {
                        'AgentID': 'testagent',
                        'type': 'NEW_SCHEDULE',
                        'requesterID': 'testagent', #The name of the requesting agent.
                        'taskID': str(key), #The desired task ID for this task. It must be unique among all other scheduled tasks.
                        'priority': 'HIGH', #The desired task priority, must be 'HIGH', 'LOW', or 'LOW_PREEMPT'
                    }
                msg = [['campus/building/modbus', str(data['start']), str(data['end'])]]
                result = self.vip.pubsub.publish('pubsub',topics.ACTUATOR_SCHEDULE_REQUEST,headers,msg)
                _log.info(str(result))
                _log.info("##########################################################################")
                self.data.updateStatus('2',self.schedules[key],'registration')
                if (len(self.schedules)) > 0:
                    self.data.updateBatchStatus('2')
    
    @PubSub.subscribe('pubsub',topics.ACTUATOR_SCHEDULE_ANNOUNCE(campus='campus',building='building',unit='modbus'))
    def runOnScheduleself(self, peer, sender, bus,  topic, headers, message):
        _log.info("############################This event triggered on#################" + str(datetime.now()))
        agent_id = headers['requesterID']
        key = headers['taskID']
        self.schedules = pickle.load( open( SQLITE_PATH+"/save.p", "rb" ) )
        _log.info(str(self.path))
        data = self.schedules[key]
        Position = int(data['pos'])
        _log.info('Position:'+str(Position))
        Default = int(data['default'])
        _log.info('Default:'+str(Default))
        #Name = headers['VAV']
        #Facility = headers['Facility']
        #_log.info('Name:'+str(Name))
        #_log.info(str(type(message)))
        gracePeriod = time.time() + 60 # 5 minutes from now
        _log.info(str(gracePeriod))
        while True:
            result = self.vip.rpc.call(
                    PLATFORM_ACTUATOR,  # Target agent
                    'get_point',  # Method
                    'campus/motiondetect_device/IsMotionDetect'  # point
                    ).get(timeout=10)
            _log.info("MOTION DETECT RESULT:"+str(result))
            _log.info("#############RESULT EXIT########"+str(result=='True'))
            time.sleep(2)
            _log.info("CURRENT TIME:"+str(time.time()))
            if (str(result) == 'True') or (time.time() > gracePeriod):
                _log.info("##############################TIMEOUT/MOTION_DETECTED############################")
                break
        if (str(result) == 'True'):
            _log.info("#####################################MOTION DETECTED#######################")
            SetPosition = Position
        else:
            _log.info("##############################DEFAULT IDLE##################################")
            SetPosition = Default
        _log.info("###################################SETTING POSITION############################"+str(SetPosition))
        result = self.vip.rpc.call(PLATFORM_ACTUATOR,'set_point',agent_id,topic2,'ON').get(timeout=10)
        result = self.vip.rpc.call(PLATFORM_ACTUATOR,'set_point',agent_id,topic3,SetPosition).get(timeout=10)
        print 'Done with Commands - Release device lock.'
        headers = {
                'type': 'CANCEL_SCHEDULE',
                'requesterID': agent_id,
                'taskID': key
                }
        _log.info("####### WORK DONE. CANCE TASK NOW !!! ###############")
        self.vip.pubsub.publish('pubsub',topics.ACTUATOR_SCHEDULE_REQUEST,headers,{})
        

def main(argv=sys.argv):
    try:
        utils.vip_main(TestAgent)
    except Exception as e:
        _log.exception(e)

if __name__ == '__main__':
    sys.exit(main())
