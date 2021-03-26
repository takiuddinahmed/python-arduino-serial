import argparse
import os
import sys

import serial 
from serial.tools import list_ports


START_STRING = "START"
END_STRING = "END"

port = ''


if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Python serial data read and visualize..")
