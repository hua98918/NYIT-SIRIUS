'''
Created on Feb 8, 2016

@author: zhang
'''

import argparse
import re
import os, sys


class MT_GROUP(object):
    def __init__(self, dest_file):
        self.lines = []
        self.trackingid = None
        self.dest_file = dest_file
    
    def output(self):
        for line in self.lines:
            self.output_file(line.value)
    '''
    according to the trackingid, if trackingId = fffffff, output the whole group, means end of the swipe.
    The begin of the trackingID always have number/data. The continious trackingId always 00000000, update the tracking ID with first trackingID

    ''' 
    def append_line(self, line):    
        line.analyze()
        if line.value["tracking_id"] == "ffffffff":
            self.output()
            self.renew()
        else:
            if len(self.lines) == 0:
                self.trackingid = line.value["tracking_id"]
            else:
                line.value["tracking_id"] = self.trackingid
            self.lines.append(line)
         
    def output_file(self, row):
        with open(self.dest_file, mode='a') as f:
            f.write(row["timestamp"])
            f.write(",")
            f.write(str(row["cell_orient"]))
            f.write(",")
            f.write(row["time"])
            f.write(",")
            f.write(row["tracking_id"])
            f.write(",")
            f.write(row["X_coordinate"])
            f.write(",")
            f.write(row["y_coordinate"])
            f.write(",")
            f.write(row["pressure"])
            f.write(",")
            f.write(row["touch_major"])
            f.write(",")            
            f.write(row["touch_minor"])
            f.write(",")
            f.write(row["finger_orient"])
            f.write("\n") 
    
    def renew(self):
        self.lines = []
        self.trackingid = None        
            
            
class MT_LINE(object):
    def __init__(self):
        self.cache=[]
        self.value = None
        
    def append(self, row):
        self.cache.append(row)
    
    def create_row(self):
        row=dict()
        row["timestamp"] = "00:00:00:000"
        row["cell_orient"] = "0"
        row["time"] = "00000000"
        row["tracking_id"] = "00000000"
        row["X_coordinate"] = "00000000"
        row["y_coordinate"] = "00000000"
        row["pressure"] = "00000000"
        row["touch_major"] = "00000000"
        row["touch_minor"] = "00000000"
        row["finger_orient"] = "00000000"
        return row
            
    def analyze(self):
        print("start analyzing......")
        output_row = self.create_row()
        for row in self.cache:
            output_row["timestamp"] = row["timestamp"]
            output_row["cell_orient"] = row["cell_orient"]
            output_row["time"] = row["time"]
            if row["event_id"]=="ABS_MT_TRACKING_ID":
                output_row["tracking_id"]=row["number"]
            elif row["event_id"]=="ABS_MT_POSITION_X":
                output_row["X_coordinate"]= row["number"]
            elif row["event_id"]=="ABS_MT_POSITION_Y":
                output_row["y_coordinate"]= row["number"]
            elif row["event_id"]=="ABS_MT_PRESSURE":
                output_row["pressure"]= row["number"]    
            elif row["event_id"]=="ABS_MT_TOUCH_MAJOR":
                output_row["touch_major"]= row["number"]       
            elif row["event_id"]=="ABS_MT_TOUCH_MINOR":
                output_row["touch_minor"]= row["number"]
            elif row["event_id"]=="003c":
                output_row["finger_orient"]= row["number"]
        self.value = output_row 
               
        
def parse_file(filename,output):
    print ("start parsing file %s, and output to %s" %(filename,output))
    if os.path.exists(output): #If the output is not exists, return false
        os.remove(output)
    #out_file_first_line(output)
    with open(filename, mode='r') as f:
        mt=MT_LINE()
        group = MT_GROUP(output)
        for line in f:
            # dict() key-value hashmap
            line = line.strip("\n").strip()
            if len(line) == 12:
                row = dict()
                row["timestamp"] = line
            elif line == "Portrait":
                row["cell_orient"] = 0
            elif line == "Landscape":
                row["cell_orient"] = 1
            else:
                check = re.compile("^\[(.*)\]\s*(\w+)\s*(\w+)\s*([A-Fa-f0-9]+)")
               # print(line)
                groups = check.match(line)
                row["time"]=groups.group(1).strip()  #group(0)is the whole line
                row["event"]=groups.group(2)
                row["event_id"]=groups.group(3)
                row["number"]= groups.group(4)
                if row["event"]=="EV_SYN":   #SYN event means end of the line
                    group.append_line(mt)    #throw line into event group
                    mt = MT_LINE()
                mt.append(row)
            

        
                   
def getParser():
    usage="""
    {program} filename output """
    
    parser =argparse.ArgumentParser(description="Create DataBase", usage=usage)
    parser.add_argument("filename",help="input filename")
    parser.add_argument("output",help="output filename")
    args= parser.parse_args()
    return args

def out_file_first_line(output):
    with open(output, mode='a') as f:
        f.write("timestamp,cell_orient,time,tracking_id,X_coordinate,Y_coordinate,pressure,touch_major,touch_minor,finger_orient\n")
            
def main():
    args = getParser()
    parse_file(args.filename,args.output)
    
if __name__ == "__main__":
    main()
            
            