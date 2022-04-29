import pyautogui
from time import sleep
import win32gui
import win32con
import win32api
import win32ui
from ctypes import windll
from PIL import Image
import winsound
import numpy as np

import win32gui
import threading

pyautogui.FAILSAFE = True # Scroll to corner to end
pyautogui.PAUSE = 0.3 # Delay between autogui presses
'''
Executes sequence of actions

Input:
seq (array[(str, int)]): Array of tuples representing (key to be pressed, number of times to press). 
			 			 If key is None sleep for second item's time.

Output:
None
'''

import cv2
import tkinter as tk

# Global levellers:
level_seq_bg = [ (0x70,1), (ord('1'),1),(ord('5'),1),(None,5), (ord('4'), 4), (0x09,1),]
farm_seq_bg = [(ord('4'), 6), (0x09,1), (ord('1'),1), (ord('5'),1),(None,1)]
fast_level_seq_bg = [ (0x70,1), (ord('1'),1),(ord('5'),1),(None,4), (ord('4'), 4), (0x09,1),]
auto_pick = [(ord('4'),4), (None, 4)]
ao_fight = [(0x71,2), (ord('1'),3), (0x72,2), (ord('1'),5), (None, 1)]
values_map = [[(None,1)], farm_seq_bg, level_seq_bg]
values = ["Pause", "Farm", "Level", "Auto Pickup"]

# Define window using TKInter. Should show a radio button panel.
root = tk.Tk()
vcmd = root.register(lambda x: (x == "") or (str.isdigit(x) and int(x) < 12))
root.title('I am PogChamp')
var = tk.StringVar(root, "1")
delay = tk.StringVar(root, "1", )
root.lift()
root.wm_attributes("-topmost", True)
root.geometry("+5+5")
root.attributes('-alpha', 0.5)
root.overrideredirect(True)

for ind, x in enumerate(values):
	tk.Radiobutton(root, text=x, variable=var,
				value=ind, indicator=0, background = "sky blue",
				).pack(fill='x', ipady=5)
exit_button = tk.Button(root, text="Exit", background = 'red', command=root.destroy).pack(fill='x', ipady=5)
tk.Entry(root, textvariable=delay, validate='all', validatecommand=(vcmd, "%P")).pack(ipady=10)

# Take and return screenshot of your window id.
def take_ss(window_id):
	hwnd = window_id
	left, top, right, bot = win32gui.GetWindowRect(hwnd)
	w = right - left
	h = bot - top

	hwndDC = win32gui.GetWindowDC(hwnd)
	mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
	saveDC = mfcDC.CreateCompatibleDC()

	saveBitMap = win32ui.CreateBitmap()
	saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

	saveDC.SelectObject(saveBitMap)

	# Change the line below depending on whether you want the whole window
	# or just the client area.
	result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 0)

	bmpinfo = saveBitMap.GetInfo()
	bmpstr = saveBitMap.GetBitmapBits(True)

	im = np.array(Image.frombuffer(
		'RGB',
		(bmpinfo['bmWidth'], bmpinfo['bmHeight']),
		bmpstr, 'raw', 'BGRX', 0, 1))

	win32gui.DeleteObject(saveBitMap.GetHandle())
	saveDC.DeleteDC()
	mfcDC.DeleteDC()
	win32gui.ReleaseDC(hwnd, hwndDC)

	return im

# Detect template in window id
def sift_detector(window_id):
	new_image = take_ss(window_id)
	hwnd = window_id
	image_template = cv2.imread("anti-nacro.png")

	# Function that compares input image to template
    # It then returns the number of SIFT matches between them
	image1 = cv2.cvtColor(new_image, cv2.COLOR_BGR2GRAY)
	image2 = image_template

	# Create SIFT detector object
	sift = cv2.xfeatures2d.SIFT_create()
	# Obtain the keypoints and descriptors using SIFT
	keypoints_1, descriptors_1 = sift.detectAndCompute(image1, None)
	keypoints_2, descriptors_2 = sift.detectAndCompute(image2, None)

	# Define parameters for our Flann Matcher
	FLANN_INDEX_KDTREE = 0
	index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 3)
	search_params = dict(checks = 100)

	# Create the Flann Matcher object
	flann = cv2.FlannBasedMatcher(index_params, search_params)

	# Obtain matches using K-Nearest Neighbor Method
	# the result 'matchs' is the number of similar matches found in both images
	matches = flann.knnMatch(descriptors_1, descriptors_2, k=2)

	# Store good matches using Lowe's ratio test
	good_matches = []
	for m,n in matches:
		if m.distance < 0.7 * n.distance:
			good_matches.append(m)
	print(len(good_matches))

	if len(good_matches) > 150:
		print('beep')
		duration = 3000  # milliseconds
		freq = 560  # Hz
		winsound.Beep(freq, duration)
		winsound.Beep(freq, duration)
		sleep(10000)
	return

def exec_sequence_bg(seq, window_id):
	eat = 0
	og_val = seq
	while(True):
		# Pause if pause clicked
		if int(var.get()) == 0:
			continue
		else:
			seq = values_map[int(var.get())]
			if og_val != int(var.get()):
				print(f"Sequence changed, new sequence: {seq}")
				og_val = int(var.get())


		# Check for eat
		if eat % 200 == 0:
			win32gui.SendMessage(window_id, win32con.WM_ACTIVATE, win32con.WA_CLICKACTIVE, 0)
			win32api.PostMessage(window_id, win32con.WM_KEYDOWN, 0x71, 0)
			sleep(0.2)
			win32api.PostMessage(window_id, win32con.WM_KEYUP, 0x71, 0)
		if eat % 10 == 0:
			win32gui.SendMessage(window_id, win32con.WM_ACTIVATE, win32con.WA_CLICKACTIVE, 0)
			win32api.PostMessage(window_id, win32con.WM_KEYDOWN, 0x74, 0)
			sleep(0.2)
			win32api.PostMessage(window_id, win32con.WM_KEYUP, 0x74, 0)

		# Detect macro
		sift_detector(window_id)

		# Read sequence
		for key,reps in seq:
			if key:
				for i in range(reps):
					win32gui.SendMessage(window_id, win32con.WM_ACTIVATE, win32con.WA_CLICKACTIVE, 0)
					win32api.PostMessage(window_id, win32con.WM_KEYDOWN, key, 0)
					sleep(0.1)
					win32api.PostMessage(window_id, win32con.WM_KEYUP, key, 0)
					win32api.PostMessage(window_id, win32con.WM_KEYDOWN, ord('4'), 0)
					win32api.PostMessage(window_id, win32con.WM_KEYUP,  ord('4'), 0)
			else:
				for i in range(int(delay.get() or 0)):
					# Break out if u change during a delay
					if og_val != int(var.get()):
						og_val = int(var.get())
						break
					pyautogui.sleep(1)
		eat+=1
	pass

def winEnumHandler( hwnd, ctx ):
    if win32gui.IsWindowVisible( hwnd ):
        print (hex(hwnd), win32gui.GetWindowText( hwnd ))

def show_window(hwnd, on):
	# Show overlay if tabbed in
	if win32gui.GetForegroundWindow() == hwnd:
		if not on:
			root.deiconify()
		on = True
	else:
		if on:
			root.withdraw()
		on = False
	root.after(2, lambda: show_window(hwnd, on))
	return
# win32gui.EnumWindows( winEnumHandler, None )

# Get window id for game.
window_id = win32gui.FindWindow(None, "Client Version 1.2.0(37842)")
print(window_id)

# Start thread for bot.
sift_detector(window_id)
t1 = threading.Thread(target=exec_sequence_bg, args=[farm_seq_bg, window_id])
t1.daemon = True  # background thread will exit if main thread exits
t1.start()
root.after(2, lambda : show_window(window_id, False))
root.mainloop()