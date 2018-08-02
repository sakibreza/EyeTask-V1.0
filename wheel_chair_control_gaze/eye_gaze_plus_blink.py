# USAGE
# python detect_blinks.py --shape-predictor shape_predictor_68_face_landmarks.dat --video blink_detection_demo.mp4
# python detect_blinks.py --shape-predictor shape_predictor_68_face_landmarks.dat

# import the necessary packages
from scipy.spatial import distance as dist
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from imutils import face_utils
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2

i=0
con_frame = 2
dir_c = 0
dir_l = 0
dir_r = 0
init = [0,0]
coordinate = [0,0]
eye_cascade = cv2.CascadeClassifier('cascade.xml')

def direction (ini,cur) :
	ix = ini[0]
	iy = ini[1]
	cx = cur[0]
	cy = cur[1]
	rad = 30
	if init == [0,0] :
		return "not initialized"
	elif cx<=ix+rad and cx>=ix-rad :
		return "center"
	elif cx>=ix+rad :
		return "right"
	elif cx<=ix-rad :
		return "left"
		
def getangle (ini,cur) :
	ix = ini[0]
	iy = ini[1]
	cx = cur[0]
	cy = cur[1]
	a = np.array([cx,cy])
	b = np.array([ix,iy])
	c = np.array([1000,iy])
	ba = a-b
	bc = c-b
	cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
	angle = np.arccos(cosine_angle)
	return str(np.degrees(angle))

def eye_aspect_ratio(eye):
	# compute the euclidean distances between the two sets of
	# vertical eye landmarks (x, y)-coordinates
	A = dist.euclidean(eye[1], eye[5])
	B = dist.euclidean(eye[2], eye[4])

	# compute the euclidean distance between the horizontal
	# eye landmark (x, y)-coordinates
	C = dist.euclidean(eye[0], eye[3])

	# compute the eye aspect ratio
	ear = (A + B) / (2.0 * C)

	# return the eye aspect ratio
	return ear
 
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--shape-predictor", required=True,
	help="path to facial landmark predictor")
ap.add_argument("-v", "--video", type=str, default="",
	help="path to input video file")
args = vars(ap.parse_args())
 
# define two constants, one for the eye aspect ratio to indicate
# blink and then a second constant for the number of consecutive
# frames the eye must be below the threshold
EYE_AR_THRESH = 0.27
EYE_AR_CONSEC_FRAMES = 6

# initialize the frame counters and the total number of blinks
COUNTER = 0
COUNTER_L = 0
COUNTER_R = 0
TOTAL = 0
TOTAL_L = 0
TOTAL_R = 0

flag = 0 
run = 0

# initialize dlib's face detector (HOG-based) and then create
# the facial landmark predictor
print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(args["shape_predictor"])

# grab the indexes of the facial landmarks for the left and
# right eye, respectively
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

# start the video stream thread
print("[INFO] starting video stream thread...")
vs = cv2.VideoCapture(0)
fileStream = True
# vs = VideoStream(src=0).start()
# vs = VideoStream(usePiCamera=True).start()
# fileStream = False
time.sleep(1.0)

# loop over frames from the video stream
while True:
	# if this is a file video stream, then we need to check if
	# there any more frames left in the buffer to process


	# grab the frame from the threaded video file stream, resize
	# it, and convert it to grayscale
	# channels)
	ret, frame = vs.read()
	#print(type(frame))
	frame = imutils.resize(frame, width=450)
	frame = cv2.flip(frame,1)
	blink_frame = frame 
	gray = cv2.cvtColor(blink_frame, cv2.COLOR_BGR2GRAY)

	# detect faces in the grayscale frame
	rects = detector(gray, 0)

	# loop over the face detections
	for rect in rects:
		# determine the facial landmarks for the face region, then
		# convert the facial landmark (x, y)-coordinates to a NumPy
		# array
		shape = predictor(gray, rect)
		shape = face_utils.shape_to_np(shape)

		# extract the left and right eye coordinates, then use the
		# coordinates to compute the eye aspect ratio for both eyes
		leftEye = shape[rStart:rEnd]
		rightEye = shape[lStart:lEnd]
		leftEAR = eye_aspect_ratio(leftEye)
		rightEAR = eye_aspect_ratio(rightEye)

		# average the eye aspect ratio together for both eyes
		ear = (leftEAR + rightEAR) / 2.0
		blink_frame = frame
		# compute the convex hull for the left and right eye, then
		# visualize each of the eyes
		leftEyeHull = cv2.convexHull(leftEye)
		rightEyeHull = cv2.convexHull(rightEye)	
		
		#both
		flag = 0
		# check to see if the eye aspect ratio is below the blink
		# threshold, and if so, increment the blink frame counter
		if leftEAR < EYE_AR_THRESH and rightEAR < EYE_AR_THRESH:
			COUNTER += 1

		# otherwise, the eye aspect ratio is not below the blink
		# threshold
		else:
			# if the eyes were closed for a sufficient number of
			# then increment the total number of blinks
			if COUNTER >= EYE_AR_CONSEC_FRAMES:
				TOTAL += 1
				flag = 1

			# reset the eye frame counter
			COUNTER = 0
			
			#left
		
			# check to see if the eye aspect ratio is below the blink
			# threshold, and if so, increment the blink frame counter
			if leftEAR < EYE_AR_THRESH:
				COUNTER_L += 1
			

			# otherwise, the eye aspect ratio is not below the blink
			# threshold
			else:
				# if the eyes were closed for a sufficient number of
				# then increment the total number of blinks
				if COUNTER_L >= EYE_AR_CONSEC_FRAMES:
					TOTAL_L += 1
					flag = 1

				# reset the eye frame counter
				COUNTER_L = 0
			

			#right
		
			# check to see if the eye aspect ratio is below the blink
			# threshold, and if so, increment the blink frame counter
			if rightEAR < EYE_AR_THRESH:
				COUNTER_R += 1

			# otherwise, the eye aspect ratio is not below the blink
			# threshold
			else:
				# if the eyes were closed for a sufficient number of
				# then increment the total number of blinks
				if COUNTER_R >= EYE_AR_CONSEC_FRAMES:
					TOTAL_R += 1
					flag = 1 

				# reset the eye frame counter
				COUNTER_R = 0			
			
			if flag == 1 :
				if run == 0 :
					run = 1 
					cv2.putText(frame, "Start", (10, 30),
					cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
				else :
					run = 0
					cv2.putText(frame, "Stop", (10, 30),
					cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
					
			elif run == 1 :
				cv2.putText(frame, "Running...", (10, 30),
				cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
			
		
		# draw the total number of blinks on the frame along with
		# the computed eye aspect ratio for the frame
		
		cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
			cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
		
		cv2.putText(frame, "L-EAR: {:.2f}".format(leftEAR), (10, 300),
			cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
		
		cv2.putText(frame, "R-EAR: {:.2f}".format(rightEAR), (300, 300),
			cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
		
		
		
		
		frame = frame[max(leftEye[1][1],0):leftEye[5][1], max(leftEye[0][0],0):leftEye[3][0]]
		frame = cv2.resize(frame, (0,0), fx=8, fy=8)
		init[0] = int(frame.shape[1]/2)
		init[1] = int(frame.shape[0]/2)
		
 
	gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
	#ret, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
	# noise removal
	kernel = np.ones((3,3),np.uint8)
	opening = cv2.morphologyEx(gray,cv2.MORPH_OPEN,kernel, iterations = 2)
 
	# sure background area
	sure_bg = cv2.dilate(opening,kernel,iterations=3) 

	# Finding sure foreground area
	dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,5)
	ret, sure_fg = cv2.threshold(dist_transform,0.7*dist_transform.max(),255,0)
	# Finding unknown region
	sure_fg = np.uint8(sure_fg)
	unknown = cv2.subtract(sure_bg,sure_fg)
	
	img = opening
	eye = eye_cascade.detectMultiScale(img, 1.1, 5)
	cv2.circle(img, (init[0],init[1]), 3, (255, 0, 0), -1)
	cv2.line(img, (init[0]-20, init[1]), (init[0]+20, init[1]), (255,0,0), 2)
	cv2.line(img, (init[0], init[1]-20), (init[0], init[1]+20), (255,0,0), 2)
	cv2.circle(img, (coordinate[0],coordinate[1]), 3, (255, 0, 0), -1)
	#cv2.line(img, (init[0], init[1]), (coordinate[0],coordinate[1]), (0,255,0), 2)
	for (x,y,w,h) in eye:
		#cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),3)
		roi_gray = gray[y:y+h, x:x+w]
		roi_color = img[y:y+h, x:x+w]
		coordinate = [int(x+w/2),int(y+h/2)]
		print("-----")
		print("initial = " + str(init))
		print("current = " + str(coordinate))
		dir = direction(init,coordinate)
		print("direction = " + dir)
		angle = getangle(init,coordinate)
		print("angle = " + angle)

		font  = cv2.FONT_HERSHEY_SIMPLEX
		bottomLeftCornerOfTextr = (20,30)
		bottomLeftCornerOfTextc = (20,30)
		bottomLeftCornerOfTextl = (20,30)
		fontScale              = 1
		fontColor              = (255,255,255)
		lineType               = 2
		
		if dir == "center" :
			
			dir_c += 1
			
			if dir_c > con_frame :
				dir_l = 0
				dir_r = 0
				img = cv2.putText(img,'< Center >', 
				bottomLeftCornerOfTextc, 
				font, 
				fontScale,
				fontColor,
				lineType)
			
			
		elif dir == "right" :
			dir_r += 1
			
			if dir_r > con_frame :
				dir_l = 0
				dir_c = 0
				img = cv2.putText(img,'Right >', 
				bottomLeftCornerOfTextc, 
				font, 
				fontScale,
				fontColor,
				lineType)
		
		elif dir == "left" :
			dir_l += 1
			
			if dir_l > con_frame :
				dir_c = 0
				dir_r = 0
				img = cv2.putText(img,'< Left', 
				bottomLeftCornerOfTextc, 
				font, 
				fontScale,
				fontColor,
				lineType)
			
	cv2.imshow('eye_gaze',img)
	cv2.imshow('eye_blink',blink_frame)
	
	k = cv2.waitKey(30) & 0xff
	if k == 27:
		break
# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()