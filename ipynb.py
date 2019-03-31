import io
import json
import logging
import sys

from flask import jsonify, render_template


def render_notebook(inputs, outputs):
    """"""
    return render_template(
        'jupyter.html',
        cells=zip(range(len(inputs)), inputs, outputs)
    )


def execute_snippet(snippet):
    """Temporary changes the standard output stream to capture exec output"""
    temp_buffer = io.StringIO()

    sys.stdout = temp_buffer
    exec(snippet)
    sys.stdout = sys.__stdout__
    
    return temp_buffer.getvalue()


def export(inputs, outputs, filename='ipynb.json'):
    """Exports current state to ipynb format"""
    with open(filename, 'r') as f:  # json file with basic jupyter metadata
        ipynb_json = json.loads(f.read())

    # add cell data in jupyter-like format
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


def _get_cell_output(cell_json):
    """Get info of type 'output'"""
    cell_stdouts = [
        output for output in cell_json['outputs']
        if output.get('name', '') == 'stdout'
    ]
    return ''.join(cell_stdouts[0]['text'])


def _is_valid_ipynb(ipynb_json):
    if ipynb_json.get('cells') is None:
        return False
    return True


def import_from_json(ipynb_json):
    if not _is_valid_ipynb(ipynb_json):
        return ''
    inputs = []
    outputs = []
    for cell in ipynb_json['cells']:
        try:
            if cell['cell_type'] != 'code':
                continue
            cell_input = ''.join(cell['source'])
            cell_output = _get_cell_output(cell)
        except KeyError as e:
            logging.error(e)
            continue

        inputs.append(cell_input)
        outputs.append(cell_output)

    logging.info('Imported {} inputs, {} outputs'.format(len(inputs), len(outputs)))
    return inputs, outputs
