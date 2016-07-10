from master_driver.interfaces import BaseInterface, BaseRegister, BasicRevert
from master_driver.classAPI_vav_rtu import API
import socket
import logging
from StringIO import StringIO
from csv import DictReader
_log = logging.getLogger(__name__)
type_mapping = {"string": str,
                "int": int,
                "integer": int,
                "float": float,
                "bool": bool,
                "boolean": bool}

class VAVRegister(BaseRegister):
    '''Inherits from  Volttron Register Class'''
    def __init__(self, read_only, pointName, device_point_name, units,reg_type ,default_value,description):
        '''Initialize register with read_only,pointName, device_point_name, units and default_value '''
        '''Point Name,Volttron Point Name,Units,Units Details,Writable,Starting Value,Type,Notes'''
        super(VAVRegister, self).__init__('byte', read_only, pointName, units, default_value)
        self.default_value = default_value
        self.device_point_name = device_point_name
        self.value = False

class Interface(BaseInterface):
    def __init__(self, **kwargs):
        super(Interface, self).__init__(**kwargs)
        _log.info('starting motion detect')

    def configure(self, config_dict, registry_config_str):
        _log.info('configure called')
        self.parse_config(registry_config_str)
        self.target_address = config_dict["device_address"]
        self.slave_id = config_dict["slave_id"]

    def get_point(self, point_name):
        _log.info('get_point called')
        register = self.get_register_by_name(point_name)
        Prolon = API(model='VC1000', type='VAV', api='API', address=self.target_address+":"+self.slave_id)
        Prolon.getDeviceStatus()
        register.value = Prolon.get_variable(point_name)
        _log.info(register.value)
        return register.value
    
    def set_point(self, point_name, value):
        _log.info('set point called')
        _log.info('POINT_NAME:'+str(point_name))
        register = self.get_register_by_name(point_name)
        _log.info("get register by name")
        Prolon = API(model='VC1000', type='VAV', api='API', address=self.target_address+":"+self.slave_id)
        if Prolon.setDeviceStatus({point_name:value}):
            return Prolon.get_variable(point_name)
        if register.read_only:
            raise IOError("Trying to write to a point configured read only: " + point_name)
        return register.value

    def scrape_all(self):
        _log.info('scarpe all called')
        result = {}
        read_registers = self.get_registers_by_type("byte", True)
        write_registers = self.get_registers_by_type("byte", False)
        for register in read_registers + write_registers:
            pass
        return result
    
    def revert_all(self, **kwargs):
        pass
       
    
    def revert_point(self, point_name, **kwargs):
        pass

    def parse_config(self, config_string):
        _log.info('parse_config called')
        if config_string is None:
            return 
        f = StringIO(config_string)
        configDict = DictReader(f)
        for regDef in configDict:
            read_only = regDef['Writable'].lower() != 'true'
            point_name = regDef['Volttron Point Name']
            _log.info(str(point_name))
            device_pointName = regDef['Point Name']
            description = regDef.get('Notes', '')  
            units = regDef['Units']
            default_value = regDef.get("Starting Value", '').strip()
            if not default_value:
                default_value = None
            type_name = regDef.get("Type", 'string')
            _log.info('<====='+type_name+'======>')
            reg_type = type_mapping.get(type_name, str)
            _log.info('Getting type')
            register_type = VAVRegister
            _log.info('constructor before')
            _log.info('READ ONLY:'+str(read_only) +',POINT_NAME:'+ str(point_name) + ',DEVICE_POINTNAME:' + str(device_pointName) + ',UNITS:' + str(units) + ',REG_TYPE:' + str(reg_type) + ',DEFAULT:' + str(default_value) + ',DESCRIPTION:' + str(description))
            register = register_type(
                read_only,
                point_name,
                device_pointName,
                units,
                reg_type,
                default_value=default_value,
                description=description)
            _log.info("INSERTING")
            self.insert_register(register)
            _log.info("INSERTED REGISTER")


