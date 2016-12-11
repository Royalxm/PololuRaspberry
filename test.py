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
photo = 0
tourId = time.strftime("%Y%m%d%H%M%S")



def creat_new_tour():
    global tourId
    tourId= time.strftime("%Y%m%d%H%M%S")
    db.child("ListeTour").child(tourId).set(   {"Etat": 0 }  ,user['idToken'])
    print("Creation nouveau tour")
    return tourId

    
def take_photo_from_raspbery():
        pictureName = time.strftime("%Y%m%d%H%M%S")
        global tourId
        db.child("ListeTour").child(tourId).child("ListePhoto").push({"Name":pictureName},user['idToken'])
        print("La photo a été prise")

creat_new_tour()
while 1:
    take_photo_from_raspbery()
    time.sleep(2)
    photo = photo + 1
    if photo == 4 or photo == 8:
        creat_new_tour()
    
