import logging
from datetime import timedelta
from pathlib import Path
import argparse
from datetime import datetime

import numpy as np

import georinex as gr


def eachfile(fn: Path):
    times = gr.gettime(fn)

    # %% output
    Ntimes = times.size

    if Ntimes == 0:
        raise ValueError(f"{fn.name}: no times found")

    t0 = times[0].astype(datetime)
    t1 = times[-1].astype(datetime)

    ostr = f"{fn.name}:" f" {t0.isoformat()}" f" {t1.isoformat()}" f" {Ntimes}"

    hdr = gr.rinexheader(fn)
    interval = hdr.get("interval", np.nan)
    if ~np.isnan(interval):
        ostr += f" {interval}"
        Nexpect = (t1 - t0) // timedelta(seconds=interval) + 1
        if Nexpect != Ntimes:
            logging.warning(f"{fn.name}: expected {Nexpect} but got {Ntimes} times")

    print(ostr)

    print(times)


p = argparse.ArgumentParser(description="Print times in RINEX file")
p.add_argument("filename", help="RINEX filename to get times from")
p.add_argument("-glob", help="file glob pattern", nargs="+", default="*")
p = p.parse_args()

filename = Path(p.filename).expanduser()

print("filename: start, stop, number of times, interval")

if filename.is_dir():
    flist = gr.globber(filename, p.glob)
    for f in flist:
        try:
            eachfile(f)
        except ValueError as err:
            logging.error(f"{f.name}: {err}")
elif filename.is_file():
    eachfile(filename)
else:
    raise FileNotFoundError(f"{filename} is not a path or file")
