// Utilities for creating and extracting files from archives using libarchive
// for use in conda-packaging-handling
#define LIBARCHIVE_STATIC

#include <fcntl.h>
#include <archive.h>
#include <archive_entry.h>

#ifndef O_BINARY
#define O_BINARY    0
#endif

const char * checked_strdup(const char * err) {
    if (err == NULL) {
        return NULL;
    }
    return strdup(err);
}

struct archive * prepare_gnutar_archive(
    const char *outname, const char *filtername, const char *opts, const char **err_str)
{
    struct archive *a;
    if (!err_str) {
        return NULL;
    }
    a = archive_write_new();
    if (a == NULL) {
        return a;
    }
    if (archive_write_set_format_gnutar(a) < ARCHIVE_OK) {
        *err_str = checked_strdup(archive_error_string(a));
        archive_write_close(a);
        archive_write_free(a);
        return NULL;
    }
    if (archive_write_add_filter_by_name(a, filtername) < ARCHIVE_OK) {
        *err_str = checked_strdup(archive_error_string(a));
        archive_write_close(a);
        archive_write_free(a);
        return NULL;
    }
    if (archive_write_set_options(a, opts) < ARCHIVE_OK) {
        *err_str = checked_strdup(archive_error_string(a));
        archive_write_close(a);
        archive_write_free(a);
        return NULL;
    }
    if (archive_write_open_filename(a, outname) < ARCHIVE_OK) {
        *err_str = checked_strdup(archive_error_string(a));
        archive_write_close(a);
        archive_write_free(a);
        return NULL;
    }
    return a;
}

void close_archive(struct archive *a) {
    archive_write_close(a);
    archive_write_free(a);
}

struct archive_entry * prepare_entry(void) {
    struct archive_entry *entry;
    entry = archive_entry_new();
    return entry;
}

void close_entry(struct archive_entry *entry) {
    archive_entry_free(entry);
}

static int add_file(
    struct archive *a, struct archive_entry *entry, const char *filename, const char **err_str)
{
    struct archive *disk;
    char buff[8192];
    int len;
    int fd;
    int flags;
    flags = 0;

    disk = archive_read_disk_new();
    if (disk == NULL) {
        return 1;
    }
    if (archive_read_disk_set_behavior(disk, flags) < ARCHIVE_OK) {
        *err_str = checked_strdup(archive_error_string(disk));
        return 1;
    }
    if (archive_read_disk_open(disk, filename) < ARCHIVE_OK) {
        *err_str = checked_strdup(archive_error_string(disk));
        return 1;
    }
    if (archive_read_next_header2(disk, entry) < ARCHIVE_OK) {
        *err_str = checked_strdup(archive_error_string(disk));
        return 1;
    }
    if (archive_read_disk_descend(disk) < ARCHIVE_OK) {
        *err_str = checked_strdup(archive_error_string(disk));
        return 1;
    }
    if (archive_write_header(a, entry) < ARCHIVE_OK) {
        *err_str = checked_strdup(archive_error_string(a));
        return 1;
    }
    fd = open(filename, O_RDONLY | O_BINARY);
    len = read(fd, buff, sizeof(buff));
    while ( len > 0 ) {
        archive_write_data(a, buff, len);
        len = read(fd, buff, sizeof(buff));
    }
    close(fd);
    if (archive_write_finish_entry(a) < ARCHIVE_OK) {
        *err_str = checked_strdup(archive_error_string(a));
        return 1;
    }
    archive_read_close(disk);
    archive_read_free(disk);
    archive_entry_clear(entry);
    return 0;
}


static int copy_data(struct archive *ar, struct archive *aw)
{
    int r;
    const void *buff;
    size_t size;
    la_int64_t offset;
    for (;;) {
        r = archive_read_data_block(ar, &buff, &size, &offset);
        if (r == ARCHIVE_EOF)
            return (ARCHIVE_OK);
        if (r < ARCHIVE_OK)
            return (r);
        r = archive_write_data_block(aw, buff, size, (int)offset);
        if (r < ARCHIVE_OK) {
            return (r);
    }
  }
}

static int extract_file_c(const char *filename, const char **err_str) {
    struct archive *a;
    struct archive *ext;
    struct archive_entry *entry;
    int flags;
    int r;

    if (!err_str) {
        return 0;
    }
    /* attributes we want to restore. */
    flags = ARCHIVE_EXTRACT_TIME;
    flags |= ARCHIVE_EXTRACT_PERM;
    flags |= ARCHIVE_EXTRACT_SECURE_NODOTDOT;
    flags |= ARCHIVE_EXTRACT_SECURE_SYMLINKS;
    flags |= ARCHIVE_EXTRACT_SECURE_NOABSOLUTEPATHS;
    flags |= ARCHIVE_EXTRACT_SPARSE;
    flags |= ARCHIVE_EXTRACT_UNLINK;

    a = archive_read_new();
    archive_read_support_format_all(a);
    archive_read_support_filter_all(a);
    ext = archive_write_disk_new();
    archive_write_disk_set_options(ext, flags);
    archive_write_disk_set_standard_lookup(ext);
    if ((r = archive_read_open_filename(a, filename, 10240))) {
        *err_str = checked_strdup(archive_error_string(a));
        return 1;
    }
    for (;;) {
        r = archive_read_next_header(a, &entry);
        if (r == ARCHIVE_EOF)
            break;
        if (r < ARCHIVE_WARN) {
            *err_str = checked_strdup(archive_error_string(a));
            return 1;
        }
        r = archive_write_header(ext, entry);
        if (r < ARCHIVE_OK) {
            *err_str = checked_strdup(archive_error_string(ext));
            return 1;
        }
        else if (archive_entry_size(entry) > 0) {
            r = copy_data(a, ext);
            if (r < ARCHIVE_WARN) {
                *err_str = checked_strdup(archive_error_string(ext));
                if (*err_str == NULL) {
                  *err_str = checked_strdup(archive_error_string(a));
                }
                return 1;
            }
        }
        r = archive_write_finish_entry(ext);
        if (r < ARCHIVE_WARN) {
            *err_str = checked_strdup(archive_error_string(ext));
            return 1;
        }
    }
    archive_read_close(a);
    archive_read_free(a);
    archive_write_close(ext);
    archive_write_free(ext);
    return 0;
}
