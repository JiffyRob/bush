import asyncio
import gc
import os.path

from bush.util_load import *
from bush import util

if util.is_pygbag():
    loaded = load_persistent("files")
    if loaded is None:
        pass
    else:
        print(loaded)
        filepaths = json.loads(loaded) or ()
        print("Loading from persistent", filepaths)
        for filepath in filepaths:
            if not os.path.exists(filepath):
                with open(filepath, "w") as file:
                    file.write(load_persistent(filepath))
    del loaded


class AssetHandler:
    """
    A Loader of resources.  Catches things by filepath so that you don't have to load them again.
    """

    _loaders = {
        "png": load_image,
        "jpeg": load_image,
        "jpg": load_image,
        "bmp": load_image,
        "wav": load_audio,
        "ogg": load_audio,
        "txt": load_text,
        "json": load_json,
        "csv": load_csv,
        "pkl": load_pickle,
        "tmx": load_map,
        "world": load_world,
        "gz": load_gzip,
        "sav": load_gzip,
        "generic": load_text,
    }

    _savers = {
        "png": save_image,
        "jpeg": save_image,
        "bmp": save_image,
        "txt": save_text,
        "json": save_json,
        "csv": save_csv,
        "pkl": save_pickle,
        "gz": load_gzip,
        "sav": save_gzip,
        "generic": save_text,
    }

    _persisters = {
        "txt": str,
        "json": json.dumps,
        "csv": save_csv,
        "generic": str,
    }

    _cache = {}
    base = ""

    def __init__(self, base=None, join=True, cache_all=False):
        if base is not None:
            if join:
                self.base = os.path.join(self.base, base)
            else:
                self.base = os.path.join(base)
        if cache_all:
            self.cache_folder()

    @classmethod
    def register_filetype(cls, extension, loader=None, saver=None, persister=False):
        if loader:
            cls._loaders[extension] = loader
        if saver:
            cls._savers[extension] = saver
        if persister:
            cls._persisters[extension] = persister

    @classmethod
    def clear_cache(cls):
        cls._cache = {}
        gc.collect()

    def cache_folder(self, path=None):
        if path is None:
            path = self.base
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if filename.split(".")[-1] in self._loaders:
                    file_path = join(dirpath, filename)
                    file_path = os.path.relpath(file_path, self.base)
                    self.load(file_path)

    def set_home(self, path):
        self.base = os.path.join(path)

    @classmethod
    def set_global_home(cls, path):
        cls.base = path

    def join(self, path):
        return os.path.join(self.base, path)

    def load(self, filepath, cache=True, loader=None, **kwargs):
        filepath = os.path.join(self.base, filepath)
        # get file extension
        filetype = filepath.split(".")[-1]
        # see if file was cached, return that
        if filepath in self._cache:
            return self._cache[filepath]
        # load file
        # print("loading", filepath)
        loader = loader or self._loaders.get(filetype, load_text)
        result = loader(filepath, **kwargs)
        # add to cache if needed
        if cache:
            self._cache[filepath] = result
        return result

    def load_spritesheet(self, path, size=(16, 16), margin=(0, 0), spacing=0):
        image = self.load(path)
        return make_spritesheet(image, size, margin, spacing)

    def save(self, data, path, persist=False):
        filetype = path.split(".")[-1]
        filepath = os.path.join(self.base, path)
        # if we are one web we can use persistant data
        if persist and util.is_pygbag() and filetype in self._persisters:
            save_persistent(filepath, self._persisters[filetype](data))
            already_saved = json.loads(load_persistent("files"))
            if filepath not in already_saved:
                already_saved.append(filepath)
                save_persistent(
                    "files",
                    json.dumps(already_saved),
                )
        self._savers.get(filetype, "generic")(data, filepath)


glob_loader = AssetHandler()
