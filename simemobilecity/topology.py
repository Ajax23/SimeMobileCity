################################################################################
# Topology Class                                                               #
#                                                                              #
"""OSMNX python wrapper."""
################################################################################


import math
import osmnx as ox
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


class Topology:
    """This class is a python wrapper for the osmnx package. The input is a
    dictionary containing the location name **name**, and optionally preloaded
    graph **G** and projection objects **Gp**.

    Parameters
    ----------
    loc : dictionary
        Location for simulation as dictionary {"name": "", "G": None, "Gp": None}
    is_log : bool, optional
        True to print osmnx console output
    """
    def __init__(self, loc, is_log=True):
        # Set osmnx output
        ox.config(log_console=is_log)
        self._loc = loc

        # Process input
        self._G = ox.graph_from_place(loc["name"], network_type="walk") if not "G" in loc.keys() else loc["G"]
        self._Gp = ox.project_graph(self._G) if not "Gp" in loc.keys() else loc["Gp"]
        self._nodes = list(self._G)

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

    def dist_poi(self, orig, poi):
        """Calculate the distance to nearest poi node.

        Parameters
        ----------
        orig : integer
            Node of origin
        poi : networkx.MultiDiGraph
            Poi graph

        Returns
        -------
        dest : integer
            Node of destination
        route_len : float
            Route length in m
        """
        # Get position of origin
        pos = dict(self._G.nodes(data=True))[orig]

        # Get nearest charging station
        dest = ox.nearest_nodes(poi, pos["x"], pos["y"])

        # Get shortest route
        return dest, self.dist(orig, dest, is_route=False)

    def poi(self, tags, radius=0, is_gdf=False):
        """Get nodes for given point of interest.

        Parameters
        ----------
        tags : Dictionary
            OSM tags in format - tags={"amenity": ["cafe"]}
        radius : float, optional
            Distance of pois from center in m
        is_gdf : bool, optional
            True to return GDF object

        Returns
        -------
        poi : networkx.MultiDiGraph
            OSM graph object
        gdf : geopandas.GeoDataFrame, optional
            GDF object
        """
        # Get pois geometry
        gdf = ox.geometries_from_place(self._loc["name"], tags=tags)

        # Find nearest nodes in graph
        pos = gdf["geometry"]["node"]
        poi_nodes = ox.nearest_nodes(self._G, pos.x, pos.y)

        # Find nodes within radius
        if radius:
            nodes = []
            for node in poi_nodes:
                poi = nx.ego_graph(self._G, node, radius, distance="length")
                nodes += list(poi)
            nodes = list(set(nodes))
        else:
            nodes = poi_nodes

        # Create subgraph from nodes
        P = self._G.subgraph(nodes)

        # Return
        if is_gdf:
            return P, gdf
        else:
            return P

    def charging_station(self, tags={"amenity": ["charging_station"]}):
        """Create charging station graph and capacity dictionaries.

        Parameters
        ----------
        tags : string, optional
            Charging station tag name

        Returns
        -------
        stations : networkx.MultiDiGraph
            OSM graph object containing all charging stations
        capacity : dictionary
            Charging stations capacities
        """
        # Get chargin stations
        gdf = ox.geometries_from_place(self._loc["name"], tags=tags)

        # Find nearest nodes in graph
        pos = gdf["geometry"]
        nodes = ox.nearest_nodes(self._G, pos.x, pos.y)

        # Create subgraph from nodes
        C = self._G.subgraph(nodes)

        # Create list conatining capacities
        capacity_list = gdf["capacity"]
        capacity_list = pd.to_numeric(capacity_list, downcast="integer")
        capacity_list = {node: int(val) if not math.isnan(val) else 1 for node, val in dict(capacity_list["node"]).items()}

        capacity = {}
        for i, node in enumerate(pos["node"].index):
            node_new = nodes[i]
            if node_new not in capacity:
                capacity[node_new] = capacity_list[node]
            else:
                capacity[node_new] += capacity_list[node]

        return C, capacity

    def plot(self, pois=[], routes=[], ax=None, kwargs={"G": {}, "P": {}, "R": {}}):
        """Plot graph optionally with chargin stations and routes.

        Parameters
        ----------
        poi : list, optional
            List of points of interest graphs to show
        routes : list, optional
            List of routes to show
        ax : Axis, optional
            Axis object
        kwargs: dictionary, optional
            Dictionary with plotting parameters for the graph **G**, Pois **P**
            and routes **R**

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
        if pois:
            for poi in pois:
                ox.plot_graph(poi, ax=ax, node_size=40, edge_linewidth=0, node_color="#4C72B0", show=False, **kwargs["P"])

        # Plot routes
        if routes:
            if len(routes)==1:
                ox.plot_graph_route(self._G, routes[0], ax=ax, route_color="#C44E52", route_linewidth=6, node_size=0, **kwargs["R"])
            else:
                ox.plot_graph_routes(self._G, routes, ax=ax, route_color="#C44E52", route_linewidth=6, node_size=0, **kwargs["R"])

        return ax


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

    def get_nodes(self):
        """Get list of nodes of graph.

        Returns
        -------
        val : list
            List of node ids of graph
        """
        return self._nodes
