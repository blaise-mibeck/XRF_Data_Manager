"""
Configuration module for XRF Data Manager.
Contains atomic numbers, oxide conversion factors, and other constants.
"""

# Atomic numbers for all elements
ATOMIC_NUMBERS = {
    'H': 1, 'He': 2, 'Li': 3, 'Be': 4, 'B': 5, 'C': 6, 'N': 7, 'O': 8,
    'F': 9, 'Ne': 10, 'Na': 11, 'Mg': 12, 'Al': 13, 'Si': 14, 'P': 15,
    'S': 16, 'Cl': 17, 'Ar': 18, 'K': 19, 'Ca': 20, 'Sc': 21, 'Ti': 22,
    'V': 23, 'Cr': 24, 'Mn': 25, 'Fe': 26, 'Co': 27, 'Ni': 28, 'Cu': 29,
    'Zn': 30, 'Ga': 31, 'Ge': 32, 'As': 33, 'Se': 34, 'Br': 35, 'Kr': 36,
    'Rb': 37, 'Sr': 38, 'Y': 39, 'Zr': 40, 'Nb': 41, 'Mo': 42, 'Tc': 43,
    'Ru': 44, 'Rh': 45, 'Pd': 46, 'Ag': 47, 'Cd': 48, 'In': 49, 'Sn': 50,
    'Sb': 51, 'Te': 52, 'I': 53, 'Xe': 54, 'Cs': 55, 'Ba': 56, 'La': 57,
    'Ce': 58, 'Pr': 59, 'Nd': 60, 'Pm': 61, 'Sm': 62, 'Eu': 63, 'Gd': 64,
    'Tb': 65, 'Dy': 66, 'Ho': 67, 'Er': 68, 'Tm': 69, 'Yb': 70, 'Lu': 71,
    'Hf': 72, 'Ta': 73, 'W': 74, 'Re': 75, 'Os': 76, 'Ir': 77, 'Pt': 78,
    'Au': 79, 'Hg': 80, 'Tl': 81, 'Pb': 82, 'Bi': 83, 'Po': 84, 'At': 85,
    'Rn': 86, 'Fr': 87, 'Ra': 88, 'Ac': 89, 'Th': 90, 'Pa': 91, 'U': 92,
    'Np': 93, 'Pu': 94, 'Am': 95, 'Cm': 96, 'Bk': 97, 'Cf': 98, 'Es': 99,
    'Fm': 100, 'Md': 101, 'No': 102, 'Lr': 103, 'Rf': 104, 'Db': 105, 'Sg': 106,
    'Bh': 107, 'Hs': 108, 'Mt': 109, 'Ds': 110, 'Rg': 111, 'Cn': 112, 'Nh': 113,
    'Fl': 114, 'Mc': 115, 'Lv': 116, 'Ts': 117, 'Og': 118
}

# Oxide conversion factors using standard stoichiometry
# Element to (oxide formula, conversion factor)
OXIDE_FACTORS = {
    'Na': ('Na2O', 1.3480),   # Na × 1.3480 = Na2O
    'Mg': ('MgO', 1.6583),
    'Al': ('Al2O3', 1.8895),
    'Si': ('SiO2', 2.1393),
    'P': ('P2O5', 2.2914),
    'S': ('SO3', 2.4972),
    'Cl': ('Cl', 1.0000),     # Not typically reported as oxide
    'K': ('K2O', 1.2046),
    'Ca': ('CaO', 1.3992),
    'Ti': ('TiO2', 1.6681),
    'V': ('V2O5', 1.7852),
    'Cr': ('Cr2O3', 1.4616),
    'Mn': ('MnO', 1.2912),
    'Fe': ('Fe2O3', 1.4297),  # Assuming Fe3+
    'Co': ('CoO', 1.2715),
    'Ni': ('NiO', 1.2725),
    'Cu': ('CuO', 1.2518),
    'Zn': ('ZnO', 1.2448),
    'Ga': ('Ga2O3', 1.3442),
    'Ge': ('GeO2', 1.4408),
    'As': ('As2O3', 1.3203),
    'Se': ('SeO2', 1.4053),
    'Rb': ('Rb2O', 1.0936),
    'Sr': ('SrO', 1.1826),
    'Y': ('Y2O3', 1.2699),
    'Zr': ('ZrO2', 1.3508),
    'Nb': ('Nb2O5', 1.4305),
    'Mo': ('MoO3', 1.5003),
    'Sn': ('SnO2', 1.2696),
    'Sb': ('Sb2O3', 1.1973),
    'Ba': ('BaO', 1.1165),
    'La': ('La2O3', 1.1728),
    'Ce': ('CeO2', 1.2284),
    'Pr': ('Pr6O11', 1.1703),
    'Nd': ('Nd2O3', 1.1664),
    'Sm': ('Sm2O3', 1.1596),
    'Eu': ('Eu2O3', 1.1579),
    'Gd': ('Gd2O3', 1.1526),
    'Tb': ('Tb4O7', 1.1762),
    'Dy': ('Dy2O3', 1.1477),
    'Ho': ('Ho2O3', 1.1455),
    'Er': ('Er2O3', 1.1435),
    'Tm': ('Tm2O3', 1.1421),
    'Yb': ('Yb2O3', 1.1387),
    'Lu': ('Lu2O3', 1.1371),
    'Hf': ('HfO2', 1.1793),
    'Ta': ('Ta2O5', 1.2211),
    'W': ('WO3', 1.2610),
    'Pb': ('PbO', 1.0772),
    'Bi': ('Bi2O3', 1.1148),
    'Th': ('ThO2', 1.1379),
    'U': ('U3O8', 1.1792)
}

# Constants
PPM_TO_PERCENT = 0.0001  # 1 ppm = 0.0001%
TRACE_THRESHOLD = 1000   # ppm (0.1%)
