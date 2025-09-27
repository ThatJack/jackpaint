#Paint.py

from pygame import *
from math import *
from random import *
from tkinter import *
from tkinter import filedialog

Tk().withdraw()
font.init()
mixer.init()
init()

width, height = 1000,900
screen = display.set_mode((width, height))
display.set_caption("Nature Paint") #set window title to nature paint
defFont = font.SysFont("Helvetica", 40)
bigFont = font.SysFont("Helvetica", 80)
medFont = font.SysFont("Helvetica", 60)
smallFont = font.SysFont("Helvetica", 20)
#define fonts for some UI

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

tool = ""
col = (0, 0, 0) #colour of brush/pencil/shape
size = 5 #size of brush/eraser

mx, my = 0, 0
omx, omy = 0, 0 #mx, my from last frame
sx, sy = 150, 60   #mx, my from last click, default at top left of canvas

undo = [] #list of undone frames
redo = [] #list of frames you can redo

#background for program
bgs = []
bgsNames = ["resources/bambooforest.jpg", "resources/desert.jpg", "resources/lake.jpg", "resources/tunnel.jpg"]
for name in bgsNames:
    bgs.append(image.load(name)) #load bg images
    print(f"loading BGs {(bgsNames.index(name)+1)/4 * 100}%") #quick loading message i added so that i could tell the program was doing something when it was loading the images
bgIndex = randint(0, len(bgs) - 1)

#music
songs = ["resources/Forest Sounds.ogg", "resources/Forest Symphony.ogg"]
songIndex = 0 #index of currently playing song

mixer.music.load(songs[songIndex])
mixer.music.play(loops = -1) #play current song

#UI for music player
playerRect = Rect(580, 675, 290, 140) #music player area

paused = False #will be true when music is paused
pauseIcon = ["", "", "", ""] #icon displayed on pause button; pauseBlack, pauseWhite, playBlack, playWhite

musicRects = [Rect(755, 695, 40, 40), Rect(655, 695, 40, 40), Rect(705, 695, 40, 40)]
#               next song                prev song                   pause

#stamps
stamps = []
preStamps = [] #preview of stamp shown in box in sidebar
stampNames = ["resources/tiger.png", "resources/parrot.png", "resources/baboon.png", "resources/fox.png", "resources/bear.png", "resources/pinkflower.png", "resources/rose.png", "resources/dahlia.png"]
for name in stampNames: #load stamp images
    preStamps.append(transform.scale(image.load(name), (80, 80))) #stamp shown on button
    stamps.append(image.load(name))  #stamp that you put on canvas
    print(f"loading Stamps {(stampNames.index(name)+1)/len(stampNames) * 100:.1f}%")
stScale = 200

stIndex = 0
stampRect = Rect(40, 475, 90, 90) #area you drag stamp from
stUpRect = Rect(40, 430, 90, 40)  #change to next stamp in list
stDownRect = Rect(40, 570, 90, 40) #change to previous stamp in list

#function buttons

functions = [Rect(150, 10, 40, 40), Rect(200, 10, 40, 40), Rect(300, 10, 40, 40), Rect(350, 10, 40, 40), Rect(400, 10, 40, 40), Rect(500, 10, 40, 40), Rect(550, 10, 40, 40)]
            #save picture           load picture            add custom bg             add custom stamp      add custom song         undo                redo
funcInfo = ["Save the canvas as a image.", "Load an image to draw on.", "Upload a custom background.", "Upload a custom stamp.", "Upload a custom song.", "Undo previous action.", "Redo previous action."]

clearRect = Rect(40, 360, 90, 40)
leftBGRect = Rect(30, 700, 80, 80)
rightBGRect = Rect(width - 110, 700, 80, 80)

#icon images for function buttons

wIcons = [] #white icons
bIcons = [] #black icons
iconNames = ["resources/saveBlack.png", "resources/saveWhite.png", "resources/uploadBlack.png", "resources/uploadWhite.png", "resources/bgBlack.png", "resources/bgWhite.png", "resources/stampBlack.png", "resources/stampWhite.png", "resources/musicBlack.png", "resources/musicWhite.png", "resources/undoBlack.png", "resources/undoWhite.png", "resources/redoBlack.png", "resources/redoWhite.png"]
for name in iconNames: #load icon images
    if iconNames.index(name) % 2 == 1:
        wIcons.append(image.load(name))
    else:
        bIcons.append(image.load(name))
    print(f"loading icons {(iconNames.index(name)+1) / len(iconNames) * 100:.1f}%")

#tool buttons
tools = [Rect(40, 60, 40, 40), Rect(90, 60, 40, 40), Rect(40, 110, 40, 40), Rect(90, 110, 40, 40), Rect(40, 160, 40, 40), Rect(90, 160, 40, 40), Rect(40, 210, 40, 40), Rect(90, 210, 40, 40)]
tFill = [            2,                 2,                     2,                      2,                    2,                   2,                       2,                       2]
tool_n = [       "pencil",           "eraser",              "brush",               "eyedrop",             "line",              "rect",                 "ellipse",               "triangle"]
info = ["Draw a freehand line.", "Erases drawings and stamps.", "Paint the screen.", "Get the colour on screen.", "Draw a straight line.", "Draw a rectangle. [Hold F to fill] [Hold Left Shift for Square]", "Draw an ellipse. [Hold F to fill] [Hold Left Shift for Circle]", "Draw a triangle. [Hold F to fill]"]
squareFlag = False #for rect and ellipse tool, if shift is held draw a square or circle
shapeIcons = [[(45, 165), (75, 195)], Rect(95, 165, 30, 30), Rect(45, 215, 30, 30), [(95, 240), (110, 215), (125, 240)]]
#            line p1 and p2             #rect icon              #ellipse icon           #triangle points
iconColour = [BLACK, BLACK, BLACK, BLACK] #will be true if hovering and tool is not selected or if not hovering and tool is selected
toolIcons = []
toolIcons_n = ["resources/pencil.png", "resources/eraser.png", "resources/brush.png", "resources/eyedrop.png"]
for name in toolIcons_n:
    toolIcons.append(image.load(name)) #load icon images

fill = size #by default the fill of the shape tools is the size of the brush

increaseRect = Rect(40, 310, 40, 40) #increase brush size
decreaseRect = Rect(90, 310, 40, 40) #decrease brush size

canvasRect = Rect(150, 60, 800, 600)

#RBG Sliders

xpos =     [145,                          145,                          145]                    #x position of slider UI rects
slideBG =  [Rect(150, 675, 255, 40), Rect(150, 725, 255, 40), Rect(150, 775, 255, 40)]          #slider part of slider
lockFlag = [False,                       False,                       False]
sliderUI = [Rect(xpos[0], 670, 10, 50), Rect(xpos[1], 720, 10, 50), Rect(xpos[2], 770, 10, 50)] #change rect x positions in running loop
RGB =      [RED,                         GREEN,                        BLUE]
preRect = Rect(480, 700, 80, 80) #current colour preview

draw.rect(screen, WHITE, canvasRect)
screencap = screen.subsurface(canvasRect).copy() #screencap of canvas that is updated whenever a permanent change is made
bg = screen.copy() #used in eraser, use entire screen so that it does not crash near canvas edges
undo.append(screencap) #start undo list with blank screen

clock = time.Clock()
running = True

#since otherwise i would have had to have these lines in 2 different places in the running loop, i made them functions to save lines

def eraser():
    dx, dy = (mx - omx, my - omy)
    dist = sqrt(dx**2 + dy**2) #distance from current pos to old mouse pos
    screen.blit(bg.subsurface(mx - size, my - size, 2 * size, 2 * size), (mx - size, my - size)) #replace drawing with bg image at that position
    if 150 < omx < 950 and 60 < omy < 660: #only fill in gaps if the mouse pos from last frame was on the canvas
        for d in range(1, int(dist)):
            dotX = omx + d * dx / dist
            dotY = omy + d * dy / dist
            #fill in spaces
            screen.blit(bg.subsurface(int(dotX) - size, int(dotY) - size, 2 * size, 2 * size), (int(dotX) - size, int(dotY) - size)) #fill in gaps

def brush():
    dx, dy = (mx - omx, my - omy)
    dist = sqrt(dx**2 + dy**2) #distance from current pos to old mouse pos
    draw.circle(screen, col, (mx, my), size)
    for d in range(1, int(dist)):
        dotX = omx + d * dx / dist
        dotY = omy + d * dy / dist
        #fill in spaces
        draw.circle(screen, col, (int(dotX), int(dotY)), size)

def drawRect():
    if squareFlag == False:
        tempRect = Rect(sx, sy, mx - sx, my - sy) #define rect
    else: #define perfect square
        if mx - sx > my - sy:
            tempRect = Rect(sx, sy, mx - sx, mx - sx)
        else:
            tempRect = Rect(sx, sy, my - sy, my - sy)
        #if dist from sx to mx > sy to my use x dist, otherwise use y dist
    tempRect.normalize() #normalize for better drawing
    draw.rect(screen, col, tempRect, fill)

def drawEllipse():
    if squareFlag == False:
        tempRect = Rect(sx, sy, mx - sx, my - sy) #define rect for ellipse
    else: #define perfect circle
        if mx - sx > my - sy:
            tempRect = Rect(sx, sy, mx - sx, mx - sx)
        else:
            tempRect = Rect(sx, sy, my - sy, my - sy)
        #if dist from sx to mx > sy to my use x dist, otherwise use y dist
    tempRect.normalize() #normalize for better drawing
    draw.ellipse(screen, col, tempRect, fill)

while running:
    for evt in event.get():
        if evt.type == QUIT:
            running = False
        if evt.type == MOUSEBUTTONDOWN:
            if evt.button == 1:
                #save image
                if functions[0].collidepoint(mx, my):
                    fname = filedialog.asksaveasfilename(defaultextension = ".png")
                    if fname != "": #dont save files with no name
                            image.save(screen.subsurface(canvasRect), fname)

                #load image to draw on
                if functions[1].collidepoint(mx, my):
                    fname = filedialog.askopenfilename(filetypes = [("PNG files", "*.png"), ("JPG files", "*.jpg")]) #2 different allowed types of files
                    if fname[len(fname) - 3:].lower() == "png" or fname[len(fname) - 3:].lower() == "jpg":
                        draw.rect(screen, WHITE, canvasRect)
                        newImage = image.load(fname)
                        if newImage.get_width() > 800 or newImage.get_height() > 600:
                            newImage = transform.scale(newImage, (800, 600))
                        screen.blit(newImage, (150, 60))
                        screencap = screen.subsurface(canvasRect).copy()
                        undo[0] = screencap #change 1st screen in undo list to new bg
                        bg = screen.copy() #copy entire screen so that eraser does not crash near edge of canvas

                #add bg to choices
                if functions[2].collidepoint(mx, my):
                    fname = filedialog.askopenfilename(filetypes = [("PNG files", "*.png"), ("JPG files", "*.jpg")])
                    if fname[len(fname) - 3:].lower() == "png" or fname[len(fname) - 3:].lower() == "jpg":
                        draw.rect(screen, WHITE, canvasRect)
                        newBG = image.load(fname)
                        newBG = transform.scale(newBG, (1000, 900))
                        bgs.append(newBG)
                        #draw new bg on canvas and add it to list of bgs

                #add custon stamp
                if functions[3].collidepoint(mx, my):
                    fname = filedialog.askopenfilename(filetypes = [("PNG files", "*.png"), ("JPG files", "*.jpg")])
                    if fname[len(fname) - 3:].lower() != "png" and fname[len(fname) - 3:].lower() != "jpg":
                        print("invalid format")
                    else:
                        newStamp = image.load(fname)
                        stamps.append(newStamp) #add new stamp to list
                        preStamps.append(transform.scale(newStamp, (80, 80))) #add new preview of stamp

                #add custom song
                if functions[4].collidepoint(mx, my):
                    fname = filedialog.askopenfilename(filetypes=[("OGG files", "*.ogg"), ("MP3 files", "*.mp3")])
                    if fname[len(fname) - 3:] != "ogg" and fname[len(fname) - 3:] != "mp3":
                        print("Invalid format") #dont try and play non-music files
                    else:
                        songs.append(fname)

                #undo button
                if functions[5].collidepoint(mx, my):
                    if len(undo) > 1:
                        redo.insert(0, undo[-1]) #add undone screen to redo list
                        del undo[-1]          #remove undone screen from list
                        screencap = undo[-1]  #replace undone screen with new last screen
                #redo button
                if functions[6].collidepoint(mx, my):
                    if len(redo) >= 1:
                        #new, old, oldest
                        #on press restore screens in that order
                        screencap = redo[0]
                        undo.append(redo[0])
                        del redo[0]
                
                #change bg
                if leftBGRect.collidepoint(mx, my):
                    bgIndex = (bgIndex - 1 + len(bgs)) % len(bgs)
                if rightBGRect.collidepoint(mx, my):
                    bgIndex = (bgIndex + 1) % len(bgs)

                #change song
                if musicRects[0].collidepoint(mx, my):
                    songIndex = (songIndex + 1) % len(songs)
                    mixer.music.stop()
                    mixer.music.unload()
                    mixer.music.load(songs[songIndex])
                    mixer.music.play(-1)
                    #stop current song and play next song in list
                if musicRects[1].collidepoint(mx, my):
                    songIndex = (songIndex - 1 + len(songs)) % len(songs)
                    mixer.music.stop()
                    mixer.music.unload()
                    mixer.music.load(songs[songIndex])
                    mixer.music.play(-1)
                    #stop current song and play previous song in list

                #pause song
                if musicRects[2].collidepoint(mx, my):
                    if paused == False: #if you click pause when the music is not paused
                        mixer.music.pause()
                        paused = True
                    else:                            #otherwise play the music again
                        mixer.music.unpause()
                        paused = False
           
                #drag stamp (check user is holding after clicking on stamp button)
                if stampRect.collidepoint(mx, my):
                    tool = "stamp"
                #change stamp
                if stUpRect.collidepoint(mx, my):
                    stIndex = (stIndex + 1) % len(stamps)
                if stDownRect.collidepoint(mx, my):
                    stIndex = (stIndex - 1 + len(stamps)) % len(stamps)
                
                #lock slider to mx when clicked
                for i in range(3):
                    if sliderUI[i].collidepoint(mx, my):
                        lockFlag[i] = True
                
                #change brush size
                if increaseRect.collidepoint(mx, my) and size < 50: #dont allow brush size to be 55+ because eraser will break on edge and cause crash
                    size += 5
                if decreaseRect.collidepoint(mx, my) and size > 5: #dont allow brush size to be 0 or negative
                    size -= 5

                #eyedrop tool use
                if canvasRect.collidepoint(mx, my) and tool == "eyedrop":
                    col = screen.get_at((mx, my))
                    for i in range(3):
                        xpos[i] = col[i] + 145 #move sliders

                #get start x and y for shape tools
                if canvasRect.collidepoint(mx, my) and tool == "line" or tool == "rect" or tool == "ellipse" or tool == "triangle":
                    sx, sy = evt.pos

                #clear screen
                if clearRect.collidepoint(mx, my):
                    draw.rect(screen, WHITE, canvasRect)
                    screencap = screen.subsurface(canvasRect).copy() #draw canvas and reset screencap
                    undo = [screen.subsurface(canvasRect).copy()] #reset undo back to just blank canvas
                    redo = [] #reset redo

            if evt.button == 4:
                if tool == "stamp":
                    #increase size (default 200x200 px)
                    stScale += 5
                if stampRect.collidepoint(mx, my):
                    stIndex = (stIndex - 1 + len(stamps)) % len(stamps) #if mouse on stamp button and scroll change stamp index

            if evt.button == 5:
                if tool == "stamp":
                    #decrease size if size is above 5
                    if stScale > 5:
                        stScale -= 5
                if stampRect.collidepoint(mx, my):
                    stIndex = (stIndex + 1) % len(stamps) #if mouse on stamp button and scroll change stamp index
                
        if evt.type == MOUSEBUTTONUP:
            if evt.button == 1:
                for i in range(3):  #if user is not clicking they cannot be able to move the sliders
                    lockFlag[i] = False

                if tool == "stamp":
                    if canvasRect.collidepoint(mx, my):
                        screencap = screen.subsurface(canvasRect).copy()
                    tool = "" #if user is not clicking they cannot continue to move a stamp
                    stScale = 200 #reset scale to default size for convenience

                #save canvas for shape tools
                if tool == "line" or tool == "rect" or tool == "ellipse" or tool == "triangle":
                    screen.blit(screencap, canvasRect) #stops the text descriptions from getting saved onto the canvas, however we must now redraw the shapes in this loop :(
                    if canvasRect.collidepoint(mx, my):
                        if tool == "line":
                            draw.line(screen, col, (sx, sy), (mx, my), size)
                        elif tool == "rect":
                            drawRect() #use functions from earlier
                        elif tool == "ellipse":
                            drawEllipse()
                        else:
                            draw.polygon(screen, col, [(sx, my), ((mx + sx) // 2, sy), (mx, my)], fill)
                        screencap = screen.subsurface(canvasRect).copy()
                        sx, sy = 0, 0 #reset sx sy

                #add canvas screenshot to undo list
                if canvasRect.collidepoint(mx, my):
                    if tool == "eraser":
                        eraser()
                    if tool == "brush":
                        brush()
                    screen.blit(screencap, canvasRect)
                    #use tool one more time so that brush size marker is not saved in screenshot
                    undo.append(screen.subsurface(canvasRect).copy())

    mx, my = mouse.get_pos()
    mb = mouse.get_pressed()
    keys = key.get_pressed()

    #define slider UI with new x pos
    for i in range(3):
        sliderUI[i] = Rect(xpos[i], 670 + i * 50, 10, 50)

    screen.blit(bgs[bgIndex], (0, 0)) #draw layers in reverse order (bg -> ui)

    for i in range(3): #draw sliders -> UI filled -> UI outline
        draw.rect(screen, RGB[i], slideBG[i])
        draw.rect(screen, WHITE, sliderUI[i])
        draw.rect(screen, BLACK, sliderUI[i], 2)

    #draw tool buttons
    for i in range(len(tools)):
        draw.rect(screen, BLACK, tools[i], tFill[i])
        if i < 4:
            screen.blit(toolIcons[i], (tools[i][0] + 2, tools[i][1] + 2)) #blit icons for first 4 buttons centered in button
        if i == 4: #draw icons for shape tools using values from icons list
            draw.line(screen, iconColour[0], shapeIcons[0][0], shapeIcons[0][1], 4)
        elif i == 5:
            draw.rect(screen, iconColour[1], shapeIcons[1], 4)
        elif i == 6:
            draw.ellipse(screen, iconColour[2], shapeIcons[2], 4)
        else:
            draw.polygon(screen, iconColour[3], [shapeIcons[3][0], shapeIcons[3][1], shapeIcons[3][2]], 4)

    for i in range(4):
        iconColour[i] = BLACK #reset icon colours

    #draw function buttons
    for i in range(len(functions)):
        draw.rect(screen, BLACK, functions[i])
        screen.blit(wIcons[i], (functions[i][0] + 2, functions[i][1] + 2))
        
    draw.rect(screen, BLACK, increaseRect)
    screen.blit(medFont.render("+", True, WHITE), (45, 291))
    draw.rect(screen, BLACK, decreaseRect)
    screen.blit(bigFont.render("-", True, WHITE), (100, 276))

    #clear button and text
    clearText = smallFont.render(("CLEAR"), True, WHITE)
    draw.rect(screen, BLACK, clearRect)
    screen.blit(clearText, (56, 367))

    #left and right buttons for changing bg
    draw.rect(screen, BLACK, leftBGRect) #button
    draw.polygon(screen, WHITE, [(40, 740), (100, 710), (100, 770)]) #arrow
    draw.rect(screen, BLACK, rightBGRect) #button
    draw.polygon(screen, WHITE, [(width - 100, 710), (width - 100, 770), (width - 40, 740)]) #arrow

    #stamp buttons
    draw.rect(screen, BLACK, stampRect)
    screen.blit(preStamps[stIndex], (45, 480))
    draw.rect(screen, BLACK, stUpRect)
    draw.polygon(screen, WHITE, [(50, 460), (85, 440), (120, 460)]) #arrow
    draw.rect(screen, BLACK, stDownRect)
    draw.polygon(screen, WHITE, [(50, 580), (85, 600), (120, 580)]) #arrow

    screen.blit(screencap, canvasRect)           

    #move slider and change colour
    for i in range(3):
        if lockFlag[i] == True: #for each slider if they are locked, move them unless the mouse is past the slider edges
            if mx > 400:
                xpos[i] = 400
            elif 145 <= mx <= 400:
                xpos[i] = mx
            else:
                xpos[i] = 145
        screen.blit(defFont.render(str(col[i]), True, BLACK), (415, 670 + i * 50))
    col = (xpos[0] - 145, xpos[1] - 145, xpos[2] - 145)

    #preview of colour
    draw.rect(screen, col, preRect)
    draw.rect(screen, BLACK, preRect, 4)

    #music player
    screen.set_clip(playerRect) #set clip so that text does not show outside of the music player area
    trueName = songs[songIndex] #name of song without file path or extension
    for i in range(songs[songIndex].count("/")): #remove everything after the last /
        pos = trueName.find("/")
        trueName = trueName[pos + 1:] #song name + extension will be everything after the last /
    trueName = trueName[:trueName.rfind(".")] #remove extension
    #since custom music files are supported this must work for any file name (as long as you dont have a / in the song name)

    draw.rect(screen, (40, 40, 40), playerRect)
    for i in range(len(musicRects)):
        draw.rect(screen, BLACK, musicRects[i])
    songName = smallFont.render(f"Now Playing: {trueName}", True, WHITE)
    screen.blit(songName, (playerRect[0] + (playerRect[3] - songName.get_width() / 2), playerRect[1] + 90)) #centre text in playerRect

    screen.set_clip(None) #remove clip on screen

    #selecting tool 
    #hover over effect
    for i in range(len(tools)):
        if tools[i].collidepoint(mx, my):
            draw.rect(screen, WHITE, tools[i], tFill[i]) #draw button on screen from list in white
            if i < 4:
                screen.blit(toolIcons[i], (tools[i][0] + 2, tools[i][1] + 2)) #re-blit icons for first 4 buttons centered in button so that they are over the button
            if tool != tool_n[i] and i > 3:
                iconColour[i - 4] = WHITE
            elif tool == tool_n[i] and i > 3:
                iconColour[i - 4] = BLACK
            else:
                iconColour[i - 4] = BLACK
            if i == 4: #redraw icons for shape tools using values from icons list
                draw.line(screen, iconColour[0], shapeIcons[0][0], shapeIcons[0][1], 4)
            elif i == 5:
                draw.rect(screen, iconColour[1], shapeIcons[1], 4)
            elif i == 6:
                draw.ellipse(screen, iconColour[2], shapeIcons[2], 4)
            else:
                draw.polygon(screen, iconColour[3], [shapeIcons[3][0], shapeIcons[3][1], shapeIcons[3][2]], 4)
            des = smallFont.render(info[i], True, BLACK) #create temp variable for description of tool
            draw.rect(screen, WHITE, (mx, my, des.get_width() + 10, des.get_height() + 10)) #use width and height to draw a rect
            draw.rect(screen, BLACK, (mx, my, des.get_width() + 10, des.get_height() + 10), 2) #black outline for rect
            screen.blit(des, (mx + 5, my + 5)) #blit text (since width and height of rect is 10px longer blit at mx + 5, my + 5 to centre text)
            if mb[0]:
                tool = tool_n[i]

        #filled when selected
        if tool == tool_n[i]:
            tFill[i] = 0
            if i > 3:
                iconColour[i - 4] = WHITE
        else:
            tFill[i] = 2

    for i in range(len(functions)):
        if functions[i].collidepoint(mx, my):
            draw.rect(screen, WHITE, functions[i])
            screen.blit(bIcons[i], (functions[i][0] + 2, functions[i][1] + 2))
            des = smallFont.render(funcInfo[i], True, BLACK) #create temp variable for description of tool
            draw.rect(screen, WHITE, (mx, my, des.get_width() + 10, des.get_height() + 10)) #use width and height to draw a rect
            draw.rect(screen, BLACK, (mx, my, des.get_width() + 10, des.get_height() + 10), 2) #black outline for rect
            screen.blit(des, (mx + 5, my + 5)) #blit text (since width and height of rect is 10px longer blit at mx + 5, my + 5 to centre text)

    #hover over effect for increase decrease size and clear and stamp buttons
        
    if increaseRect.collidepoint(mx, my):
        draw.rect(screen, WHITE, increaseRect)
        screen.blit(medFont.render("+", True, BLACK), (45, 291))
        #info for increase
        des = smallFont.render(f"Increase brush size. Current Size: {size}", True, BLACK)
        draw.rect(screen, WHITE, (mx, my, des.get_width() + 10, des.get_height() + 10))
        draw.rect(screen, BLACK, (mx, my, des.get_width() + 10, des.get_height() + 10), 2)
        screen.blit(des, (mx + 5, my + 5))
    if decreaseRect.collidepoint(mx, my):
        draw.rect(screen, WHITE, decreaseRect)
        screen.blit(bigFont.render("-", True, BLACK), (100, 276))
        #info for decrease
        des = smallFont.render(f"Decrease brush size. Current Size: {size}", True, BLACK)
        draw.rect(screen, WHITE, (mx, my, des.get_width() + 10, des.get_height() + 10))
        draw.rect(screen, BLACK, (mx, my, des.get_width() + 10, des.get_height() + 10), 2)
        screen.blit(des, (mx + 5, my + 5))
        
    if clearRect.collidepoint(mx, my):
        draw.rect(screen, WHITE, clearRect)
        screen.blit(smallFont.render(("CLEAR"), True, BLACK), (56, 367))
        #info for clear button
        des = smallFont.render(f"Clear the screen back to a white canvas.", True, BLACK)
        draw.rect(screen, WHITE, (mx, my, des.get_width() + 10, des.get_height() + 10))
        draw.rect(screen, BLACK, (mx, my, des.get_width() + 10, des.get_height() + 10), 2)
        screen.blit(des, (mx + 5, my + 5))

    if stUpRect.collidepoint(mx, my):
        draw.rect(screen, WHITE, stUpRect)
        draw.polygon(screen, BLACK, [(50, 460), (85, 440), (120, 460)]) #when button is white, arrow is black
    if stDownRect.collidepoint(mx, my):
        draw.rect(screen, WHITE, stDownRect)
        draw.polygon(screen, BLACK, [(50, 580), (85, 600), (120, 580)])

    if stampRect.collidepoint(mx, my):
        des = smallFont.render(f"Drag to put stamp on screen. [Use up/down arrow keys or scroll wheel to scale]", True, BLACK)
        draw.rect(screen, WHITE, (mx, my, des.get_width() + 10, des.get_height() + 10))
        draw.rect(screen, BLACK, (mx, my, des.get_width() + 10, des.get_height() + 10), 2)
        screen.blit(des, (mx + 5, my + 5))

    #hover effect for change bg buttons

    if leftBGRect.collidepoint(mx, my):
        draw.rect(screen, WHITE, leftBGRect)
        draw.polygon(screen, BLACK, [(40, 740), (100, 710), (100, 770)])
    if rightBGRect.collidepoint(mx, my):
        draw.rect(screen, WHITE, rightBGRect)
        draw.polygon(screen, BLACK, [(width - 100, 710), (width - 100, 770), (width - 40, 740)])

    screen.set_clip(canvasRect) #only canvas can be updated

    #using tool

    #scale up and down stamps with keyboard
    if keys[K_UP]:
        if tool == "stamp":
            #increase size (default 200x200 px)
            stScale += 5
        if stampRect.collidepoint(mx, my):
            stIndex = (stIndex + 1) % len(stamps) #change stamp index if on stampRect
                
    if keys[K_DOWN]:
        if tool == "stamp":
            #decrease size if size is above 5
            if stScale > 5:
                stScale -= 5
        if stampRect.collidepoint(mx, my):
            stIndex = (stIndex - 1 + len(stamps)) % len(stamps) #change stamp index if on stampRect

    #check for squareLock
    if keys[K_LSHIFT]:
        squareFlag = True
    else:
        squareFlag = False

    #check for shape fill
    if keys[K_f]:
        fill = 0
    else:
        fill = size
    
    if mb[0] and canvasRect.collidepoint(mx, my):
            if tool == "pencil":
                draw.line(screen, col, (mx, my), (omx, omy)) #draw line from last mouse pos to current mouse pos
                screencap = screen.subsurface(canvasRect).copy() #save changes to screen
            
            if tool == "eraser":
                eraser()
                screencap = screen.subsurface(canvasRect).copy() #save screen
                
            if tool == "brush":
                brush()
                screencap = screen.subsurface(canvasRect).copy() #save screen

            if tool == "line":
                draw.line(screen, col, (sx, sy), (mx, my), size)

            if tool == "rect":
                drawRect() #use function from earlier

            if tool == "ellipse":
                drawEllipse()

            if tool == "triangle":
                draw.polygon(screen, col, [(sx, my), ((mx + sx) // 2, sy), (mx, my)], fill) #top point will be in the middle of the bottom 2 points

            if tool == "stamp":
                screen.blit(transform.scale(stamps[stIndex], (stScale, stScale)), (mx - stScale // 2, my - stScale // 2)) #transform stamp when blitting to not mess up image in list

            redo = [] #reset redo list when drawing after undoing

    if canvasRect.collidepoint(mx, my) and tool == "brush":
        draw.circle(screen, BLACK, (mx, my), size, 1)
    if canvasRect.collidepoint(mx, my) and tool == "eraser":
        draw.rect(screen, BLACK, (mx - size, my - size, 2 * size, 2 * size), 1)
    #show brush size on screen for brush and eraser

    screen.set_clip(None) #remove clip for next time loop is run

    omx, omy = mx, my
    clock.tick(60)
    display.flip()
            
quit()
