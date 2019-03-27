from flask import Flask, request, render_template

app = Flask(__name__)
inputs = ['"Type your code snippet here"']
outputs = ['']


def render_notebook():
    global inputs
    global outputs
    return render_template(
        'jupyter.html',
        cells=zip(range(len(inputs)), inputs, outputs)
    )


@app.route('/', methods=['GET'])
def get():
    assert len(inputs) == len(outputs)
    return render_notebook()


@app.route('/execute_cell/<cell_id>', methods=['POST'])
def execute(cell_id=None):
    try:
        cell_id = int(cell_id)
    except ValueError:
        return render_notebook()

    inputs[cell_id] = request.form['input{}'.format(cell_id)]
    try:
        result = eval(inputs[cell_id])
    except BaseException as e:
        result = str(e)
    outputs[cell_id] = result
    return render_notebook()


@app.route('/add_cell', methods=['POST'])
def add_cell():
    inputs.append('')
    outputs.append('')
    return render_notebook()


@app.route('/remove_cell/<cell_id>', methods=['POST'])
def remove_cell(cell_id=0):
    try:
        cell_id = int(cell_id)
        if len(inputs) < 2:
            raise ValueError('Cannot remove the last cell')
        if cell_id < 0 or cell_id >= len(inputs):
            raise ValueError('Bad cell id')
    except ValueError:
        return render_notebook()

    inputs.pop(cell_id)
    outputs.pop(cell_id)
    return render_notebook()


if __name__ == "__main__":
    app.run()