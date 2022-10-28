import argparse
import os
import sys
from pprint import pprint

from . import __version__, api


def parse_args(parse_this=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        help="Show the conda-package-handling version number and exit.",
        version=f"conda-package-handling {__version__}",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="Disable interactive terminal printing.",
    )
    sp = parser.add_subparsers(title="subcommands", dest="subcommand", required=True)

    extract_parser = sp.add_parser("extract", help="extract package contents", aliases=["x"])
    extract_parser.add_argument("archive_path", help="path to archive to extract")
    extract_parser.add_argument(
        "--dest",
        help="destination folder to extract to.  If not set, defaults to"
        " package filename minus extension in the same folder as the input archive."
        " May be relative path used in tandem with the --prefix flag.",
    )
    extract_parser.add_argument(
        "--prefix",
        help="base directory to extract to. Use this to set the base"
        " directory, while allowing the folder name to be automatically determined "
        "by the input filename. An abspath --prefix with an unset --dest will "
        "achieve this.",
    )
    extract_parser.add_argument(
        "--info",
        help="If the archive supports separate metadata, this"
        " flag extracts only the metadata in the info folder from the "
        "package.  If the archive does not support separate metadata, this "
        "flag has no effect and all files are extracted.",
        action="store_true",
    )

    create_parser = sp.add_parser("create", help="bundle files into a package", aliases=["c"])
    create_parser.add_argument(
        "prefix",
        help="folder of files to bundle.  Not strictly required to"
        " have conda package metadata, but if conda package metadata isn't "
        "present, you'll see a warning and your file will not work as a "
        "conda package",
    )
    create_parser.add_argument(
        "out_fn", help="Filename of archive to be created.  Extension " "determines package type."
    )
    create_parser.add_argument(
        "--file-list",
        help="Path to file containing one relative path per"
        " line that should be included in the archive.  If not provided, "
        "lists all files in the prefix.",
    )
    create_parser.add_argument("--out-folder", help="Folder to dump final archive to")

    verify_parser = sp.add_parser(
        "verify", help="verify converted files against their reference", aliases=["v"]
    )
    verify_parser.add_argument(
        "glob",
        help="filename glob pattern to match pairs and verify.  Use"
        "the --reference-ext argument to change which extension is used "
        "as the ground truth, and which is considered corrupt in any "
        "mismatch",
    )
    verify_parser.add_argument(
        "--target-dir",
        help="folder for finding pairs of files.  Defaults " "to cwd.",
        default=os.getcwd(),
    )
    verify_parser.add_argument(
        "--reference-ext",
        "-r",
        help="file extension to consider as "
        "'ground truth' in comparison.  Use this with the --all flag.",
        default=".tar.bz2",
    )
    verify_parser.add_argument(
        "--processes",
        type=int,
        help="Max number of processes to use.  If " "not set, defaults to your CPU count.",
    )

    convert_parser = sp.add_parser(
        "transmute", help="convert from one package type to another", aliases=["t"]
    )
    convert_parser.add_argument(
        "in_file", help="existing file to convert from.  Glob patterns " "accepted."
    )
    convert_parser.add_argument(
        "out_ext", help="extension of file to convert to.  " "Examples: .tar.bz2, .conda"
    )
    convert_parser.add_argument("--out-folder", help="Folder to dump final archive to")
    convert_parser.add_argument(
        "--force", action="store_true", help="Force overwrite existing package"
    )
    convert_parser.add_argument(
        "--processes",
        type=int,
        help="Max number of processes to use.  If " "not set, defaults to your CPU count.",
    )
    convert_parser.add_argument(
        "--zstd-compression-level",
        help=(
            "When building v2 packages, set the compression level used by "
            "conda-package-handling. Defaults to the maximum."
        ),
        type=int,
        choices=range(1, 22),
        default=22,
    )
    return parser.parse_args(parse_this)


def main(args=None):
    args = parse_args(args)
    if hasattr(args, "out_folder") and args.out_folder:
        args.out_folder = (
            os.path.abspath(os.path.normpath(os.path.expanduser(args.out_folder))) + os.sep
        )
    if args.subcommand in ("extract", "x"):
        if args.info:
            api.extract(args.archive_path, args.dest, components="info", prefix=args.prefix)
        else:
            api.extract(args.archive_path, args.dest, prefix=args.prefix)
    elif args.subcommand in ("create", "c"):
        api.create(args.prefix, args.file_list, args.out_fn, args.out_folder)
    elif args.subcommand in ("transmute", "t"):
        failed_files = api.transmute(
            args.in_file,
            args.out_ext,
            args.out_folder,
            args.processes or 1,
            force=args.force,
            compression_tuple=(
                ".tar.zst",
                "zstd",
                f"zstd:compression-level={args.zstd_compression_level}",
            ),
            ci=args.ci,
        )
        if failed_files:
            print("failed files:")
            pprint(failed_files)
            sys.exit(1)
    elif args.subcommand in ("verify", "v"):
        failed_files = api.verify_conversion(args.glob, args.target_dir, args.reference_ext, ci=args.ci)
        if failed_files:
            print("failed files:")
            pprint(failed_files)
            sys.exit(1)


if __name__ == "__main__":
    main(args=None)
