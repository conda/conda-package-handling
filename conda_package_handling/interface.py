from abc import ABC, abstractmethod
import os


class AbstractBaseFormat(ABC):

    @staticmethod
    @abstractmethod
    def extract(fn, dest_dir=None, **kw):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def create(prefix, file_list, out_fn, out_folder=os.getcwd(), **kw):
        raise NotImplementedError
