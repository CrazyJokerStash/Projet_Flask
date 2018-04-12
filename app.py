#! /usr/bin/python
# -*- coding:utf-8 -*-

import mysql.connector
from flask import Flask, g, render_template, request, session, redirect, url_for
from passlib.hash import argon2

app = Flask(__name__)
app.config.from_object('config')
app.config.from_object('secret_config')

def connect_db () :
    g.mysql_connection = mysql.connector.connect(
        host = app.config['DATABASE_HOST'],
        user = app.config['DATABASE_USER'],
        password = app.config['DATABASE_PASSWORD'],
        database = app.config['DATABASE_NAME']
    )
    return g.mysql_connection

def get_db () :
    if not hasattr(g, 'db') :
        g.db = connect_db()
        return g.db

@app.route('/accueil/', methods=['GET'])
def accueil ():
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT id, name, States FROM WebSites')
    status = cur.fetchall()
    return render_template('accueil.html', status = status)

@app.route('/admin/modif/')
def modif ():
    if not session.get('user') or not session.get('user')[2] :
        return redirect(url_for('login'))

    return render_template('modif.html')

@app.route('/admin/suppr/', methods = ['GET', 'POST'])
def suppr ():
    if not session.get('user') or not session.get('user')[2] :
        return redirect(url_for('login'))
    suppr = request.form.get('suppr')
    if suppr == None :
        return render_template('suppr.html')
    else :
        db = get_db()
        cur = db.cursor()
        cur.execute('DELETE FROM WebSites WHERE name=(%s)', (suppr,))
        db.commit()
        return render_template('accueil.html')

@app.teardown_appcontext
def close_db (error) :
    if hasattr(g, 'db') :
        g.db.close()

@app.route('/admin/add/', methods = ['GET', 'POST'])
def ajout () :
    if not session.get('user') or not session.get('user')[2] :
        return redirect(url_for('login'))
    name = request.form.get('name')
    if name == None :
        return render_template('addwebsite.html')
    else :
        db = get_db()
        cur = db.cursor()
        cur.execute('INSERT INTO WebSites (name) VALUES (%s)', (name,))
        db.commit()
        return render_template('accueil.html')

@app.route('/login/', methods = ['GET', 'POST'])
def login () :
    email = str(request.form.get('email'))
    password = str(request.form.get('password'))

    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT email, password, is_admin FROM user WHERE email = %(email)s', {'email' : email})
    users = cur.fetchall()

    valid_user = False
    for user in users :
        if argon2.verify(password, user[1]) :
            valid_user = user

    if valid_user :
        session['user'] = valid_user
        return redirect(url_for('admin'))

    return render_template('login.html')

@app.route('/admin/')
def admin () :
    if not session.get('user') or not session.get('user')[2] :
        return redirect(url_for('login'))

    return render_template('admin.html', user = session['user'])

@app.route('/admin/logout/')
def admin_logout () :
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
