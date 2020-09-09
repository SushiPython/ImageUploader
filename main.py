from flask import Flask, render_template, redirect, request, send_file
import os
import base64
import pymongo
from pymongo import MongoClient
from io import BytesIO
from PIL import Image
import io
import sys
import numpy as np
import random
import string
import randomstr
from threading import Thread
import time
from randomstr import randomstr

key = os.getenv('key')
client = pymongo.MongoClient(f"mongodb+srv://dbUser:{key}@cluster0-ylmii.mongodb.net/test?retryWrites=true&w=majority")

collection = client['main']['main']

secondsInADay = 86400

app = Flask(__name__, static_url_path='/static')  

app.config['UPLOAD_FOLDER'] = 'static/images'

@app.route('/')  
def upload():  
    return render_template("file_upload_form.html")  

@app.route('/success', methods = ['POST'])  
def success():  
    if request.method == 'POST':  
        f = request.files['file']
        f = f.read()
        rs = (randomstr(length=10, charset='alphanumeric', readable=False, capitalization=False))
        im = Image.open(io.BytesIO(f))
        with io.BytesIO() as b:
          im.save(b,quality=20,optimize=True, format=im.format)
          output_bytes = b.getvalue() 
          collection.insert_one({
            "imageId": rs, 
            "image": output_bytes,
            "lastView": time.time()
          })
          x = {
            "image_loc": f"https://i.sushipython.us/i/{rs}",
            "image_id": rs
          }
        return x

def deleteOldImages():
  while True:
    time.sleep(secondsInADay - (time.time() % secondsInADay))
    for doc in collection.find({
    'last_view': {'$lt': time.time() - 86400 * 30}
    }):
      collection.delete_one(doc)
      print('ok, deleted an image')

@app.route('/i/<image>')
def img(image):
  i = collection.find_one({"imageId": image})['image']
  collection.update_one({
    "imageId": image
  }, {
    '$set': {
      "lastView": time.time()
    }
  })
  return send_file(
    io.BytesIO(i),
    mimetype='image/jpeg')

Thread(None, deleteOldImages).start()

if __name__ == '__main__':  
  app.run(host='0.0.0.0', debug = True)