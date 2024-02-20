import sys
import glob
import serial
import minimalmodbus
from pymodbus.client import ModbusSerialClient as ModbusClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
import logging
from bitstring import Bits
from dlms_cosem import cosem
import time

"""
communication = https://github.com/arendst/Tasmota/issues/18724

"""


hiking_total_energyH = 0x0000
hiking_total_energyL = 0x0001
hiking_export_energyH = 0x0008
hiking_export_energyL = 0x0009
hiking_import_energyH = 0x000A
hiking_import_energyL = 0x000B
hiking_pf = 0x0010
hiking_freq = 0x0011
hiking_relay = 0x001A
hiking_voltaje = 0x000C
hiking_baudrate = 0x0015
hiking_reactive_power = 0x000F

map_hiking = {"hiking-pf": 0x0010, 
              "hiking-freq": 0x0011, 
              "hiking-relay": 0x001A, 
              "hiking-voltaje": 0x000C, 
              "hiking-baudrate": 0x0015}

class HikinTest():
    def __init__(self):
        self.ser = serial.Serial(baudrate=9600, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE, bytesize=serial.SEVENBITS, timeout=1.5)
        self.chanel = None
        self.client = None
        
        self.data = {"Voltaje": None,
                     "Current": None,
                     "Active Power": None,
                     "Reactive Power": None,
                     "Power Factor": None}
        
        print("pepe")
    
    # write serial.
    def _writeSerial(self, command):
        self.ser.port = self.serial_ports()[0]
        self.ser.open()

        #serialx = "/?!\r\n"
        #erialx1 = "/75443141\r\n"
        id = b'/ISk5MT174-0001\r\n' 
        trama_init = "/?!\r\n"
        trama_mid = "/75443141\r\n1-0:0.9.1\r\n"
        #trama2 = "\x06\x30\x35\x31\x0D\xDA"
        #prueba = cosem.Obis(1, 0, 1, 8, 0, 255).to_bytes()
        #print(prueba)
        #self.ser.write(trama_init.encode())
        #time.sleep(0.5)
        #self.ser.write(trama_mid.encode())
        pe = b'0-0:C.1.0*255'
        temp = '\x2F\x3F\x21\x0D\x0A'
        cam = '\x5C\x78\x30\x31\x42\x30\x5C\x78\x30\x33\x71'
        #temp2 = '\x2F\'
        temp3 = b'1-0:0.9.2/?!\r\n'
        
        #time.sleep(0.5)
        self.ser.write(temp.encode())
        self.ser.write(cam.encode())
        #self.ser.write(command.encode())
        print("[debug] comando escrito")
        
        while True:
            response = self.ser.readline()
            print(response)
            if response == b'':
                break
        
        #self.ser.write(cam.encode())
        #while True:
        #    response = self.ser.readline()
        #    print(response)
        #    if response == b'':
        #        break

        self.ser.close()            
        #response = self.ser.readline()
        #print(response)
        #if response == b"":
            #exit()
        
        
        data = b"0103000C000085C9"    
    
    # test connection to RTU.    
    def testRTU(self):
        """
            Funcion prueba de lectura datos.
        
        """

        self.client = ModbusClient(method = 'rtu', port=self.chanel, stopbits = 1, bytesize = 8, parity = 'N' , baudrate= 9600)
        self.client.connect()


        res = self.client.read_holding_registers(hiking_voltaje, 4, unit=1)
        #res_reac = self.client.read_holding_registers(hiking_reactive_power,1,unit=1)
        #print(res_reac.registers)
        res1 = self.client.read_holding_registers(hiking_pf, 1, unit=1)
        res_complete = self.client.read_holding_registers(0x00,0x2c, unit=1)
        print(f"\n\n {res_complete.registers} \n\n")
        
        # Total Energy
        total_low = res_complete.registers[1]
        total_high = res_complete.registers[0]
        total_combined = (total_high << 16) | (total_low)
        print(total_combined / 100) # 1/100 KWh for conversion. (map register)
        
        #reactive power
        reac_power = res_complete.registers[0x0F]
        
        self.data["Voltaje"] = str((res.registers[0] / 10)) + "VAC"
        self.data["Current"] = str((res.registers[1] / 100)) + "A"
        self.data["Active Power"] = str((res.registers[2])) + "W"
        self.data["Reactive Power"] = str((res.registers[3])) + "VAr"
        self.data["Power Factor"] = str((res1.registers[0] / 1000)) + "PF"
        
        
        print(self.data)
        #print(Bits(bin=bin(reac_power)))
        
        #print(self.twos_comp(reac_power, 8))
        #self.client.close()
    
    # Cambiar estado RELE.
    def switchRelay(self):
        """
        The meter does not understand the 'write sigle register' function code (06h), only the 'write multiple registers' function code (10h).

        """

        state = int(input("Selecciona estado del rele 0x000[A] A: "))
        res = self.client.write_registers(hiking_relay, state, unit=1)
               
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
        app.selectPort() # select port
        app._writeSerial('1-0:0.9.1\r\n')
        #app.testRTU() # test RTU
        #app.switchRelay() # test relay.
    finally:
        pass
        #app.client.close()
