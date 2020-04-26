"""features.py

Python implementation of ModelImageWithSmallGaborSet
"""
# pylint: disable=no-member
import cv2, numpy, tqdm
from numpy import pi, ceil
import matplotlib.pyplot as plt
from os.path import join
import itertools

## settings
plotdir = 'plots'
img_fpath = 'images/dog_200.png'
n_sfs = 12
n_oris = 6

## other constants
bandwidth_constant = 0.56   ## 0.56 corresponds to bandwidth of 1
min_sf = 1.5                ## lowest spatial frequency in cyles / image
gamma = 0.5                 ## spatial aspect ratio a.k.a "ellipsicity"; 1 is round, 0 straight line
min_wavelength_pix = 4      ## smallest wavelength in pixels
kernel_extent = 4           ## how far to extend kernel from center in std of the gaussian (sigma)

## read image
image = cv2.imread(img_fpath)                           ## 3 channels, uint8
image = 1/255* cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  ## 1 channel float

## derived settings
size = image.shape[0]
max_sf = size / min_wavelength_pix
frequencies = numpy.geomspace(min_sf, max_sf, num=n_sfs)
orientations = numpy.arange(n_oris) * (pi/n_oris)
ori_freq_idx = list(itertools.product(range(n_oris), range(n_sfs)))

## loop with indices instead to be able to index gain
gain = numpy.full([n_oris, n_sfs, size, size], numpy.nan)
for o, f in tqdm.tqdm(ori_freq_idx, desc='kernel gain'):
    wavelength = size / frequencies[f]
    gaussian_std = wavelength * bandwidth_constant
    kside = 1 + 2 * int(ceil(kernel_extent * gaussian_std))
    kernel_params = dict(
        ksize=(kside, kside),
        sigma=gaussian_std,
        theta=orientations[o],
        lambd=wavelength,
        gamma=gamma,
        ktype=cv2.CV_32F
    )
    kernel_real = cv2.getGaborKernel(psi=0, **kernel_params)
    kernel_imag = cv2.getGaborKernel(psi=pi/2, **kernel_params)
    filt_real = cv2.filter2D(image, -1, kernel_real)
    filt_imag = cv2.filter2D(image, -1, kernel_imag)
    gain[o, f, :, :] = numpy.abs(filt_real + 1j * filt_imag)

for o, f in tqdm.tqdm(ori_freq_idx, desc='local selection'):
    pass