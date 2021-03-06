import string, re, time, socket

from packet import Identifier, DataRecord, LogicalRecord
import serial

DATA_REQUEST = LogicalRecord.BEGIN + LogicalRecord.END

class IO(object):
    def write(self, data):
        "writes a string out"
        raise NotImplementedError, "subclasses of IO must implement this method"
    def read(self):
        """reads a string in"""
        raise NotImplementedError, "subclasses of IO must implement this method"
    def close(self):
        "closes connection"
        raise NotImplementedError, "subclasses of IO must implement this method"

class SerialIO(IO):
    def __init__(self, serial):
        self.serial = serial

    def write(self, data):
        self.serial.write(data)
        
    def read(self):
        data = []
        new_data = None
        while(new_data != ''):
            new_data = self.serial.read()
            data.append(new_data)
        return ''.join(data)

    def close(self):
        self.serial.close()

class TCPIO(IO):
    def __init__(self, socket, timeout=.25):
        self.socket = socket
        self.timeout = timeout

    def write(self, data):
        self.socket.send(data)

    def read(self):
        data = ""
        self.socket.settimeout(self.timeout)
        try:
            while 1:
                resp = self.socket.recv(2048)
                data += resp
        except:
            pass
        return data

    def close(self):
        self.socket.close()

class Parser(object):
    def parse(self, data):
        "parses string into required format"
        raise NotImplementedError, "subclasses of IO must implement this method"

class WITS0Parser(Parser):
    LOGICAL_RECORD_REGEX = re.compile(LogicalRecord.BEGIN + '[^&^!]*' +
                                      LogicalRecord.END,re.DOTALL)

    def parse(self, data):
        return self.parse_data(data)

    def parse_data(self,data):
        logical_record_strings = WITS0Parser.LOGICAL_RECORD_REGEX.findall(data)
        return [self.parse_logical_record(x)
                for _,x in enumerate(logical_record_strings)]

    def parse_logical_record(self,logical_record_string):
        begin_length = len(LogicalRecord.BEGIN)
        end_length = len(LogicalRecord.END)
        stripped_logical_record = logical_record_string[begin_length:-end_length]
        data_record_strings = stripped_logical_record.split(DataRecord.SEPERATOR)
        data_records = [self.parse_data_record(x)
                        for x in data_record_strings if x != '']
        return LogicalRecord(data_records)

    def parse_data_record(self,data_record_string):
        record_identifier = data_record_string[0:2]
        item_identifier = data_record_string[2:4]
        value = data_record_string[4:]
        ident = Identifier(record_identifier,item_identifier)
        return DataRecord(ident,value)

class Communicator(object):
    def __init__(self, io, parser):
        self.io = io
        self.parser = parser

    def write(self,data):
        self.io.write(data)

    def ask(self,question):
        self.write(question)
        return self.read()

    def read(self):
        return self.parser.parse(self.io.read())

    def close(self):
        self.io.close()

class PasonCommunicator(Communicator):
    PASON_DATA_REQUEST = (LogicalRecord.BEGIN + '0111-9999' +
                          DataRecord.SEPERATOR + LogicalRecord.END)

    def __init__(self, io):
        Communicator.__init__(self, io, WITS0Parser())

    def read_pason_data(self):
        return self.ask(PasonCommunicator.PASON_DATA_REQUEST)


class PasonSerialCommunicator(PasonCommunicator):
    def __init__(self, comport):
        self.comport = serial.Serial(port=comport,
                                     baudrate=9600,
                                     bytesize=8,
                                     parity='N',
                                     stopbits=1,
                                     timeout=3)
        io = SerialIO(self.comport)
        PasonCommunicator.__init__(self,io)

class PasonEthernetCommunicator(PasonCommunicator):
    def __init__(self, address, port):
        self.socket = socket.socket()
        self.socket.connect((address, port))
        self.socket.settimeout(1)
        io = TCPIO(self.socket)
        PasonCommunicator.__init__(self,io)

if __name__ == '__main__':

    test_str = '&&\r\n1984PASON/EDR\r\n0108519.48\r\n01103705.81\r\n01130.00\r\n01230.00\r\n01240.00\r\n01250.00\r\n0137987626.00\r\n01426229.27\r\n0143495787.00\r\n0144491839.00\r\n01450.00\r\n!!\r\n'

    p = WITS0Parser()
    print p.parse(test_str)

