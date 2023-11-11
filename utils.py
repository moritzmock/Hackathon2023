import argparse
import pandas as pd
import os
import rasterio
import numpy as np
from rasterio.mask import mask


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_time_series_data_from_polygon(polygon, stat="mean"):
    paths_dataset = get_dataset_file_paths()
    dti = pd.date_range("2020-03-22", end="2022-12-31", freq="12D")
    rows = []
    for d in dti:
        try:
            date_string = d.strftime("%Y-%m-%d")
            row = extract_raster_data_from_polygon(polygon, paths_dataset[date_string], stat)
            rows.append(row)
        except Exception as e:
            # print(str(e))
            # print(d)
            rows.append({
                "gdd": np.nan,
                "pmm": np.nan,
                "tmax": np.nan,
                "tmean": np.nan,
                "tmin": np.nan,
                "elevation": np.nan,
                "exposure": np.nan,
                "slope": np.nan,
                "ndvi": np.nan,
                "ndwi": np.nan,
                "reci": np.nan,
            })

    ts = pd.DataFrame(index=dti, data=rows)

    return ts


def get_dataset_file_paths():
    # directory = "../../../Desktop/konverto_data_package"  # MORITZ
    directory = "../../konverto_data_package"  # JONAS

    datasets = {}
    for root, dirs, files in os.walk(directory):
        # print(f"Current directory: {root}")
        if "visual" in root:
            continue

        tif_files = [f for f in files if f.endswith(".tif") and not f.startswith(".")]
        tif_paths = [os.path.join(root, f) for f in tif_files]

        if len(tif_files) > 0:

            if "climate" in tif_paths[0]:
                dates = ["-".join(f.replace(".tif", "").split("_")[1:]) for f in tif_files]
            elif "satellite" in tif_paths[0]:
                datestrings = [f.replace(".tif", "").split("_")[0] for f in tif_files]
                dates = [d[:4] + "-" + d[4:6] + "-" + d[6:] for d in datestrings]
            else:
                dates = None

            if dates:
                dataset_name = os.path.basename(root)

                for date, fp in zip(dates, tif_paths):
                    if date in datasets:
                        datasets[date].update({dataset_name: fp})
                    else:
                        datasets[date] = {dataset_name: fp}

            if "terrain" in tif_paths[0]:
                dataset_names = [n.replace(".tif", "") for n in tif_files]
                for date in datasets.keys():
                    for dn, fp in zip(dataset_names, tif_paths):
                        datasets[date].update({dn: fp})

    return datasets



def extract_raster_data_from_polygon(polygon, paths_data, stat = "mean"):

    data = {}
    mean = {}
    std = {}

    if stat != "mean_std":
        np_function = getattr(np, "nan" + stat)

    for dataset_name, fpath in paths_data.items():
        raster = rasterio.open(fpath)

        if stat != "mean_std":
            try:
                data[dataset_name] = np_function(mask(raster, polygon, crop=True, invert=False, all_touched=True, nodata=np.nan)[0])
            except:
                data[dataset_name] = np_function(mask(raster, polygon, crop=False, invert=True, all_touched=True, nodata=np.nan)[0])

        else:
            try:
                mean[dataset_name] = np.nanmean(mask(raster, polygon, crop=True, invert=False, all_touched=True, nodata=np.nan)[0])
                std[dataset_name] = np.nanstd(mask(raster, polygon, crop=True, invert=False, all_touched=True, nodata=np.nan)[0])
            except:
                mean[dataset_name] = np.nanmean(mask(raster, polygon, crop=False, invert=True, all_touched=True, nodata=np.nan)[0])
                std[dataset_name] = np.nanstd(mask(raster, polygon, crop=False, invert=True, all_touched=True, nodata=np.nan)[0])
            data = (mean, std)



    return data