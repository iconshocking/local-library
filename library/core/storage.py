import importlib
import logging
import os
from uuid import uuid4

from django.contrib.staticfiles.storage import ManifestStaticFilesStorage as Base
from django.core.files.storage import Storage


class HashOnlyManifestStaticFilesStorage(Base):
    # remove the original file after creating cache-busting hashed version
    def post_process(self, *args, **kwargs):
        process = super().post_process(*args, **kwargs)
        for name, hashed_name, processed in process:
            yield name, hashed_name, processed
            if processed:
                # don't need to ship scss files; better way would be to exclude them from
                # collectstatic but this works for now
                if name.endswith(".scss"):
                    os.remove(self.path(name))
                    os.remove(self.path(hashed_name))
                elif name != hashed_name:
                    # Django isn't detecting source map URL comments correctly, so we need to keep the
                    # unhashed source maps
                    if name.endswith(".map"):
                        os.remove(self.path(name))


# wraps a storage class passed via "class_name" option and adds a uuid to the filename to avoid
# possible collisions
class UuidNameStorage:
    def __init__(self, **settings):
        class_name = settings.pop("class_name")
        module, name = class_name.rsplit(".", 1)
        class_ref = getattr(importlib.import_module(module), name)
        self.__base: Storage = class_ref(**settings)

    # only called when attr is not found, which is why this class doesn't extend Storage (so all
    # attributes are passed through to __base)
    def __getattr__(self, attr, **kwargs):
        return getattr(self.__base, attr, **kwargs)

    def generate_filename(self, filename: str) -> str:
        filename = self.__base.generate_filename(filename)
        try:
            name, ext = filename.rsplit(".", 1)
            filename = f"{name}_{uuid4().hex}.{ext}"
        except IndexError:
            logging.getLogger("django").error(f"Filename {filename} has no extension")

        return filename
