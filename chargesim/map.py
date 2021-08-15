################################################################################
# Map Class                                                                    #
#                                                                              #
"""OSMNX python wrapper."""
################################################################################


import math
import osmnx as ox
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


class Map:
    """This class is a python wrapper for the osmnx package. The input is a
    dictionary containing the location name **name**, and optionally preloaded
    graph **G** and projection objects **Gp**.

    Parameters
    ----------
    loc : dictionary
        Location for simulation as dictionary {"name": "", "G": None, "Gp": None}
    log : bool
        True to print osmnx console output
    """
    def __init__(self, loc, tags={"amenity" : ["charging_station"]}, log=True):
        # Set osmnx output
        ox.config(log_console=log)
        self._loc = loc

        # Process input
        self._G = ox.graph_from_place(loc["name"], network_type="walk") if not "G" in loc.keys() else loc["G"]
        self._Gp = ox.project_graph(self._G) if not "Gp" in loc.keys() else loc["Gp"]
        self._nodes = list(self._G)

        # Get charging stations
        if tags:
            self.set_station(tags)

    def dist(self, orig, dest, is_route=False):
        """Calculate the distance between two locations

        Parameters
        ----------
        orig : integer
            Node of origin
        dest : integer
            Node of destination
        is_route : bool
            True to return route

        Returns
        -------
        route_len : float
            Route length in m
        route : list, optional
            Route as list of nodes
        """
        # Calculate shortest distance
        route_len = nx.shortest_path_length(self._G, orig, dest, weight="length")

        # Get shortest route
        if is_route:
            route = ox.shortest_path(self._G, orig, dest, weight="length")
            return route_len, route
        else:
            return route_len

    def dist_charge(self, orig, is_route=False):
        """Calculate the distance to nearest charging station.

        Parameters
        ----------
        orig : integer
            Node of origin
        is_route : bool
            True to return route

        Returns
        -------
        route_len : float
            Route length in m
        route : list, optional
            Route as list of nodes
        """
        # Get position of origin
        pos = dict(self._G.nodes(data=True))[orig]

        # Get nearest charging station
        dest = ox.nearest_nodes(self._C, pos["x"], pos["y"])

        # Get shortest route
        return self.dist(orig, dest, is_route)

    def plot(self, routes=[], ax=None, is_station=True, kwargs={"G": {}, "C": {}, "R": {}}):
        """Plot graph optionally with chargin stations and routes.

        Parameters
        ----------
        routes : list, optional
            List of routes to show
        ax : Axis, optional
            Axis object
        kwargs: dictionary, optional
            Dictionary with plotting parameters for the graph **G**, charging
            stations **C** and routes **R**

        Returns
        -------
        ax : Axis
            Axis object
        """
        # Initialize
        if ax is None:
            _, ax = plt.subplots(figsize=(12, 8))

        # Plot edges
        ox.plot_graph(self._G, ax=ax, node_size= 0, edge_linewidth=1, edge_color="#262626", show=False, edge_alpha=0.1, **kwargs["G"])

        # Plot charging stations
        if is_station:
            ox.plot_graph(self._C, ax=ax, node_size=40, edge_linewidth=0, node_color="#4C72B0", show=False, **kwargs["C"])

        # Plot routes
        if routes:
            if len(routes)==1:
                ox.plot_graph_route(self._G, routes[0], ax=ax, route_color="#C44E52", route_linewidth=6, node_size=0, **kwargs["R"])
            else:
                ox.plot_graph_routes(self._G, routes, ax=ax, route_color="#C44E52", route_linewidth=6, node_size=0, **kwargs["R"])

        return ax


    ##################
    # Setter Methods #
    ##################
    def set_station(self, tags):
        """Set charging station graph.

        Parameters
        ----------
        tags : dictionary
            OSM tags for charging station
        """
        # Get chargin stations
        gdf = ox.geometries_from_place(self._loc["name"], tags)

        # Find nearest nodes in graph
        pos = gdf["geometry"]
        nodes = ox.nearest_nodes(self._G, pos.x, pos.y)

        # Create subgraph containing charging stations
        self._C = self._G.subgraph(nodes)

        # Create list conatining capacities
        capacity = gdf["capacity"]
        capacity = pd.to_numeric(capacity, downcast="integer")
        capacity = {node: int(val) if not math.isnan(val) else 1 for node, val in dict(capacity["node"]).items()}

        self._capacity = {}
        for i, node in enumerate(pos["node"].index):
            node_new = nodes[i]
            if node_new not in self._capacity:
                self._capacity[node_new] = capacity[node]
            else:
                self._capacity[node_new] += capacity[node]


    ##################
    # Getter Methods #
    ##################
    def get_G(self):
        """Get OSM graph object.

        Returns
        -------
        val : networkx.MultiDiGraph
            OSM graph object
        """
        return self._G

    def get_Gp(self):
        """Get OSM graph projection object.

        Returns
        -------
        val : networkx.MultiDiGraph
            OSM graph projection object
        """
        return self._Gp

    def get_station(self):
        """Get charging station graph object.

        Returns
        -------
        val : networkx.MultiDiGraph
            charging station graph projection object
        """
        return self._C

    def get_capacity(self):
        """Get charging station capacity.

        Returns
        -------
        val : dictionary
            charging station capacity
        """
        return self._capacity

    def get_nodes(self):
        """Get list of nodes of graph.

        Returns
        -------
        val : list
            List of node ids of graph
        """
        return self._nodes
