#!/usr/bin/env python3


def format_deplist(pkgs: str, deptype: str) -> str:
    """ take a white-space delimited string of pkgs and a deptype

        it wraps them with a width of 80 by default, but takes care
        to not break $(vopt_if) blocks in half.

        actions done for the symbols given:
        1. create 'pkgstr' that is pkgs with deptype and formatting for XBPS
           dependency template
        2. wrap the text to 80 chars, no long_words or hyphen_breaks
         also add ' ' as a subsequent_indent
        3. use wrap.fill to return a single multi-line string
        4. replace '/' and '/' with ' '
        5. replace '>' with ')'
        6. replace 'vopt' with '$(vopt_if'
        7. return the string
    """

    from textwrap import TextWrapper

    pkgstr: str = deptype + '="' + pkgs.replace('vopt', '$(vopt_if') + '"'

    text_wrapper = TextWrapper(width=80,
                               break_long_words=False,
                               break_on_hyphens=False,
                               subsequent_indent=' ',)

    pkgstr = text_wrapper.fill(pkgstr)

    pkgstr = pkgstr.replace('/', ' ')
    pkgstr = pkgstr.replace('|', ' ')
    pkgstr = pkgstr.replace('>', ')')

    return pkgstr


def main():
    from argparse import ArgumentParser
    from subprocess import run, PIPE
    from os.path import isfile
    from re import sub, MULTILINE

    canbedeps = ["hostmakedepends", "makedepends", "depends", "checkdepends"]

    p = ArgumentParser(description="trim dependencies of templates.")
    p.add_argument('pkgname', metavar='template', type=str,
                   help='name of the package to be trimmed')
    p.add_argument('--deps', dest='deptypes', nargs='+',
                   help='single white-space separated string of deptypes')
    p.add_argument('pkgs', type=str,
                   help='single white-space separated string of packages')
    p.add_argument('-i', dest='replace', action='store_true', default=False,
                   help='replace dependencies in template')

    args = p.parse_args()

    """
        Create a path by taking the output of xdistdir and adding srcpkgs/
        the pkgname and /template to the end
    """
    filepath = 'srcpkgs/' + args.pkgname + '/template'
    xdistdir = run('xdistdir', stdout=PIPE)
    filepath = xdistdir.stdout.decode('utf-8').replace('\n', '/') + filepath

    if not isfile(filepath):
        print('invalid path: ' + filepath)
        exit(2)

    """ packages recieved might be broken into multiple lines, we do our own
        text formatting on format_deplist
    """
    pkgs: str = args.pkgs.replace('\n', ' ')

    """ we might have multiple deptypes separated by white-space
        we will iterate over each one of them separately as they
        are independented of one another
    """
    for deptype in args.deptypes:
        if deptype not in canbedeps:
            continue

        pkgs = format_deplist(pkgs, deptype)

        print(pkgs)

        if args.replace:
            with open(filepath, 'r') as file_in:
                mod = file_in.read()

                regex = deptype + '=\"(.*\\n){0,}?.*\"'
                mod = sub(r'^%s' % regex, pkgs, str(mod),
                          flags=MULTILINE)

            with open(filepath, 'w') as file_out:
                file_out.write(mod)


if __name__ == "__main__":
    main()
