import pyrebase
import RPi.GPIO as GPIO
from picamera import PiCamera

#Configuration Firebase
config = {
    "apiKey": "AIzaSyDVft5fm1neJ27jwQmPDhFiE-ewjKB9DNs",
    "authDomain": "robotics-17a2b.firebaseapp.com",
    "databaseURL": "https://robotics-17a2b.firebaseio.com",
    "storageBucket": "robotics-17a2b.appspot.com"
  };


firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
user = auth.sign_in_with_email_and_password("ro@ro.com", "azerty")
db = firebase.database()
storage = firebase.storage()
print ("database OKAY")

#Configuration GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(14, GPIO.OUT, initial=GPIO.LOW)# broche 12 est une sortie initialement a l'etat haut
GPIO.setup(15, GPIO.OUT, initial=GPIO.LOW)# broche 12 est une sortie initialement a l'etat haut



#Configuration camera

camera = PiCamera()
camera.resolution = (1024, 768)
#camera.start_preview()
# Camera warm-up time
#sleep(2)
def control_robot(data):

	if data['Avance'] == 1:
		GPIO.output(14, GPIO.HIGH)
	else:
		GPIO.output(14, GPIO.LOW)

	if data['Recule'] == 1:
		GPIO.output(15, GPIO.HIGH)
	else:
		GPIO.output(15, GPIO.LOW)

	if data['Photo'] == 1:
		camera.capture('images/example.jpg')
		storage.child("images/example.jpg").put("ImageTest/ex.jpg",user['idToken'])

	


while 1:

	data = db.child("RobotControl").get(user['idToken'])
	control_robot(data.val())



