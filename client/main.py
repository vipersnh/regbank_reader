import argparse;
from pdb import set_trace
from regbank_parser import *

parser = argparse.ArgumentParser();
parser.add_argument('fnames', nargs=1);
parse_res = parser.parse_args();
fnames = parse_res.fnames;


if __name__ == "__main__":
    db = regbank_to_database(fnames[0]);
    set_trace();
