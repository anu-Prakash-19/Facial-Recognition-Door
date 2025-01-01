# It helps in identifying the faces
import cv2, sys, numpy, os
import smtplib
from email.message import EmailMessage
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
mesg = MIMEMultipart()



size = 4
haar_file = 'haarcascade_frontalface_default.xml'
datasets = 'Dataset'
# Part 1: Create fisherRecognizer
print('Recognizing Face Please Be in sufficient Lights...')
# Create a list of images and a list of corresponding names
(images, lables, names, id) = ([], [], {}, 0)
for (subdirs, dirs, files) in os.walk(datasets):
    for subdir in dirs:
        names[id] = subdir
        subjectpath = os.path.join(datasets, subdir)
        for filename in os.listdir(subjectpath):
            path = subjectpath + '/' + filename
            lable = id
            images.append(cv2.imread(path, 0))
            lables.append(int(lable))
        id += 1
(width, height) = (130, 100)
# Create a Numpy array from the two lists above
(images, lables) = [numpy.array(lis) for lis in [images, lables]]
# OpenCV trains a model from the images
# NOTE FOR OpenCV2: remove '.face'
#model = cv2.face.LBPHFaceRecognizer_create()

model = cv2.face_LBPHFaceRecognizer.create()
model.train(images, lables)

# Part 2: Use fisherRecognizer on camera stream
face_cascade = cv2.CascadeClassifier(haar_file)
webcam = cv2.VideoCapture(0)
count = 0
while True:
    (_, im) = webcam.read()
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        cv2.rectangle(im, (x, y), (x + w, y + h), (255, 0, 0), 2)
        face = gray[y:y + h, x:x + w]
        face_resize = cv2.resize(face, (width, height))
        # Try to recognize the face
        prediction = model.predict(face_resize)
        cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 3)

        if prediction[1] < 60:
            cv2.putText(im, '% s - %.0f' %
                    (names[prediction[0]], prediction[1]), (x - 10, y - 10),
                    cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
        else:
            count=count+1
            if count==100:
                cv2.imwrite("unknown.jpg",im)
                count=0
                s = smtplib.SMTP('smtp.gmail.com', 587)
                s.starttls()
                s.login("kmrkrmd@gmail.com", "ahujxmdfzzibqzqf")
                body="Unidentified Person is Found infornt of Door!"
                mesg['Subject'] = "Security Alert"
                mesg['From'] = "kmrkrmd@gmail.com"
                mesg['To'] = "xdrprabhu@gmail.com"
                mesg.attach(MIMEText(body,'plain'))
                file_path = 'unknown.jpg'
                # Open the file to be sent
                attachment = open(file_path, 'rb')

                # Instance of MIMEBase and named as p
                p = MIMEBase('application', 'octet-stream')

                # To change the payload into encoded form
                p.set_payload((attachment).read())

                # encode into base64
                encoders.encode_base64(p)

                p.add_header('Content-Disposition', f'attachment; filename= {file_path}')

                # Attach the instance 'p' to instance 'msg'
                mesg.attach(p)
                s.send_message(mesg)
                s.quit()
            cv2.putText(im, 'not recognized'+str(prediction[1]),
                    (x - 10, y - 10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))

    cv2.imshow('OpenCV', im)

    key = cv2.waitKey(10)
    if key == 27:
        break
