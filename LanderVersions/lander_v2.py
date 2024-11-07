#Randomly generated terrain

from tkinter import *
import time
import math
import numpy as np
from random import randrange,uniform

screen = Tk()
screen.geometry('500x500')

canvas = Canvas(screen, width=500, height=500, background="white")
canvas.pack()

class Lander:

    def __init__(self):
        self.avel = 0
        self.angle = randrange(170,190)
        self.x = 250
        self.y = 50
        self.xvel = uniform(-1,1)
        self.yvel = 0

    def r_left(self,event):
        if self.avel >= -25: self.avel -= 0.4

    def r_right(self,event):
        if self.avel <= 25: self.avel += 0.4

    def mthrottle(self,event):
        thr = find_thrust(self.angle)
        self.xvel += (thr[1]/100)*1
        self.yvel += (thr[0]/100)*1

    def sas(self):
        if self.avel > 0:
            self.avel -= 0.1
        elif self.avel < 0: self.avel += 0.1

def find_thrust(angle):
    q = int(angle/90)
    tx = (angle % 90)/90 * 100
    if q == 1 or q == 3: tx = 100-tx
    ty = 100-tx
    if q == 0: return [ty,tx]
    if q == 1: return [-1*(ty),tx]
    if q == 2: return [-1*(ty),-1*(tx)]
    if q == 3: return [ty,-1*(tx)]

def draw_simple():
    canvas.delete("all")
    draw_ground(ground)
    canvas.create_oval(lander.x,lander.y,lander.x+10,lander.y+10,fill='black')
    p2 = [math.sin(math.radians(lander.angle))*25,math.cos(math.radians(lander.angle))*25]
    canvas.create_oval(lander.x+p2[0],lander.y+p2[1],lander.x+p2[0]+10,lander.y+p2[1]+10,fill='black')

def draw_ground(plist):
    for x in range(0,len(plist)):
        if x != 0:
            canvas.create_line(plist[x-1][0],plist[x-1][1],plist[x][0],plist[x][1],fill='black')
        else:
            canvas.create_line(plist[0][0],plist[0][1],plist[1][0],plist[1][1],fill='black')

def gen_precise_collider(plist,width,point):
    dist_list = sorted([[point-terr_point[0],terr_point[0]] for terr_point in plist])
    dist_list_negative = sorted([dist_list.pop(ind) for ind in [0 for _ in range(len(dist_list))] if dist_list[ind][0] < 0])
    end_x = [dist_list[0][1],dist_list_negative[-1][1]]
    endpoints = [point for point in plist if point[0] in end_x]
    return find_y(endpoints[0],endpoints[1],point)

def find_y(p1,p2,x):
    m = (p2[1]-p1[1])/(p2[0]-p1[0])
    b = p1[1]-m*p1[0]
    return int(m*x + b)
    

def restart():
    global lander,crashed,landed,l_text,sas_flag
    lander = Lander()
    time.sleep(1)
    sas_flag = False
    landed,crashed = False,False
    screen.bind('<q>',lander.r_right)
    screen.bind('<e>',lander.r_left)
    screen.bind('<w>',lander.mthrottle)
    screen.bind('<t>',enable_sas)
    l_text.destroy()
    draw_simple()

def check_collision():
    global crashed,landed,l_text
    if lander.x >= 500 or lander.x <= 0 or lander.y <= 0 or landed: restart()
    if lander.y >= 435:
        if lander.xvel+lander.yvel <= 1 and lander.angle >= 170 and lander.angle <= 190 and crashed == False:
            landed = True
            l_text = Label(text='You Landed!')
            l_text.place(x=200,y=200)
        elif lander.xvel+lander.yvel >= 2:
            crashed,landed = True,True
            l_text = Label(text='You Crashed!')
            l_text.place(x=200,y=200)
            return True

def enable_sas(event):
    global sas_flag
    if sas_flag: sas_flag = False
    else: sas_flag = True

def display_info():
    global disp_text
    if disp_text: disp_text.destroy()
    disp_text = Label(text='SAS: {} \n ALT: {} \n ANGLE: {} \n V_SPEED:{} \n H_SPEED:{}'.format(sas_flag,int(450-lander.y),int(180-lander.angle),int(lander.yvel*10),round(lander.xvel*10)))
    disp_text.place(x=350,y=25)

def create_ground(points,lower,upper,width):
    plist = []
    curr_y = 0
    for x in range(points):
        if x % 2 == 0: curr_y = width - randrange(lower,upper) 
        default_x = int((x/points)*width)
        if x != 0 and x != points-1: plist.append([randrange((default_x - int(width/(points*2))),(default_x + int(width/(points*2)))),curr_y])
        elif x == 0: plist.append([0,curr_y])
        else: plist.append([width,curr_y])
    return plist

l_text = None
disp_text = None           
lander = Lander()
landed = False
crashed = False
sas_flag = False
ground = create_ground(8,50,150,500)

screen.bind('<q>',lander.r_right)
screen.bind('<e>',lander.r_left)
screen.bind('<w>',lander.mthrottle)
screen.bind('<t>',enable_sas)

    
while True:
    display_info()
    lander.angle += lander.avel
    if not landed: lander.yvel += 0.05
    if landed: lander.yvel,lander.xvel = 0,0
    if lander.avel > -0.1 and lander.avel < 0.1: lander.avel = 0
    lander.x += lander.xvel
    lander.y += lander.yvel
    lander.angle = lander.angle % 359
    if sas_flag: lander.sas()
    draw_simple()
    check_collision()
    screen.update()
    time.sleep(0.05)
