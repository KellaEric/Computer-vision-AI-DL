#Librries used
import numpy as np
import cv2 as cv
import time
import psutil
import datetime
import pyttsx3
from random import randint




#Functions for persons detection and counting
class MyPerson:
    tracks = []
    def __init__(self, i, xi, yi, max_age):
        self.i = i
        self.x = xi
        self.y = yi
        self.tracks = []
        self.R = randint(0,255)
        self.G = randint(0,255)
        self.B = randint(0,255)
        self.done = False
        self.state = '0'
        self.age = 0
        self.max_age = max_age
        self.dir = None
    def getRGB(self):
        return (self.R,self.G,self.B)
    def getTracks(self):
        return self.tracks
    def getId(self):
        return self.i
    def getState(self):
        return self.state
    def getDir(self):
        return self.dir
    def getX(self):
        return self.x
    def getY(self):
        return self.y
    def updateCoords(self, xn, yn):
        self.age = 0
        self.tracks.append([self.x,self.y])
        self.x = xn
        self.y = yn
    def setDone(self):
        self.done = True
    def timedOut(self):
        return self.done
    def going_UP(self,mid_start,mid_end):
        if len(self.tracks) >= 2:
            if self.state == '0':
                if self.tracks[-1][1] < mid_end and self.tracks[-2][1] >= mid_end: 
                    state = '0'
                    self.dir = 'up'
                    return True
            else:
                return False
        else:
            return False
    def going_DOWN(self,mid_start,mid_end):
        if len(self.tracks) >= 2:
            if self.state == '0':
                if self.tracks[-1][1] > mid_start and self.tracks[-2][1] <= mid_start: 
                    state = '1'
                    self.dir = 'down'
                    return True
            else:
                return False
        else:
            return False
    def age_one(self):
        self.age += 1
        if self.age > self.max_age:
            self.done = True
        return True
class MultiPerson:
    def __init__(self, persons, xi, yi):
        self.persons = persons
        self.x = xi
        self.y = yi
        self.tracks = []
        self.R = randint(0,255)
        self.G = randint(0,255)
        self.B = randint(0,255)
        self.done = False
        
currentframe =0

def new_func():
    engine = pyttsx3.init()
    voice = engine.getProperty('voices')
    engine.setProperty('voice',voice[0].id)
    rate = engine.getProperty('rate')
    engine.setProperty("rate", 120)
    def speak(audio):
       engine.say(audio)
       engine.runAndWait()
    
    speak(" Welcome to our advanced Human monitoring System for Access Bank."
         
"Title:A COMPUTERIZED HUMAN DETECTION AND COUNTING SYSTEM FOR  BANKS USING ACCRA TECHNICAL UNIVERSITY ACCESS  BANK AS A CASE STUDY"
# "BANK AS A CASE STUDY"
#  "Computer Science"
# "students"
# "@author:Kella Eric ID 01201181D"
# "@author:Benjamin Abakah" 
# "@author:Brimah zakiyah Mohammad"
         )
    return speak

speak = new_func()
today = datetime.datetime.now()
d = today.strftime("%A")
di = today.strftime("%d")
m = today.strftime("%b")
Y = today.strftime("%y")
H = datetime.datetime.now().strftime("%H")
M = datetime.datetime.now().strftime("%M:")
S = datetime.datetime.now().strftime("%S")

try:
    data = open(d+' '+' '+str(di)+' '+' '+m+' '+str(Y)+ '.csv',"w",newline='')
except:
    print( "file not found")


cnt_up   = 0
cnt_down = 0
fourcc = cv.VideoWriter_fourcc(*'XVID')
#__path__("/Model/MobileNetSSD_deploy.caffemodel")
output=cv.VideoWriter("Documents"+d+' '+' '+str(di)+' '+' '+m+' '+str(Y)+ "frame"+ '.mp4',fourcc,20.0,(640,480))

out_frame=cv.VideoWriter("Documents/"+d+' '+' '+str(di)+' '+' '+m+' '+str(Y)+ "heat"+  '.mp4',fourcc,20.0,(640,480))

cap = cv.VideoCapture(0)
# address = "http://192.168.43.63:8080/video"
# cap.open(address)

for i in range(19):
    print( i, cap.get(i))

h = 600
w = 1000
frameArea = h*w
areaTH = frameArea/250
print( 'Area Threshold', areaTH)

line_up = int(2*(h/5))
line_down   = int(3*(h/5))

up_limit =   int(1*(h/5))
down_limit = int(4*(h/5))

#This is the boundries of lines for entries and exit.
print( "Red line denotes Enering:",str(line_down))
print( "Blue linedenotes Exiting:", str(line_up))
#print( "The white lines denotes the premises of the bank:", str(line_up, line_down))
line_down_color = (255,3,0)
line_up_color = (0,15,255)
pt1 =  [0, line_down];
pt2 =  [w, line_down];
pts_L1 = np.array([pt1,pt2], np.int32)
pts_L1 = pts_L1.reshape((-1,1,2))
pt3 =  [0, line_up];
pt4 =  [w, line_up];
pts_L2 = np.array([pt3,pt4], np.int32)
pts_L2 = pts_L2.reshape((-1,1,2))

pt5 =  [0, up_limit];
pt6 =  [w, up_limit];
pts_L3 = np.array([pt5,pt6], np.int32)
pts_L3 = pts_L3.reshape((-1,1,2))
pt7 =  [0, down_limit];
pt8 =  [w, down_limit];
pts_L4 = np.array([pt7,pt8], np.int32)
pts_L4 = pts_L4.reshape((-1,1,2))


fgbg = cv.createBackgroundSubtractorMOG2(detectShadows = False)


kernelOp = np.ones((3,3),np.uint8)
kernelOp2 = np.ones((5,5),np.uint8)
kernelCl = np.ones((11,11),np.uint8)


font = cv.FONT_HERSHEY_SIMPLEX
persons = []
max_p_age = 5
pid = 1

while(cap.isOpened()):

 
    ret, frame = cap.read()


    for i in persons:
        i.age_one() 
    fgmask = fgbg.apply(frame)
    fgmask2 = fgbg.apply(frame)

   
    try:
        ret,imBin= cv.threshold(fgmask,200,255,cv.THRESH_BINARY)
        ret,imBin2 = cv.threshold(fgmask2,200,255,cv.THRESH_BINARY)
      
        mask = cv.morphologyEx(imBin, cv.MORPH_OPEN, kernelOp)
        mask2 = cv.morphologyEx(imBin2, cv.MORPH_OPEN, kernelOp)
       
        mask =  cv.morphologyEx(mask , cv.MORPH_CLOSE, kernelCl)
        mask2 = cv.morphologyEx(mask2, cv.MORPH_CLOSE, kernelCl)
    except:
        print('Status')
        print( 'EXited  Bank Premisis:',cnt_up)
        print ('Entered inside Bank Premisis:',cnt_down)
        break
  
    contours0, hierarchy = cv.findContours(mask2,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
    
    for cnt in contours0:
        cv.imwrite("frames/"+str(' '+str(di)+' '+' '+' '+m+' '+str(Y))+' '+str(currentframe)+'.jpg',frame)
        currentframe+=1
        area = cv.contourArea(cnt)
        if area > areaTH:
      
            
            M = cv.moments(cnt)
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            x,y,w,h = cv.boundingRect(cnt)

            new = True
            if cy in range(up_limit,down_limit):
                for i in persons:
                    if abs(x-i.getX()) <= w and abs(y-i.getY()) <= h:
                       
                        new = False
                        i.updateCoords(cx,cy)  
                        if i.going_UP(line_down,line_up) == True:
                            
                            cnt_up += 1;
                            print( "ID:",i.getId(),'entering Bank',time.strftime("%c"),"Human Detection")
                            data.write("ID: "+str(i.getId())+' Exiting Bank ' + time.strftime("%c") + '\n')
                            
                        elif i.going_DOWN(line_down,line_up) == True:
                           
                            cnt_down += 1;
                            print( "ID:",i.getId(),'exit the area on',time.strftime("%c"),"Tracking system")
                            data.write("ID: " + str(i.getId()) + ' Exiting.. ' + time.strftime("%c") + '\n')
                        break
                    if i.getState() == '1':
                        if i.getDir() == 'down' and i.getY() > down_limit:
                            i.setDone()
                        elif i.getDir() == 'up' and i.getY() < up_limit:
                            i.setDone()
                    if i.timedOut():
                      
                        index = persons.index(i)
                        persons.pop(index)
                        del i    
                if new == True:
                    p = MyPerson(pid,cx,cy, max_p_age)
                    persons.append(p)
                    pid += 1     

            circle = cv.circle(frame,(cx,cy), 5, (0,0,255), -1)
            img = cv.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)            
            
            

    for i in persons:

        cv.putText(frame, str(i.getId()),(i.getX(),i.getY()),font,0.3,i.getRGB(),1,cv.LINE_AA)
        
        cv.imwrite("ID/"+str(' '+str(di)+' '+' '+' '+m+' '+str(Y))+' '+'ID'+str(i.getId())+'.jpg',frame)
    total = cnt_down+cnt_up
    str_up = 'Exit: '+ str(cnt_up)
    str_down = 'Enter: '+ str(cnt_down)
    
    frame = cv.polylines(frame,[pts_L1],False,line_down_color,thickness=2)
    frame = cv.polylines(frame,[pts_L2],False,line_up_color,thickness=2)
    frame = cv.polylines(frame,[pts_L3],False,(255,255,255),thickness=1)
    frame = cv.polylines(frame,[pts_L4],False,(255,255,255),thickness=1)
    imggray = cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
    cv.putText(frame, str_up ,(50,60),font,0.6,(255,255,255),2,cv.LINE_AA)
    cv.putText(frame, str_up ,(50,40),font,0.6,(0,0,255),1,cv.LINE_AA)
    cv.putText(frame, str_down ,(50,90),font,0.6,(255,0,255),2,cv.LINE_AA)
    cv.putText(frame, str_down ,(50,90),font,0.6,(255,0,122),1,cv.LINE_AA)
    cv.putText(frame,f"Total number : {total}" ,(50,140),font,0.6,(255,0,0),1,cv.LINE_AA)
    cv.putText(frame, f"Status Detecting Live ... " ,(50,190),font,0.6,(255,0,0),1,cv.LINE_AA)
    cv.rectangle(frame, (0,0), (6400, 40), (215, 110, 12), -1)
    cv.putText(frame, "COUNTING SYSTEM FOR BANKS ", (30,30), 
                       cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv.LINE_AA)
    
    cv.rectangle(frame, (0,0), (25, 6440), (215, 110, 12), -1)
    hsv = cv.cvtColor(frame,cv.COLOR_BGR2HSV)
    
    
     
    cv.imshow('Human Detection',cv.resize(hsv,(480,480)))
    cv.imshow('Real Time Traking',cv.resize(frame,(480,480)))
    out_frame.write(frame)
    output.write(hsv)


    key = cv.waitKey(1) & 0xff
    if key == ord('q'):
        break
     
speak(f" Peole Exit {str_up}")
speak(f"  People Entered {str_down}")
speak(f"total number of people{total}")
data.flush()
data.close()
if data.close():
    print( "system exited")


cap.release()
cv.destroyAllWindows()
