# -*- coding: utf-8 -*-
import threading
import zipfile
import zlib
import os
import shutil
import re
import time
try:
    import urllib.request
except ImportError:
    pass


UPDATE_LINK = "https://bitbucket.org/topmettanant/opus/get/master.zip"
UPDATE_FILE = "opus_update.zip"


class Updater(threading.Thread):
    def __init__(self, current_version, force_update=False):
        self.current_version = current_version
        self.force_update = force_update
        self.version = None
        self.failed = True
        self.ready = False
        self.version_pattern = re.compile("VERSION\\s*=\\s*\"([\\d\\.]+)\"")
        threading.Thread.__init__(self)

    def crc(self, filename):
        prev = 0
        for line in open(filename, "rb"):
            prev = zlib.crc32(line, prev)
        return prev

    def download_update(self):
        try:
            if os.path.exists(UPDATE_FILE):
                os.remove(UPDATE_FILE)
            urllib.request.install_opener(
                urllib.request.build_opener(urllib.request.ProxyHandler())
            )
            data = urllib.request.urlopen(UPDATE_LINK).read()
            f = open(UPDATE_FILE, "wb")
            f.write(data)
            f.close()
            return os.path.exists(UPDATE_FILE)
        except Exception:
            return False

    def has_new_update(self):
        return (
            self.version is not None and self.version != self.current_version or
            self.version is not None and self.force_update
        )

    def get_version(self):
        return self.version

    def finish(self):
        return not self.is_alive()

    def ready_to_update(self):
        self.ready = True

    def update(self):
        self.start()

    def is_failed(self):
        return self.failed

    def run(self):
        if not self.download_update():
            return
        zfile = zipfile.ZipFile(UPDATE_FILE, "r")
        test = zfile.testzip()
        if test is not None:
            zfile.close()
            return
        top_dir = None
        for info in zfile.infolist():
            if os.path.basename(info.filename) == "opus.py":
                m = self.version_pattern.search(
                    zfile.read(info).decode("utf-8")
                )
                if m is not None:
                    self.version = m.group(1)
                break
        if not self.has_new_update():
            self.failed = False
            zfile.close()
            if os.path.exists(UPDATE_FILE):
                os.remove(UPDATE_FILE)
            return
        while not self.ready:
            time.sleep(0.1)
        for info in zfile.infolist():
            if top_dir is None and info.file_size == 0:
                top_dir = info.filename
            target_file = os.path.relpath(info.filename, top_dir)
            if os.path.basename(target_file).startswith("."):
                continue
            if os.path.isdir(target_file):
                if not os.path.exists(target_file):
                    os.mkdir(target_file)
                continue
            if (target_file.endswith(".opus") or
                target_file.endswith(".bib") or
                    target_file.endswith(".opus.project")):
                continue
            file_exists = os.path.exists(target_file)
            if file_exists and info.CRC == self.crc(target_file):
                continue
            if os.path.exists(target_file):
                os.remove(target_file)
            source = zfile.open(info)
            target = open(target_file, "wb")
            with source, target:
                shutil.copyfileobj(source, target)
        zfile.close()
        if os.path.exists(UPDATE_FILE):
            os.remove(UPDATE_FILE)
        self.failed = False
