from tkinter import *
import time
import math
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
    canvas.create_line(0,450,500,450,fill='black')
    canvas.create_oval(lander.x,lander.y,lander.x+10,lander.y+10,fill='black')
    p2 = [math.sin(math.radians(lander.angle))*25,math.cos(math.radians(lander.angle))*25]
    canvas.create_oval(lander.x+p2[0],lander.y+p2[1],lander.x+p2[0]+10,lander.y+p2[1]+10,fill='black')

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

l_text = None
disp_text = None           
lander = Lander()
landed = False
crashed = False
sas_flag = False

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
