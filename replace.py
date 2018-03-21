#!/usr/bin/env python3

import re
import sys


POSSIBLE_DEPTYPES = ["hostmakedepends", "makedepends", "depends",
                     "checkdepends"]


def main():
    if len(sys.argv) < 2:
        print('no template provided')
        sys.exit(1)
    elif len(sys.argv) < 3:
        print('no deptype ... provided')
        sys.exit(1)
    elif len(sys.argv) < 4:
        print('no replace string provided')
        sys.exit(1)

    filepath = 'srcpkgs/' + sys.argv[1] + '/template'
    pkgs = sys.argv[3].replace('\n', ' ')

    with open(filepath, 'r') as file_in:
        mod = file_in.read()

    deptypes = sys.argv[2].split(" ")

    for deptype in deptypes:
        if deptype not in POSSIBLE_DEPTYPES:
            continue

        regex = deptype + '=\"(.*\\n){0,}?.*\"'
        mod = re.sub(r'^%s' % regex, deptype + '="' + pkgs + '"',
                     str(mod), flags=re.MULTILINE)

        print(deptype + '="' + pkgs + '"')

    file_in.close()

    with open(filepath, 'w') as file_out:
        file_out.write(mod)
        file_out.close()


if __name__ == "__main__":
    main()
