import sys
import glob
import serial
import minimalmodbus

from pymodbus.client import ModbusSerialClient as ModbusClient


hiking_pf = 0x0010
hiking_freq = 0x0011
hiking_relay = 0x001A
hiking_voltaje = 0x000C
hiking_baudrate = 0x0015

class HikinTest():
    def __init__(self):
        self.ser = serial.Serial()
        self.chanel = None
        self.client = None
        
        print("pepe")

    def _writeSerial(self):
        self.ser.port = self.serial_ports()[0]
        self.ser.open()
        self.ser.write(b"pepe")

    def testRTU(self):
        #self.instrument = minimalmodbus.Instrument(self.chanel, 1)
        #self.instrument.serial.baudrate = 9600
        #self.instrument.serial.parity = serial.PARITY_NONE
        #self.instrument.clear_buffers_before_each_transaction = True
        #self.instrument.serial.close()
        # test
        # print(self.instrument.read_register(hiking_voltage))
        
        self.client = ModbusClient(method = 'rtu', port=self.chanel, stopbits = 1, bytesize = 8, parity = 'N' , baudrate= 9600)
        self.client.connect()

        res = self.client.read_holding_registers(hiking_relay, 1, unit=1)
        print(hex(res.registers[0]))

        #self.client.close()

    def switchRelay(self):
        """
        The meter does not understand the 'write sigle register' function code (06h), only the 'write multiple registers' function code (10h).

        """


        res = self.client.write_registers(hiking_relay, 0x0001, unit=1)
        #res = self.client.write_register(hiking_relay, 0, unit=1)
        #print("[Debug] Respuesta Escritura: ", res)
        pass
    def selectPort(self):
        tempPorts = self.serial_ports()
        print(tempPorts)
        port = int(input("Seleccionar PORT RS485 (index lista): "))
        self.chanel = tempPorts[port]
        print("Seleccionaste--> ", self.chanel) 

    def serial_ports(self):
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result


if __name__ == '__main__':
    try:
        app = HikinTest()
        app.selectPort()
        app.testRTU()
        app.switchRelay()
    finally:
        app.client.close()
