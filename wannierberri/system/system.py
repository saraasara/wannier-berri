#                                                            #
# This file is distributed as part of the WannierBerri code  #
# under the terms of the GNU General Public License. See the #
# file `LICENSE' in the root directory of the WannierBerri   #
# distribution, or http://www.gnu.org/copyleft/gpl.txt       #
#                                                            #
# The WannierBerri code is hosted on GitHub:                 #
# https://github.com/stepan-tsirkin/wannier-berri            #
#                     written by                             #
#           Stepan Tsirkin, University of Zurich             #
#                                                            #
# ------------------------------------------------------------

import numpy as np
from functools import cached_property
from ..symmetry import Group
from ..__utility import real_recip_lattice

pauli_x = [[0, 1], [1, 0]]
pauli_y = [[0, -1j], [1j, 0]]
pauli_z = [[1, 0], [0, -1]]
pauli_xyz = np.array([pauli_x, pauli_y, pauli_z]).transpose((1, 2, 0))


def num_cart_dim(key):
    """
    returns the number of cartesian dimensions of a matrix by key
    """
    if key in ["Ham"]:
        return 0
    elif key in ["AA", "BB", "CC", "SS", "SH", "OO"]:
        return 1
    elif key in ["SHA", "SA", "SR", "SHR", "GG", "FF"]:
        return 2
    else:
        raise ValueError(f"unknown matrix {key}")


class System:

    """
    The base class for describing a system. Does not have its own constructor,
    please use the child classes, e.g  :class:`System_w90` or :class:`System_tb`


    Parameters
    -----------
    periodic : [bool,bool,bool]
        set ``True`` for periodic directions and ``False`` for confined (e.g. slab direction for 2D systems). If less then 3 values provided, the rest are treated as ``False`` .
    frozen_max : float
        position of the upper edge of the frozen window. Used in the evaluation of orbital moment. But not necessary.
    NKFFT :
        the FFT grid which further will be used in calculations by default
    force_internal_terms_only : bool
        only internal terms will be evaluated in all formulae, the external or cross terms will be excluded.
        the internal terms are defined only by the Hamiltonian and spin
    name : str
        name that will be used by default in names of output files
    """

    def __init__(self,
                 frozen_max=-np.Inf,
                 periodic=(True, True, True),
                 NKFFT=None,
                 force_internal_terms_only=False,
                 name='wberri'
                 ):

        # TODO: move some initialization to child classes
        self.frozen_max = frozen_max
        self.periodic = periodic
        self.name = name


        if NKFFT is not None:
            self._NKFFT_recommended = NKFFT

        self.periodic = np.zeros(3, dtype=bool)
        self.periodic[:len(self.periodic)] = periodic
        self.is_phonon = False
        self.force_internal_terms_only = force_internal_terms_only


    def set_real_lattice(self, real_lattice=None, recip_lattice=None):
        assert not hasattr(self, 'real_lattice')
        self.real_lattice, _ = real_recip_lattice(real_lattice=real_lattice, recip_lattice=recip_lattice)



    @cached_property
    def recip_lattice(self):
        real, recip = real_recip_lattice(real_lattice=self.real_lattice)
        return recip

    def set_symmetry(self, symmetry_gen=()):
        """
        Set the symmetry group of the :class:`System`

        Parameters
        ----------
        symmetry_gen : list of :class:`symmetry.Symmetry` or str
            The generators of the symmetry group.

        Notes
        -----
        + Only the generators of the symmetry group are essential. However, no problem if more symmetries are provided.
          The code further evaluates all possible products of symmetry operations, until the full group is restored.
        + Providing `Identity` is not needed. It is included by default
        + Operations are given as objects of :class:`symmetry.Symmetry` or by name as `str`, e.g. ``'Inversion'`` , ``'C6z'``, or products like ``'TimeReversal*C2x'``.
        + ``symetyry_gen=[]`` is equivalent to not calling this function at all
        + Only the **point group** operations are important. Hence, for non-symmorphic operations, only the rotational part should be given, neglecting the translation.

        """
        self.symgroup = Group(symmetry_gen, recip_lattice=self.recip_lattice, real_lattice=self.real_lattice)


    @cached_property
    def cell_volume(self):
        return abs(np.linalg.det(self.real_lattice))

    @cached_property
    def range_wann(self):
        return np.arange(self.num_wann)



class System_k(System):

    pass
