from flask_pymongo import PyMongo
from flask import Flask, render_template, url_for, request, session, redirect
import bcrypt
from twilio import twiml
from twilio.rest import Client
import requests
from pprint import pprint
from twilio.twiml.messaging_response import MessagingResponse
app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'mymongodb'
app.config['MONGO_URI'] = 'mongodb://hemantuser:hemantuser@ds012578.mlab.com:12578/mymongodb'
mongo = PyMongo(app)
subscription_key = "ffb7ffe983934ba0a89d7160a14e0b86"
text_analytics_base_url = "https://westcentralus.api.cognitive.microsoft.com/text/analytics/v2.0/"
sentiment_api_url = text_analytics_base_url + "sentiment"
print(sentiment_api_url)

assert subscription_key
@app.route('/')
def index():
    return render_template('register.html')


@app.route('/dashboard', methods=['POST','GET'])
def dashboard():
    return  render_template('dashboard.html')

@app.route('/loginpage', methods=['POST','GET'])
def loginpage():
    return  render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username']})

        if existing_user:
            if bcrypt.hashpw(request.form['pass'].encode('utf-8'), existing_user['password'].encode('utf-8')) == existing_user['password'].encode('utf-8'):
                session['username'] = request.form['username']
                return redirect(url_for('dashboard'))
        return 'Wrong! Credentials'
    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name' : request.form['username'], 'password' : hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('loginpage'))

        return 'That username already exists!'

    return render_template('register.html')

@app.route('/check')
def check():
    if request.method == 'POST':
        if request.form['submit'] == '1':
            return render_template('register.html')
        elif request.form['submit'] == '2':
            return render_template('login.html')
        else:
            pass

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/contact')
def contact():
    return render_template('register.html')



@app.route('/sends',methods=['GET', 'POST'])
def sends():
    # Your Account SID from twilio.com/console
    account_sid = "ACbc363fe9b448c224b1a47de31c9afc43"
    # Your Auth Token from twilio.com/console
    auth_token  = "5ee7b553fb030587ea94e5e790028f9f"
    client = Client(account_sid, auth_token)

    pt=request.form['producttype']
    number=request.form['clientnumber']
    name=request.form['namee']
    message = client.messages.create(
        to=str(number),
        from_="+15005550006",
        body="Hi "+name+"  I saw that your product "+pt+" Coke was delivered, How do you like it?")
    print(message.sid,message.status,message.body)# prints the message succesfully but cannot send as i had a trial account. Screenshot in ZIP
    return render_template('about.html')
@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)

    doc={'documents':[{'id':'1','text':body}]}

    headers   = {"Ocp-Apim-Subscription-Key": subscription_key}
    response  = requests.post(sentiment_api_url, headers=headers, json=doc)
    sentiments = response.json()
    resp = MessagingResponse()

    print(sentiments)
    if(sentiments['documents'][0]['score']>0.5):
        resp.message("Great Can you describe what you love the most?")
    else:
        resp.message("I am sorry to hear that, what do you dislike about the product?")

    return str(resp)

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True)
