"""
Various utilities.
"""
from numpy import abs, pi


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