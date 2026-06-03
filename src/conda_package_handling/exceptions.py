from errno import ENOENT


class InvalidArchiveError(Exception):
    """Raised when libarchive can't open a file"""

    def __init__(self, fn, msg, *args, **kw):
        msg = (
            f"Error with archive {fn}.  You probably need to delete and re-download "
            f"or re-create this file.  Message was:\n\n{msg}"
        )
        self.errno = ENOENT
        super().__init__(msg)


class ArchiveCreationError(Exception):
    """Raised when an archive fails during creation"""

    pass


class CaseInsensitiveFileSystemError(InvalidArchiveError):
    def __init__(self, package_location, extract_location, **kwargs):
        message = f"""
        Cannot extract package to a case-insensitive file system. Your install
        destination does not differentiate between upper and lowercase
        characters, and this breaks things. Try installing to a location that
        is case-sensitive. Windows drives are usually the culprit here - can
        you install to a native Unix drive, or turn on case sensitivity for
        this (Windows) location?

          package location: {package_location}
          extract location: {extract_location}
        """
        self.package_location = package_location
        self.extract_location = extract_location
        super().__init__(package_location, message, **kwargs)


class ConversionError(Exception):
    def __init__(self, missing_files, mismatching_sizes, *args, **kw):
        self.missing_files = missing_files
        self.mismatching_sizes = mismatching_sizes
        errors = ""
        if self.missing_files:
            errors = f"Missing files in converted package: {self.missing_files}\n"
        errors = (
            errors
            + f"Mismatching sizes (corruption) in converted package: {self.mismatching_sizes}"
        )

        super().__init__(errors, *args, **kw)
