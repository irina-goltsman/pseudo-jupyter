# -*- coding: utf-8 -*-
import os
import flask

from app import ipynb
from app import app, logger

# global variables to store the current state of our notebook
INPUTS = ['print("Type your code snippet here")']
OUTPUTS = ['']
EXECUTE_COUNTERS = [0]
CURRENT_EXECUTE_COUNT = 0


@app.route('/favicon.ico')
def favicon():
    """Handles browser's request for favicon"""
    return flask.send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico'
    )


@app.route('/', methods=['GET'])
def get():
    """This triggers when you first open the site with your browser"""
    assert len(INPUTS) == len(OUTPUTS)
    return ipynb.render_notebook(INPUTS, OUTPUTS, EXECUTE_COUNTERS)


@app.route('/execute_cell/<cell_id>', methods=['POST'])
def execute(cell_id=None):
    """Gets piece of code from cell_id and executes it"""
    try:
        cell_id = int(cell_id)
    except ValueError as e:
        logger.warning(e)
        return flask.redirect('/')

    global CURRENT_EXECUTE_COUNT
    try:
        CURRENT_EXECUTE_COUNT += 1
        EXECUTE_COUNTERS[cell_id] = CURRENT_EXECUTE_COUNT

        INPUTS[cell_id] = flask.request.form['input{}'.format(cell_id)]
        result = ipynb.execute_snippet(INPUTS[cell_id], globals())
    except Exception as e:
        # anything could happen inside, even `exit()` call
        result = str(e)

    OUTPUTS[cell_id] = result
    return flask.redirect('/')


@app.route('/add_cell', methods=['POST'])
def add_cell():
    """Appends empty cell data to the end"""
    INPUTS.append('')
    OUTPUTS.append('')
    EXECUTE_COUNTERS.append(0)
    return flask.redirect('/')


@app.route('/remove_cell/<cell_id>', methods=['POST'])
def remove_cell(cell_id=0):
    """Removes a cell by number"""
    try:
        cell_id = int(cell_id)
        if len(INPUTS) < 2:
            raise ValueError('Cannot remove the last cell')
        if cell_id < 0 or cell_id >= len(INPUTS):
            raise ValueError('Bad cell id')
    except ValueError as e:
        # do not change internal info
        logger.warning(e)
        return flask.redirect('/')

    # remove related data
    INPUTS.pop(cell_id)
    OUTPUTS.pop(cell_id)
    EXECUTE_COUNTERS.pop(cell_id)
    return flask.redirect('/')


@app.route('/ipynb', methods=['GET', 'POST'])
def ipynb_handler():
    """
    Imports/exports notebook data in .ipynb format (a.k.a Jupyter Notebook)
    Docs: https://nbformat.readthedocs.io/en/latest/format_description.html
    """
    global INPUTS, OUTPUTS
    if flask.request.method == 'GET':
        # return json representation of the notebook here
        return ipynb.export(INPUTS, OUTPUTS)
    elif flask.request.method == 'POST':
        # update internal data
        imported = ipynb.import_from_json(flask.request.get_json())
        # we can return None if json is not a valid ipynb
        if imported:
            INPUTS, OUTPUTS = imported
        # common practice for POST/PUT is returning empty json
        # when everything is 200 OK
        return flask.jsonify({})
