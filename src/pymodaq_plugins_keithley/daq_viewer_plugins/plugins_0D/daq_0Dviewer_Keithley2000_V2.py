from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, main, comon_parameters
from pymodaq.utils.data import DataFromPlugins
#from pymodaq.utils.daq_utils import DataFromPlugins
from easydict import EasyDict as edict
#from collections import OrderedDict
#from ...hardware.keithley2000.keithley2000_VISADriver import Keithley2000VISADriver as Keithley2000
import ...hardware.keithley2000.keithley2000_VISADriver as Keithley2000
import numpy as np


class DAQ_0DViewer_Keithley2000_V2(DAQ_Viewer_base):
    """
        Naive implementation of a DAQ 0D Viewer using the Keithley 2000 as data source
        This DAQ0D Viewer plugin only supports measurement mode selection and a simple data read acquisition mechanism
        with no averaging supported
        V2 uses the Keithley2000_VISADriver.py
        =============== =================
        **Attributes**  **Type**
        *params*        dictionnary list
        *x_axis*        1D numpy array
        *ind_data*      int
        =============== =================
    """

    # checking VISA ressources to populate the available devices
    try:
        from pyvisa import ResourceManager
        VISA_rm = ResourceManager()
        devices = list(VISA_rm.list_resources())    # get list of communication available (serial,GPIB,...)
    except Exception as e:
        devices = []
        device = ''
        raise e


    available_baud_rate_list = [300,600,1200,2400,4800,9600,19200]

    params = comon_parameters+[
        {'title': 'VISA:', 'name': 'VISA_ressources', 'type': 'list', 'limits': devices},
        {'title': 'Keithley2000 Parameters',  'name': 'K2000Params', 'type': 'group', 'children': [
            {'title': 'Mode', 'name': 'mode', 'type': 'list', 'limits': ['VDC', 'VAC', 'R2W', 'R4W'], 'value': 'VDC'}

        ]}
    ]

    def __init__(self, parent=None, params_state=None): # init_params is a list of tuple where each tuple contains info on a 1D channel (Ntps,amplitude, width, position and noise)
        super(DAQ_0DViewer_Keithley2000_V2, self).__init__(parent, params_state)

        from pyvisa import ResourceManager
        self.VISA_rm = ResourceManager()
        self.controller=None
        #self.x_axis = None
        #self.ind_data = 0


    def commit_settings(self, param):
        """
            ============== ========= =================
            **Parameters**  **Type**  **Description**
            *param*        child node  could be the following setting parameter: 'mode'
            ============== ========= =================
        """
        if param.name() == 'mode':
            """Updates the newly selected measurement mode"""
            self.controller.set_mode(param.value())

    def ini_detector(self, controller=None):
        """
            Initialisation procedure of the detector.

            Returns
            -------
                the initialized status.
        """
       # import pdb
       # pdb.set_trace()

        self.status.update(edict(initialized=False, info="", x_axis=None, y_axis=None, controller=None))
        if self.settings.child(('controller_status')).value() == "Slave":
            if controller is None: 
                raise Exception('no controller has been defined externally while this detector is a slave one')
            else:
                self.controller = controller
        else:
            try:
                self.controller = Keithley2000('K2000')
            except Exception as e:
                raise Exception('No controller could be defined because an error occurred\
                 while connecting to the instrument. Error: {}'.format(str(e)))

        self.controller.set_mode(self.settings.child('K2000Params', 'mode').value())

        # initialize viewers with the future type of data
        self.data_grabed_signal.emit(
                    [DataFromPlugins(name='Keithley2000', data=[0], dim='Data0D', labels=['Meas', 'Time'])])
            #self.controller = self.VISA_rm.open_resource(self.settings.child('VISA_ressources').value(),
            #                                             baud_rate=19200,
            #                                             read_termination='\n',write_termination='\n')

        #self.controller.set_mode(self.settings.child('K2000Params', 'mode').value())

        #Set the timeout (of the controller or VISA ressource??
        #self.controller.timeout = self.settings.child(('timeout')).value()
        #self.controller.timeout = 100

        #self.controller.write("*rst; *cls;")
        self.controller.reset()

        txt = self.controller.get_identification()
        #self.settings.child(('id')).setValue(txt)

        # initialize viewers with the future type of data
        self.data_grabed_signal.emit([DataFromPlugins(name='Keithley2000', data=[np.array([0])], dim='Data0D')])

        self.status.initialized = True
        self.status.controller = self.controller
        return self.status

    def close(self):
        """
            not implemented.
        """
       #pass
        self.controller.close()

    def grab_data(self, Naverage=1, **kwargs):
        """
            | Start new acquisition.
            |
            |
            | Send the data_grabed_signal once done.

            =============== ======== ===============================================
            **Parameters**  **Type**  **Description**
            *Naverage*      int       specify the threshold of the mean calculation
            =============== ======== ===============================================

        """

        #Normally get data from controller but to test just set a numpy array
        #data = float(self.controller.query('READ?'))
        data = self.controller.read()
        data_value = np.array([data])
        #data_value = self.controller.query_ascii_values('READ?')
        #data_value = np.array([1, 2, 3, 4, 5, 6])
        self.data_grabed_signal.emit([DataFromPlugins(name='Keithley2000', data=[data_value], dim='Data0D',)])
        #self.ind_data += 1

    def stop(self):
        """
            not implemented.
        """

        return ""
if __name__ == '__main__':
    main(__file__, init=False)