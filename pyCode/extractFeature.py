'''
Created on Feb 19, 2016

@author: zhang
'''
import argparse
import re
import math
from math import sqrt
import os
from datetime import datetime



class Line(object):
    def __init__(self, trackingid, dotx, doty):
        self.trackingid = trackingid
        self.dotx = dotx
        self.doty = doty

    def out_Line_file_first_line(self,output):
        with open(output, mode='a') as f:
            f.write("tracking_id,time_period,X_start,x_stop,y_start,y_stop,mid_stroke_pressure,mid_stroke_area_covered,mid_finger_width,X_length_of_trajectory,Y_length_of_trajectory,Distance_EndToEnd,Direction,X_speed,Y_speed,mid_trajectory_speed,absolute_velocity,velocity_angle,finger_orient_change\n")
         
    def output(self,lineouput):
        if os.path.isfile(lineouput):
            with open(lineouput, mode='a') as f:
                f.write(self.trackingid)
                f.write(",")
                f.write(str(self.get_period()))  #period =  float(doty.timestamp) - float(dotx.timestamp)
                f.write(",")
                f.write(str(self.dotx.x))  #x_start = dotx.x
                f.write(",")
                f.write(str(self.doty.x))  #x_stop = doty.x
                f.write(",")
                f.write(str(self.dotx.y))  #y_start = dotx.y
                f.write(",")
                f.write(str(self.doty.y))  #y_stop = doty.y
                f.write(",")
                f.write(str(self.get_mid_stroke_pressure()))
                f.write(",")            
                f.write(str(self.get_mid_stroke_area_covered()))
                f.write(",")     
                f.write(str(self.get_mid_finger_width()))
                f.write(",")            
                f.write(str(self.get_x_length_of_trajectory()))
                f.write(",")     
                f.write(str(self.get_y_length_of_trajectory()))
                f.write(",")            
                f.write(str(self.get_distance()))  
                f.write(",")     
                f.write(str(self.get_direction()))
                f.write(",")            
                f.write(str(self.get_x_speed()))
                f.write(",")     
                f.write(str(self.get_y_speed()))
                f.write(",")      
                f.write(str(self.get_mid_trajectory_speed()))
                f.write(",")     
                f.write(str(self.get_absolute_velocity()))
                f.write(",")      
                f.write(str(self.get_velocity_angle()))
                f.write(",")      
                f.write(str(self.get_finger_orient_change()))
                f.write("\n")                 
        else:
            self.out_Line_file_first_line(lineouput)
    
    @classmethod
    def create_lines(self, trackingid, dot_list):
        last_dot= None
        lines = []
        for dot in dot_list:
            if last_dot is not None:
                line = Line(trackingid, last_dot, dot)
                lines.append(line)
            else:
                last_dot = dot
        return lines
    
    def get_sec(self,td):
       # print((td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6)
        return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6

    def get_period(self):
        #print(datetime.strptime(self.doty.timestamp,'%H:%M:%S:%f')- datetime.strptime(self.dotx.timestamp,'%H:%M:%S:%f'))
        return self.get_sec(datetime.strptime(self.doty.timestamp,'%H:%M:%S:%f')- datetime.strptime(self.dotx.timestamp,'%H:%M:%S:%f'))
    
    def get_phone_orient_change(self):
        if self.doty.phone_orient != self.dotx.phone_orient:
            return 1
        else:
            return 0

    def get_mid_stroke_pressure(self):
        return (self.dotx.pressure+ self.doty.pressure)/2

    def get_mid_stroke_area_covered(self):
        return (self.dotx.area + self.doty.area)/2
    
    def get_mid_finger_width(self):
        return (self.dotx.width + self.doty.width)/2
    
    def get_x_length_of_trajectory(self):
        return (self.doty.x + self.dotx.x)/2
    
    def get_y_length_of_trajectory(self):
        return (self.doty.y + self.dotx.y)/2
    
    def get_distance(self):
        return sqrt( pow((self.doty.y - self.dotx.y),2) + pow((self.doty.x - self.dotx.x),2) )
    
    def get_direction(self):
        if self.doty.x - self.dotx.x == 0:
            return 0
        else:
            return (self.doty.y - self.dotx.y)/(self.doty.x - self.dotx.x)
        
    def get_x_speed(self):
        #print(self.get_period())
        #print(self.get_x_length_of_trajectory()/self.get_period())
        return (self.get_x_length_of_trajectory()/self.get_period())

    def get_y_speed(self):
        return (self.get_y_length_of_trajectory()/self.get_period())        
    
    def get_mid_trajectory_speed(self):
        return (self.get_distance()/self.get_period())
        
    def get_absolute_velocity(self):    
        return math.hypot(self.get_x_speed(), self.get_y_speed())  # euclidean norm Vx^2+Vy^2
    
    def get_velocity_angle(self):
        return math.atan2(self.get_y_speed(), self.get_x_speed())
    
    def get_finger_orient_change(self):               #Start with ff, then the orient is negative, start with 00, then the finger orient is positive,last minus them
        return self.doty.finger_orient-self.dotx.finger_orient
        #if self.doty.finger_orient.startswith('ff'):
        #    tempy = -int(self.doty.finger_orient[-2],16)
        #else:
        #    tempy = int(self.doty.finger_orient[-2],16)
        #if self.dotx.finger_orient.startswith('ff'):
        #    tempx = -int(self.dotx.finger_orient[-2],16)
        #else:
        #    tempx = int(self.dotx.finger_orient[-2],16)
        #return tempy - tempx   
    
    #def get_acceleration(self):
    #    return ()

class Dot(object):
    def __init__(self, timestamp, phone_orient, time, trackingid, x, y, pressure, touch_major, touch_minor, finger_orient):
        self.timestamp = timestamp
        self.phone_orient = phone_orient
        self.time = time
        self.trackingid = trackingid
        self.x = int(x,16)
        self.y = int(y,16)
        self.pressure = int(pressure,16)
        self.area = self.get_area(touch_major,touch_minor)
        self.width = int(touch_major,16)
        self.finger_orient = self.get_finger_orient(finger_orient)
        #print(self.x)

    def out_Dot_file_first_line(self,output):
        with open(output, mode='a') as f:
            f.write("timestamp,phone_orient,time,tracking_id,X_start,y_stop,mid_stroke_pressure,stroke_area_covered,finger_width,finger_orient\n")

    def output(self,dotouput):
        if os.path.isfile(dotouput):
            with open(dotouput, mode='a') as f:
                f.write(self.timestamp)
                f.write(",")
                f.write(self.phone_orient)
                f.write(",")
                f.write(self.time)
                f.write(",")
                f.write(self.trackingid)
                f.write(",")
                f.write(str(self.x))
                f.write(",")
                f.write(str(self.y))
                f.write(",")
                f.write(str(self.pressure))
                f.write(",")
                f.write(str(self.area))
                f.write(",")            
                f.write(str(self.width))
                f.write(",")            
                f.write(str(self.finger_orient))
                f.write("\n") 
        else:
            self.out_Dot_file_first_line(dotouput)
            
    @classmethod
    def create_dot(cls, row):
        dot = Dot(row["timestamp"],row["cell_orient"],row["time"], row["tracking_id"], row["x_coordinate"], row["y_coordinate"], row["pressure"], row["touch_major"], row["touch_minor"], row["finger_orient"])
        return dot
    
    def get_area(self, major, minor):
        return math.pi*int(major,16)*int(minor,16)
    
    def get_finger_orient(self,finger_orient):
        if finger_orient.startswith('ff'):
            return -int(finger_orient[-2],16)
        else:
            return  int(finger_orient[-2],16)
            
            
class Action(object):
    def __init__(self, trackingid):
        self.dot_list = []   
        self.trackingid = trackingid
        
    def add_dot(self, dot):   #input 
        self.dot_list.append(dot)
    
    def output(self, dotfile, linefile):  # output
        lines = Line.create_lines(self.trackingid, self.dot_list)
        #print(len(lines))
        for line in lines:
            print("there is line\n")
            line.output(linefile)
            
        if not lines or len(lines) < 1:
            for dot in self.dot_list:
                print("there is dot\n")
                dot.output(dotfile)
    
        
def parse_file(filename):
    #print ("start parsing file %s" %(filename))
    actions = []
    last_action = None
    with open(filename, mode='r') as f:
        for line in f:      
            line = line.strip("\n").strip()
            check = re.compile("^(\d+\:\d+\:\d+\:\d+)\,(\d)\,(\d+\.\d+)\,(\w+)\,(\w+)\,(\w+)\,(\w+)\,(\w+)\,(\w+)\,(\w+)")
            groups = check.match(line)
            row = dict()     # dict() key-value hashmap
            row["timestamp"]=groups.group(1).strip()  
            row["cell_orient"]=groups.group(2).strip()
            row["time"]=groups.group(3).strip()
            row["tracking_id"]=groups.group(4)
            row["x_coordinate"]=groups.group(5)
            row["y_coordinate"]= groups.group(6)
            row["pressure"]=groups.group(7)
            row["touch_major"]= groups.group(8)
            row["touch_minor"]=groups.group(9)
            row["finger_orient"]=groups.group(10)
            if last_action is None or last_action.trackingid != row["tracking_id"]:   #if tracking id is new or no tracking id, means new action
                last_action = Action(row["tracking_id"])      #new an action object
                actions.append(last_action)      #same tracking_id in one action object
            dot = Dot.create_dot(row)    #every row is a dot, create dot object
            last_action.add_dot(dot)     #add dot object into action object
            
    return actions
                   
def getParser():
    usage="""
    {program} filename dot_output_filename line_output_filename """
    
    parser = argparse.ArgumentParser(description="extract Feature", usage=usage)
    parser.add_argument("filename",help="input filename")
    parser.add_argument("lineoutput",help="Line_output filename")
    parser.add_argument("dotouput",help="Dot_output filename")
    args= parser.parse_args()
    return args   

def main():
    args = getParser()
    actions = parse_file(args.filename)
    #print(len(actions)) 
    for action in actions:               #every stroke are action. action.output will identify the dot and line action,and output to different csv
        action.output(args.lineoutput,args.dotouput)
    
if __name__ == "__main__":
    main()
            
            