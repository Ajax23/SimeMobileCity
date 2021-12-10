################################################################################
# Poi Class                                                                    #
#                                                                              #
"""Class defining points of interest."""
################################################################################


from simemobilecity.partition import P


class Poi(P):
    """This class defines a point of interest.

    Parameters
    ----------
    topo : Topology
        Topology object
    tags : Dictionary
        OSM tags in format - tags={"amenity": ["cafe"]}
    p : dictionary, float
        Probability each hour each weekday, either a float for the same
        probability each hour, dictionary of hours for same hour distribution
        for all days, a dictionary of days for the same hour probability for
        different days, or a dictionary of days each with a dictionary of hours
    radius : float, optional
        Distance of nodes from poi center in m
    max_dist : float, optional
        Maximal allowed distance from charging station poi in m
    """
    def __init__(self, topo, tags, p, radius=200, max_dist=500):
        # Call super class
        super(Poi, self).__init__(p)

        # Process input
        self._topo = topo
        self._tags = tags
        self._max_dist = max_dist

        # Load graph
        self._G = topo.poi(tags, radius=radius)
        self._nodes = list(self._G)


    ##################
    # Setter Methods #
    ##################
    def set_max_dist(self, val):
        """Set maximal allowed distance from charging station to POI.

        Parameters
        ----------
        val : float
            Maximal allowed distance from charging station poi in m
        """
        self._max_dist = val


    ##################
    # Getter Methods #
    ##################
    def get_topo(self):
        """Return Topology object.

        Returns
        -------
        val : Topology
            Topology object
        """
        return self._topo

    def get_tags(self):
        """Return OSM tags.

        Returns
        -------
        val : dictionary
            Poi tags
        """
        return self._tags

    def get_G(self):
        """Get OSM graph object.

        Returns
        -------
        val : networkx.MultiDiGraph
            OSM graph object
        """
        return self._G

    def get_nodes(self):
        """Get list of nodes of graph.

        Returns
        -------
        val : list
            List of node ids of graph
        """
        return self._nodes

    def get_max_dist(self):
        """Get maximal allowed distance from charging station to POI.

        Returns
        -------
        val : float
            Maximal allowed distance from charging station to POI in m
        """
        return self._max_dist
