#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""IS211 Assignment Final Project - Blog Application.  Tested in Python 3.6.3 :: Anaconda, Inc."""

from flask import Flask, session, render_template, request, redirect, flash, url_for
from functools import wraps
import datetime
import re
import sqlite3

connection = sqlite3.connect('blog.db')
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

def init_db():
    with open('schema.sql') as db:
        cursor.executescript(db.read())

    testposts = [
        (1, 'admin', 'Blog 1st Post', '2018-12-14', 'Today is December 14, 2018, Friday.  The weather is cold at mid 40s degree.  Forecast with rain in NYC.  Remember to bring an umbrella', 'True'),
        (2, 'admin', 'Blog 2nd Post', '2018-12-15', 'Today is December 15, 2018, Saturday.  The weather is cold at low 40s degree.  No rain in the forecast', 'True'),
        (3, 'admin', 'Blog 3rd Post', '2018-12-16', 'Today is December 16, 2018, Sunday.  The weather is cold in in high 30s and low 40s degree.  Rain all day today.  Perfect day to work on blog app', 'True')
    ]
    cursor.executemany('INSERT into blogposts VALUES (?,?,?,?,?,?)', testposts)
    connection.commit()

app = Flask(__name__)
app.secret_key = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'

def login_required(f):
   @wraps(f)
   def wrap(*args, **kwargs):
       if 'logged_in' in session and session['logged_in'] == True:
           return f(*args, **kwargs)
       else:
           return redirect('/login')
   return wrap

@app.route('/')
def index():
    published = "True"
    if 'user' in session:
        user = session['user']
    else:
        user = 'Guest'
    cursor.execute('SELECT * FROM blogposts WHERE publish=? ORDER BY id DESC', [published])
    blogposts = cursor.fetchall()
    return render_template('index.html', blogposts=blogposts, user=user)

@app.route('/login', methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or \
                request.form['password'] != 'password':
            session['logged_in'] = False
            session['user'] = 'Guest'
            error = 'The information entered is not correct. Please enter correct username and password.'
        else:
            session['user'] = request.form['username']
            session['logged_in'] = True
            return redirect('/dashboard')
    return render_template('login.html', error=error)

@app.route('/logout', methods=['GET'])
def logout():
    session['user'] = 'Guest'
    session['logged_in'] = False
    return redirect('/')

@app.route('/dashboard')
@login_required
def dashboard():
    cursor.execute('SELECT * FROM blogposts ORDER BY id DESC')
    blogposts = cursor.fetchall()
    return render_template('dashboard.html', blogposts=blogposts)

@app.route('/delete/<id>')
@login_required
def delete_post(id):
    cursor.execute('DELETE from blogposts WHERE id = ?', id)
    connection.commit()
    return redirect('/dashboard')

@app.route('/add', methods=['GET','POST'])
@login_required
def add():
    error = None
    if request.method == 'POST':
        if re.match(r'^\s*$', request.form['title']) \
                or re.match(r'^\s*$', request.form['entry']):
            error = 'Field(s) can not be blank. Please try again.'
        else:
            title = request.form['title']
            entry = request.form['entry']
            postdate = datetime.date.today()
            author = session['user']
            published = "True"
            cursor.execute(
                'INSERT INTO blogposts(author, title, postdate, entry, publish) '
                'VALUES (?,?,?,?,?)', (author, title, postdate, entry, published))
            connection.commit()
            return redirect('/')
    return render_template('add.html', error=error)

@app.route('/edit/<id>', methods=['GET','POST'])
@login_required
def edit(id):
    error = None
    if request.method == 'GET':
        cursor.execute('SELECT * FROM blogposts WHERE id=?', id)
        blogpost = cursor.fetchone()
        return render_template('edit.html', blogpost=blogpost)
    elif request.method == 'POST':
        if re.match(r'^\s*$', request.form['entry']):
            error = 'Field(s) can not be blank. Please try again.'
            cursor.execute('SELECT * FROM blogposts WHERE id=?', id)
            blogpost = cursor.fetchone()
            return render_template('edit.html', error=error, blogpost=blogpost)
        else:
            entry = request.form['entry']
            id = request.form['blogid']
            cursor.execute('UPDATE blogposts SET entry=? WHERE id=?', (entry,id))
            connection.commit()
            return redirect('/')

@app.route('/permalink/<id>')
def permalink(id):
    cursor.execute('SELECT * FROM blogposts WHERE id=?', id)
    blogpost = cursor.fetchone()
    return render_template('permalink.html', blogpost=blogpost)

@app.route('/publish/<id>')
@login_required
def publish_post(id):
    cursor.execute('SELECT * FROM blogposts WHERE id=?', id)
    blogpost = cursor.fetchone()
    if blogpost['publish'] == "True":
        published = "False"
    elif blogpost['publish'] == "False":
        published = "True"
    cursor.execute('UPDATE blogposts SET publish=? WHERE id=?', (published, id))
    connection.commit()
    return redirect('/dashboard')

if __name__ == '__main__':
    init_db()
    app.run()