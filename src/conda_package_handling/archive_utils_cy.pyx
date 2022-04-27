# Cython wrapper around archive_utils_c


cdef extern from "archive_utils_c.c":
    void * prepare_gnutar_archive(
        const char *outname, const char *filtername, const char *opts, const char **err_str)
    void close_archive(void *a)
    void * prepare_entry()
    void close_entry(void *entry)
    int add_file(void *a, void *entry, const char *filename, const char **err_str)
    int extract_file_c(const char *filename, const char **err_str)

    struct archive:
        pass

    int	*archive_open_callback(archive *, void *_client_data);
    size_t *archive_read_callback(archive *, void *_client_data, const void **_buffer);
    int *archive_close_callback(archive *, void *_client_data);

    archive* archive_read_new();
    int archive_read_open(
        archive *,
        void *_client_data,
        archive_open_callback *,
        archive_read_callback *,
        archive_close_callback *
        );
    int archive_read_support_filter_all(archive *);

#define	ARCHIVE_EOF	  1	/* Found end of archive. */
#define	ARCHIVE_OK	  0	/* Operation was successful. */
#define	ARCHIVE_RETRY	(-10)	/* Retry might succeed. */
#define	ARCHIVE_WARN	(-20)	/* Partial success. */
# /* For example, if write_header "fails", then you can't push data. */
#define	ARCHIVE_FAILED	(-25)	/* Current operation cannot complete. */
# /* But if write_header is "fatal," then this archive is dead and useless. */
#define	ARCHIVE_FATAL	(-30)	/* No more operations are possible. */

ARCHIVE_OK = 0


from cython.operator import dereference


def extract_file(tarball):
    """Extract a tarball into the current directory."""
    cdef const char *err_str = NULL
    result = extract_file_c(tarball, &err_str)
    if result:
        assert err_str != NULL
        return 1, <bytes> err_str
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


cdef ssize_t myread(archive *a, void *client_data, const void **buff):
    func = <object>client_data

    dereference(buff) = mydata.buff;
    buf = func(10240)
    # return (read(mydata.fd, mydata.buff, 10240));
    # copy Python buffer to C buffer, or use buffer protocol

    return len(buf)


cdef int myopen(archive *a, void *client_data):
    func = <object>client_data

    # Python file-like should already be open
    # Check for read method?
    # mydata->fd = open(mydata->name, O_RDONLY);
    # return (mydata->fd >= 0 ? ARCHIVE_OK : ARCHIVE_FATAL);

    return ARCHIVE_OK


cdef int myclose( archive *a, void *client_data):
    func = <object>client_data

    # drop a refcount?

    # if (mydata->fd > 0):
    #     close(mydata->fd)

    return ARCHIVE_OK;


def read_zstd(reader):
    """Decompress .zstd given a reader with a .read() method"""
    cdef archive *a;

    a = archive_read_new();
    archive_read_support_filter_all(a);
    # archive_read_support_format_all(a);
    archive_read_open(a, <void*>reader, myopen, myread, myclose);

