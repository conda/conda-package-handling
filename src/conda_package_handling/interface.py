import abc
import hashlib
import os


class AbstractBaseFormat(metaclass=abc.ABCMeta):
    @staticmethod
    @abc.abstractmethod
    def supported(fn):  # pragma: no cover
        return False

    @staticmethod
    @abc.abstractmethod
    def extract(fn, dest_dir, **kw):  # pragma: no cover
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def create(prefix, file_list, out_fn, out_folder=os.getcwd(), **kw):  # pragma: no cover
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def get_pkg_details(in_file):  # pragma: no cover
        raise NotImplementedError

    @staticmethod
    def get_sha256(file_path: str, chunk_size: int = 1_048_576) -> str:
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                hasher.update(chunk)

        return hasher.hexdigest()
