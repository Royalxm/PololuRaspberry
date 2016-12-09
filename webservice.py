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
user = auth.sign_in_with_email_and_password("ro@ro.com", "")
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

####################
#
#
#       Value to send
#
#       0 - Rien a faire
#       1 - Avance
#       2 - Recule
#       3 - Tourne a gauche
#       4 - Tourne a droite
#       5 - Manual control
#       6 - Start new path
#       7 - stop
#
#
#
#       Value received
#
#       0 - Rien a faire (stop)
#       1 - Prend Photo
#       2 - J'ai terminer un tour
#       3 - j'avance
#       4 - je recule
#       5 - Je tourne a droite
#       6 - je tourne a gauche
#       7 - 
#
#
#

def control_robot(data,user, tourId):

        if data['Avance'] == 1:
                set_output(1)
                print("Je le fait avancer")
        if data['Recule'] == 1:
                set_output(2)
                print("Je le fait reculer")
        if data['Droite'] == 1:
                set_output(3)
                print("Je le fait droite")
        if data['Gauche'] == 1:
                set_output(4)
                print("Je le fait gauche")
        if data['Manuel'] == 1:
                set_output(5)
                print("MANUEL")
                db.child("RobotControl").update({"Manuel":0},user['idToken'])
        if data['NewPath'] == 1:
                set_output(6)
                print("AUTOMATIC")
                db.child("RobotControl").update({"NewPath":0},user['idToken'])
        if data['Stop'] == 1:
                print("Je le fait reculer")
                set_output(7)
                db.child("RobotControl").update({"Stop":0},user['idToken'])
        if data['Avance'] == 0 and data['Recule'] == 0 and data['Droite'] == 0 and data['Gauche'] == 0 :
              #  print("Je me stop car aucun commande")
                set_output(7)
        if data['Photo'] == 1:
                pictureName = time.strftime("%Y%m%d%H%M%S")
                camera.capture('images/' +pictureName+ '.jpg')
                storage.child('images/' +tourId+'/' +pictureName+ '.jpg').put('images/'+pictureName+ '.jpg',user['idToken'])
                db.child("RobotControl").update({"Photo":0},user['idToken'])


def action_from_input( nb_received):
        
        if nb_received == 0:
                print("Rien a faire")
        elif nb_received == 1 :
                take_photo_from_raspbery(tourId)
        elif nb_received == 2 :
                print("Le tour est terminer")
        elif nb_received == 3 :
                print("Le robot avance")
        elif nb_received == 4 :
                print("Le robot recule")
        elif nb_received == 5 :
                print("Le robot tourne a droite")
        elif nb_received == 6 :
                print("Le robot tourne a gauche")



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
        
        if nb > 7 or nb < 1:
                return

        
        if(nb % 2 == 1):
                GPIO.output(14, GPIO.HIGH)

                        
        nb = int(nb/2)
        if nb < 1:
                return
        
        if(nb % 2 == 1):
                GPIO.output(15, GPIO.HIGH)
                        
        nb = int(nb/2)
        if nb < 1:
                return
        
        if(nb % 2 == 1):
                GPIO.output(18, GPIO.HIGH)                        
       
def get_input():
        
        nb = 0
        nb = nb + ( 2**0) * GPIO.input(17)
        nb = nb + ( 2**1) * GPIO.input(22)
        nb = nb + ( 2**2) * GPIO.input(27)

        return nb

         

nbToSend = 1
set_output(0)
while 1:
        data = db.child("RobotControl").get(user['idToken'])
        control_robot(data.val(),user, tourId)
        nb_receive = get_input()
        action_from_input(nb_receive)
        
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

        
        
        
                
                
