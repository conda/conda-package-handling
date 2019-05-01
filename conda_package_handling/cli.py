import argparse
from conda_package_handling import api, __version__


def parse_args(parse_this=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-V', '--version',
        action='version',
        help='Show the conda-package-handling version number and exit.',
        version='conda-package-handling %s' % __version__,
    )
    sp = parser.add_subparsers(title='subcommands', dest='subparser_name')

    extract_parser = sp.add_parser('extract', help='extract package contents', aliases=['x'])
    extract_parser.add_argument('archive_path', help='path to archive to extract')
    extract_parser.add_argument('--dest', help='destination to extract to.  If not set, defaults to'
                                ' package filename minus extension in cwd.')
    extract_parser.add_argument('--info', help='If the archive supports separate metadata, this'
                                ' flag extracts only the metadata in the info folder from the '
                                'package.  If the archive does not support separate metadata, this '
                                'flag has no effect and all files are extracted.',
                                action="store_true")

    create_parser = sp.add_parser('create', help='bundle files into a package', aliases=['c'])
    create_parser.add_argument('prefix', help="folder of files to bundle.  Not strictly required to"
                               " have conda package metadata, but if conda package metadata isn't "
                               "present, you'll see a warning and your file will not work as a "
                               "conda package")
    create_parser.add_argument("out_fn", help="Filename of archive to be created.  Extension "
                               "determines package type.")
    create_parser.add_argument('--file-list', help="Path to file containing one relative path per"
                               " line that should be included in the archive.  If not provided, "
                               "lists all files in the prefix.")
    create_parser.add_argument("--out-folder", help="Folder to dump final archive to")

    convert_parser = sp.add_parser('transmute', help='convert from one package type to another',
                                   aliases=['t'])
    convert_parser.add_argument('in_file', help="existing file to convert from.  Glob patterns "
                                "accepted.")
    convert_parser.add_argument('out_ext', help="extension of file to convert to.  "
                                "Examples: .tar.bz2, .conda")
    convert_parser.add_argument("--out-folder", help="Folder to dump final archive to")

    gpg_sign_parser = sp.add_parser('gpg-sign', help="sign package using GPG", aliases=['gpgs'])
    gpg_sign_parser.add_argument('--tool', help="GPG program to be used to sign archives",
                                 default='gpg', dest='gpgs_tool')
    gpg_sign_parser.add_argument('--identity', help="GPG identity to be used to sign archives",
                                 dest='gpgs_identity')
    gpg_sign_parser.add_argument('--homedir', help="GPG home directory", dest='gpgs_homedir')
    gpg_sign_parser.add_argument('archives', help="Path to archive(s) which need(s) to be signed. "
                                 "Glob patterns accepted")
    gpg_sign_parser.add_argument("--out-folder", help="Folder to dump signed archive(s) to")

    gpg_verify_parser = sp.add_parser('gpg-verify', help="verify package using GPG",
                                      aliases=['gpgv'])
    gpg_verify_parser.add_argument('--tool', help="GPG program to be used to verify archives",
                                   default='gpg', dest='gpgv_tool')
    gpg_verify_parser.add_argument('--homedir', help="GPG home directory", dest='gpgv_homedir')
    gpg_verify_parser.add_argument('archives', help="Path to archive(s) which need(s) to be "
                                   "verified. Glob patterns accepted")

    return parser.parse_args(parse_this)


def main(args=None):
    args = parse_args(args)
    if args.subparser_name in ('extract', 'x'):
        if args.info:
            api.extract(args.archive_path, args.dest, components='info')
        else:
            api.extract(args.archive_path, args.dest)
    elif args.subparser_name in ('create', 'c'):
        api.bundle(args.prefix, args.file_list, args.out_fn, args.out_folder)
    elif args.subparser_name in ('transmute', 't'):
        api.transmute(args.in_file, args.out_ext, args.out_folder)
    elif args.subparser_name in ('gpg-sign', 'gpgs'):
        api.gpg_sign(args.archives, out_folder=args.out_folder,
                     tool=args.gpgs_tool, identity=args.gpgs_identity,
                     homedir=args.gpgs_homedir)
    elif args.subparser_name in ('gpg-verify', 'gpgv'):
        api.gpg_verify(args.archives, tool=args.gpgv_tool,
                       homedir=args.gpgv_homedir)
    else:
        raise NotImplementedError("Command {} is not implemented".format(args.subparser_name))


if __name__ == "__main__":
    main(args=None)
