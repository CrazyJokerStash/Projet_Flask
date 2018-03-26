#! /usr/bin/python
# -*- coding:utf-8 -*-

from flask import Flask

app = Flask(__name__)
app.config.from_object('config')
app.config.from_object('secret_config')

@app.route('/accueil')
def helloworld():
    return 'Hello World'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
