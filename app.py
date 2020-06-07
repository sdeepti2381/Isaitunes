from flask import Flask, render_template, json, redirect, url_for, request, flash
import csv
import requests
import random
import config
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from forms import FeedbackForm


x = [] 
counter = 0
cred = credentials.Certificate("./isaitunes-b24a3-firebase-adminsdk-gdo3f-c73d7bc378.json")
default_app = firebase_admin.initialize_app(cred)
db = firestore.client()



app = Flask(__name__)
#in order to prevent a CSRF attack
app.secret_key = "isaitune key"

@app.route("/")
def home():

    # randomly select a movie
    with open('spotify.csv', encoding="utf8") as f:
        reader = csv.reader(f)
        row = random.choice(list(reader))
    
    doc_ref = db.collection(u'songLD').document(row[3])
    val = None
    dval = None
    if (doc_ref.get(field_paths={'Likes'}).to_dict() is not None):
        print("HALLELUJAHHH")
        val = doc_ref.get(field_paths={'Likes'}).to_dict().get('Likes')
        dval = doc_ref.get(field_paths={'Dislikes'}).to_dict().get('Dislikes')
    else: 
        print("You suck")
        val=0
        dval = 0

    song = {
        'serialNo': row[0],
        'country': row[1],
        'rank': row[2],
        'title': row[3],
        'artists': row[4],
        'album': row[5],
        'explicit': row[6],
        'duration': row[7],
        # default poster just so we see something
        'image': 'https://i.pinimg.com/originals/4d/6f/56/4d6f56105fbf65ad87ba645f624ba93a.jpg',
        'snip': "",
        'likes': val,
        'dislikes': dval
   }

    url = "https://deezerdevs-deezer.p.rapidapi.com/search"

    querystring = {"q": row[3]}

    headers = {
        'x-rapidapi-host': "deezerdevs-deezer.p.rapidapi.com",
        'x-rapidapi-key': "a45731503amsh14457246b0a87aap102755jsn445d414e80d9"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    x.append(song)


    # parse result into JSON and look for matching data if available
    song_data = response.json()
   
    doc_ref.set({
        u'Title': song['title'],
        u'Artist': song['artists'],
        u'Duration': song['duration'],
        u'Likes': song['likes'],
        u'Dislikes': song['dislikes']
        })

    if not song_data['total'] == 0:
        songID = song_data['data'][0]['id']
        if 'cover' in song_data['data'][0]['album']:
            song['image'] = song_data['data'][0]['album']['cover_big']
            song['snip'] = song_data['data'][0]['preview']
    
    #doc_ref = db.collection(u'songLD').document(song['title'])
    #doc = doc_ref.get()
    #if doc.exists:
    #    song['likes'] = doc.get(Likes)
     #   song['dislikes'] = doc.get(Dislikes)

    # send all this data to the home.html template
    return render_template("home.html", song=song)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/feedback", methods=['GET', 'POST'])
def feedback():
    form = FeedbackForm()

    if (request.method == 'POST'):
        if (form.validate() == False):
            print("NOOOOOOOOOO")
            flash('All fields are required.')
            return render_template('feedback.html', form=form)
        else:
            #this is the place where we store the items inside a database.
            return("Form posted.")

    elif (request.method == 'GET'):
        return render_template('feedback.html', form=form)

    #return render_template('feedback.html', form=form)

@app.route("/updateLike")
def updateLike(): 
    theSong = x[0]
    doc_ref = db.collection(u'songLD').document(theSong['title'])
    doc = doc_ref.get()
    if doc.exists:
        theSong['likes'] = theSong['likes'] + 1
        doc_ref.update({u'Likes':theSong['likes']})
        print("found")
        print(theSong['likes'])
        x.remove(theSong)
        return home()
    else:
        print("""Like button was pressed,
        and so the song was newly added""")
        print(theSong['title'])
        return home()
    
    return home()

@app.route("/updateDislike")
def updateDislike(): 
    theSong = x[0]
    doc_ref = db.collection(u'songLD').document(theSong['title'])
    doc = doc_ref.get()
    if doc.exists:
        theSong['dislikes'] = theSong['dislikes'] + 1
        doc_ref.update({u'Dislikes':theSong['dislikes']})
        print("found dislike")
        print(theSong['dislikes'])
        x.remove(theSong)
        return home()
    else: 
        print(theSong['dislikes'])
        print("""Dislike button was pressed,
        and so the song was newly added""")
        return home()

    return home()

@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")

if __name__ == "__main__":
    app.run(debug=True)