#To Do:
#2. Model landing 'legs'

#Imports: Tk for graphics, time for running loop, math for angles,
#random for terrain and initial angle+velocity
from tkinter import *
import time
import math
from random import randrange,uniform

#initialize screen
screen = Tk()
screen.geometry('500x500')

canvas = Canvas(screen, width=500, height=500, background="white")
canvas.pack()

#Keys pressed
class held_keys:

    def __init__(self):
        self.q = False
        self.e = False
        self.w = False

#Lander class
class Lander:

    #Initialize variables
    def __init__(self):
        #Angular velocity
        self.avel = 0
        #Angle
        self.angle = randrange(170,190)
        #Coordinates
        self.x = 250
        self.y = 50
        #Velocity in x and y directions
        self.xvel = uniform(-1,1)
        self.yvel = 0

    #Functions for turning left and right
    def r_left(self):
        if self.avel >= -25: self.avel -= 0.2

    def r_right(self):
        if self.avel <= 25: self.avel += 0.2

    #Main throttle
    def mthrottle(self):
        #find x and y impacts from thrust
        thr = find_thrust(self.angle)
        #Change velocity based on thrust
        self.xvel += (thr[1]/100)*0.2
        self.yvel += (thr[0]/100)*0.2

    #SAS control
    def sas(self):
        if self.avel > 0:
            self.avel -= 0.1
        elif self.avel < 0: self.avel += 0.1

#Find change in velocity based on rocket angle
def find_thrust(angle):
    #Find what quadrant the motor is pointing in
    q = int(angle/90)
    #Find where in the quadrant the motor is pointed
    tx = (angle % 90)/90 * 100
    #Invert thrustx based on quadrant
    if q == 1 or q == 3: tx = 100-tx
    #Define thrust in y direction
    ty = 100-tx
    #Return total thrust based on quadrant
    if q == 0: return [ty,tx]
    if q == 1: return [-1*(ty),tx]
    if q == 2: return [-1*(ty),-1*(tx)]
    if q == 3: return [ty,-1*(tx)]

#Initial draw function
def draw_simple():
    #Reset canvas
    canvas.delete("all")
    #Draw ground
    draw_ground(ground)
    #Draw bottom circle of rocket
    canvas.create_oval(lander.x,lander.y,lander.x+10,lander.y+10,fill='black')
    #Draw top circle of rocket
    p2 = [math.sin(math.radians(lander.angle))*25,math.cos(math.radians(lander.angle))*25]
    canvas.create_oval(lander.x+p2[0],lander.y+p2[1],lander.x+p2[0]+10,lander.y+p2[1]+10,fill='black')

#Draws the ground
def draw_ground(plist):
    for x in range(0,len(plist)):
        if x != 0:
            canvas.create_line(plist[x-1][0],plist[x-1][1],plist[x][0],plist[x][1],fill='black')
        else:
            canvas.create_line(plist[0][0],plist[0][1],plist[1][0],plist[1][1],fill='black')

#Finds exact y value of point on ground
def gen_precise_collider(plist,width,point):
    point = int(point)
    #Finds endpoints based on the closest values of sorted lists
    dist_list = sorted([[point-terr_point[0],terr_point[0]] for terr_point in plist])
    dist_list_negative = sorted([dist_list.pop(ind) for ind in [0 for _ in range(len(dist_list))] if dist_list[ind][0] < 0])
    end_x = [dist_list[0][1],dist_list_negative[-1][1]]
    endpoints = [point for point in plist if point[0] in end_x]
    print(endpoints,point)
    #Returns y-value for given x-value
    return find_y(endpoints[0],endpoints[1],point)

#Solves a linear equation to find the point on a line based on an x-value
def find_y(p1,p2,x):
    m = (p2[1]-p1[1])/(p2[0]-p1[0])
    b = p1[1]-m*p1[0]
    return int(m*x + b)

#Resets all variables
def restart():
    global lander,crashed,landed,l_text,sas_flag,ground
    lander = Lander()
    time.sleep(1)
    print('\n')
    sas_flag = False
    landed,crashed = False,False
    ground = create_ground(8,50,150,500)
    screen.bind('<KeyPress>',detected_keydown)
    screen.bind('<KeyRelease>',detected_keyup)
    screen.bind('<t>',enable_sas)
    if l_text: l_text.destroy()
    draw_simple()

#Checks collision with ground
def check_collision():
    global crashed,landed,l_text,ground
    #Checks if rocket is out of bounds
    if lander.x >= 500 or lander.x <= 0 or lander.y <= 0 or landed: restart()
    #Checks for if rocket is near ground
    y = gen_precise_collider(ground,500,lander.x) - 10
    print(lander.y, y)
    if lander.y >= y:
        #If angle is mostly vertical and little horizontal and vertical speed:
        if lander.xvel+lander.yvel <= 1 and lander.angle >= 170 and lander.angle <= 190 and crashed == False:
            landed = True
            l_text = Label(text='You Landed!')
            l_text.place(x=200,y=200)
        #If fails the speed check:
        else:
            crashed,landed = True,True
            l_text = Label(text='You Crashed!')
            l_text.place(x=200,y=200)
            return True

#Function to enable SAS
def enable_sas(event):
    global sas_flag
    if sas_flag: sas_flag = False
    else: sas_flag = True

#Displays flight information to the player
def display_info():
    global disp_text
    if disp_text: disp_text.destroy()
    disp_text = Label(text='SAS: {} \n ALT: {} \n ANGLE: {} \n V_SPEED:{} \n H_SPEED:{}'.format(sas_flag,int(450-lander.y),int(180-lander.angle),int(lander.yvel*10),round(lander.xvel*10)))
    disp_text.place(x=350,y=25)

#Creates the ground model
def create_ground(points,lower,upper,width):
    plist = []
    curr_y = 0
    for x in range(points):
        #If x is even: set y value of new point to random
        if x % 2 == 0: curr_y = width - randrange(lower,upper)
        #Finds approximate x value for each point
        default_x = int((x/points)*width)
        #Adds new points to list
        if x != 0 and x != points-1: plist.append([randrange((default_x - int(width/(points*2))),(default_x + int(width/(points*2)))),curr_y])
        #Special cases for start and end of list
        elif x == 0: plist.append([0,curr_y])
        else: plist.append([width,curr_y])
    return plist

#Detects keydown
def detected_keydown(e):
    char = e.char
    if char == 'q': keys.q = True
    if char == 'e': keys.e = True
    if char == 'w': keys.w = True

def detected_keyup(e):
    char = e.char
    if char == 'q': keys.q = False
    if char == 'e': keys.e = False
    if char == 'w': keys.w = False

#Initializes variables
keys = held_keys()
l_text = None
disp_text = None
lander = Lander()
landed = False
crashed = False
sas_flag = False
ground = create_ground(8,50,150,500)

#Binds toggle keys
screen.bind('<t>',enable_sas)

#Binds press keys
screen.bind('<KeyPress>',detected_keydown)
screen.bind('<KeyRelease>',detected_keyup)

while True:
    if keys.q: lander.r_right()
    if keys.e: lander.r_left()
    if keys.w: lander.mthrottle()
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
