from volttron.platform.agent import utils
import sqlite3
import logging
from datetime import date
from dateutil.rrule import *
from dateutil import parser
import hashlib
import json

utils.setup_logging()
_log = logging.getLogger(__name__)

class ClassData(object):
    _schedules = dict()
    def __init__(self, **kwargs):
        litePath = kwargs.get('litePath',None)
        _log.info(litePath)
        if litePath is not None:
            con = sqlite3.connect(litePath)
            self.cur = con.cursor()
        if self._schedules is None:
            self._schedules = {}
    @property
    def schedules(self):
        return self._schedules

    @schedules.setter
    def schedules(self,value):
        self._schedules = value

    def getAllSchedules(self):
        self._schedules.clear()
        if cur is None:
            print 'None cursor'
        self.cur.execute('SELECT * FROM registration')
        rows = self.cur.fetchall()
        return rows
   
    def getAllActiveSchedules(self):
        self._schedules.clear()
        self.cur.execute('SELECT * FROM scheduler_airflow WHERE status = 1')
        a_rows = self.cur.fetchall()
        if len(a_rows) > 1:
            self.cur.execute('SELECT * FROM scheduler_registration WHERE status = 1')
            rows = self.cur.fetchall()
            count = 1
            for row in rows:
                all_days = self.generateDays(row)
                for day in all_days:
                    _log.info("DICT ITEMS"+str(len(all_days)))
                    dateRange = self.attachTime(day,row)
                    if dateRange is not None:
                        posData = self.getDamperPos(row)
                        _log.info(str(dateRange))
                        classdata = {
                                'rowid': row[0],
                                'start': str(dateRange[0]),
                                'end':str(dateRange[1]),
                                'facility':str(row[16]),
                                'vav':str(posData[0]),
                                'default':posData[2],
                                'pos':posData[1]
                                }
                        key = hashlib.sha1(json.dumps(classdata,sort_keys=True)).hexdigest()
                        self._schedules[key] = classdata
                count += 1
        return self._schedules

    def attachTime(self,day,row):
        dates = []
        _log.info('ATTACHING TIME FACOTR')
        if row[12] is not None:
            startTime = parser.parse(str(row[12]))
            _log.info('Parsed row 17')
            if row[13] is not None:
                endTime = parser.parse(str(row[13]))
                date1 = day.replace(hour = startTime.hour,minute = startTime.minute, second = startTime.second)
                dates.append(date1)
                date2 = day.replace(hour = endTime.hour,minute = endTime.minute, second = endTime.second)
                dates.append(date2)
                return dates
        return None
    
    def generateDays(self,day):
        _log.info(str(type(day[21])))
        _log.info(str(type(day[22])))
        strDate = parser.parse(str(day[21])) 
        endDate = parser.parse(str(day[22]))
        scheduledDays = list(rrule(WEEKLY, byweekday=self.findWeekDay(day), dtstart=strDate, until=endDate))
        return scheduledDays
        
    def findWeekDay(self,day):
        separator = ""
        resultStr = ""
        for i in range(14,21):
            #_log.info('For day:{} value is {} '.format(i,day[i]))
            if day[i] == 'Y':
                resultStr += separator + str((i % 14))
                separator = ','
        _log.info(str([int(x) for x in resultStr.split(",")]))
        return [int(x) for x in resultStr.split(",")]
    

    def getAllScheduled(self):
        self._schedules.clear()
        self.cur.execute('SELECT * FROM registration  WHERE Status = 2')
        rows = self.cur.fetchall()
        return rows

    
    def updateBatchStatus(self,Status):
        self.cur.execute("UPDATE scheduler_airflow SET status=" +str(Status))

    def updateStatus(self,Status,schedule,table):
        _log.info("#####################UPDATING STATUS###########################"+str(schedule['rowid']))
        self.cur.execute("UPDATE scheduler_" +table+ " SET status=" +str(Status)+" WHERE id = " + str(schedule['rowid']))

    def getDamperPos(self,row):
        _log.info('Facl ID:'+str(row[11]))
        self.cur.execute('SELECT vav,reqDamperPosition,idleDamperPosition FROM scheduler_airflow WHERE facilID IN (SELECT facilID FROM scheduler_registration WHERE status = 1 AND facilID LIKE "%'+str(row[11])+'%")')
        damperrow = self.cur.fetchone()
        _log.info("DAMPER ROW"+str(damperrow))
        return damperrow

    def getCount(self):
        return self.cur.rowcount

    def __enter__(self):
        self.schedules = {}
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.schedules.clear()

class VavClass(object):
    def __init__(self,start,end,facility,VAVname,defaultPos,valuePos):
        self.start = start
        self.end = end
        self.facility = facility
        self.VAV = VAVname
        self.Default = defaultPos
        self.Pos = valuePos
