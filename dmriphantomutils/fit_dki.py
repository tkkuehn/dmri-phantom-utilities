#!/usr/bin/python3

import argparse
import sys

import dipy.reconst.dki as dki
import numpy as np
import scipy.ndimage as ndi

from dmriphantomutils import image_io

def fit_dki(dwi, blur=False):
    """Fit a DKI model to a DWI, applying a mask if provided.

    Parameters
    ---------
    dkimodel
        A dki model derived from the scan parameters
    img
        DWI data to fit to the model

    Returns
    -------
    dwifit
        A fit from which parameter maps can be generated
    """
    dkimodel = dki.DiffusionKurtosisModel(dwi.gtab)

    data = dwi.getImage()
    
    if blur:
        data = ndi.gaussian_filter(data, [0.5, 0.5, 0, 0])

    try:
        mask = dwi.mask
    except AttributeError:
        mask = np.ones(data.shape[:3])

    return dkimodel.fit(data, mask)

def save_metric_imgs(
        dwi, dkifit, fa_path=None, md_path=None, ad_path=None,
        rd_path=None, mk_path=None, ak_path=None, rk_path=None):
    source_affine = dwi.img.affine
    source_header = dwi.img.header

    # Should think about theoretical min and max kurtosis values for us
    if fa_path is not None:
        image_io.save_image(dkifit.fa, source_affine, source_header, fa_path)

    if md_path is not None:
        image_io.save_image(dkifit.md, source_affine, source_header, md_path)

    if ad_path is not None:
        image_io.save_image(dkifit.ad, source_affine, source_header, ad_path)

    if rd_path is not None:
        image_io.save_image(dkifit.rd, source_affine, source_header, rd_path)

    if mk_path is not None:
        image_io.save_image(dkifit.mk(), source_affine, source_header, mk_path)

    if ak_path is not None:
        image_io.save_image(dkifit.ak(), source_affine, source_header, ak_path)

    if rk_path is not None:
        image_io.save_image(dkifit.rk(), source_affine, source_header, rk_path)

def main(nifti_path, bval_path, bvec_path, mask_path=None, blur=False,
         fa_path=None, md_path=None, ad_path=None, rd_path=None, mk_path=None,
         ak_path=None, rk_path=None):
    """Load and fit an image to a DKI model, then save its parameters.

    This is meant to deal with the functionality of this module being called as
    a script.

    Parameters
    ----------
    nifti_path : string
        Path to the nifti DWI
    bval_path : string
        Path to the .bval file
    bvec_path : string
        Path to the .bvec file
    mask_path : string, optional
        Path to the nifti mask, if one exists
    fa_path : string, optional
        Path to which the fractional anisotropy image should be saved
    md_path : string, optional
        Path to which the mean diffusivity image should be saved
    ad_path : string, optional
        Path to which the axial diffusivity image should be saved
    rd_path : string, optional
        Path to which the radial diffusivity image should be saved
    mk_path : string, optional
        Path to which the mean kurtosis image should be saved
    ak_path : string, optional
        Path to which the axial kurtosis image should be saved
    rk_path : string, optional
        Path to which the radial kurtosis image should be saved
    """

    dwi = image_io.load_dwi(nifti_path, bval_path, bvec_path, mask_path)

    dkifit = fit_dki(dwi, blur)

    save_metric_imgs(dwi, dkifit, fa_path=fa_path, md_path=md_path,
                     ad_path=ad_path, rd_path=rd_path, mk_path=mk_path,
                     ak_path=ak_path, rk_path=rk_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=
            'Load a nifti image and fit the data to a DKI model.')
    parser.add_argument('nifti')
    parser.add_argument('bval')
    parser.add_argument('bvec')
    parser.add_argument('--mask')
    parser.add_argument('--blur', action='store_true')
    parser.add_argument('--fa')
    parser.add_argument('--md')
    parser.add_argument('--ad')
    parser.add_argument('--rd')
    parser.add_argument('--mk')
    parser.add_argument('--ak')
    parser.add_argument('--rk')
    args = parser.parse_args()
    main(args.nifti, args.bval, args.bvec, args.mask, blur=args.blur,
         fa_path=args.fa, md_path=args.md, ad_path=args.ad, rd_path=args.rd,
         mk_path=args.mk, ak_path=args.ak, rk_path=args.rk)

