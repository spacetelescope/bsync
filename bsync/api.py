import json
import os
import hashlib

from boxsdk import Client, JWTAuth

from bsync.settings import BOX_UPLOAD_LIMIT


class BoxAPI:
    """
    Wraps boxsdk to create a client and perform actions, logging results
    """

    def __init__(self, logger, settings):
        self.settings = settings
        self.logger = logger
        self._client = None

    @property
    def client(self):
        """
        Gets a boxsdk.Client instance from the JSON settings file using JWT
        """
        if self._client:
            return self._client
        config = json.load(open(self.settings))
        CLIENT_ID = config['boxAppSettings']['clientID']
        CLIENT_SECRET = config['boxAppSettings']['clientSecret']
        PUBLIC_KEY_ID = config['boxAppSettings']['appAuth']['publicKeyID']
        PRIVATE_KEY = config['boxAppSettings']['appAuth']['privateKey']
        PASSPHRASE = config['boxAppSettings']['appAuth']['passphrase']
        ENTERPRISE_ID = config.get('enterpriseID')
        auth = JWTAuth(CLIENT_ID, CLIENT_SECRET, ENTERPRISE_ID, PUBLIC_KEY_ID,
                       rsa_private_key_data=PRIVATE_KEY, rsa_private_key_passphrase=PASSPHRASE)
        auth.authenticate_instance()
        client = Client(auth)
        self.logger.info(f'Created client instance for ID {CLIENT_ID}')
        self._client = client
        return client

    def send_chunked(self, path, session_func):
        """
        Uses the chunked upload API from Box to upload sequential segments of a file
        """
        total_size = os.stat(path).st_size
        sha1 = hashlib.sha1()
        upload_session = session_func(total_size, path.name)
        part_array = []
        content_stream = open(path, 'rb')

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
            percent = part_num * upload_session.part_size / total_size * 100
            self.logger.info(f'Uploading {path.name} {percent:.0f}%...')
            uploaded_part = upload_session.upload_part_bytes(chunk, part_num * upload_session.part_size, total_size)
            part_array.append(uploaded_part)
            sha1.update(chunk)
        content_sha1 = sha1.digest()
        uploaded_file = upload_session.commit(content_sha1=content_sha1, parts=part_array)
        return uploaded_file

    def upload(self, parent_id, fname):
        """
        Uploads a file to the parent folder_id
        Handles large files by chunking
        """
        total_size = os.stat(fname).st_size
        folder = self.client.folder(parent_id)
        if total_size < BOX_UPLOAD_LIMIT:
            uploaded_file = folder.upload(fname, upload_using_accelerator=True)
        else:
            uploaded_file = self.send_chunked(fname, folder.create_upload_session)
        self.logger.info(f'Uploaded File: {uploaded_file.name}({uploaded_file.id})')
        return uploaded_file

    def update(self, file_id, fname):
        """
        Updates the contents of a file and uploads it to an existing file on Box
        """
        total_size = os.stat(fname).st_size
        boxfile = self.client.file(file_id)
        if total_size < BOX_UPLOAD_LIMIT:
            updated_file = boxfile.update_contents(fname, upload_using_accelerator=True)
        else:
            updated_file = self.send_chunked(fname, boxfile.create_upload_session)
        self.logger.info(f'Updated File: {updated_file.name}({updated_file.id})')
        return updated_file

    def create_folder(self, parent_id, name):
        """
        Creates a subfolder in an existing Box folder
        """
        subfolder = self.client.folder(parent_id).create_subfolder(name)
        self.logger.info(f'Created subfolder {name}({subfolder.id}) in {parent_id}')
        return subfolder
