import os

class AbstractBaseFormat(object):

    @staticmethod
    def extract(fn):
        raise NotImplementedError

    def create(prefix, file_list, out_fn, out_folder=os.getcwd(), **kw):
        raise NotImplementedError
