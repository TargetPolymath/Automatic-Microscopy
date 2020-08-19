# Orchestration for image capture in Automatic Microscopy

import serial
import time
import gphoto2 as gp

import atexit

import os
import sys
import datetime

import subprocess

delay_time = float(sys.argv[3])

popen_closeout_registry = [];

# Serial Setup

stage_com = serial.Serial('/dev/ttyACM0', 115200); # My TTY for Arduino. Configure to taste.

time.sleep(2);

if stage_com.isOpen():
	print("PORT OPEN")

stage_pos = 0;

def stage_closeout():
	stage_com.write(b'X0');
	time.sleep(0.1); # ensure the message reaches the driver; we don't need to wait for the move to complete before we disconnect
	stage_com.close()

atexit.register(stage_closeout)
# ser.write(b'X10');


###################

# gphoto2 setup

camera = gp.Camera()
print('Please connect and switch on your camera')
while True:
	try:
		camera.init()
	except gp.GPhoto2Error as ex:
		if ex.code == gp.GP_ERROR_MODEL_NOT_FOUND:
			print('-')
			# no camera, try again in 2 seconds
			time.sleep(2)
			continue
		# some other error we can't handle here
		raise
	# operation completed successfully so exit loop
	break
# continue with rest of program

atexit.register(camera.exit)

now = datetime.datetime.now()
rel_folderpath = os.path.join(os.getcwd(), now.strftime('%Y-%m-%d_%H:%M:%S'))
os.mkdir(rel_folderpath)

text = camera.get_summary()
print('Summary')
print('=======')
print(str(text))
print('=======')



def move_stage():
	global stage_pos
	stage_pos += int(sys.argv[2])

	stage_com.write(b'X%d '%stage_pos) # Doesn't block for movement




def single_capture():
	now = datetime.datetime.now()

	file_path = camera.capture(gp.GP_CAPTURE_IMAGE);

	target = os.path.join(rel_folderpath, now.strftime('%Y-%m-%d_%H:%M:%S?') + file_path.name)

	# print(target)

	camera_file = camera.file_get(file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL)
	camera_file.save(target)

	popen_closeout_registry.append(subprocess.Popen(["ufraw-batch", "--out-type", "png", target])); # Doesn't block until an atexit manager waits for completion


def ufraw_closeout():
	print("Waiting for ufraw closeout...")
	for subp in popen_closeout_registry:
		subp.wait();
	print("ufraw closeout complete...")
atexit.register(ufraw_closeout)

if __name__ == "__main__":

	for image in range(int(sys.argv[1])):
		print("Frame");
		start_snap = time.time()
		single_capture()
		move_stage()
		end_snap = time.time()
		if (delay_time != 0) and (end_snap < start_snap + delay_time):
			print("Sleeping");
			time.sleep(delay_time - (end_snap - start_snap))

		stage_com.write(b'X0 ') # Reset to starting position






