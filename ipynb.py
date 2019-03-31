from flask import jsonify
import json


def export(inputs, outputs):
    with open('ipynb.json', 'r') as f:
        ipynb_json = json.loads(f.read())

    for in_cell, out_cell in zip(inputs, outputs):
        cell_json = {
            'cell_type': 'code',
            'execution_count': None,
            'metadata': {
                'collapsed': False,
                'scrolled': False,
            },
            'source': in_cell,
            'outputs': [{
                'output_type': 'stream',
                'name': 'stdout',
                'text': out_cell
            }]
        }
        ipynb_json['cells'].append(cell_json)

    return jsonify(ipynb_json)


def get_cell_output(cell):
    cell_stdouts = [
        output for output in cell['outputs']
        if output['name'] == 'stdout'
    ]
    if cell_stdouts:
        return ''.join(cell_stdouts[0]['text'])
    else:
        return ''


def is_valid_ipynb(ipynb_json):
    if ipynb_json.get('cells') is None:
        return False
    return True


def import_from_json(ipynb_json):
    if not is_valid_ipynb(ipynb_json):
        return ''
    inputs = []
    outputs = []
    for cell in ipynb_json['cells']:
        try:
            if cell['cell_type'] != 'code':
                continue
            cell_input = ''.join(cell['source'])
            # print(cell['outputs'])
            cell_output = get_cell_output(cell)
        except KeyError:
            continue
        inputs.append(cell_input)
        outputs.append(cell_output)
    print('Imported {} inputs, {} outputs'.format(len(inputs), len(outputs)))
    return inputs, outputs
