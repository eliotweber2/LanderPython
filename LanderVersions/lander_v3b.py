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
        self.f = False

#Generic node class
class Node:

    def __init__(self,init_x,init_y,poss_rotate):
        #Whether this point can cause torque
        self.poss_rotate = poss_rotate
        #Angle and coordiates
        self.x = init_x
        self.y = init_y
        #Velocity in x and y directions, as well as angular velocity
        self.rcsvel = 0
        self.xvel = 0
        self.yvel = 0


    #Functions for turning left and right
def r_left():
    if lander.rcsvel >= -25: lander.rcsvel += 0.2

def r_right():
    if lander.rcsvel <= 25: lander.rcsvel -= 0.2

#Main throttle
def mthrottle():
    #find x and y impacts from thrust
    thr = find_thrust((find_degrees(lander,nose)+360)%359)
    #Change velocity based on thrust
    for node in craft:
        node.xvel += (-1*(thr[0])/100)*0.1
        node.yvel += (-1*(thr[1])/100)*0.1

def sas():
    if lander.rcsvel < 0: lander.rcsvel += 0.05
    elif lander.rcsvel > 0: lander.rcsvel -= 0.05

def find_degrees(p1,p2):
    if p1.x-p2.x == 0: return 90
    else: return math.degrees(math.atan2(lander.y-nose.y,lander.x-nose.x))

def angular_rotate(root_node,craft,deg):
    delta_x_y_lst = []
    for node in craft: delta_x_y_lst.append(find_dist_new_point([root_node.x,root_node.y],[node.x,node.y],deg))
    return delta_x_y_lst

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

def rotate_craft(craft,force_lst):
    delta_lst = [[0,0] for _ in range(len(craft))]
    for rotation in force_lst:
        delta_x_y = angular_rotate(rotation[0],craft,rotation[1])
        for ind in range(len(craft)):
            delta_lst[ind][0] += delta_x_y[ind][0]
            delta_lst[ind][1] += delta_x_y[ind][1]
    for ind in range(len(craft)):
        craft[ind].x += delta_lst[ind][0]
        craft[ind].y += delta_lst[ind][1]


#Initial draw function
def draw_simple():
    #Reset canvas
    canvas.delete("all")
    #Draw ground
    draw_ground(ground)
    for node in craft:
        canvas.create_oval(node.x-2,node.y-2,node.x+2,node.y+2,fill='black')

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
    #Returns y-value for given x-value
    return find_y(endpoints[0],endpoints[1],point)

#Solves a linear equation to find the point on a line based on an x-value
def find_y(p1,p2,x):
    m = (p2[1]-p1[1])/(p2[0]-p1[0])
    b = p1[1]-m*p1[0]
    return int(m*x + b)

#Finds the distance between 2 points on a circle based on a degree of rotation
def find_dist_new_point(p1,p2,deg):
    radius = math.sqrt((p2[0]-p1[0])**2+(p2[1]-p1[1])**2)
    new_x = p1[0] + math.cos(math.radians(deg)) * (p2[0] - p1[0]) - math.sin(math.radians(deg)) * (p2[1] - p1[1])
    new_y = p1[1] + math.sin(math.radians(deg)) * (p2[0] - p1[0]) + math.cos(math.radians(deg)) * (p2[1] - p1[1])
    return [-1*(p2[0] - new_x),-1*(p2[1] - new_y)]

#Resets all variables
def restart():
    global lander,nose,crashed,landed,l_text,sas_flag,ground
    for node in craft: node.xvel,node.yvel,node.rcsvel = 0,0,0
    lander.x,lander.y = 250,50
    nose.x,nose.y = 250,30
    l1.x,l1.y = 240,60
    l2.x,l2.y = 260,60
    time.sleep(1)
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
    if lander.y >= y:
        #If angle is mostly vertical and little horizontal and vertical speed:
        if lander.xvel+lander.yvel <= 1 and crashed == False:
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
    disp_text = Label(text='SAS: {} \n ALT: {} \n V_SPEED:{} \n H_SPEED:{} \n KEYS_PRESSED: \n Q:{} E:{} W:{}'.format(sas_flag,int(450-lander.y),int(lander.yvel*10),round(lander.xvel*10), keys.q,keys.e,keys.w))
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
    if char == 'f': keys.f = True

def detected_keyup(e):
    char = e.char
    if char == 'q': keys.q = False
    if char == 'e': keys.e = False
    if char == 'w': keys.w = False
    if char == 'f': keys.f = False

def game_mainloop():
    cont = True
    while cont:
        if keys.f: cont = False
        if keys.q: r_right()
        if keys.e: r_left()
        if keys.w: mthrottle()
        display_info()
        rot_lst = []
        rot_lst.append([lander, 5*lander.rcsvel])
        rotate_craft(craft,rot_lst)
        for node in craft:
            if not landed: node.yvel += 0.05
            node.x += node.xvel
            node.y += node.yvel
        if lander.rcsvel > -0.1 and lander.rcsvel < 0.1: lander.rcsvel = 0
        if sas_flag: sas()
        draw_simple()
        check_collision()
        screen.update()
        time.sleep(0.05)

#Initializes variables
keys = held_keys()
l_text = None
disp_text = None
lander = Node(250,50,True)
nose = Node(250,30,False)
l1 = Node(240,60,True)
l2 = Node(260,60,True)
landed = False
crashed = False
sas_flag = False
ground = create_ground(8,50,150,500)
craft = [lander,nose,l1,l2]

#Binds toggle keys
screen.bind('<t>',enable_sas)

#Binds press keys
screen.bind('<KeyPress>',detected_keydown)
screen.bind('<KeyRelease>',detected_keyup)

game_mainloop()
