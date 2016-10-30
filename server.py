import json
import os
#import ibm_db
import re
import psycopg2 as dbapi2
from flask import Flask
from flask import redirect
from flask import render_template
from flask.helpers import url_for
from flask import Flask, render_template, request
import random
app = Flask(__name__)


def get_elephantsql_dsn(vcap_services):
    """Returns the data source name for ElephantSQL."""
    parsed = json.loads(vcap_services)
    uri = parsed["elephantsql"][0]["credentials"]["uri"]
    match = re.match('postgres://(.*?):(.*?)@(.*?)(:(\d+))?/(.*)', uri)
    user, password, host, _, port, dbname = match.groups()
    dsn = """user='{}' password='{}' host='{}' port={}
             dbname='{}'""".format(user, password, host, port, dbname)
    return dsn
    
@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/samplecommit')
def movies_page():
    return render_template('samplecommit.html')

@app.route('/signup', methods = ['POST', 'GET'])
def page_signup():
    
    if request.method == 'POST':
       # if request.type['submit'] == 'register':
            idr = random.randint(1,10000)
            eml = request.form['email']
            nm = request.form['firstname']
            lstnm = request.form['lastname']
            phnm =  request.form['phonenumber']
            pssw = request.form['password']
            gndr = request.form['gender']
            
            with dbapi2.connect(app.config['dsn']) as connection:
                 cursor = connection.cursor()
                 
                 #query = "UPDATE COUNTER SET N = N + 1"
                 #cursor.execute(query)
                 
                 query = """INSERT INTO USERS (ID,EMAIL,NAME,LASTNAME,PHONENUMBER,PASSWORD,GENDER)
                        VALUES
                        (%s,'%s', '%s', '%s', '%s', '%s', '%s')""" % (idr,eml,nm,lstnm,phnm,pssw,gndr)
                 cursor.execute(query)
                 
                 
                 connection.commit()
                 
            return render_template('page_signup.html')
      
    elif request.method == 'GET':
        
        return render_template('page_signup.html')
    
  

@app.route('/adminuser')
def page_adminuser():
    return render_template('page_useradmin.html')


@app.route('/tweetsPage')
def efe_page():
    return render_template('tweetsPage.html')

@app.route('/samplecommit4')
def emre_page():
    return render_template('samplecommit4.html')

@app.route('/samplecommit5')
def kursat_page():
    return render_template('samplecommit5.html')

@app.route('/tweetsPage/addTweet', methods=['GET', 'POST'])
def add_tweet_page():
    if 'add_tweet' in request.form:
        print 'Added tweet to database'

        content = str(request.form['CONTENT'])

        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
        
            cursor.execute("""INSERT INTO TWEETS (CONTENT) VALUES (%s)""", [content])

            connection.commit()

    return render_template('addTweet.html')

@app.route('/tweetsPage/allTweets')
def all_tweets_page():
    allTweets = get_allTweets()

    return render_template('allTweets.html', tweets = allTweets)

def get_allTweets():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        
        cursor.execute("SELECT * FROM TWEETS")
        tweets = cursor.fetchall()
        
        connection.commit()
        
        return tweets

@app.route('/count')
def counter_page():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = "UPDATE COUNTER SET N = N + 1"
        cursor.execute(query)
        connection.commit()

        query = "SELECT N FROM COUNTER"
        cursor.execute(query)
        count = cursor.fetchone()[0]
    return "This page was accessed %d times." % count


@app.route('/initdb')
def initialize_database():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = """DROP TABLE IF EXISTS COUNTER"""
        cursor.execute(query)

        query = """CREATE TABLE COUNTER (N INTEGER)"""
        cursor.execute(query)

        query = """INSERT INTO COUNTER (N) VALUES (0)"""
        cursor.execute(query)


        query = """DROP TABLE IF EXISTS USERS"""
        cursor.execute(query)

        query = """CREATE TABLE USERS (
        ID SERIAL PRIMARY KEY,
        EMAIL VARCHAR(80),
        NAME VARCHAR(80),
        LASTNAME VARCHAR(80),
        PHONENUMBER VARCHAR(20),
        PASSWORD VARCHAR(80),
        GENDER VARCHAR(10)
          )"""
        cursor.execute(query)

        query = """DROP TABLE IF EXISTS TWEETS"""
        cursor.execute(query)

        query = """CREATE TABLE TWEETS (
        ID SERIAL NOT NULL,
        CONTENT VARCHAR(140),
        PRIMARY KEY(ID)
        )"""
        cursor.execute(query)

        query = """INSERT INTO USERS (ID,EMAIL,NAME,LASTNAME,PHONENUMBER,PASSWORD,GENDER) VALUES (6312,'koksalb@itu.edu.tr','Berkay','Koksal','05385653858','parola123','Male')"""
        cursor.execute(query)
        
        query = """INSERT INTO USERS (ID,EMAIL,NAME,LASTNAME,PHONENUMBER,PASSWORD,GENDER) VALUES (6313,'helvacie@itu.edu.tr','Efe','Helvaci','05442609613','efeparola','Male')"""
        cursor.execute(query)

        query = """INSERT INTO TWEETS (CONTENT) VALUES ('Hello, twitter!')"""
        cursor.execute(query)

        query = """DROP TABLE IF EXISTS NOTIFICATIONS"""
        cursor.execute(query)

        query = """CREATE TABLE NOTIFICATIONS (
        ID SERIAL PRIMARY KEY,
        FROMID SERIAL,
        TWEETID SERIAL,
        TYPE VARCHAR(40), 
        TIME VARCHAR (80) )
        """
        cursor.execute(query)

        query = """INSERT INTO NOTIFICATIONS (ID, FROMID, TWEETID, TYPE, TIME) VALUES (6312, 6213, 3455, 'LIKE', '30.10.2016, 01:12')"""
        cursor.execute(query)

        connection.commit()
    return redirect(url_for('home_page'))


if __name__ == '__main__':

    VCAP_APP_PORT = os.getenv('VCAP_APP_PORT')
    if VCAP_APP_PORT is not None:
        port, debug = int(VCAP_APP_PORT), False
    else:
        port, debug = 5000, True
    VCAP_SERVICES = os.getenv('VCAP_SERVICES')
    if VCAP_SERVICES is not None:
        app.config['dsn'] = get_elephantsql_dsn(VCAP_SERVICES)
    else:
        app.config['dsn'] = """user='hknbgryr' password='Yte_gcTO9oEeCFVM7dKv53djw8VnaJwP'
                               host='jumbo.db.elephantsql.com' port=5432 dbname='hknbgryr'"""
   
    app.run(host='0.0.0.0', port=port, debug=debug)

