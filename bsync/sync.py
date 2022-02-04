from pathlib import Path
import csv
import os

from click import UsageError
from boxsdk.object.folder import Folder


class BoxSync:
    """
    Syncs the parent folder files to Box.

    Compares current files, checks for any missing in Box or any changed locally,
    creates directory structure and finally uploads all files
    """

    def __init__(self, api, logger, box_folder_id, source_folder_paths):
        self.api = api
        self.logger = logger
        self.box_folder_id = int(box_folder_id)
        self.glob = '*'
        if ':' in str(source_folder_paths):
            self.source_folder, self.glob = source_folder_paths.split(':')
            self.source_folder = Path(self.source_folder).expanduser()
        else:
            self.source_folder = Path(source_folder_paths).expanduser()
        if not self.source_folder.is_dir():
            raise UsageError(f'Source folder {self.source_folder} is not a directory')
        self.changes = []
        self._parent = None

    @property
    def parent_folder(self):
        """
        Gets the parent folder in Box via API GET
        """
        if self._parent:
            return self._parent
        self._parent = self.api.client.folder(self.box_folder_id).get()
        return self._parent

    def to_path(self, item):
        """
        Converts a Box File/Folder to a filepath from the parent folder
        """
        path_collection = item.get(fields=['path_collection']).path_collection
        item_path = None
        for entry in path_collection['entries']:
            if entry == self.parent_folder:
                item_path = self.source_folder
            elif item_path is not None:
                item_path = item_path / entry.name
        return item_path / item['name']

    def get_box_paths(self, folder_id=None):
        """
        Yields all paths recursively from the parent folder ID
        """
        if folder_id is None:
            folder_id = self.box_folder_id
        for item in self.api.client.folder(folder_id).get_items():
            yield self.to_path(item), item
            if isinstance(item, Folder):
                yield from self.get_box_paths(item._object_id)

    def prepare(self):
        """
        Loads entries from local filesystem and Box
        Used to decide later which items to sync
        """
        local_paths = list(self.source_folder.rglob(self.glob))
        self.local_files = [path for path in local_paths if path.is_file()]
        self.local_dirs = [path for path in local_paths if path.is_dir()]
        self.new_dirs = {}
        self.box_paths = dict(self.get_box_paths())

    def get_parent(self, path):
        """
        Returns the Box Folder object for the parent folder of path
        """
        parent = path.parent
        if parent == self.source_folder:
            return self.parent_folder
        elif parent in self.box_paths:
            return self.box_paths[parent]
        elif parent in self.new_dirs:
            return self.new_dirs[parent]
        raise ValueError(f'Unable to resolve folder path: {parent}')

    def sync_folders(self):
        """
        Creates the subfolders in Box.com to match local filesystem
        Runs before new files are updated/uploaded
        """
        for path in self.local_dirs:
            if path not in self.box_paths:
                parent = self.get_parent(path)
                self.new_dirs[path] = subfolder = self.api.create_folder(parent._object_id, path.name)
                self.changes.append((parent, subfolder))

    def has_changed(self, boxfile, path):
        """
        Compares the file on Box with the path on disk
        Used to see if the local file has changed
        """
        # TODO: compare sha1? expensive for large local files
        return boxfile.get(fields=['size']).size != os.stat(path).st_size

    def sync_files(self):
        """
        Uploads the new or updated files to Box.com
        Folder structure must be created before running
        """
        for path in self.local_files:
            parent = self.get_parent(path)
            if path not in self.box_paths:
                new_file = self.api.upload(parent._object_id, path.resolve())
                self.changes.append((parent, new_file))
            else:
                boxfile = self.box_paths[path]
                if self.has_changed(boxfile, path):
                    updated_file = self.api.update(boxfile._object_id, path.resolve())
                    self.changes.append((parent, updated_file))

    def __call__(self):
        self.prepare()
        self.logger.info(f'Syncing {len(self.local_files)} files in '
                         f'{len(self.local_dirs) + 1} folders from {self.source_folder}')
        self.sync_folders()
        self.sync_files()
        if not self.changes:
            self.logger.warning('No changes detected')

    def output(self, filename):
        """
        Writes output CSV of what files are synced and their destinations in Box
        """
        header = ('Item Type', 'Parent Folder ID', 'Parent Folder Name', 'Item ID', 'Item Name')
        with open(filename, 'w') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(header)
            for parent, item in self.changes:
                writer.writerow([item.__class__.__name__, parent._object_id, parent.name,
                                 item._object_id, item.name])
