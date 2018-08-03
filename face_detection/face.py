import numpy as np
import cv2

face_cascade = cv2.CascadeClassifier('face.xml')

cap = cv2.VideoCapture(0)
init = [0,0]
coordinate = [0,0]


# flag = 0 for only center/left/right
# flag = 1 for center/left/right/up/down

def direction (ini,cur,flag=1) : 
	ix = ini[0]
	iy = ini[1]
	cx = cur[0]
	cy = cur[1]
	rad = 10
	if init == [0,0] :
		return "not initialized"
	elif cx<=ix+rad and cx>=ix-rad :
		if flag == 0 :
			return "center"
		elif flag == 1 and cy>=iy+rad :
			return "down"
		elif flag == 1 and cy<=iy-rad :
			return "up"
		else :
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
	
while 1:
	ret, img = cap.read()
	img = cv2.flip(img,1)
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	faces = face_cascade.detectMultiScale(gray, 1.3, 3)
	cv2.circle(img, (init[0],init[1]), 3, (0, 255, 0), -1)
	cv2.line(img, (init[0], init[1]), (coordinate[0],coordinate[1]), (0,255,0), 2)
	for (x,y,w,h) in faces:
		cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),3)
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
		bottomLeftCornerOfTextr = (200,250)
		bottomLeftCornerOfTextc = (80,250)
		bottomLeftCornerOfTextl = (20,250)
		fontScale              = 1
		fontColor              = (255,255,255)
		lineType               = 2
		
		if dir == "center" :
			img = cv2.putText(img,'< Center >', 
			bottomLeftCornerOfTextc, 
			font, 
			fontScale,
			fontColor,
			lineType)
		elif dir == "right" :
			img = cv2.putText(img,'Right >', 
			bottomLeftCornerOfTextr, 
			font, 
			fontScale,
			fontColor,
			lineType)
		
		elif dir == "left" :
			img = cv2.putText(img,'< left', 
			bottomLeftCornerOfTextl, 
			font, 
			fontScale,
			fontColor,
			lineType)
		
		elif dir == "up" :
			img = cv2.putText(img,'< Up >', 
			bottomLeftCornerOfTextc, 
			font, 
			fontScale,
			fontColor,
			lineType)
		
		elif dir == "down" :
			img = cv2.putText(img,'< Down >', 
			bottomLeftCornerOfTextc, 
			font, 
			fontScale,
			fontColor,
			lineType)
		
	cv2.imshow('img',img)
	k = cv2.waitKey(30) & 0xff
	
	# init is happening here for pressing 'i', you've to do it using eye blinks
	if k == 105:
		init = [int(x+w/2),int(y+h/2)]
	elif k == 27:
		break

cap.release()
cv2.destroyAllWindows()