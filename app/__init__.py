# -*- coding: utf-8 -*-
import flask
import logging

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'dskjgdskfjghdskjfhdfg'

# create logger instance
logger = logging.getLogger(__name__)
logger.setLevel('INFO')
