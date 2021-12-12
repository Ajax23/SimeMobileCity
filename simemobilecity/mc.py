################################################################################
# MC Class                                                                     #
#                                                                              #
"""Monte Carlo algorithm for calculating occupancy probability."""
################################################################################


import sys
import random

import simemobilecity.utils as utils

from simemobilecity.partition import P, T


class MC:
    """This class runs the Monte Carlo simulation.

    Parameters
    ----------
    topo : Topology
        Topology object

    Examples
    --------
    Following example runs the MC simulation

    .. code-block:: python

        import simemobilecity as sec

        # Load topology of Munich
        topo = sec.Topology({"name": "Munich, Bavaria, Germany"}, tags={})

        # Create user with a probability of 0.5 to drive at any hour
        user = sec.User(0.5)

        # Load cafe POIs from OSM
        poi = sec.Poi(topo, tags, {"amenity": ["cafe"]})

        # Initialize MC object
        mc = sec.MC(topo)

        # Add 100 percent of the user
        mc.add_user(user, 100)

        # Add cafe poi
        mc.add_poi(poi)

        # Set number of drivers to 100 every hour
        mc.set_drivers(100)

        # Run MC simulation with 1 equilibration and 4 production weeks
        mc.run("output/traj.obj", weeks=4, weeks_equi=1)
    """
    def __init__(self, topo):
        # Initialize
        self._topo = topo
        self._users = {}
        self._pois = []
        self._drivers = {}

    def add_user(self, user, percentage):
        """Add User to simulation system.

        Parameters
        ----------
        user : User
            User object
        percentage : integer
            Percentage of user in simulation from 1%-100% in steps of 1
        """
        # Process percentage
        if not isinstance(percentage, int):
            print("MC.user: Wrong percentage format...")
            return
        elif sum([x["percent"] for x in self._users.values()])+percentage > 100:
            print("MC.user: Total percentage cannot be greater than 100 percent...")
            return

        # Append to list
        self._users[len(self._users.keys())] = {"user": user, "percent": percentage}

    def add_poi(self, poi):
        """Add POI to simulation system.

        Parameters
        ----------
        poi : Poi
            POI object
        """
        self._pois.append(poi)

    def set_drivers(self, drivers):
        """Add number of drivers.

        Parameters
        ----------
        drivers : dictionary, integer
            Number of drivers each hour, either an integer for the same hour,
            dictionary of hours or dictionary of days with a dictionary of hours
        """
        # Process input
        if isinstance(drivers, int):
            drivers = {day: {hour: drivers for hour in range(24)} for day in range(7)}
        elif isinstance(drivers, dict):
            if not (0 in drivers.keys() and isinstance(drivers[0], dict)):
                if 23 in drivers.keys():
                    drivers = {day: {hour: drivers[hour] for hour in range(24)} for day in range(7)}
                elif 6 in drivers.keys():
                    drivers = {day: {hour: drivers[day] for hour in range(24)} for day in range(7)}
                else:
                    print("MC: Invalid dirver input...")
                    return
        else:
            print("MC: Invalid dirver input...")
            return

        self._drivers = drivers

    def _prepare(self, node_p, p_norm, max_dist):
        """This helper function processes user and poi inputs into node list.
        User ids are added to a user list for the nodes, to count the number
        of successful and unsuccessfull attempts to reach destination.
        POI probabilities are added to the nodes to set the probability for
        choosing certain nodes as a destination.

        Nodes have a dictionary contatining a probability object, while charging
        stations are a dictionary used for simulation to fill in the capacity
        and compare to the maximum capacity.

        Parameters
        ----------
        node_p : dictionary, float
            Probability of all nodes not covered by pois each hour each weekday,
            either a float for the same probability each hour, dictionary of hours
            for same hour distribution for all days, a dictionary of days for the
            same hour probability for different days, or a dictionary of days each
            with a dictionary of hours
        p_norm: string
            Normalize POI dicts with maximum value from all nodes based on given
            type :math:`\\rightarrow` largest value is equal to one
        max_dist : float
            Maximal allowed walking distance from charging station to node in m, for
            nodes not covered by given POI objects
        """
        # Initialize
        self._nodes = {}
        self._nodes_dist = {}

        # Process poi
        max_p = {day: {hour: 0 for hour in range(24)} for day in range(7)}
        for poi in self._pois:
            for node in poi.get_nodes():
                if node not in self._nodes.keys():
                    self._nodes[node] = P(p=poi.get_p())
                    self._nodes_dist[node] = [poi.get_max_dist(), 1]
                else:
                    # Sum up probabilitty
                    temp_p = {}
                    for day in range(7):
                        temp_p[day] = {}
                        for hour in range(24):
                            temp_p[day][hour] = self._nodes[node].get_p_hour(day, hour)+poi.get_p_hour(day, hour)
                            max_p[day][hour] = temp_p[day][hour] if temp_p[day][hour]>max_p[day][hour] else max_p[day][hour]
                    self._nodes[node] = P(p=temp_p)
                    # Sum up distance
                    self._nodes_dist[node][0] += poi.get_max_dist()
                    self._nodes_dist[node][1] += 1

        # Fill empty nodes
        for node in self._topo.get_nodes():
            if node not in self._nodes.keys():
                self._nodes[node] = node_p
                self._nodes_dist[node] = [max_dist, 1]

        # Normalize probability matrix
        if p_norm:
            max_p_week = max([max(max_p[day].values()) for day in range(7)])
            max_p_day = {day: max(max_p[day].values()) for day in range(7)}
            for node, p in self._nodes.items():
                if p_norm=="week":
                    p.set_p({day: {hour: p.get_p_hour(day, hour)/max_p_week if p.get_p_hour(day, hour) and max_p_week else 0 for hour in range(24)} for day in range(7)})
                elif p_norm=="day":
                    p.set_p({day: {hour: p.get_p_hour(day, hour)/max_p_day[day] if p.get_p_hour(day, hour) and max_p_day[day] else 0 for hour in range(24)} for day in range(7)})
                elif p_norm=="hour":
                    p.set_p({day: {hour: p.get_p_hour(day, hour)/max_p[day][hour] if p.get_p_hour(day, hour) and max_p[day][hour] else 0 for hour in range(24)} for day in range(7)})

        # Normalize distance matrix
        self._nodes_dist = {node: dist[0]/dist[1] for node, dist in self._nodes_dist.items()}

        # Process stations
        self._stations = {station: {"max": capacity, "cap": [0 for user_id in range(len(self._users.keys()))]} for station, capacity in self._capacity.items()}

        # Create trajectory
        self._traj["nodes"] = T(len(self._nodes.keys()), len(self._users.keys()), node_keys={node: i for i, node in enumerate(list(self._nodes.keys()))})
        self._traj["cs"] = T(len(self._stations.keys()), len(self._users.keys()), node_keys={cs: i for i, cs in enumerate(list(self._stations.keys()))})
        self._traj["dist"] = T(len(self._stations.keys()), len(self._users.keys()), node_keys={cs: i for i, cs in enumerate(list(self._stations.keys()))}, failures=["dist"])

    def run(self, file_out, weeks, weeks_equi, capacity={}, trials=100, node_p=0.1, p_norm="", max_dist=500):
        """Run Monte Carlo code. Hereby the number of drivers for each hour
        represent the number of MC steps. During the equilibration run, the
        trajectory is not edited until sttarting the production run. If a user
        or POI choice fails, it is repeated for the given number of trials.
        POI probabilities are added to the nodes to set the probability for
        choosing certain nodes as a destination. The probability matrix for the
        graph nodes can be normalized using the options

        * **week** - Normalize all node probabilities with the maximum value from the week
        * **day** -  Normalize all node probabilities each day with the maximum value from the day
        * **hour** - Normalize all node probabilities each hour with the maximum value from the hour
        * *empty string* - Do not normalize

        Once finished, the trajectories are saved in form of a dictionary for

        * **nodes** - Node trajectory
        * **cs** - Charging station trajectory
        * **dist** - Charging station accumulated walking distance

        Parameters
        ----------
        file_out : string
            file link for output object file
        weeks : integer
            Number of weeks to simulate
        weeks_equi : integer
            Number of weeks for equilibration
        capacity : dictionary
            Dictionary containing charing station nodes and capacities
        trials : integer, optional
            Number of trials for faild user and node selections per driver
        node_p : dictionary, float, optional
            Probability of all nodes not covered by pois each hour each weekday,
            either a float for the same probability each hour, dictionary of hours
            for same hour distribution for all days, a dictionary of days for the
            same hour probability for different days, or a dictionary of days each
            with a dictionary of hours
        p_norm: string, optional
            Normalize POI dicts with maximum value based on given type
            :math:`\\rightarrow` largest value is equal to one
        max_dist : float, optional
            Maximal allowed walking distance from charging station to node in m, for
            nodes not covered by given POI objects

        Returns
        -------
        traj : dictionary
            Dictionary containing trajectories inputs and distance accumulation
        """
        # Process capacity
        if capacity:
            self._charge_G = self._topo.get_G().subgraph(capacity.keys())
            self._capacity = capacity
        else:
            self._charge_G, self._capacity = self._topo.charging_station()

        # Process users
        if sum([x["percent"] for x in self._users.values()]) < 100:
            print("MC.run: ERROR - User percentages do not add up to 100...")
            return
        users = sum([[user_id for x in range(user["percent"])] for user_id, user in self._users.items()], [])

        # Process normalization
        if p_norm not in ["", "week", "day", "hour"]:
            print("MC.run: ERROR - Wrong p_norm value - choose from \"\", \"week\", \"day\", \"hour\"...")
            return

        # Process drivers
        if not self._drivers:
            print("MC.run: ERROR - No drivers set...")
            return

        # Prepare trajectories
        print("Starting preparation...")
        self._traj = {}
        self._traj["inp"] = {"weeks": weeks, "cs": self._capacity}
        self._prepare(P(node_p), p_norm, max_dist)

        # Run equilibration
        if weeks_equi:
            print("Starting equilibration...")
            self._run_helper(weeks_equi, users, trials, is_equi=True)

        # Run production
        if weeks:
            print("Starting production...")
            self._run_helper(weeks, users, trials, is_equi=False)

        # Save trajectory
        if file_out:
            utils.save(self._traj, file_out)

        return self._traj


    def _run_helper(self, weeks, users, trials, is_equi):
        """Run helper for processing weeks.

        Parameters
        ----------
        weeks : int
            Number of weeks to run
        users : dictionary
            User dictionary
        trials : integer
            Number of trials for faild user and node selections per driver
        is_equi : bool
            True for equilibration run to not add instances to trajectory
        """
        # Initialize
        progress_form = "%"+str(len(str(weeks*7)))+"i"

        # Run through weeks
        for week in range(weeks):
            # Run through days
            for day in range(7):
                # Run through hours
                for hour in range(24):
                    ################
                    # Filling Step #
                    ################
                    # Run through dirvers
                    for driver in range(self._drivers[day][hour]):
                        # Choose random user
                        user_id = random.choice(users)
                        user = self._users[user_id]["user"]
                        rand = random.uniform(0, 1)
                        # User MC step
                        for i in range(trials):
                            if rand <= user.get_p_hour(day, hour):
                                # Choose random node
                                node = random.choice(list(self._nodes.keys()))
                                rand = random.uniform(0, 1)
                                # POI MC step
                                for j in range(trials):
                                    if rand <= self._nodes[node].get_p_hour(day, hour):
                                        # Determine nearest charging station and calculate distance
                                        dest, dist = self._topo.dist_poi(node, self._charge_G)
                                        # Process success
                                        is_success = True
                                        ## Check occupancy and fail move if necessary with reason occupancy
                                        if is_success and sum(self._stations[dest]["cap"])==self._stations[dest]["max"]:
                                            if not is_equi:
                                                self._traj["nodes"].add_fail(day, hour, node, user_id, "occ")
                                                self._traj["cs"].add_fail(day, hour, dest, user_id, "occ")
                                            is_success = False
                                        ## Check distance and fail move if necessary with reason distance
                                        if is_success and dist > self._nodes_dist[node]:
                                            if not is_equi:
                                                self._traj["nodes"].add_fail(day, hour, node, user_id, "dist")
                                                self._traj["cs"].add_fail(day, hour, dest, user_id, "dist")
                                                self._traj["dist"].add_fail_dist(day, hour, dest, user_id, dist)
                                            is_success = False
                                        ## Add session if successful
                                        if is_success:
                                            if not is_equi:
                                                self._traj["nodes"].add_success(day, hour, node, user_id)
                                                self._traj["cs"].add_success(day, hour, dest, user_id)
                                                self._traj["dist"].add_success_dist(day, hour, dest, user_id, dist)
                                            self._stations[dest]["cap"][user_id] += 1
                                        # End node trials if successful
                                        break
                                # End user trials if successful
                                break

                    ##############
                    # Empty Step #
                    ##############
                    # Run through stations
                    for station in self._stations.values():
                        # Run through users
                        for user_id in self._users.keys():
                            # Get leaving probability
                            user = self._users[user_id]["user"]
                            p_leave = 1-user.get_p_hour(day, hour)
                            # Run through users parking
                            for i in range(station["cap"][user_id]):
                                rand = random.uniform(0, 1)
                                # Check if user leaves
                                if rand < p_leave:
                                    station["cap"][user_id] -= 1

                # Progress
                sys.stdout.write("Finished day "+progress_form%(week*7+day+1)+"/"+progress_form%(weeks*7)+"...\r")
                sys.stdout.flush()
        print()
