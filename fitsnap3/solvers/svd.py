from .solver import Solver
from ..parallel_tools import pt
from ..io.input import config
from scipy.linalg import lstsq
import numpy as np
from sys import float_info as fi


class SVD(Solver):

    def __init__(self, name):
        super().__init__(name)

    @pt.sub_rank_zero
    def perform_fit(self):
        if pt.shared_arrays['configs_per_group'].testing_elements != 0:
            testing = -1*pt.shared_arrays['configs_per_group'].testing_elements
        else:
            testing = len(pt.shared_arrays['w'].array)
        w = pt.shared_arrays['w'].array[:testing]
        aw, bw = w[:, np.newaxis] * pt.shared_arrays['a'].array[:testing], w * pt.shared_arrays['b'].array[:testing]
#       Look into gradient based linear solvers as well.
        if config.sections['EXTRAS'].apply_transpose:
            if np.linalg.cond(aw)**2 < 1 / fi.epsilon:
                bw = aw[:, :].T @ bw
                aw = aw[:, :].T @ aw
            else:
                print("The Matrix is ill-conditioned for the transpose trick")
        self.fit, residues, rank, s = lstsq(aw, bw, 1.0e-13)

    @staticmethod
    def _dump_a():
        np.savez_compressed('a.npz', a=pt.shared_arrays['a'].array)

    def _dump_x(self):
        np.savez_compressed('x.npz', x=self.fit)

    def _dump_b(self):
        b = pt.shared_arrays['a'].array @ self.fit
        np.savez_compressed('b.npz', b=b)
