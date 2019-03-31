import sys
from io import StringIO

from flask import Flask, request, render_template, redirect
import ipynb


app = Flask(__name__)
inputs = ['print("Type your code snippet here")']
outputs = ['']


def render_notebook(inputs, outputs):
    return render_template(
        'jupyter.html',
        cells=zip(range(len(inputs)), inputs, outputs)
    )


def execute_snippet(snippet):
    temp_buffer = StringIO()

    sys.stdout = temp_buffer
    exec(snippet)
    sys.stdout = sys.__stdout__
    
    return temp_buffer.getvalue()


@app.route('/', methods=['GET'])
def get():
    assert len(inputs) == len(outputs)
    return render_notebook(inputs, outputs)


@app.route('/execute_cell/<cell_id>', methods=['POST'])
def execute(cell_id=None):
    try:
        cell_id = int(cell_id)
    except ValueError:
        return redirect('/')

    inputs[cell_id] = request.form['input{}'.format(cell_id)]
    try:
        result = execute_snippet(inputs[cell_id])
    except BaseException as e:
        result = str(e)
    outputs[cell_id] = result
    return redirect('/')


@app.route('/add_cell', methods=['POST'])
def add_cell():
    inputs.append('')
    outputs.append('')
    return redirect('/')


@app.route('/remove_cell/<cell_id>', methods=['POST'])
def remove_cell(cell_id=0):
    try:
        cell_id = int(cell_id)
        if len(inputs) < 2:
            raise ValueError('Cannot remove the last cell')
        if cell_id < 0 or cell_id >= len(inputs):
            raise ValueError('Bad cell id')
    except ValueError:
        return redirect('/')

    inputs.pop(cell_id)
    outputs.pop(cell_id)
    return redirect('/')


# https://nbformat.readthedocs.io/en/latest/format_description.html
@app.route('/ipynb', methods=['GET', 'POST'])
def ipynb_handler():
    global inputs
    global outputs
    if request.method == 'GET':
        return ipynb.export(inputs, outputs)
    elif request.method == 'POST':
        inputs, outputs = ipynb.import_from_json(request.get_json())
        return ''  # why do I need it?


if __name__ == "__main__":
    app.run()
