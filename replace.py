#!/usr/bin/env python3

import re
import subprocess
import argparse
import os
import sys

POSSIBLE_DEPTYPES = ["hostmakedepends", "makedepends", "depends",
                     "checkdepends"]


def format_deplist(pkgs: str, deptype: str) -> str:
    """ take a white-space delimited string of pkgs and a deptype

        iterate over them creating a single multi-line (if required)
        string that is ready for using in xbps templates.

        the end-string returns with xbps $(vopt_if) blocks at the end

        it also wraps them with a width of 80 by default, but takes care
        to not break $(vopt_if) blocks in half.

        actions done for the symbols given:
        1. separate by whitespace
        2. if string vopt not found then add to pkglist list
        3. if string vopt found then check if | is not present
        3.1. if string | is not present then we replace ' with nothing
        3.2 add it to pkgvpostlist
        4. add all members of pkgvopstlist to pkglist.
        5. create 'pkgstr' that is pkglist converted to string
        6. wrap the text to 80 chars, no long_words or hyphen_breaks
         also add ' ' as a subsequent_indent
        7. use wrap.fill to return a single multi-line string
        8. replace '/' and '/' with ' '
        9. replace '>' with ')'
        10. replace 'vopt' with '$(vopt_if'
        11. return the string
    """

    from typing import List
    import textwrap

    pkglist: List[str] = []
    pkgvoptlist: List[str] = []

    for pkg in pkgs.split(' '):
        if 'vopt' not in pkg:
            pkglist.append(pkg)
        else:
            if '|' not in pkg:
                pkg = pkg.replace("'", "")

            pkgvoptlist.append(pkg)

    for vpkg in pkgvoptlist:
        pkglist.append(vpkg)

    pkgstr: str = deptype + '="' + ' '.join(pkglist) + '"'

    text_wrapper = textwrap.TextWrapper(width=80,
                                        break_long_words=False,
                                        break_on_hyphens=False,
                                        subsequent_indent=' ',)

    pkgstr = text_wrapper.fill(pkgstr)

    pkgstr = pkgstr.replace('/', ' ')
    pkgstr = pkgstr.replace('|', ' ')
    pkgstr = pkgstr.replace('>', ')')
    pkgstr = pkgstr.replace('vopt', '$(vopt_if')
    return pkgstr


def main():
    p = argparse.ArgumentParser(description="trim dependencies of templates.")
    p.add_argument('pkgname', metavar='template', type=str,
                   help='name of the package to be trimmed')
    p.add_argument('deptypes', metavar='deptypes', type=str,
                   help='single white-space separated string of deptypes')
    p.add_argument('pkgs', metavar='pkgs', type=str,
                   help='single white-space separated string of packages')
    p.add_argument('-i', dest='replace', action='store_true', default=False,
                   help='replace dependencies in template')

    args = p.parse_args()

    """
        Create a path by taking the output of xdistdir and adding srcpkgs/
        the pkgname and /template to the end
    """
    filepath = 'srcpkgs/' + args.pkgname + '/template'
    xdistdir = subprocess.run('xdistdir', stdout=subprocess.PIPE)
    filepath = xdistdir.stdout.decode('utf-8').replace('\n', '/') + filepath

    if not os.path.isfile(filepath):
        print('invalid path: ' + filepath, file=sys.stderr)
        sys.exit(2)

    """ packages recieved might be broken into multiple lines, we do our own
        text formatting on format_deplist
    """
    pkgs = args.pkgs.replace('\n', ' ')

    with open(filepath, 'r') as file_in:
        mod = file_in.read()

    """ we might have multiple deptypes separated by white-space
        we will iterate over each one of them separately as they
        are independented of one another
    """
    for deptype in args.deptypes.split(' '):
        if deptype not in POSSIBLE_DEPTYPES:
            continue

        pkgs: str = format_deplist(pkgs, deptype)

        regex = deptype + '=\"(.*\\n){0,}?.*\"'
        mod = re.sub(r'^%s' % regex, pkgs,
                     str(mod), flags=re.MULTILINE)

        print(pkgs)

    file_in.close()

    if args.replace:
        with open(filepath, 'w') as file_out:
            file_out.write(mod)
            file_out.close()


if __name__ == "__main__":
    main()
