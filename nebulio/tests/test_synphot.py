"""These tests compare filter parameters from pysynphot with the ones
I have calculated myself."""

from __future__ import (print_function, absolute_import, division, unicode_literals)

import os
import pytest
import nebulio
from nebulio.tests.utils import this_func_name
from nebulio.legacy import wfc3_utils
from matplotlib import pyplot as plt

wfc3_filters_to_test = [
    "F658N", "F656N", "F673N", "F547M",
    "FQ575N", "FQ672N", "FQ674N"
]

multiplets_to_test = [
    "[N II] 6583", "[O III] 5007"
]

def plot_compare_bandpass(bp0, bp, fn):
    fig, ax = plt.subplots()
    ax.plot(bp0.wave, bp0.T, '-', label='legacy')
    ax.plot(bp.wave, bp.T, '-', label='synphot')
    ax.set_xlim(bp.wav0 - bp.Wj, bp.wav0 + bp.Wj)
    ax.set_title(fn)
    ax.legend()
    plotfile = os.path.join("plots", '{}-{}.pdf'.format(this_func_name(), fn))
    fig.savefig(plotfile)

class LegacyBandpass(object):
    """Lightweight OO wrapper around `wfc3_utils` bandpass"""
    pass
    
@pytest.fixture(scope="module", params=wfc3_filters_to_test)
def bandpass_by_both_methods(request):
    """Fixture to read in both the legacy and pysynphot bandpasses"""
    fn = request.param
    bp0 = LegacyBandpass()
    bp0.wave, bp0.T = wfc3_utils.get_filter(fn, return_wavelength=True)
    bp0.Tm = wfc3_utils.Tm(bp0.T)
    bp = nebulio.Bandpass(','.join(['wfc3', 'uvis1', fn]))
    plot_compare_bandpass(bp0, bp, fn)
    return (bp0, bp, fn)


@pytest.fixture(scope="module", params=wfc3_filters_to_test)
def wfc3_bandpass(request):
    """Fixture to read in the pysynphot bandpass for a WFC3 filter"""
    return nebulio.Bandpass(','.join(['wfc3', 'uvis1', request.param]))


@pytest.fixture(scope="module", params=multiplets_to_test)
def emission_line_multiplet(request):
    lineid = request.param
    return nebulio.EmissionLine(lineid, velocity=30.0, fwhm_kms=20.0)


def test_version():
    """Silly test just to test that tests work"""
    assert nebulio.__version__ == "0.1a1", nebulio.__version__

def test_wfc3_utils(bandpass_by_both_methods):
    """Compare results from `nebulio.filterset` with results from wfc3_utils"""

    bp0, bp, fn = bandpass_by_both_methods
    allowed_tolerance = 0.015
    assert abs(bp0.Tm - bp.Tm) < allowed_tolerance, "Tm({}) = {}, {}".format(fn, bp0.Tm, bp.Tm)

def test_multiplet(emission_line_multiplet):
    em = emission_line_multiplet
    assert em.multiplicity == 3

def test_gaussian_multiplet(emission_line_multiplet, wfc3_bandpass):
    """This is testing that we can find the transmission at the line
    wavelength for each member of the multiplet

    """
    em = emission_line_multiplet
    bp = wfc3_bandpass
    Ti = bp.Ti(em)
    assert len(Ti) == 3

    
