# -*- coding: utf-8 -*-
from flask import Flask
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dskjgdskfjghdskjfhdfg'

# create logger instance
logger = logging.getLogger(__name__)
logger.setLevel('INFO')
