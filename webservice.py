import pyrebase
import RPi.GPIO as GPIO
from picamera import PiCamera
import time
#import PyFCM as FCMNotification

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


#Configuration Notification Push

#push_service = FCMNotification(api_key = "AIzaSyDVft5fm1neJ27jwQmPDhFiE-ewjKB9DNs")

#registration_id = "eZ3XCEG8q3Q:APA91bFmtVF_kSyz5qbaYjNJ4qMq0FaTRb3LX3gwh3yDtkZslbS2F3MN28c4d2zW-zKStO7pdI26lLcUusZTLbwNLXzLUb5JP1UVg2W_xIy1-c6EjwZ9_neHt2pDh9TSBEWfOQnZ49op"
#message_title = "Pololu"
#message_body = "Envoie d'un message via notification push By Owaa"

#Configuration GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


GPIO.setup(14, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(15, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(2, GPIO.OUT, initial=GPIO.LOW)

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
tourId = time.strftime("%Y%m%d%H%M%S")


#   Configuration capteur

# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BCM)

# Define GPIO to use on Pi
GPIO_TRIGGER = 23
GPIO_ECHO    = 24

# Speed of sound in cm/s at temperature
temperature = 20
speedSound = 33100 + (0.6*temperature)

# Set pins as output and input
GPIO.setup(GPIO_TRIGGER,GPIO.OUT)  # Trigger
GPIO.setup(GPIO_ECHO,GPIO.IN)      # Echo

# Set trigger to False (Low)
GPIO.output(GPIO_TRIGGER, False)

#  Allow module to settle
time.sleep(0.5)


listeMouv = ""
manuelMode = True



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

def creat_new_tour():
    global tourId
    tourId= time.strftime("%Y%m%d%H%M%S")
    db.child("ListeTour").child(tourId).set(   {"Etat": 0 }  ,user['idToken'])
    print("Creation nouveau tour")



def control_robot(data,user, tourId):

        global manuelMode
        global listeMouv
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
                manuelMode = True
                db.child("RobotControl").update({"Manuel":0},user['idToken'])
                print("Je push le HistoMouv")
                db.child("RobotHistoMov").child(tourId).set(   {"Path": listeMouv }  ,user['idToken'])
                listeMouv = ""
                    
        if data['NewPath'] == 1:
                set_output(6)
                print("AUTOMATIC")
                manuelMode = False
                db.child("RobotControl").update({"NewPath":0},user['idToken'])
                tourId = time.strftime("%Y%m%d%H%M%S")
                creat_new_tour()
        if data['Stop'] == 1:
                print("Je le fait stop")
                set_output(0)
                db.child("RobotControl").update({"Stop":0},user['idToken'])
        if data['Avance'] == 0 and data['Recule'] == 0 and data['Droite'] == 0 and data['Gauche'] == 0 :
              #  print("Je me stop car aucun commande")
                set_output(7)
        if data['Photo'] == 1:
                #pictureName = time.strftime("%Y%m%d%H%M%S")
                #camera.capture('images/' +pictureName+ '.jpg')
                #storage.child('images/' +tourId+'/' +pictureName+ '.jpg').put('images/'+pictureName+ '.jpg',user['idToken'])
                #db.child("RobotControl").update({"Photo":0},user['idToken'])
                take_photo_from_raspbery()
                print("Prend photo")


def action_from_input( nb_received):
        global listeMouv
        if nb_received == 0:
                db.update({"RobotDoMove":1},user['idToken'])
                listeMouv = listeMouv + "1"
        elif nb_received == 1 :
                #take_photo_from_raspbery()
                print("Prend photo")
        elif nb_received == 2 :
                print("Le tour est terminer")
                
                db.child("RobotHistoMov").push({"Path":listeMouv},user['idToken'])
        elif nb_received == 3 :
                print("Le robot avance")
                db.update({"RobotDoMove":2},user['idToken'])
                listeMouv = listeMouv + "2"
        elif nb_received == 4 :
                print("Le robot recule")
                db.update({"RobotDoMove":3},user['idToken'])
                listeMouv = listeMouv + "3"
        elif nb_received == 5 :
                print("Le robot tourne a droite")
                db.update({"RobotDoMove":4},user['idToken'])
                listeMouv = listeMouv + "4"
        elif nb_received == 6 :
                print("Le robot tourne a gauche")
                db.update({"RobotDoMove":5},user['idToken'])
                listeMouv = listeMouv + "5"



def take_photo_from_raspbery():
        pictureName = time.strftime("%Y%m%d%H%M%S")
        #result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)

        global tourId
        camera.capture('images/' +pictureName+ '.jpg')
        storage.child('images/'+tourId+'/' +pictureName+ '.jpg').put('images/' +pictureName+ '.jpg',user['idToken'])
        db.child("RobotControl").update({"Photo":"0"},user['idToken'])
        db.child("ListeTour").child(tourId).child("ListePhoto").push({"Name":pictureName},user['idToken'])
        db.child("ListeTour").child(tourId).update({"Etat":1},user['idToken'])

        print("La photo a été prise")

def set_output( nb ):

        GPIO.output(14, GPIO.LOW)
        GPIO.output(15, GPIO.LOW)
        GPIO.output(2, GPIO.LOW)
        
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
                GPIO.output(2, GPIO.HIGH)                        
       
def get_input():
        
        nb = 0
        nb = nb + ( 2**0) * GPIO.input(17)
        nb = nb + ( 2**1) * GPIO.input(22)
        nb = nb + ( 2**2) * GPIO.input(27)

        return nb

         

nbToSend = 1
set_output(0)
ToStop = False
photoToTake = True
while 1:
    time.sleep(0.2)
    if ToStop == False:
        data = db.child("RobotControl").get(user['idToken'])
        control_robot(data.val(),user, tourId)
            
            
    if manuelMode == False:
        nb_receive = get_input()
        action_from_input(nb_receive)

     # Send 10us pulse to trigger
    GPIO.output(GPIO_TRIGGER, True)
    # Wait 10us
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    start = time.time()

    while GPIO.input(GPIO_ECHO)==0:
        start = time.time()

    while GPIO.input(GPIO_ECHO)==1:
        stop = time.time()

    # Calculate pulse length
    elapsed = stop-start

    # Distance pulse travelled in that time is time
    # multiplied by the speed of sound (cm/s)
    distance = elapsed * speedSound

    # That was the distance there and back so halve the value
    distance = distance / 2
        
    #print("Distance : {0:5.2f}".format(distance))
    if distance < 6:
        set_output(5)
        ToStop = True
        manuelMode = True
        if photoToTake == True:
            print("Prend une photo")
            photoToTake = False
            take_photo_from_raspbery()
    elif distance > 8:
        photoToTake = True
        ToStop = False
            
