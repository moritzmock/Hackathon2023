import os
import re
from argparse import ArgumentParser

TYPES = ["gdd", "pmm", "rad", "rad_h", "tmax", "tmean", "tmin"]

def read_args():
    parser = ArgumentParser()

    parser.add_argument("--path", type=str, required=True)

    return parser.parse_args()

if __name__ == "__main__":
    args = read_args()
    print(args)
    for type in TYPES:
        file_names = os.listdir("{}/{}/{}".format(args.path, "climate", type))
        print("Type --> ", type)
        print("Number of samples: ", len(file_names))
        mod = [re.sub(".tif", "", file) for file in file_names]
        mod = [file.split("_")[1] for file in file_names]

        for key in set(mod):
            print("{} appears in the data {}".format(key, mod.count(key)))


        print("------------------")

