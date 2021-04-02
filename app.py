import argparse
import os
import sys
import threading
from time import sleep
from typing import List

import csv

import serial 
from serial.tools import list_ports
import matplotlib.pyplot as plt


available_ports = []

START_STRING = "START"
END_STRING = "END"

def get_available_ports():
    '''
    Get all available ports......
    '''
    all_ports_tuples = list_ports.comports()
    all_ports = []
    index = 0
    for ap,_,_ in all_ports_tuples:
        all_ports.append(ap)
    return all_ports

def view_available_ports():
    '''
    View available ports
    '''
    print("Available Ports: ")
    available_ports = get_available_ports()
    for i,port in enumerate(available_ports):
        print(f'{i} : {port}')

class SerialConnection():
    def __init__(self,port:str,baudrate:int,data_control,total_read_number):
        self.port = port
        self.baudrate = baudrate
        self.connected = False
        self.data_control = data_control
        self.read_raw_data = ''
        self.read_extracted_data = ''
        self.total_read_number = total_read_number
    
    def connect(self):
        self.connection = serial.Serial(self.port,self.baudrate,timeout=0)
        self.connected = True 
        # self.read_thread = threading.Thread(target=self.read_data_loop,daemon=True)
        # self.read_thread.start()
        self.read_data_loop()
    
    def disconnect(self):
        self.connection.close()
        self.connected = False
    
    def check_connection(self):
        if not self.connection.is_open:
            self.connected = False 
            self.disconnect()


    def read_data_loop(self):
        self.check_connection();
        while self.connected and self.data_control.length() < total_read_number:
            try:
                chunk_data = self.connection.readline();
            except:
                self.disconnect();
                pass
            try:
                self.read_raw_data += chunk_data.decode();
            except UnicodeDecodeError:
                print("error")
                
            if b'\n' in chunk_data:
                if (len(self.read_raw_data)):
                    # print(self.read_raw_data);
                    self.read_extracted_data = self.extract_data(
                        self.read_raw_data)
                    if(self.read_extracted_data):
                        self.data_control.append(self.read_extracted_data);
                    self.read_raw_data = ''
        
                sleep(.01)
            else:
                sleep(.2)
    def extract_data(self, string_data):
        splited_arr = string_data.split(';')
        # print(splited_arr);
        splited_arr_length = len(splited_arr)
        extracted_data = {}
        if splited_arr[0].find(START_STRING) > -1 and splited_arr[splited_arr_length-1].find(END_STRING) > -1:
            for i in range(1, splited_arr_length-1):
                each_data_string = splited_arr[i]
                each_data_splited_arr = each_data_string.split(':')
                if(len(each_data_splited_arr) == 2):
                    extracted_data[each_data_splited_arr[0]] = float(each_data_splited_arr[1])
        return extracted_data

class DataControl():
    def __init__(self,filename):
        self.data = []
        self.filename = filename

    def append(self,d:dict):
        print(d)
        self.data.append(d)

    def get(self)->dict:
        return self.data
    
    def length(self)->int:
        return len(self.data)
    
    def writeCSV(self,columns:List):
        with open(self.filename+'.csv',mode='w') as csv_file:
            data_writer = csv.DictWriter(csv_file,fieldnames=columns)
            data_writer.writeheader()
            for d in self.data:
                data_writer.writerow(d)
    
    def plot(self,x,y):
        xData = []
        yData = []
        for d in self.data:
            xData.append(d[x])
            yData.append(d[y])
        fig = plt.figure()
        plt.plot(xData,yData)
        # plt.show()
        fig.savefig(self.filename+'.png')

    


def serial_connect():
    available_ports = get_available_ports();
    if len(available_ports) == 0:
        print("Please insert a serial port")
    elif len(available_ports) == 1:
        return (available_ports[0],baudrate)
    else:
        print("Select a port:")
        print("Index : port")
        for i,port in enumerate(available_ports):
            print(f'{i} : {port}')
        select_port = 0
        try:
            select_port = int(input("Enter an index: "))

            if(select_port < len(available_ports) and select_port >-1):
                return (port,baudrate)
            else:
                print("Invalid index")

        except:
            print("Invalid input")
    return False


def main_progam(total_read_number,filename):
    port,baudrate = serial_connect()
    print(f'{port} {baudrate}')
    data_control = DataControl(filename=filename)
    serial_connection = SerialConnection(port=port,baudrate=baudrate,data_control=data_control,total_read_number=total_read_number)
    serial_connection.connect()

    # for now column name are fixed
    data_control.writeCSV(columns=['LOAD','DISTANCE'])
    data_control.plot("LOAD","DISTANCE")



if __name__=="__main__":
    baudrate = 9600
    total_read_number = 100
    filename = 'data'
    parser = argparse.ArgumentParser(description="Python serial data read and visualize..")
    parser.add_argument('-c','--command',help='Set command.\n Example: list_ports, plot',required=True)
    parser.add_argument('-n','--number',help=f'Total read number. Defaults: {total_read_number}')
    parser.add_argument('-b','--baudrate',help=f'Baudrate. Default {baudrate}')
    parser.add_argument('-f','--filename',help=f'Filename. Default: {filename}')
    args = parser.parse_args()

    

    if args.command == 'list_ports':
        view_available_ports()
    elif args.command == 'plot':
        if(args.number):
            total_read_number = int(args.number)
        if(args.filename):
            filename = args.filename
        main_progam(total_read_number=total_read_number,filename=filename)

    else:
        print("Unknown command")