import cv2
from cv2 import cv
from PIL import ImageGrab
import numpy as np
import os, sys, time, win32api, win32con, text_send, QCV

cap = cv2.VideoCapture(0)

class Paladin_Class(object):

    def __init__(self, name):
        self.name = name
        self.res_bar_loc = [(96,79),(181,95)]
        self.res_width = self.res_bar_loc[1][0] - self.res_bar_loc[0][0]
        self.res_height = self.res_bar_loc[1][1] - self.res_bar_loc[0][1]
        self.resource_bar = None
        self.resource_num = 0
        self.cds = {'holy_shock': 0, 'current_cast': 0, 'holy_power': 0}
        self.holy_shock_cd = 0

    def update_resource_count(self, img):
        x = QCV.color_thresh(img, 200)
        if x == 0:
            self.resource_num = 0
        elif x == 16:
            self.resource_num = 1
        elif x == 24:
            self.resource_num = 2
        elif x > 30:
            self.resource_num = 3
        self.cds['holy_power'] = self.resource_num
    def update(self, frame):
        self.resource_bar = frame[self.res_bar_loc[0][1]:self.res_bar_loc[0][1]+self.res_height, self.res_bar_loc[0][0]:self.res_bar_loc[0][0]+self.res_width]
        #cv2.imshow('resource',self.resource_bar)
        self.update_resource_count(self.resource_bar)

    def logic(self, pty):
        a = pty.roster_health.keys()
        min_health = np.min(a)
        player = pty.roster_health[min_health]
        if player.health < 60 and player.health != 0:
            mousePos(player.pos)
            leftClick()
            leftClick()
            
            if sum(pty.list_health) < 400:
                #spell2spell("?/cast divine shield?")
                flash_heal(self.cds)
            else:
                Divine_light(self.cds)

        if player.health < 90 and player.health != 0:
            mousePos(player.pos)
            leftClick()
            leftClick()
            #print(sum(pty.list_health))

            if sum(pty.list_health) < 400:
                #spell2spell("?/cast divine shield?")
                flash_heal(self.cds)
            else:
                if all(i <= 95 for i in pty.list_health):
                    spell2spell("?/cast holy radiance?")

                else:
                    holy_light(self.cds)

class Player(object):

    def __init__(self, pos, name):
        self.name = name
        self.health = 100
        self.debuffs = 0
        self.buffs = 0
        self.pos = pos

    def update(self):
        pass
class Party(object):

    def generate_roster(self, num_players):

        for i in range(num_players):
            self.roster.append(Player((self.ytop+i*self.unit_height+self.unit_height/2,self.frame_width/2 + self.xlef), "party"+str(i+1)))
        for player in self.roster:
            print(player.pos)
    
    def __init__(self, xlef=28, ytop=143, xrit=160, ybot=500):
        self.xlef = xlef
        self.ytop = ytop
        self.xrit = xrit
        self.ybot = ybot

        self.frame_left = xlef
        self.frame_right = xrit
        self.frame_width = xrit-xlef
        self.frame_height = ybot - ytop
        self.unit_height = self.frame_height/5

        self.roster = []
        self.roster_health = {}
        self.list_health = []
        self.generate_roster(5)

    def update(self, img):
        self.update_health(img)

    def update_health(self, img):
        self.roster_health = {}
        self.list_health = []
        for player in self.roster:
            dead_px_count = 0
            for pixel in range(self.frame_left,self.frame_right):
                if img.item(player.pos[0],pixel,1) < 100:
                    dead_px_count += 1
            player.health = 100 - (dead_px_count*100/self.frame_width)
            if player.health < 5:
                player.health = 101
            self.roster_health[player.health] = player
            self.list_health.append(player.health)
            print(self.list_health)

def resizeImage(img):
    dst = cv2.resize(img, None, fx=0.60, fy=0.65, interpolation = cv2.INTER_LINEAR)
    return dst

def leftClick():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
    time.sleep(.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)

def holy_light(cds):
    casttime = 2.25
    if time.clock()-cds.get('current_cast') > 0:
        if cds.get('holy_power') == 3:
            spell2spell('?/cast eternal flame?')
        elif holy_shock(cds):
            spell2spell('?/cast holy light?')
            time.sleep(.1)
            cds['current_cast'] = time.clock()+casttime

def Divine_light(cds):
    casttime = 2.25
    if time.clock()-cds.get('current_cast') > 0:
        if cds.get('holy_power') == 3:
            spell2spell('?/cast eternal flame?')
        elif holy_shock(cds):
            spell2spell('?/cast divine light?')
            time.sleep(.1)
            cds['current_cast'] = time.clock()+casttime

def flash_heal(cds):
    if holy_shock(cds):
        spell2spell('?/cast flash of light?')
        time.sleep(.1)

def holy_shock(cds):
    if time.clock()-cds.get('holy_shock') > 6:
        spell2spell('?/cast holy shock?')
        time.sleep(.1)
        cds['holy_shock'] = time.clock()
        return -1
    else:
        return 1

def follow_path(me):
    if time.clock()-me.cds.get('current_cast') > 0:
        spell2spell("?/targetfriend?")
        spell2spell("?/follow?")
    else:
        spell2spell("?/target marrul?")
        spell2spell("?/follow?")


def mousePos(cord):
    win32api.SetCursorPos((cord[1], cord[0]))
     
def get_cords():
    x,y = win32api.GetCursorPos()
    print(str(x) + " " + str(y))


def PIL_to_cv(im):

	# PIL RGB 'im' to CV2 BGR 'imcv'
	imcv = np.asarray(im)[:,:,::-1].copy()
	# Or
	imcv = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR)
	 
	# To gray image
	#imcv = np.asarray(im.convert('L'))
	# Or
	#imcv = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2GRAY)
	return imcv

def spell2spell(text):
    for i in text:
        text_send.press(i)

pty = Party()
me = Paladin_Class("marrul")
time.clock()

while(True):

    # Capture frame-by-frame
    #Webcam

    ret, frame = cap.read()
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    #Screen
    screencap = ImageGrab.grab()
    screencap = PIL_to_cv(screencap)


    pty.update(screencap)
    me.update(screencap)
    me.logic(pty)
    if not win32api.GetAsyncKeyState(0x11):
        follow_path(me)
    # print(pty.list_health)

    #rolls
    # if screencap[914,860,2] > 150:
    #     mousePos((862,917))
    #     leftClick()
    #     leftClick()

   #holy_light(me.cds)
    #src = cv.fromarray(screencap)
    #screencap = cv2.Laplacian(screencap,cv2.CV_64F)
    #cv.Smooth(src,src,cv.CV_GAUSSIAN,5,5)
    
    # img = screencap
    # w, h, d = img.shape

    # for row in range(0, h):
    #     for column in range(0, w):
    #         if img.item(column,row,1) < 120:
    #             img[column,row,0] = 0
    #             img[column,row,1] = 0
    #             img[column,row,2] = 0
    # screencap = img
    # Display the resulting frame
    
    screencap = resizeImage(screencap)
    cv2.imshow('frame',screencap)
    if cv2.waitKey(1) & 0xFF == ord('E'):
        break

    if win32api.GetAsyncKeyState(0x1B):
        break

cv2.destroyAllWindows()