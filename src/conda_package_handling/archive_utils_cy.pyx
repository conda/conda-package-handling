# Cython wrapper around archive_utils_c


cdef extern from "archive_utils_c.c":
    void * prepare_gnutar_archive(
        const char *outname_u8, const char *filtername, const char *opts, const char ** err_str_u8)
    void close_archive(void *a)
    void * prepare_entry()
    void close_entry(void *entry)
    int add_file(void *a, void *entry, const char *filename_u8, const char ** err_str_u8)
    int extract_file_c(const char *filename_u8, const char ** err_str_u8)


def extract_file(tarball):
    """Extract a tarball into the current directory."""
    cdef const char *err_str_u8 = NULL
    result = extract_file_c(tarball, &err_str_u8)
    if result:
        assert err_str != NULL
        return 1, <bytes> err_str_u8
    return 0, b''


def create_archive(fullpath, files, compression_filter, compression_opts):
    """ Create a compressed gnutar archive. """
    cdef void *a
    cdef void *entry
    cdef const char *err_str = NULL
    a = prepare_gnutar_archive(fullpath, compression_filter, compression_opts, &err_str)
    if a == NULL:
        return 1, <bytes> err_str, b''
    entry = prepare_entry()
    if entry == NULL:
        return 1, b'archive entry creation failed', b''
    for f in files:
        result = add_file(a, entry, f, &err_str)
        if result:
            return 1, <bytes> err_str, f
    close_entry(entry)
    close_archive(a)
    return 0, b'', b''
