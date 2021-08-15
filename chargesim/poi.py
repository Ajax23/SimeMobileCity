################################################################################
# Poi Class                                                                    #
#                                                                              #
"""Class defining points of interest."""
################################################################################


class Poi:
    """This class defines a point of interest.

    Parameters
    ----------
    topo : Map
        Map/topology object
    name : string
        Optional car name
    radius : float, optional
        Distance of nodes from poi center in m
    p : dictionary, optional
        Dictionary containing leave probabilities for each day - if empty, all
        hours have the same probability
    """
    def __init__(self, topo, name, radius=200, p={}):
        # Process input
        self._map = topo
        self._name = name
        self._p = p if p else {day: {hour: 1/7 for hour in range(24)} for day in range(7)}

        # Load graph
        self._G = topo.poi(name, radius=radius)
        self._nodes = list(self._G)


    ##################
    # Setter Methods #
    ##################
    def set_p(self, val):
        """Set complete probability dictionary.

        Parameters
        ----------
        val : dictionary
            Probability dictionary for each day and hour
        """
        self._p = val

    def set_p_day(self, day, val):
        """Set probability for a day.

        Parameters
        ----------
        day : integer
            Day index
        val : dictionary
            Probability dictionary for a day with each hour
        """
        self._p[day] = val

    def set_p_hour(self, day, hour, val):
        """Set probability for an hour.

        Parameters
        ----------
        day : integer
            Day index
        hour : integer
            Hour index
        val : float
            Probability of selected hour
        """
        self._p[day][hour] = val


    ##################
    # Getter Methods #
    ##################
    def get_map(self):
        """Return Map object.

        Returns
        -------
        val : Map
            Map object
        """
        return self._map

    def get_name(self):
        """Return poi name.

        Returns
        -------
        val : string
            Poi name
        """
        return self._name

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

    def get_p(self):
        """Return complete probability dictionary.

        Returns
        -------
        val : dictionary
            Probability dictionary for each day and hour
        """
        return self._p

    def get_p_day(self, day):
        """Return probability for a day.

        Parameters
        ----------
        day : integer
            Day index

        Returns
        -------
        val : dictionary
            Probability dictionary for a day with each hour
        """
        return self._p[day]

    def get_p_hour(self, day, hour):
        """Return probability for an hour.

        Parameters
        ----------
        day : integer
            Day index
        hour : integer
            Hour index

        Returns
        -------
        val : float
            Probability of selected hour
        """
        return self._p[day][hour]
