import json
import os
import hashlib
from functools import cached_property

from boxsdk import Client, JWTAuth
from boxsdk.exception import BoxAPIException
from progress.bar import Bar


class BoxAPI:
    def __init__(self, options, logger):
        self.options = options
        self.logger = logger

    @cached_property
    def client(self):
        user = self.options['box_user']
        config = json.load(open(self.options['settings']))
        CLIENT_ID = config['boxAppSettings']['clientID']
        CLIENT_SECRET = config['boxAppSettings']['clientSecret']
        PUBLIC_KEY_ID = config['boxAppSettings']['appAuth']['publicKeyID']
        PRIVATE_KEY = config['boxAppSettings']['appAuth']['privateKey']
        PASSPHRASE = config['boxAppSettings']['appAuth']['passphrase']
        ENTERPRISE_ID = config['enterpriseID']
        auth = JWTAuth(CLIENT_ID, CLIENT_SECRET, ENTERPRISE_ID, PUBLIC_KEY_ID,
                       rsa_private_key_data=PRIVATE_KEY, rsa_private_key_passphrase=PASSPHRASE)
        auth.authenticate_instance()
        client = Client(auth)
        me = list(client.users(filter_term=user))[0]
        client = client.as_user(me)
        self.logger.info(f'Created Box client for user {user}')
        return client

    def upload_simple(self, folder_id, fn):
        new_file = self.client.folder(folder_id).upload(fn)
        self.logger.info(f'File "{new_file.name}" uploaded to Box with file ID {new_file.id}')
        return new_file

    def upload(self, parent_id, fn):
        total_size = os.stat(fn).st_size
        if total_size < 20000000:
            return self.upload_simple(parent_id, fn)
        parent_folder = self.client.folder(parent_id)
        sha1 = hashlib.sha1()
        upload_session = parent_folder.create_upload_session(file_size=total_size, file_name=fn.name)
        part_array = []
        bar = Bar(fn.name, max=upload_session.total_parts)
        content_stream = open(fn, 'rb')

        for part_num in range(upload_session.total_parts):
            copied_length = 0
            chunk = b''
            while copied_length < upload_session.part_size:
                bytes_read = content_stream.read(upload_session.part_size - copied_length)
                if bytes_read is None:
                    continue
                if len(bytes_read) == 0:
                    break
                chunk += bytes_read
                copied_length += len(bytes_read)

            uploaded_part = upload_session.upload_part_bytes(chunk, part_num * upload_session.part_size, total_size)
            bar.next()
            part_array.append(uploaded_part)
            sha1.update(chunk)
        content_sha1 = sha1.digest()
        uploaded_file = upload_session.commit(content_sha1=content_sha1, parts=part_array)
        bar.finish()
        self.logger.info(f'Uploaded File ID: {uploaded_file.id} and File Name: {uploaded_file.name}')
        return uploaded_file

    def create_folder(self, parent_id, name):
        subfolder = self.client.folder(parent_id).create_subfolder(name)
        self.logger.info(f'Created subfolder {subfolder.id}({name}) in {parent_id}')
        return subfolder

    def box_item(attr):
        def inner(self, fid, get=True):
            item = getattr(self.client, attr)(fid)
            if get:
                self.logger.debug(f'API GET {attr} {fid}')
                return item.get()
            return item
        inner.__name__ = attr
        return inner
    folder = box_item('folder')
    file = box_item('file')

    def get_or_404(self, box_id, get=True, getter=None):
        getter_name = getter.__name__.title()
        try:
            return getter(box_id, get)
        except BoxAPIException as exc:
            if exc.message == 'Item is trashed':
                self.logger.warning(f'{getter_name} {box_id} already trashed')
            elif exc.message == 'Not Found':
                self.logger.warning(f'{getter_name} {box_id} not found')
            else:
                raise
        else:
            self.logger.debug(f'Fetched {box_id}')

    def get_file_or_404(self, box_id, get=True):
        return self.get_or_404(box_id, get, self.file)

    def get_folder_or_404(self, box_id, get=True):
        return self.get_or_404(box_id, get, self.folder)


if __name__ == '__main__':
    import ipdb
    from IPython import embed
    with ipdb.launch_ipdb_on_exception():
        api = BoxAPI('jquick')
        api.sync()
        embed()
