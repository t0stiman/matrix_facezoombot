import cv2

#zoom in on the first face found and return True.
#If no faces are found return False.
def do_facezoom(imagePath):
	faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
	eyeCascade = cv2.CascadeClassifier('haarcascade_eye.xml')

	anImage = cv2.imread(imagePath)
	grayImage = cv2.cvtColor(anImage, cv2.COLOR_BGR2GRAY)

	# Detect faces in the image
	faces = faceCascade.detectMultiScale(
		grayImage,
		scaleFactor=1.2,
		minNeighbors=5,
		# minSize=(30, 30)
	)

	for (x, y, w, h) in faces:
		zoomed_gray = grayImage[y:y+h, x:x+w]
		#detect eyes
		eyes = eyeCascade.detectMultiScale(
			zoomed_gray,
			scaleFactor=1.2,
			minNeighbors=5,
			# minSize=(30, 30)
		)

		if len(eyes) > 0:
			extraCrop = float(20)    #procent extra crop on each side
			horOffset = int(round(h*(extraCrop/100.0)))
			verOffset = int(round(w*(extraCrop/100.0)))

			#crop & save image
			cropped_color = anImage[y+horOffset:y+h-horOffset, x+verOffset:x+w-verOffset]
			cv2.imwrite(imagePath, cropped_color)

			print('face found and saved')
			return True

	print('no face found!')
	return False