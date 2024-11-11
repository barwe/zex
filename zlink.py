#!/bin/env python
import os
from os.path import exists, join, relpath, dirname, abspath, basename

source_dir: str = abspath(dirname(__file__))
allowed_extensions = [".py", ".txt", "safe_builtins"]


def select(s: str):
    for x in allowed_extensions:
        if s.endswith(x):
            return True
    return False


def are_hard_links(file1, file2):
    try:
        stat_info1 = os.stat(file1)
        stat_info2 = os.stat(file2)
        return (stat_info1.st_dev == stat_info2.st_dev) and (stat_info1.st_ino == stat_info2.st_ino)
    except FileNotFoundError:
        return False
    except Exception as e:
        return False


def main(args):
    dest_dir: str = abspath(args.dest_dir)
    if basename(dest_dir) != "zex":
        dest_dir = join(dest_dir, "zex")

    if not exists(dest_dir):
        os.makedirs(dest_dir)

    items = []
    for dp, _, fns in os.walk(source_dir):
        for fn in fns:
            if select(fn):
                ofp = join(dp, fn)
                rfp = relpath(ofp, source_dir)
                nfp = join(dest_dir, rfp)
                if exists(nfp):
                    if not are_hard_links(ofp, nfp):
                        raise FileExistsError(nfp)
                    continue
                nfd = dirname(nfp)
                if not exists(nfd):
                    os.makedirs(nfd)
                items.append((ofp, nfp))

    for a in items:
        os.link(*a)


if __name__ == "__main__":
    from argparse import ArgumentParser  # fmt:skip
    parser = ArgumentParser()
    parser.add_argument("dest_dir")
    args = parser.parse_args()
    main(args)
