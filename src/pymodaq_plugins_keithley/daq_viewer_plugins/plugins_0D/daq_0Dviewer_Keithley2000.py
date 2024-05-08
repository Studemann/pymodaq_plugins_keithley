from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, main, comon_parameters
from pymodaq.utils.data import DataFromPlugins
from easydict import EasyDict as edict
from ...hardware.keithley2000.keithley2000_VISADriver import Keithley2000VISADriver as Keithley2000

import numpy as np


class DAQ_0DViewer_Keithley2000(DAQ_Viewer_base):
    """
        Naive implementation of a DAQ 0D Viewer using the Keithley 2000 as data source
        This DAQ0D Viewer plugin only supports measurement mode selection and a simple data read acquisition mechanism
        with no averaging supported
        uses the Keithley2000_VISADriver.py
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

    # List of Keithley 2000 available baud rate
    available_baud_rate_list = [300,600,1200,2400,4800,9600,19200]

    params = comon_parameters+[
        {'title': 'VISA Resource', 'name': 'visa_resources', 'type': 'group', 'children': [
        {'title': 'Devices:', 'name': 'visa_device', 'type': 'list', 'limits': devices},
        {'title': 'Baud Rate:', 'name': 'visa_baud_rate', 'type': 'list', 'limits': available_baud_rate_list, 'value':available_baud_rate_list[6]},]},

        {'title': 'Keithley2000 Parameters',  'name': 'K2000Params', 'type': 'group', 'children': [
            {'title': 'Identication:', 'name': 'id', 'type': 'text', 'value': "Identification instrument string"},
            {'title': 'Mode', 'name': 'mode', 'type': 'list', 'limits': ['VDC', 'VAC', 'R2W', 'R4W'], 'value': 'VDC'}

        ]}
    ]

    def __init__(self, parent=None, params_state=None): # init_params is a list of tuple where each tuple contains info on a 1D channel (Ntps,amplitude, width, position and noise)
        super(DAQ_0DViewer_Keithley2000, self).__init__(parent, params_state)

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

        # Check if controller act as a slave or a master one
        if self.settings.child(('controller_status')).value() == "Slave":
            if controller is None: 
                raise Exception('no controller has been defined externally while this detector is a slave one')
            else:
                self.controller = controller
        else:
            try:

                # Init Driver with the VISA resource selected
                selected_VISA = self.settings.child('visa_resources','visa_device').value()
                selected_baudrate = self.settings.child('visa_resources','visa_baud_rate').value()
                self.controller = Keithley2000(selected_VISA, selected_baudrate)

            except Exception as e:
                raise Exception('No controller could be defined because an error occurred\
                 while connecting to the instrument. Error: {}'.format(str(e)))

        # Set the controller
        # Set Resistance measurement mode
        self.settings.child('K2000Params', 'mode').setValue('R2W')
        self.controller.set_mode(self.settings.child('K2000Params', 'mode').value())

        # Reset the controller
        self.controller.reset()

        # Get the controller identification and display it in the viewer
        txt = self.controller.get_identification()
        self.settings.child('K2000Params','id').setValue(txt)

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

        # Get data from controller
        data = self.controller.read()
        # Convert in a numpy array
        data_value = np.array([data])
        self.data_grabed_signal.emit([DataFromPlugins(name='Keithley2000', data=[data_value], dim='Data0D',)])


    def stop(self):
        """
            not implemented.
        """

        return ""

if __name__ == '__main__':
    main(__file__, init=False)
