################################################################################
# MC Class                                                                     #
#                                                                              #
"""Monte Carlo algorithm for calculating occupation probability."""
################################################################################


import osmnx as ox


class MC:
    """This class run a Monte Carlo simulation

    Parameters
    ----------
    users : list
        List of user objects
    loc : string
        Location for simulation
    """
    def __init__(self, users, loc):
        self._users = users
