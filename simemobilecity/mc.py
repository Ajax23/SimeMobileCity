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
    """This class run a Monte Carlo simulation. Probability of every node is the
    sum of given probabilities from the poi list. This means, nodes intersecting
    multiple pois have a higher probability than the single pois.

    Parameters
    ----------
    topo : Topology
        Topology object
    node_p : dictionary, float, optional
        Probability of all nodes not covered by pois each hour each weekday,
        either a float for the same probability each hour, dictionary of hours
        for same hour distribution for all days, a dictionary of days for the
        same hour probability for different days, or a dictionary of days each
        with a dictionary of hours
    is_normalize: bool, optional
        True to normalize POI dicts with maximum value :math:`\\rightarrow`
        largest value is equal to one
    """
    def __init__(self, topo, node_p=0.1, is_normalize=False):
        # Initialize
        self._topo = topo
        self._node_p = P(node_p)
        self._users = {}
        self._pois = []
        self._is_normalize = is_normalize

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
        """Add Poi to simulation system.

        Parameters
        ----------
        poi : Poi
            Poi object
        """
        self._pois.append(poi)

    def _prepare_nodes(self):
        """This helper function processes user and poi inputs into node list.
        User ids are added to a user list for the nodes, to count the number
        of successful and unsuccessfull attempts to reach destination.
        Poi probabilities are added to the nodes to set the probability for
        choosing certain nodes as a destination.

        Nodes have a dictionary contatining a probability object, while charging
        stations are a dictionary used for simulation to fill in the capacity
        and compare to the maximum capacity.

        Parameters
        ----------
        is_normalize : bool
            True to normalize POI dicts with maximum value :math:`\\rightarrow`
            largest value is equal to one
        """
        # Initialize
        self._nodes = {}

        # Process poi
        max_p = 0
        for poi in self._pois:
            for node in poi.get_nodes():
                if node not in self._nodes.keys():
                    self._nodes[node] = P(p=poi.get_p())
                else:
                    temp_p = {}
                    for day in range(7):
                        temp_p[day] = {}
                        for hour in range(24):
                            temp_p[day][hour] = self._nodes[node].get_p_hour(day, hour)+poi.get_p_hour(day, hour)
                            max_p = temp_p[day][hour] if temp_p[day][hour]>max_p else max_p
                    self._nodes[node] = P(p=temp_p)

        # Fill empty nodes
        for node in self._topo.get_nodes():
            if node not in self._nodes.keys():
                self._nodes[node] = self._node_p

        # Normalize matrix
        if self._is_normalize:
            for node, p in self._nodes.items():
                p = P(p={day: {hour: p.get_p_hour(day, hour)/max_p for hour in range(24)} for day in range(7)})

        # Get charging stations
        self._charge_G, self._capacity = self._topo.charging_station()
        self._stations = {station: {"max": capacity, "cap": [0 for user_id in range(len(self._users.keys()))]} for station, capacity in self._capacity.items()}

        # Create trajectory
        self._traj = {}
        self._traj["nodes"] = T(len(self._nodes.keys()), len(self._users.keys()), node_keys={node: i for i, node in enumerate(list(self._nodes.keys()))})
        self._traj["cs"] = T(len(self._stations.keys()), len(self._users.keys()), node_keys={cs: i for i, cs in enumerate(list(self._stations.keys()))})

    def run(self, file_out, weeks, drivers, max_dist=150, weeks_equi=4, trials=100):
        """Run Monte Carlo code.

        Parameters
        ----------
        file_out : string
            file link for output object file
        weeks : integer
            Number of weeks to simulate
        drivers : dictionary, integer
            Number of drivers each hour, either an integer for the same hour,
            dictionary of hours or dictionary of days with a dictionary of hours
        max_dist : float, optional
            Maximal allowed walking distance
        weeks_equi : integer
            Number of weeks for equilibration
        trials : integer, optional
            Number of trials for faild user and node selections per driver

        Returns
        -------
        results : dictionary
            Node occupance
        """
        # Process users
        if sum([x["percent"] for x in self._users.values()]) < 100:
            print("MC.run: User percentages do not add up to 100...")
            return
        users = sum([[user_id for x in range(user["percent"])] for user_id, user in self._users.items()], [])

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

        # Process nodes
        self._prepare_nodes()

        # Run equilibration
        self._run_helper(weeks_equi, drivers, users, max_dist, trials, is_equi=True)

        # Run production
        self._run_helper(weeks, drivers, users, max_dist, trials, is_equi=False)

        # Save trajectory
        if file_out:
            utils.save(self._traj, file_out)


    def _run_helper(self, weeks, drivers, users, max_dist, trials, is_equi):
        """Run helper for processing weeks.

        Parameters
        ----------
        weeks : int
            Number of weeks to run
        drivers : dictionary
            Dictionary containing the number of drivers per day per hour
        users : dictionary
            User dictionary
        max_dist : float, optional
            Maximal allowed walking distance
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
                    for driver in range(drivers[day][hour]):
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
                                # Poi MC step
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
                                        if is_success and dist > max_dist:
                                            if not is_equi:
                                                self._traj["nodes"].add_fail(day, hour, node, user_id, "dist")
                                                self._traj["cs"].add_fail(day, hour, dest, user_id, "dist")
                                            is_success = False
                                        ## Add session if successful
                                        if is_success:
                                            if not is_equi:
                                                self._traj["nodes"].add_success(day, hour, node, user_id)
                                                self._traj["cs"].add_success(day, hour, dest, user_id)
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
