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

    struct archive_entry:
        pass

    ctypedef int (*archive_open_callback)(archive *, void *_client_data);
    ctypedef size_t (*archive_read_callback)(archive *, void *_client_data, const void **_buffer);
    ctypedef int (*archive_close_callback)(archive *, void *_client_data);

    archive* archive_read_new();

    int archive_read_support_filter_all(archive *);
    int archive_read_support_filter_zstd(archive *);
    int archive_read_support_format_all(archive *);
    int archive_read_support_format_raw(archive *);

    int archive_read_open(
        archive *,
        void *_client_data,
        archive_open_callback *,
        archive_read_callback *,
        archive_close_callback *
        );

    int archive_read_next_header(archive *, archive_entry **);

    ssize_t	archive_read_data(archive *, void *, size_t);

    int archive_errno(archive *);
    char* archive_error_string(archive *);

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


BLOCK_SIZE = 10240


cdef ssize_t myread(archive *a, void *client_data, const void **buff):
    cdef char *c_string = NULL
    cdef Py_ssize_t length = 0

    func = <object>client_data

    # might need to save a reference to buf
    buf = func(BLOCK_SIZE)   # read function returning bytes

    print('pass', buf, 'to libarchive')

    c_string = buf[::1]

    # update pointer to pointer
    buff[0] = c_string

    return len(buf)


cdef int myopen(archive *a, void *client_data):
    func = <object>client_data

    # Python file-like should already be open
    # Check for read method?

    # mydata->fd = open(mydata->name, O_RDONLY);
    # return (mydata->fd >= 0 ? ARCHIVE_OK : ARCHIVE_FATAL);

    print('myopen called')

    return ARCHIVE_OK


cdef int myclose(archive *a, void *client_data):
    func = <object>client_data

    # drop a refcount?

    # if (mydata->fd > 0):
    #     close(mydata->fd)

    return ARCHIVE_OK;


cdef archive_check(archive *a, note=None):
    note = note or ""
    errno = archive_errno(a)
    cdef const char* errstr = archive_error_string(a)

    print(note, errno, errstr or "<no error>")


def read_zstd(reader):
    """Decompress .zstd given a reader with a .read() method"""
    cdef archive *a;
    cdef archive_entry *ae;

    a = archive_read_new();

    print('support filter zstd only', archive_read_support_filter_zstd(a))

    # beware slower 'using external zstd to decompress'
    archive_check(a)

    # raw format, otherwise will expect e.g. `.tar.zst`
    print('support format raw', archive_read_support_format_raw(a))
    archive_check(a)

    #define	ARCHIVE_FATAL	(-30)	/* No more operations are possible.

    # can this be made to work without all the <archive_ ...> casts?
    print('read open', archive_read_open(a,
        <void*>reader,
        <archive_open_callback*>&myopen,
        <archive_read_callback*>&myread,
        <archive_close_callback*>&myclose
        ))

    archive_check(a);

    archive_read_next_header(a, &ae);
    archive_check(a)

    cdef char outbuf[10240];

    # print('read next header', archive_read_next_header(a, &ae))
    bytes_read = archive_read_data(a, outbuf, 10240)
    archive_check(a)

    print('bytes read', bytes_read)
    print(outbuf[:bytes_read])

