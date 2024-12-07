import numpy as np
import os
import urllib.request
import zipfile
import rasterio
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

# download the image file
def download_tiff(url="https://srtm.csi.cgiar.org/wp-content/uploads/files/srtm_5x5/TIFF/srtm_65_04.zip"):
    # resulting tif file name
    res = url.split('/')[-1][:-4] + ".tif"
    # download the file and unzip in working directory
    if os.path.exists("tiff.zip"):
        # skip if already downloaded
        print("file has already been downloaded")
        return res

    urllib.request.urlretrieve(url, "tiff.zip")
    with zipfile.ZipFile("tiff.zip", "r") as zip_ref:
        zip_ref.extractall(os.getcwd())

    return res

# Open the raster image
def open_tif(tif):
    dataset = rasterio.open(tif)
    band = dataset.read(1)

    # filter flagged values as 0
    band[band == -32768] = 0

    return band

# Create image of the raster
def plot_image(band, line, smoothed, start=(3600, 1200), end=(1200,4800)):
    # plot altitudes plot
    plt.subplot(1, 2, 1)
    plt.plot(smoothed)

    plt.subplot(1, 2, 2)
    plt.imshow(band, cmap="turbo")
    plt.colorbar()
    # labels
    plt.xlabel("Cols")
    plt.ylabel("Rows")

    # plot points
    plt.plot(start[1], start[0], c='black', marker='o')
    plt.plot(end[1], end[0], c='black', marker='o')

    # plot dotted line
    plt.plot(line[:, 1], line[:, 0], c='black', linestyle='dashed')

    plt.show()

# given a start and end point plot a height graph of points in between
def line_altitudes(band, start=(3600, 1200), end=(1200,4800)):
    # get all points on the line
    slope = (end[0] - start[0]) / (end[1] - start[1])
    b = start[0] - (start[1] * slope)
    on_line = []

    # add points on the line
    for x in range(start[1], end[1]):
        y = int(slope * x + b)
        on_line.append([y, x])

    heights = []
    for p in on_line:
        y = p[0]
        x = p[1]
        heights.append(band[y, x])

    # smooth the line with window?
    smoothed = []
    window_size = int(len(heights) / 100)
    cur = 0

    while cur < len(heights) - window_size + 1:
        window = heights[cur:cur+window_size]
        smoothed.append(np.mean(window))
        cur += window_size

    on_line = np.asarray(on_line)

    return on_line, smoothed

if __name__ == "__main__":
    # run the full set of functions
    tif_file = download_tiff()
    print(tif_file)
    band = open_tif(tif_file)
    line, smoothed = line_altitudes(band)
    plot_image(band, line, smoothed)
