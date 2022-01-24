from pathlib import Path
import csv
import sys

from boxsdk.object.folder import Folder


def fmt_item(item):
    return f'{item.id}:{item.name}'


class BoxSync:

    def __init__(self, options, api):
        self.options = options
        self.api = api
        self.parent_folder = api.folder(self.options['box_folder_id'])
        self.parent_path = Path(self.options['source_folder'])
        self.created = []

    def to_path(self, item):
        item = vars(item.get())
        item_path = None
        for entry in item['path_collection']['entries']:
            if int(entry.id) == self.options['box_folder_id']:
                item_path = self.parent_path
            elif item_path is not None:
                item_path = item_path / entry.name
        return item_path / item['name']

    def get_box_paths(self, folder_id=None):
        if folder_id is None:
            folder_id = self.options['box_folder_id']
        for item in self.api.folder(folder_id).get_items():
            yield self.to_path(item), item
            if isinstance(item, Folder):
                yield from self.get_box_paths(item.id)

    def __call__(self):
        box_paths = dict(self.get_box_paths())
        local_paths = list(self.options['source_folder'].rglob('*'))
        local_files = [path for path in local_paths if path.is_file()]
        local_dirs = [path for path in local_paths if path.is_dir()]
        new_dirs = {}
        for path in local_dirs:
            if path not in box_paths:
                parent = path.parent
                if parent in box_paths:
                    parent = box_paths[parent]
                elif parent in new_dirs:
                    parent = new_dirs[parent]
                else:
                    raise ValueError(f'Unable to resolve folder path: {parent}')
                new_dirs[path] = subfolder = self.api.create_folder(parent.id, path.name)
                self.created.append((parent, subfolder))
        for path in local_files:
            if path not in box_paths:
                parent = path.parent
                if parent == self.parent_path:
                    parent = self.parent_folder
                elif parent in box_paths:
                    parent = box_paths[parent]
                elif parent in new_dirs:
                    parent = new_dirs[parent]
                else:
                    raise ValueError(f'Unable to resolve folder path: {parent}')
                new_file = self.api.upload(parent.id, path.resolve())
                self.created.append((parent, new_file))

    def output(self, filename=None):
        outfile = sys.stdout if filename is None else open(filename, 'w')
        writer = csv.writer(outfile)
        writer.writerow(('Parent Folder', 'New File/Folder'))
        writer.writerows([(fmt_item(parent), fmt_item(item)) for parent, item in self.created])
        if filename is not None:
            outfile.close()
