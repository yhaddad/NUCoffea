"""
Various utilities.
"""
from numpy import abs, pi


class CMSPreliminary(object):
    import matplotlib.pyplot as plt

    style = {
        "axes.grid": False,
        "axes.labelsize": 16,
        "axes.linewidth": 1.4,  # edge linewidth
        "legend.framealpha": 0,
        "legend.fancybox": False,
        "legend.frameon": False,
        "xtick.top": True,
        "xtick.labelsize": 14,
        "xtick.direction": "in",  # direction: in, out, or inout
        "xtick.minor.visible": True,  # visibility of minor ticks on x-axis
        "xtick.major.size": 4.5,  # major tick size in points
        "xtick.minor.size": 3,  # minor tick size in points
        "xtick.major.width": 1.0,  # major tick width in points
        "xtick.minor.width": 0.8,  # minor tick width in points
        "ytick.right": True,
        "ytick.labelsize": 14,
        "ytick.direction": "in",  # direction: in, out, or inout
        "ytick.minor.visible": True,  # visibility of minor ticks on x-axis
        "ytick.major.size": 4.5,  # major tick size in points
        "ytick.minor.size": 3,  # minor tick size in points
        "ytick.major.width": 1.0,  # major tick width in points
        "ytick.minor.width": 0.8,  # minor tick width in points
    }

    CMS = r'$\mathbf{CMS}~\mathit{Preliminary}$'
    year_strings = {
        2018: r'60.0 $\mathrm{fb}^{-1}$ (13 TeV 2018)'
    }

    def __init__(self, xlabel, ylabel, year, **kwargs):
        self.plt.style.use(self.style)
        self.fig, self.ax = self.plt.subplots(1, 1, **kwargs)
        self.xlabel, self.ylabel, self.year = xlabel, ylabel, year

    def __enter__(self):
        self.ax.savefig = self.fig.savefig
        return self.ax

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ax.set_xlabel(self.xlabel, horizontalalignment='right', x=1.0)
        self.ax.set_ylabel(self.ylabel, horizontalalignment='right', y=1.0)
        bbox = self.ax.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
        h = (0.1 + bbox.height) / bbox.height
        self.ax.text(0, h, self.CMS, fontsize=15, transform=self.ax.transAxes)
        self.ax.text(1, h, self.year_strings[self.year], fontsize=12, transform=self.ax.transAxes,
                     horizontalalignment='right')
        self.fig.tight_layout()


def d_phi(phi1, phi2):
    """Calculates delta phi between objects"""
    x = abs(phi1 - phi2)
    sign = x <= pi
    return sign * x + ~sign * (2 * pi - x)

# not really sure what these are for...

# def join_collections(col_a, col_b):
#     col_a_tags = awkward.JaggedArray(col_a.starts, col_a.stops, np.full(len(col_a.content), 0, dtype=np.int64))
#     col_b_tags = awkward.JaggedArray(col_b.starts, col_b.stops, np.full(len(col_b.content), 1, dtype=np.int64))
#     col_a_index = awkward.JaggedArray(col_a.starts, col_a.stops, np.arange(len(col_a.content), dtype=np.int64))
#     col_b_index = awkward.JaggedArray(col_b.starts, col_b.stops, np.arange(len(col_b.content), dtype=np.int64))
#     tags = awkward.JaggedArray.concatenate([col_a_tags, col_b_tags], axis=1)
#     index = awkward.JaggedArray.concatenate([col_a_index, col_b_index], axis=1)
#
#     return awkward.JaggedArray(
#         tags.starts, tags.stops,
#         awkward.UnionArray(
#             tags.content, index.content,
#             [electrons.content, photons.content]
#         )
#     )
#
#
# def ret_collections(df):
#     muons = JaggedCandidateArray.candidatesfromcounts(
#         df['nMuon'],
#         pt=df['Muon_pt'].content,
#         eta=df['Muon_eta'].content,
#         phi=df['Muon_phi'].content,
#         mass=df['Muon_mass'].content,
#         charge=df['Muon_charge'].content
#     )
#     elect = JaggedCandidateArray.candidatesfromcounts(
#         df['nMuon'],
#         pt=df['Muon_pt'].content,
#         eta=df['Muon_eta'].content,
#         phi=df['Muon_phi'].content,
#         mass=df['Muon_mass'].content,
#         charge=df['Muon_charge'].content
#     )
#
#     leptons = join_collections(electrons, muons)
#     jets = JaggedCandidateArray.candidatesfromcounts(
#         df['nJet'],
#         pt=df['Jet_pt'].content,
#         eta=df['Jet_eta'].content,
#         phi=df['Jet_phi'].content,
#         mass=df['Jet_mass'].content,
#     )
#
#     return leptons, jets
