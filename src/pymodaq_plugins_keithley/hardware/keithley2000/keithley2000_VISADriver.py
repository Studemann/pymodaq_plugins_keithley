import time

import pyvisa

class Keithley2000VISADriver:
    """
        VISA class driver for the Keithley 2000
        This class relies on pyvisa module to communicate with the instrument via VISA protocol
        Either GPIB or serial can be used
    """

    def __init__(self, rsrc_name, baudrate, pyvisa_backend='@py'):
        """
        Parameters
        ----------
        rsrc_name   (string)        VISA Resource name
        baudrate    (int)           Baud Rate for serial communication
        pyvisa_backend  (string)    Expects a pyvisa backend identifier or a path to the visa backend dll (ref. to pyvisa)
        """

        from pyvisa import ResourceManager
        VISA_rm = ResourceManager()

        # Regarding the VISA resource type given through rsrc_name, open it as GPIB or serial communication
        if "GPIB" in str(rsrc_name):
            self._instr = VISA_rm.open_resource(rsrc_name)
        else:
            self._instr = VISA_rm.open_resource(rsrc_name,
                                       baud_rate=baudrate)
                                       #read_termination='\n',
                                       #write_termination='\n')



        # Set communication parameters
        self._instr.baud_rate = baudrate
        self._instr.timeout = 3000

        # Set read and write termination character
        self._instr.read_termination = '\n'
        self._instr.write_termination = '\n'

    def close(self):
        """
        Close the VISA resource
        """
        self._instr.close()

    def get_identification(self) -> str:
        """
        Request the identification string of the instrument
        return: string
        """
        return str(self._instr.query("*IDN?"))

    def reset(self):
        """
        Send command to initiate the instrument
        """
        self._instr.write("*CLS")
        self._instr.write("*RST")

    def read(self) -> float:
        """
        Send a request to get a measurement value
        return: float
        """
        return float(self._instr.query("READ?"))

    def set_mode(self, mode, **kwargs):
        """

        Parameters
        ----------
        mode    (string)    Measurement configuration ('VDC', 'VAC', 'IDC', 'IAC', 'R2W' and 'R4W' modes are supported)
        kwargs  (dict)      Could be used to pass optional arguments  such 'range' and 'resolution' a
                            but not implemented yet

        Returns
        -------

        """
        assert (isinstance(mode, str))
        mode = mode.lower()

        cmd = ':CONF:'

        if mode == "Ohm2".lower() or mode == "R2W".lower():
            cmd += "RES"
        elif mode == "Ohm4".lower() or mode == "R4W".lower():
            cmd += "FRES"
        elif mode == "VDC".lower() or mode == "V".lower():
            cmd += "VOLT:DC"
        elif mode == "VAC".lower():
            cmd += "VOLT:AC"
        elif mode == "IDC".lower() or mode == "I".lower():
            cmd += "CURR:DC"
        elif mode == "IAC".lower():
            cmd += "CURR:AC"
        # Not applicable with Keithley 2000 CONF command
        #if 'range' in kwargs.keys():
        #    cmd += ' ' + str(kwargs['range'])
        #    if 'resolution' in kwargs.keys():
        #        cmd += ',' + str(kwargs['resolution'])
        #elif 'resolution' in kwargs.keys():
        #    cmd += ' DEF,' + str(kwargs['resolution'])

        self._instr.write(cmd)


if __name__ == "__main__":
    """
    Part to test the driver in a "standalone mode"
    """

    ##checking VISA ressources available
    # ----------------------------------
    try:
        from pyvisa import ResourceManager

        VISA_rm = ResourceManager()
        devices = list(VISA_rm.list_resources())
        device = ''
        for dev in devices:
            if 'GPIB' in dev:
                device = dev
                break
    except Exception as e:
        devices = []
        device = ''
        raise e
    # -----------------

    try:
        k2000 = Keithley2000VISADriver(str(dev), 9600)
        k2000.reset()
        k2000.get_identification()
        k2000.set_mode('Ohm2')

        k2000.set_mode('R4W', range=10, resolution='MAX')
        k2000.set_mode('R4W', resolution='MIN')
        k2000.set_mode('IAC', range=0.001, resolution='MIN')
        k2000.set_mode('vdc', range=0.1, resolution='0.0001')

        #time.sleep(1)

        print(k2000.read())
        print(k2000.read())
        print(k2000.read())

        k2000.close()

    except Exception as e:
        print("Exception ({}): {}".format(type(e), str(e)))
