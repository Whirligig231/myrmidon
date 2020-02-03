import os
import pygame
from pygame.locals import *
import time
import math
import tkinter
from tkinter import messagebox, simpledialog, filedialog
import json
import copy
from ctypes import *

# Load the AY38910 DLL
ayDll = cdll.LoadLibrary("AY38910DLL.dll")

ayDll.init()

def testRect(pos, rect):
    return (pos[0] >= rect[0] and pos[1] >= rect[1] and pos[0] < rect[0] + rect[2] and pos[1] < rect[1] + rect[3])

TKW = tkinter.Tk() # Create the object
TKW.overrideredirect(1) # Avoid it appearing and then disappearing quickly
TKW.withdraw() # Hide the window as we do not want to see this one

pygame.init()

FONT = pygame.font.SysFont('arial', 18, True)

WHITE = (255, 255, 255)
LTGREY = (200, 200, 200)
GREY = (150, 150, 150)
DKGREY = (100, 100, 100)
DKDKGREY = (50, 50, 50)
BLACK = (0, 0, 0)

NOTECOLS = [(0, 153, 255), (153, 255, 0), (51, 0, 255), (255, 51, 0), (255, 204, 0)]
NOTECOLS2 = [(0, 76, 127), (76, 127, 0), (25, 0, 127), (127, 25, 0), (127, 102, 0)]

os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.key.set_repeat(500, 50)
screen = pygame.display.set_mode((1600, 900))
pygame.display.set_caption('Chip Composer: <untitled>')

surf = [None, None, None, None, None]
surf[0] = pygame.Surface((770, 390))
surf[1] = pygame.Surface((770, 390))
surf[2] = pygame.Surface((770, 390))
surf[3] = pygame.Surface((770, 180))
surf[4] = pygame.Surface((770, 180))

# X offset, in ticks, and Y offset, in notes/etc. Zoom X is in pixels per tick and Y is in pixels per note/etc.
offset_x = 0
offset_y = [55, 55, 55, 0, 0]
zoom_x = 3
zoom_y = [30, 30, 30, 30, 30]
max_y = [128, 128, 128, 6, 128]
height = [390, 390, 390, 180, 180]
width = 740

x_pos = [0, 800, 0, 800, 800]
y_pos = [60, 60, 480, 480, 690]

# Names of each y-slot
y_names = [['G9','Gb9','F9','E9','Eb9','D9','Db9','C9',
    'B8','Bb8','A8','Ab8','G8','Gb8','F8','E8','Eb8','D8','Db8','C8',
    'B7','Bb7','A7','Ab7','G7','Gb7','F7','E7','Eb7','D7','Db7','C7',
    'B6','Bb6','A6','Ab6','G6','Gb6','F6','E6','Eb6','D6','Db6','C6',
    'B5','Bb5','A5','Ab5','G5','Gb5','F5','E5','Eb5','D5','Db5','C5',
    'B4','Bb4','A4','Ab4','G4','Gb4','F4','E4','Eb4','D4','Db4','C4',
    'B3','Bb3','A3','Ab3','G3','Gb3','F3','E3','Eb3','D3','Db3','C3',
    'B2','Bb2','A2','Ab2','G2','Gb2','F2','E2','Eb2','D2','Db2','C2',
    'B1','Bb1','A1','Ab1','G1','Gb1','F1','E1','Eb1','D1','Db1','C1',
    'B0','Bb0','A0','Ab0','G0','Gb0','F0','E0','Eb0','D0','Db0','C0',
    'B-','Bb-','A-','Ab-','G-','Gb-','F-','E-','Eb-','D-','Db-','C-'
    ],
    ['G9','Gb9','F9','E9','Eb9','D9','Db9','C9',
    'B8','Bb8','A8','Ab8','G8','Gb8','F8','E8','Eb8','D8','Db8','C8',
    'B7','Bb7','A7','Ab7','G7','Gb7','F7','E7','Eb7','D7','Db7','C7',
    'B6','Bb6','A6','Ab6','G6','Gb6','F6','E6','Eb6','D6','Db6','C6',
    'B5','Bb5','A5','Ab5','G5','Gb5','F5','E5','Eb5','D5','Db5','C5',
    'B4','Bb4','A4','Ab4','G4','Gb4','F4','E4','Eb4','D4','Db4','C4',
    'B3','Bb3','A3','Ab3','G3','Gb3','F3','E3','Eb3','D3','Db3','C3',
    'B2','Bb2','A2','Ab2','G2','Gb2','F2','E2','Eb2','D2','Db2','C2',
    'B1','Bb1','A1','Ab1','G1','Gb1','F1','E1','Eb1','D1','Db1','C1',
    'B0','Bb0','A0','Ab0','G0','Gb0','F0','E0','Eb0','D0','Db0','C0',
    'B-','Bb-','A-','Ab-','G-','Gb-','F-','E-','Eb-','D-','Db-','C-'
    ],
    ['G9','Gb9','F9','E9','Eb9','D9','Db9','C9',
    'B8','Bb8','A8','Ab8','G8','Gb8','F8','E8','Eb8','D8','Db8','C8',
    'B7','Bb7','A7','Ab7','G7','Gb7','F7','E7','Eb7','D7','Db7','C7',
    'B6','Bb6','A6','Ab6','G6','Gb6','F6','E6','Eb6','D6','Db6','C6',
    'B5','Bb5','A5','Ab5','G5','Gb5','F5','E5','Eb5','D5','Db5','C5',
    'B4','Bb4','A4','Ab4','G4','Gb4','F4','E4','Eb4','D4','Db4','C4',
    'B3','Bb3','A3','Ab3','G3','Gb3','F3','E3','Eb3','D3','Db3','C3',
    'B2','Bb2','A2','Ab2','G2','Gb2','F2','E2','Eb2','D2','Db2','C2',
    'B1','Bb1','A1','Ab1','G1','Gb1','F1','E1','Eb1','D1','Db1','C1',
    'B0','Bb0','A0','Ab0','G0','Gb0','F0','E0','Eb0','D0','Db0','C0',
    'B-','Bb-','A-','Ab-','G-','Gb-','F-','E-','Eb-','D-','Db-','C-'
    ],
    ['Cr', 'OH', 'HH', 'CH', 'Sn', 'Ki'],
    [str(i) for i in range(128)]]

default_title = '<untitled>'
default_fdata = [{'name': 'Master Pattern', 'length': 288, 'notes': [[], [], [], [], []]}]
default_pattern = {'name': 'NewPattern', 'length': 288, 'notes': [[], [], [], [], []]}

dirty = False
title = default_title
fname = None
fdata = copy.deepcopy(default_fdata)

rendered_data = bytearray()

def computeRender():
    global rendered_data
    rendered_data = bytearray()
    for p in range(len(fdata)):
        rendered_data += bytearray([0, 0x04, p])
        ticks = 0
        
        all_times = []
        for i in range(5):
            for note in fdata[p]['notes'][i]:
                if note[1] not in all_times:
                    all_times += [note[1]]
                if i < 3:
                    if note[1] + note[2] not in all_times:
                        all_times += [note[1] + note[2]]
        
        all_times.sort()
        
        for time in all_times:
            # Place commands first!
            events = [note for note in fdata[p]['notes'][4] if note[1] == time]
            events.sort(key = lambda note : note[0])
            for event in events:
                diff_time = time - ticks
                ticks = time
                
                if diff_time >= 256:
                    rendered_data += bytearray([0, 0x03, diff_time // 256])
                    diff_time = diff_time % 256
                
                event_words = event[3].split(' ')
                if len(event_words) == 1:
                    event_words += ['0']
                if len(event_words) == 0:
                    event_words = ['0', '0']
                rendered_data += bytearray([diff_time, int(event_words[0], 0), int(event_words[1], 0)])
                
            # Now place the drums!
            events = [note for note in fdata[p]['notes'][3] if note[1] == time]
            events.sort(key = lambda note : note[0])
            for event in events:
                diff_time = time - ticks
                ticks = time
                
                if diff_time >= 256:
                    rendered_data += bytearray([0, 0x03, diff_time // 256])
                    diff_time = diff_time % 256

                rendered_data += bytearray([diff_time, 0x50, 5 - event[0]])
                
            # Now place notes!
            for i in range(3):
                cmdStart = 0x10 * i
                if i == 2:
                    cmdStart = 0x30
                if len([note for note in fdata[p]['notes'][i] if note[1] + note[2] == time]) != 0 and len([note for note in fdata[p]['notes'][i] if note[1] == time]) == 0:
                    diff_time = time - ticks
                    ticks = time
                    
                    if diff_time >= 256:
                        rendered_data += bytearray([0, 0x03, diff_time // 256])
                        diff_time = diff_time % 256

                    rendered_data += bytearray([diff_time, cmdStart + 0x10, 128])
                else:
                    events = [note for note in fdata[p]['notes'][i] if note[1] == time]
                    events.sort(key = lambda note : -note[0])
                    first_event = True
                    for event in events:
                        diff_time = time - ticks
                        ticks = time
                        
                        if diff_time >= 256:
                            rendered_data += bytearray([0, 0x03, diff_time // 256])
                            diff_time = diff_time % 256

                        if first_event and event[3] == 'PITCHBEND':
                            rendered_data += bytearray([diff_time, cmdStart + 0x1a, 127 - event[0]])
                        elif first_event:
                            rendered_data += bytearray([diff_time, cmdStart + 0x10, 127 - event[0]])
                        else:
                            rendered_data += bytearray([diff_time, cmdStart + 0x17, 127 - event[0]])
                        first_event = False
        
        if fdata[p]['length'] - ticks >= 256:
            rendered_data += bytearray([0, 0x03, (fdata[p]['length'] - ticks) // 256])
            ticks += ((fdata[p]['length'] - ticks) // 256) * 256
 
        if p == 0:
            rendered_data += bytearray([fdata[p]['length'] - ticks, 0x07, p])
        else:
            rendered_data += bytearray([fdata[p]['length'] - ticks, 0x05, 0])
            
    render_output = copy.copy(rendered_data)
    while len(render_output) < 4096:
        render_output += bytearray([0])
    ayDll.loadCommandBuffer(c_char_p(bytes(render_output)))

computeRender()

current_pattern = 0
grid_spacing = 9

continue_loop = 1

def setDirty(d):
    global dirty
    dirty = d
    if d:
        computeRender()
        pygame.display.set_caption('Chip Composer: ' + title + '*')
    else:
        pygame.display.set_caption('Chip Composer: ' + title)

def setTitle(t):
    global title
    title = t
    if dirty:
        pygame.display.set_caption('Chip Composer: ' + title + '*')
    else:
        pygame.display.set_caption('Chip Composer: ' + title)

def checkDirty():
    if not dirty:
        return True
    return messagebox.askokcancel('Unsaved Changes', 'Your unsaved changes will be lost. Continue with this operation?')
    
def standardizeCoords():
    global offset_y, max_y, height, zoom_y, offset_x, fdata, width, zoom_x

    for i in range(5):
        if offset_y[i] > max_y[i] - height[i] / zoom_y[i]:
            offset_y[i] = max_y[i] - height[i] / zoom_y[i]
        if offset_y[i] < 0:
            offset_y[i] = 0
            
    if offset_x > fdata[current_pattern]['length'] - width / zoom_x:
        offset_x = fdata[current_pattern]['length'] - width / zoom_x
    if offset_x < 0:
        offset_x = 0
        
def sortNotes():
    for i in range(5):
        fdata[current_pattern]['notes'][i].sort(key = lambda x : x[1])

def gotoPattern(i):
    global current_pattern
    current_pattern = i
    standardizeCoords()
    ayDll.stopPlayback()
    
def gotoPatternCurried(i):
    def gpc():
        gotoPattern(i)
    return gpc
    
def newFile():
    global fname, fdata
    if checkDirty():
        setTitle(default_title)
        fname = None
        fdata = copy.deepcopy(default_fdata)
        ayDll.resetToneSettings()
        gotoPattern(0)
        setDirty(False)
        
def openFile():
    global fname, fdata
    if checkDirty():
        fn = filedialog.askopenfilename(title='Open', filetypes=[('Chip Composer files', '*.ccf'), ('All files', '*')])
        if fn != '':
            try:
                fp = open(fn, 'r')
                fdata = json.loads(fp.read())
                fp.close()
            except Exception as e:
                print(repr(e))
                messagebox.showerror('Invalid File', 'Unable to read the file.')
            fname = fn
            head, tail = os.path.split(fn)
            setTitle(tail)

            ayDll.resetToneSettings()
            gotoPattern(0)
            computeRender()
            setDirty(False)

def saveFileBase():
    try:
        fp = open(fname, 'w+')
        fp.write(json.dumps(fdata))
        fp.close()
        setDirty(False)
    except Exception as e:
        print(repr(e))
        messagebox.showerror('File Save Error', 'Unable to save the file.')
        setDirty(True)

def saveAsFile():
    global fname
    fn = filedialog.asksaveasfilename(title='Save As', filetypes=[('Chip Composer files', '*.ccf'), ('All files', '*')])
    if fn != '':
        if fn[-4:] != '.ccf':
            fn += '.ccf'
        fname = fn
        head, tail = os.path.split(fn)
        setTitle(tail)
        saveFileBase()

def saveFile():
    if fname is None:
        saveAsFile()
    else:
        saveFileBase()
        
def renderFile():
    fn = filedialog.asksaveasfilename(title='Render', filetypes=[('Binary music files', '*.bin'), ('All files', '*')])
    if fn != '':
        if fn[-4:] != '.bin':
            fn += '.bin'
        try:
            computeRender()
            fp = open(fn, 'wb+')
            render_output = copy.copy(rendered_data)
            while len(render_output) < 4096:
                render_output += bytearray([0])
            fp.write(render_output)
            fp.close()
        except Exception as e:
            print(repr(e))
            messagebox.showerror('Render Error', 'Unable to render the file.')
    
def exit():
    global continue_loop
    if checkDirty():
        continue_loop = 0
        
def newPattern():
    global fdata
    pname = simpledialog.askstring('New Pattern', 'Enter the name of the new pattern:')
    if pname is not None:
        fdata += [copy.deepcopy(default_pattern)]
        fdata[-1]['name'] = pname
        gotoPattern(len(fdata) - 1)
        setDirty(True)

def clonePattern():
    global fdata, current_pattern
    pname = simpledialog.askstring('Clone Pattern', 'Enter the name of the cloned pattern:')
    if pname is not None:
        fdata += [copy.deepcopy(fdata[current_pattern])]
        fdata[-1]['name'] = pname
        gotoPattern(len(fdata) - 1)
        setDirty(True)
        
def renamePattern():
    global fdata, current_pattern
    if current_pattern == 0:
        messagebox.showerror('Rename Pattern', 'Cannot rename the master pattern!')
        return
    pname = simpledialog.askstring('Rename Pattern', 'Enter the new name of the pattern:')
    if pname is not None:
        fdata[current_pattern]['name'] = pname
        setDirty(True)
        
def reorderPattern():
    global fdata, current_pattern
    if current_pattern == 0:
        messagebox.showerror('Reorder Pattern', 'Cannot reorder the master pattern!')
        return
    pind = simpledialog.askinteger('Reorder Pattern', 'Enter the pattern index to move this pattern to:', minvalue=0, maxvalue=len(fdata)-1)
    if pind is not None:
        fdata.insert(pind, fdata.pop(current_pattern))
        gotoPattern(pind)
        setDirty(True)
        
def resizePattern():
    global fdata, current_pattern
    plen = simpledialog.askinteger('Resize Pattern', 'Enter the new length of this pattern in ticks:', minvalue=1)
    if plen is not None:
        fdata[current_pattern]['length'] = plen
        standardizeCoords()
        setDirty(True)
   
def clearPattern():
    global fdata, current_pattern
    if messagebox.askokcancel('Clear Pattern', 'This cannot be undone. Are you sure you want to clear the current pattern?'):
        pname = fdata[current_pattern]['name']
        fdata[current_pattern] = copy.deepcopy(default_pattern)
        fdata[current_pattern]['name'] = pname
        setDirty(True)
        
def deletePattern():
    global fdata, current_pattern
    if current_pattern == 0:
        messagebox.showerror('Delete Pattern', 'Cannot delete the master pattern!')
        return
    if messagebox.askokcancel('Delete Pattern', 'This cannot be undone. Are you sure you want to delete the current pattern?'):
        fdata.pop(current_pattern)
        if current_pattern >= len(fdata):
            current_pattern -= 1
        setDirty(True)

def gridSpacing2():
    global grid_spacing
    grid_spacing = 2

def gridSpacing3():
    global grid_spacing
    grid_spacing = 3

def gridSpacing6():
    global grid_spacing
    grid_spacing = 6

def gridSpacing9():
    global grid_spacing
    grid_spacing = 9

def gridSpacing12():
    global grid_spacing
    grid_spacing = 12

def gridSpacing18():
    global grid_spacing
    grid_spacing = 18

def gridSpacing36():
    global grid_spacing
    grid_spacing = 36

def gridSpacing():
    global grid_spacing
    gs = simpledialog.askinteger('Grid Spacing', 'Enter the new grid spacing in ticks (1/36 beat):', minvalue=1)
    if gs is not None:
        grid_spacing = gs

menus = [
    ('File', [('New', newFile), ('Open...', openFile), ('Save', saveFile), ('Save As...', saveAsFile), ('Render...', renderFile), ('Exit', exit)]),
    ('Edit', [('New Pattern...', newPattern), ('Clone Pattern...', clonePattern), ('Rename Pattern...', renamePattern), ('Reorder Pattern...', reorderPattern), ('Resize Pattern...', resizePattern), ('Clear Pattern', clearPattern), ('Delete Pattern', deletePattern)]),
    ('Pattern', []),
    ('Grid', [('1/18 Beat', gridSpacing2), ('1/12 Beat', gridSpacing3), ('1/6 Beat', gridSpacing6), ('1/4 Beat', gridSpacing9), ('1/3 Beat', gridSpacing12), ('1/2 Beat', gridSpacing18), ('1 Beat', gridSpacing36), ('Custom Spacing...', gridSpacing)])
]

def updateMenu():
    arr = []
    for i in range(len(fdata)):
        arr += [(str(i) + ': ' + fdata[i]['name'], gotoPatternCurried(i))]
    menus[2] = ('Pattern', arr)

selected_menu = -1
mode = 'normal'
scroll_pos = 0
hold_dir = 0
scrollhold_i = 0

notedrag_i = 0
notedrag_j = 0
notedrag_pos = (0, 0)

time_last = time.clock()

if __name__ == '__main__':
    while continue_loop:
        time_delta = time.clock() - time_last
        time_last = time.clock()
        
        if mode == 'hold_y':
            offset_y[scrollhold_i] += time_delta * 400 / zoom_y[scrollhold_i] * hold_dir
            standardizeCoords()
        elif mode == 'hold_x':
            offset_x += time_delta * 400 / zoom_x * hold_dir
            standardizeCoords()
        
        # Process events
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                if not pygame.mouse.get_focused():
                    continue
                (x, y) = event.pos
                if event.button == 1:
                    if y < 30:
                        for i in range(len(menus)):
                            if x >= 90*i and x < 90*i+90:
                                mode = 'menu'
                                selected_menu = i
                                updateMenu()
                                break
                    elif mode == 'menu':
                        menu_list = menus[selected_menu][1]
                        if x >= 90*selected_menu and x < 90*selected_menu+180 and y < 30+30*len(menu_list):
                            for i in range(len(menu_list)):
                                if y >= 30+30*i and y < 60+30*i:
                                    mode = 'normal'
                                    selected_menu = -1
                                    if menu_list[i][1] is not None:
                                        menu_list[i][1]() # This looks so wrong haha
                                    break
                        else:
                            mode = 'normal'
                            selected_menu = -1
                    elif mode == 'normal':
                        for i in range(5):
                            if testRect((x, y), (x_pos[i] + width + 30, y_pos[i] + 90, 30, height[i] - 120)):
                                # Scroll
                                offset_fraction = min(1, height[i] / zoom_y[i] / max_y[i])
                                offset_start = offset_y[i] / max_y[i]
                                if testRect((x, y), (x_pos[i] + width + 30, y_pos[i] + 90 + offset_start * (height[i] - 120), 30, offset_fraction * (height[i] - 120))):
                                    mode = 'scroll_y'
                                    scrollhold_i = i
                                    scroll_pos = y - (y_pos[i] + 90 + offset_start * (height[i] - 120))
                                elif y <= y_pos[i] + 90 + offset_start * (height[i] - 120):
                                    # Page Up
                                    offset_y[i] -= height[i] / zoom_y[i]
                                    standardizeCoords()
                                else:
                                    # Page Down
                                    offset_y[i] += height[i] / zoom_y[i]
                                    standardizeCoords()
                            elif testRect((x, y), (x_pos[i] + width + 30, y_pos[i], 30, 30)):
                                # Zoom In
                                zoom_y[i] *= 1.2
                                standardizeCoords()
                            elif testRect((x, y), (x_pos[i] + width + 30, y_pos[i] + 30, 30, 30)):
                                # Zoom Out
                                zoom_y[i] /= 1.2
                                standardizeCoords()
                            elif testRect((x, y), (x_pos[i] + width + 30, y_pos[i] + 60, 30, 30)):
                                # Scroll Up
                                mode = 'hold_y'
                                scrollhold_i = i
                                hold_dir = -1
                            elif testRect((x, y), (x_pos[i] + width + 30, y_pos[i] + height[i] - 30, 30, 30)):
                                # Scroll Down
                                mode = 'hold_y'
                                scrollhold_i = i
                                hold_dir = 1

                        if testRect((x, y), (30, 870, width - 60, 30)):
                            # Scroll
                            offset_fraction = min(1, width / zoom_x / fdata[current_pattern]['length'])
                            offset_start = offset_x / fdata[current_pattern]['length']
                            if testRect((x, y), (30 + offset_start * (width - 60), 870, offset_fraction * (width - 60), 30)):
                                mode = 'scroll_x'
                                scroll_pos = x - (30 + offset_start * (width - 60))
                            elif x <= 30 + offset_start * (width - 60):
                                # Page Left
                                offset_x -= width / zoom_x
                                standardizeCoords()
                            else:
                                # Page Right
                                offset_x += width / zoom_x
                                standardizeCoords()
                        elif testRect((x, y), (width, 870, 30, 30)):
                            # Zoom In
                            zoom_x *= 1.2
                            standardizeCoords()
                        elif testRect((x, y), (width + 30, 870, 30, 30)):
                            # Zoom Out
                            zoom_x /= 1.2
                            standardizeCoords()
                        elif testRect((x, y), (0, 870, 30, 30)):
                            # Scroll Left
                            mode = 'hold_x'
                            hold_dir = -1
                        elif testRect((x, y), (width - 30, 870, 30, 30)):
                            # Scroll Right
                            mode = 'hold_x'
                            hold_dir = 1
                        elif testRect((x, y), (1540, 870, 30, 30)):
                            # Play
                            if current_pattern == 0:
                                ayDll.resetToneSettings()
                            ayDll.startPattern(current_pattern)
                        elif testRect((x, y), (1570, 870, 30, 30)):
                            # Stop
                            ayDll.stopPlayback()
                            
                        for i in range(5):
                            if testRect((x, y), (x_pos[i] + 30, y_pos[i], width, height[i])):
                                for j in range(len(fdata[current_pattern]['notes'][i])-1, -1, -1):
                                    note = fdata[current_pattern]['notes'][i][j]
                                    if testRect((x, y), (x_pos[i] + (note[1] + note[2] - offset_x) * zoom_x + 25, y_pos[i] + (note[0] - offset_y[i]) * zoom_y[i], 10, zoom_y[i])):
                                        notedrag_i = i
                                        notedrag_j = j
                                        notedrag_pos = (x - (x_pos[i] + (note[1] + note[2] - offset_x) * zoom_x + 25), y - (y_pos[i] + (note[0] - offset_y[i]) * zoom_y[i]))
                                        mode = 'note_resize'
                                        break
                                    elif testRect((x, y), (x_pos[i] + (note[1] - offset_x) * zoom_x + 30, y_pos[i] + (note[0] - offset_y[i]) * zoom_y[i], note[2] * zoom_x, zoom_y[i])):
                                        notedrag_i = i
                                        notedrag_j = j
                                        notedrag_pos = (x - (x_pos[i] + (note[1] - offset_x) * zoom_x + 30), y - (y_pos[i] + (note[0] - offset_y[i]) * zoom_y[i]))
                                        mode = 'note_drag'
                                        break
                                if mode == 'normal':
                                    n0 = int((y - y_pos[i]) / zoom_y[i] + offset_y[i])
                                    n1 = int(((x - x_pos[i] - 30) / zoom_x + offset_x) / grid_spacing) * grid_spacing
                                    n2 = grid_spacing
                                    # Boundary checks
                                    if n0 < 0:
                                        n0 = 0
                                    if n0 >= max_y[i]:
                                        n0 = max_y[i] - 1
                                    if n1 < 0:
                                        n1 = 0
                                    if n1 > fdata[current_pattern]['length'] - n2:
                                        n1 = fdata[current_pattern]['length'] - n2
                                    fdata[current_pattern]['notes'][i] += [(n0, n1, n2, '2 0')]
                                    notedrag_i = i
                                    notedrag_j = len(fdata[current_pattern]['notes'][i]) - 1
                                    notedrag_pos = (x - (x_pos[i] + (n1 - offset_x) * zoom_x + 30), y - (y_pos[i] + (n0 - offset_y[i]) * zoom_y[i]))
                                    mode = 'note_drag'
                elif event.button == 2: # TODO: Figure out a better solution than this middle-click shit
                    for i in range(3):
                        if testRect((x, y), (x_pos[i] + 30, y_pos[i], width, height[i])):
                            for j in range(len(fdata[current_pattern]['notes'][i])-1, -1, -1):
                                note = fdata[current_pattern]['notes'][i][j]
                                if testRect((x, y), (x_pos[i] + (note[1] - offset_x) * zoom_x + 30, y_pos[i] + (note[0] - offset_y[i]) * zoom_y[i], note[2] * zoom_x, zoom_y[i])):
                                    n3 = ('NO BEND' if note[3] == 'PITCHBEND' else 'PITCHBEND')
                                    fdata[current_pattern]['notes'][i][j] = (note[0], note[1], note[2], n3)
                                    setDirty(True)
                                    break
                    for i in range(4, 5): # Lol
                        if testRect((x, y), (x_pos[i] + 30, y_pos[i], width, height[i])):
                            for j in range(len(fdata[current_pattern]['notes'][i])-1, -1, -1):
                                note = fdata[current_pattern]['notes'][i][j]
                                if testRect((x, y), (x_pos[i] + (note[1] - offset_x) * zoom_x + 30, y_pos[i] + (note[0] - offset_y[i]) * zoom_y[i], note[2] * zoom_x, zoom_y[i])):
                                    n3 = simpledialog.askstring('Command', 'Enter the command to execute:')
                                    if n3 is not None:
                                        fdata[current_pattern]['notes'][i][j] = (note[0], note[1], note[2], n3)
                                        setDirty(True)
                                    break
                elif event.button == 3:
                    for i in range(5):
                        if testRect((x, y), (x_pos[i] + 30, y_pos[i], width, height[i])):
                            for j in range(len(fdata[current_pattern]['notes'][i])-1, -1, -1):
                                note = fdata[current_pattern]['notes'][i][j]
                                if testRect((x, y), (x_pos[i] + (note[1] - offset_x) * zoom_x + 30, y_pos[i] + (note[0] - offset_y[i]) * zoom_y[i], note[2] * zoom_x, zoom_y[i])):
                                    fdata[current_pattern]['notes'][i].pop(j)
                                    setDirty(True)
                                    break
            elif event.type == MOUSEMOTION:
                (x, y) = event.pos
                if mode == 'scroll_y':
                    offset_y[scrollhold_i] = (y - scroll_pos - y_pos[scrollhold_i] - 90) * max_y[scrollhold_i] / (height[scrollhold_i] - 120)
                    standardizeCoords()
                elif mode == 'scroll_x':
                    offset_x = (x - scroll_pos - 30) * fdata[current_pattern]['length'] / (width - 60)
                    standardizeCoords()
                elif mode == 'note_drag':
                    note = fdata[current_pattern]['notes'][notedrag_i][notedrag_j]
                    n1 = (x - notedrag_pos[0] - x_pos[notedrag_i] - 30) / zoom_x + offset_x
                    n0 = (y - notedrag_pos[1] - y_pos[notedrag_i]) / zoom_y[notedrag_i] + offset_y[notedrag_i]
                    # Snap to grid
                    n0 = round(n0)
                    n1 = round(n1 / grid_spacing) * grid_spacing
                    # Boundary checks
                    if n0 < 0:
                        n0 = 0
                    if n0 >= max_y[notedrag_i]:
                        n0 = max_y[notedrag_i] - 1
                    if n1 < 0:
                        n1 = 0
                    if n1 > fdata[current_pattern]['length'] - note[2]:
                        n1 = fdata[current_pattern]['length'] - note[2]
                    fdata[current_pattern]['notes'][notedrag_i][notedrag_j] = (n0, n1, note[2], note[3])
                elif mode == 'note_resize':
                    note = fdata[current_pattern]['notes'][notedrag_i][notedrag_j]
                    n2 = (x - notedrag_pos[0] - x_pos[notedrag_i] - 25) / zoom_x + offset_x - note[1]
                    # Snap to grid
                    n2 = round((note[1] + n2) / grid_spacing) * grid_spacing - note[1]
                    # Boundary checks
                    if n2 <= 0:
                        n2 = 1
                    if n2 > fdata[current_pattern]['length'] - note[1]:
                        n2 = fdata[current_pattern]['length'] - note[1]
                    fdata[current_pattern]['notes'][notedrag_i][notedrag_j] = (note[0], note[1], n2, note[3])
            elif event.type == MOUSEBUTTONUP:
                if (mode == 'scroll_y' or mode == 'hold_y' or mode == 'scroll_x' or mode == 'hold_x' or mode == 'note_resize' or mode == 'note_drag') and event.button == 1:
                    if mode == 'note_resize' or mode == 'note_drag':
                        setDirty(True)
                    mode = 'normal'
                    sortNotes()
            elif event.type == KEYDOWN:
                if event.key == pygame.K_n and (pygame.key.get_mods() & KMOD_CTRL) and not (pygame.key.get_mods() & KMOD_SHIFT):
                    newFile()
                elif event.key == pygame.K_o and (pygame.key.get_mods() & KMOD_CTRL) and not (pygame.key.get_mods() & KMOD_SHIFT):
                    openFile()
                elif event.key == pygame.K_s and (pygame.key.get_mods() & KMOD_CTRL) and not (pygame.key.get_mods() & KMOD_SHIFT):
                    saveFile()
                elif event.key == pygame.K_s and (pygame.key.get_mods() & KMOD_CTRL) and (pygame.key.get_mods() & KMOD_SHIFT):
                    saveAsFile()
                elif event.key == pygame.K_r and (pygame.key.get_mods() & KMOD_CTRL) and not (pygame.key.get_mods() & KMOD_SHIFT):
                    renderFile()
            elif event.type == QUIT:
                exit()
        
        screen.fill(LTGREY)
        
        # Draw subwindows
        for i in range(5):
            surf[i].fill(DKDKGREY)
            for y_ind in range(int(offset_y[i]), int(offset_y[i] + height[i] / zoom_y[i] + 1)):
                if y_ind < 0 or y_ind >= max_y[i]:
                    continue
                for x_ind in range(int(offset_x / grid_spacing) * grid_spacing, int((offset_x + width / zoom_x) / grid_spacing + 1) * grid_spacing, grid_spacing):
                    if x_ind < 0 or x_ind >= fdata[current_pattern]['length']:
                        continue
                    pygame.draw.rect(surf[i], DKGREY, ((x_ind - offset_x) * zoom_x + 30, (y_ind - offset_y[i]) * zoom_y[i], zoom_x * grid_spacing, zoom_y[i]), 1)
                                   
            for x_ind in range(int(offset_x / 36) * 36, int((offset_x + width / zoom_x) / 36 + 1) * 36, 36):
                    if x_ind < 0 or x_ind >= fdata[current_pattern]['length']:
                        continue
                    pygame.draw.line(surf[i], LTGREY, ((x_ind - offset_x) * zoom_x + 30, 0), ((x_ind - offset_x) * zoom_x + 30, height[i]), 1)
            
            if i < 3:
                for y_ind in range(int(offset_y[i] / 12) * 12 + 8, int((offset_y[i] + height[i] / zoom_y[i]) / 12 + 1) * 12 + 8, 12):
                    if y_ind < 0 or y_ind >= max_y[i]:
                        continue
                    pygame.draw.line(surf[i], LTGREY, (30, (y_ind - offset_y[i]) * zoom_y[i]), (30 + width, (y_ind - offset_y[i]) * zoom_y[i]), 1)
                    
            tick_position = ayDll.getTickPosition()
            pygame.draw.line(surf[i], WHITE, ((tick_position - offset_x) * zoom_x + 30, 0), ((tick_position - offset_x) * zoom_x + 30, height[i]), 1)
            
            # Draw the actual notes!
            for note in fdata[current_pattern]['notes'][i]:
                pygame.draw.rect(surf[i], NOTECOLS[i], ((note[1] - offset_x) * zoom_x + 30, (note[0] - offset_y[i]) * zoom_y[i], note[2] * zoom_x, zoom_y[i]))
                pygame.draw.rect(surf[i], NOTECOLS2[i], ((note[1] - offset_x) * zoom_x + 30, (note[0] - offset_y[i]) * zoom_y[i], note[2] * zoom_x, zoom_y[i]), 2)
                if i < 3:
                    if note[3] == 'PITCHBEND':
                        pygame.draw.lines(surf[i], NOTECOLS2[i], False, (((note[1] - offset_x) * zoom_x + 35, (note[0] - offset_y[i]) * zoom_y[i] + zoom_y[i] * 0.75), ((note[1] - offset_x) * zoom_x + 40, (note[0] - offset_y[i]) * zoom_y[i] + zoom_y[i] * 0.75), ((note[1] - offset_x) * zoom_x + 45, (note[0] - offset_y[i]) * zoom_y[i] + zoom_y[i] * 0.25), ((note[1] - offset_x) * zoom_x + 50, (note[0] - offset_y[i]) * zoom_y[i] + zoom_y[i] * 0.25)), 2)
                elif i == 4:
                    textsurface = FONT.render(note[3], False, BLACK)
                    surf[i].blit(textsurface, ((note[1] - offset_x) * zoom_x + 35, (note[0] - offset_y[i]) * zoom_y[i] + zoom_y[i] / 2 - textsurface.get_height() / 2))
               
            pygame.draw.rect(surf[i], DKGREY, (0, 0, 30, height[i]))
               
            for y_ind in range(int(offset_y[i]), int(offset_y[i] + height[i] / zoom_y[i] + 1)):
                if y_ind < 0 or y_ind >= max_y[i]:
                    continue
                pygame.draw.rect(surf[i], DKDKGREY, (0, (y_ind - offset_y[i]) * zoom_y[i], 30, zoom_y[i]), 1)
                textsurface = FONT.render(y_names[i][y_ind], False, WHITE)
                surf[i].blit(textsurface, (15 - textsurface.get_width() / 2, (y_ind - offset_y[i]) * zoom_y[i] + zoom_y[i] / 2 - textsurface.get_height() / 2))


        # Draw each subwindow to the screen
        screen.blit(surf[0], (0, 60))
        screen.blit(surf[1], (800, 60))
        screen.blit(surf[2], (0, 480))
        screen.blit(surf[3], (800, 480))
        screen.blit(surf[4], (800, 690))
                
        # Draw title of each subwindow
        pygame.draw.rect(screen, DKDKGREY, (0, 30, 800, 30), 2)
        textsurface = FONT.render('Oscillator 1', False, BLACK)
        screen.blit(textsurface, (400 - textsurface.get_width() / 2, 45 - textsurface.get_height() / 2))
        
        pygame.draw.rect(screen, DKDKGREY, (800, 30, 800, 30), 2)
        textsurface = FONT.render('Oscillator 2', False, BLACK)
        screen.blit(textsurface, (1200 - textsurface.get_width() / 2, 45 - textsurface.get_height() / 2))
        
        pygame.draw.rect(screen, DKDKGREY, (0, 450, 800, 30), 2)
        textsurface = FONT.render('Bass Oscillator', False, BLACK)
        screen.blit(textsurface, (400 - textsurface.get_width() / 2, 465 - textsurface.get_height() / 2))
        
        pygame.draw.rect(screen, DKDKGREY, (800, 450, 800, 30), 2)
        textsurface = FONT.render('Drums', False, BLACK)
        screen.blit(textsurface, (1200 - textsurface.get_width() / 2, 465 - textsurface.get_height() / 2))
        
        pygame.draw.rect(screen, DKDKGREY, (800, 660, 800, 30), 2)
        textsurface = FONT.render('Commands and Settings', False, BLACK)
        screen.blit(textsurface, (1200 - textsurface.get_width() / 2, 675 - textsurface.get_height() / 2))
        
        # Draw arrows for navigation
        for i in range(5):
            pygame.draw.rect(screen, DKGREY, (x_pos[i] + width + 30, y_pos[i] + 90, 30, height[i] - 120))
            
            offset_fraction = min(1, height[i] / zoom_y[i] / max_y[i])
            offset_start = offset_y[i] / max_y[i]
            pygame.draw.rect(screen, LTGREY, (x_pos[i] + width + 30, y_pos[i] + 90 + offset_start * (height[i] - 120), 30, offset_fraction * (height[i] - 120)))
            pygame.draw.rect(screen, DKDKGREY, (x_pos[i] + width + 30, y_pos[i] + 90 + offset_start * (height[i] - 120), 30, offset_fraction * (height[i] - 120)), 2)
            
            pygame.draw.rect(screen, DKDKGREY, (x_pos[i] + width + 30, y_pos[i], 30, 30), 2)
            pygame.draw.line(screen, DKDKGREY, (x_pos[i] + width + 40, y_pos[i] + 15), (x_pos[i] + width + 51, y_pos[i] + 15), 4)
            pygame.draw.line(screen, DKDKGREY, (x_pos[i] + width + 45, y_pos[i] + 10), (x_pos[i] + width + 45, y_pos[i] + 21), 4)
            pygame.draw.rect(screen, DKDKGREY, (x_pos[i] + width + 30, y_pos[i] + 30, 30, 30), 2)
            pygame.draw.line(screen, DKDKGREY, (x_pos[i] + width + 40, y_pos[i] + 45), (x_pos[i] + width + 51, y_pos[i] + 45), 4)
            pygame.draw.rect(screen, DKDKGREY, (x_pos[i] + width + 30, y_pos[i] + 60, 30, 30), 2)
            pygame.draw.lines(screen, DKDKGREY, False, ((x_pos[i] + width + 40, y_pos[i] + 80), (x_pos[i] + width + 45, y_pos[i] + 70), (x_pos[i] + width + 50, y_pos[i] + 80)), 4)
            pygame.draw.rect(screen, DKDKGREY, (x_pos[i] + width + 30, y_pos[i] + height[i] - 30, 30, 30), 2)
            pygame.draw.lines(screen, DKDKGREY, False, ((x_pos[i] + width + 40, y_pos[i] + height[i] - 20), (x_pos[i] + width + 45, y_pos[i] + height[i] - 10), (x_pos[i] + width + 50, y_pos[i] + height[i] - 20)), 4)
            
        pygame.draw.rect(screen, DKGREY, (30, 870, width - 60, 30))
            
        offset_fraction = min(1, width / zoom_x / fdata[current_pattern]['length'])
        offset_start = offset_x / fdata[current_pattern]['length']
        pygame.draw.rect(screen, LTGREY, (30 + offset_start * (width - 60), 870, offset_fraction * (width - 60), 30))
        pygame.draw.rect(screen, DKDKGREY, (30 + offset_start * (width - 60), 870, offset_fraction * (width - 60), 30), 2)
        
        pygame.draw.rect(screen, DKDKGREY, (0, 870, 30, 30), 2)
        pygame.draw.lines(screen, DKDKGREY, False, ((20, 880), (10, 885), (20, 890)), 4)
        pygame.draw.rect(screen, DKDKGREY, (width - 30, 870, 30, 30), 2)
        pygame.draw.lines(screen, DKDKGREY, False, ((width - 20, 880), (width - 10, 885), (width - 20, 890)), 4)
        pygame.draw.rect(screen, DKDKGREY, (width, 870, 30, 30), 2)
        pygame.draw.line(screen, DKDKGREY, (width + 10, 885), (width + 21, 885), 4)
        pygame.draw.line(screen, DKDKGREY, (width + 15, 880), (width + 15, 891), 4)
        pygame.draw.rect(screen, DKDKGREY, (width + 30, 870, 30, 30), 2)
        pygame.draw.line(screen, DKDKGREY, (width + 40, 885), (width + 51, 885), 4)
        
        pygame.draw.rect(screen, DKDKGREY, (800, 870, 740, 30), 2)
        textsurface = FONT.render('Byte Usage: ' + str(len(rendered_data)) + ' / 4096', False, BLACK)
        screen.blit(textsurface, (810, 885 - textsurface.get_height() / 2))
        
        pygame.draw.rect(screen, DKDKGREY, (1540, 870, 30, 30), 2)
        pygame.draw.polygon(screen, DKDKGREY, ((1548, 878), (1562, 885), (1548, 892)))
        pygame.draw.rect(screen, DKDKGREY, (1570, 870, 30, 30), 2)
        pygame.draw.polygon(screen, DKDKGREY, ((1578, 878), (1592, 878), (1592, 892), (1578, 892)))

        # Draw menu bar
        pygame.draw.rect(screen, GREY, (0, 0, 1600, 30))
        textsurface = FONT.render(str(current_pattern) + ': ' + str(fdata[current_pattern]['name']), False, BLACK)
        screen.blit(textsurface, (800 - textsurface.get_width() / 2, 15 - textsurface.get_height() / 2))
        
        for i in range(len(menus)):
            if selected_menu == i:
                pygame.draw.rect(screen, WHITE, (90*i, 0, 90, 30))
            textsurface = FONT.render(menus[i][0], False, BLACK)
            screen.blit(textsurface, (90*i + 45 - textsurface.get_width() / 2, 15 - textsurface.get_height() / 2))
            
        if selected_menu >= 0:
            menu_list = menus[selected_menu][1]
            pygame.draw.rect(screen, WHITE, (90*selected_menu, 30, 180, 30*len(menu_list)))
            for i in range(len(menu_list)):
                item_name = menu_list[i][0]
                if item_name[0] == '*':
                    pygame.draw.line(screen, GREY, (90*selected_menu, 30*i+30), (90*selected_menu + 179, 30*i+30))
                    item_name = item_name[1:]
                textsurface = FONT.render(item_name, False, BLACK)
                screen.blit(textsurface, (90*selected_menu + 10, 30*i + 45 - textsurface.get_height() / 2))

        pygame.display.flip()