import os, json
from pathlib import Path

""" Service to write JSON serializable data to a specified folder. """


def write_json(json_serializable, name='evaluation_results', save_path='target') -> None:
    """ Write the provided JSON serializable data to a file in the specified folder. """
    path = Path(save_path + '/' + name + '.json')
    os.makedirs(path.parent, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(json_serializable, f, indent=4)
    print(f"Saved evaluation results to {path}")