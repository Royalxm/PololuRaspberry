import pyrebase
import RPi.GPIO as GPIO
from picamera import PiCamera
import time

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


GPIO.setup(14, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(15, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(18, GPIO.OUT, initial=GPIO.LOW)

GPIO.setup( 17, GPIO.IN , pull_up_down=GPIO.PUD_UP)
GPIO.setup( 22, GPIO.IN , pull_up_down=GPIO.PUD_UP)
GPIO.setup( 27, GPIO.IN , pull_up_down=GPIO.PUD_UP)


format = "%Y%m%d%H%M%S"
#Configuration camera

camera = PiCamera()
camera.resolution = (1024, 768)
#camera.start_preview()
# Camera warm-up time
#sleep(2)
phototaken = False
tourId = "Tour2"
def control_robot(data,user, tourId):

        if data['Avance'] == 1:
                GPIO.output(14, GPIO.HIGH)
        else:
                GPIO.output(14, GPIO.LOW)

        if data['Recule'] == 1:
                GPIO.output(15, GPIO.HIGH)
        else:
                GPIO.output(15, GPIO.LOW) 

        if data['Photo'] == 1:
                pictureName = time.strftime("%Y%m%d%H%M%S")
                camera.capture('images/' +pictureName+ '.jpg')
                storage.child('images/' +tourId+'/' +pictureName+ '.jpg').put('images/'+pictureName+ '.jpg',user['idToken'])
                db.child("RobotControl").update({"Photo":"0"},user['idToken'])


def take_photo_from_raspbery(tourId):
        pictureName = time.strftime("%Y%m%d%H%M%S")
        camera.capture('images/' +pictureName+ '.jpg')
        storage.child('images/'+tourId+'/' +pictureName+ '.jpg').put('images/' +pictureName+ '.jpg',user['idToken'])
        db.child("RobotControl").update({"Photo":"0"},user['idToken'])
        print("La photo a été prise")

def set_output( nb ):

        GPIO.output(14, GPIO.LOW)
        GPIO.output(15, GPIO.LOW)
        GPIO.output(18, GPIO.LOW)
        
        if nb > 7:
                return

        
        if(nb % 2 == 0):
                GPIO.output(14, GPIO.LOW)
                print( " 14 0" + str(nb) )
        else:
                GPIO.output(14, GPIO.HIGH)
                print( " 14 1" + str(nb) )

                        
        nb = int(nb/2)

        if nb < 1:
                return
        
        if(nb % 2 == 0):
                GPIO.output(15, GPIO.LOW)
                print( " 15 0" + str(nb))

        else:
                GPIO.output(15, GPIO.HIGH)
                print( " 15 1" + str(nb) ) 
                        
        nb = int(nb/2)


        if nb < 1:
                return
        
        if(nb % 2 == 0):
                GPIO.output(18, GPIO.LOW)
                print( " 18 0" + str(nb) )
        else:
                GPIO.output(18, GPIO.HIGH)
                print( " 18 1" + str(nb))
                        
       
def get_input():

        print( str(GPIO.input(17)) + '-'  + str(GPIO.input(22))+ '-'   + str(GPIO.input(27)) )

        
        nb = 0
        
        nb = nb + ( 2**0) * GPIO.input(17)
        nb = nb + ( 2**1) * GPIO.input(22)
        nb = nb + ( 2**2) * GPIO.input(27)

        return nb

         

nbToSend = 1

while 1:
        data = db.child("RobotControl").get(user['idToken'])
        control_robot(data.val(),user, tourId)
        #print(GPIO.input(3))
        #if GPIO.input(3) == True and phototaken == False:
        #        print ("Je recoint un IN")
        #        take_photo_from_raspbery(tourId)
        #        phototaken = True
        #if GPIO.input(3) == False:
        #        phototaken = False;

        
        #print( "Nouveau numero")
        #set_output(nbToSend)
        #time.sleep(2)
        #nbToSend = nbToSend + 1

        nb_receive = get_input()
        print( "Nombre recue " + str(nb_receive) )
        
                
                
