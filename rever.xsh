$ACTIVITIES = ["version_bump", "authors", "changelog"]

# Basic settings
$PROJECT = $GITHUB_REPO = $(basename $(git remote get-url origin)).split('.')[0]
$GITHUB_ORG = "conda"

# Authors settings
$AUTHORS_FILENAME = "AUTHORS.md"
$AUTHORS_SORTBY = "alpha"

# Changelog settings
$CHANGELOG_FILENAME = "CHANGELOG.md"
$CHANGELOG_PATTERN = r"\[//\]: # \(current developments\)"
$CHANGELOG_HEADER = """[//]: # (current developments)

## $VERSION ($RELEASE_DATE)

"""
$CHANGELOG_CATEGORIES = [
    "Enhancements",
    "Bug fixes",
    "Deprecations",
    "Docs",
    "Other",
]
$CHANGELOG_CATEGORY_TITLE_FORMAT = "### {category}\n\n"
$CHANGELOG_AUTHORS_TITLE = "Contributors"
$CHANGELOG_AUTHORS_FORMAT = "* @{github}\n"

$VERSION_BUMP_PATTERNS = [  # These note where/how to find the version numbers
    ('src/conda_package_handling/__init__.py', r'__version__\s*=.*', '__version__ = "$VERSION"'),
                         ]
