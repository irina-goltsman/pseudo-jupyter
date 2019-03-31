from flask import Flask, request, render_template, jsonify

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


def ipynb_export():
    global inputs
    global outputs
    ipynb_json = {
        'metadata': {
            'kernel_info': {},
            'language_info': {
                'name': 'python',
                'version': '3.5'
            }
        },
        'nbformat': 4,
        'nbformat_minor': 0,
        'cells': []
    }

    for in_cell, out_cell in zip(inputs, outputs):
        cell_json = {
            'cell_type': 'code',
            'execution_count': None,
            'metadata': {
                'collapsed': True,
                'scrolled': False,
            },
            'source': in_cell,
            'outputs': [{
                'output_type': 'stream',
                'name': 'stdout',
                'text': out_clel
            }]
        }
        ipynb_json['cells'].append(cell_json)

    return jsonify(ipynb_json)


def ipynb_import(ipynb_json):
    global inputs
    global outputs
    inputs.clear()
    outputs.clear()
    print(ipynb_json)
    for cell in ipynb_json['cells']:
        try:
            if cell['cell_type'] != 'code':
                continue
            cell_input = '\n'.join(cell['source'])
            # print(cell['outputs'])
            cell_output = '\n'.join([
                '\n'.join(out['data']['text/plain'])
                for out in cell['outputs']
                if out['output_type'] == 'execute_result'
            ])
        except KeyError:
            continue
        inputs.append(cell_input)
        outputs.append(cell_output)
    print(len(inputs), len(outputs))
    return ''


# https://nbformat.readthedocs.io/en/latest/format_description.html
@app.route('/ipynb', methods=['GET', 'POST'])
def ipynb():
    if request.method == 'GET':
        return ipynb_export()
    elif request.method == 'POST':
        return ipynb_import(request.get_json())


if __name__ == "__main__":
    app.run()
