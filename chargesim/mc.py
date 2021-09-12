################################################################################
# MC Class                                                                     #
#                                                                              #
"""Monte Carlo algorithm for calculating occupancy probability."""
################################################################################


import sys
import random

from chargesim.probability import P


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
    """
    def __init__(self, topo, node_p=0.1):
        # Initialize
        self._topo = topo
        self._node_p = P(node_p)
        self._users = {}
        self._pois = []

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
        """
        # Initialize
        self._nodes = {}

        # Process poi
        for poi in self._pois:
            for node in poi.get_nodes():
                if node not in self._nodes.keys():
                    self._nodes[node] = {"p": P(p=poi.get_p())}
                else:
                    temp_p = {}
                    for day in range(7):
                        temp_p[day] = {}
                        for hour in range(24):
                            temp_p[day][hour] = self._nodes[node]["p"].get_p_hour(day, hour)+poi.get_p_hour(day, hour)
                    self._nodes[node]["p"] = P(p=temp_p)

        # Fill empty nodes
        for node in self._topo.get_nodes():
            if node not in self._nodes.keys():
                self._nodes[node] = {"p": self._node_p}

        # Process users
        for node in self._nodes.keys():
            self._nodes[node]["users"] = {u_id: {"success": 0, "fail": 0} for u_id in self._users.keys()}

        # Get charging stations
        self._charge_G, self._capacity = self._topo.charging_station()
        self._stations = {station: {"max": capacity, "cap": 0, "users": {u_id: 0 for u_id in self._users.keys()}} for station, capacity in self._capacity.items()}

    def run(self, weeks, drivers, max_dist=300):
        """Run Monte Carlo code.

        Parameters
        ----------
        weeks : integer
            Number of weeks to simulate
        drivers : dictionary, integer
            Number of drivers each hour, either an integer for the same hour,
            dictionary of hours or dictionary of days with a dictionary of hours
        max_dist : float, optional
            Maximal allowed walking distance


        Returns
        -------
        results : dictionary
            Node occupance
        """
        # Initialize
        progress_form = "%"+str(len(str(weeks*7)))+"i"

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

        # Run through weeks
        for week in range(weeks):
            # Run through days
            for day in range(7):
                # Run through hours
                for hour in range(24):
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
                            for i in range(station["users"][user_id]):
                                rand = random.uniform(0, 1)
                                # Check if user leaves
                                if rand < p_leave:
                                    station["cap"] -= 1
                                    station["users"][user_id] -= 1

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
                        if rand <= user.get_p_hour(day, hour):
                            # Choose random node
                            node = random.choice(list(self._nodes.keys()))
                            rand = random.uniform(0, 1)
                            # Poi MC step
                            if rand <= self._nodes[node]["p"].get_p_hour(day, hour):
                                # Calculate distance to nearest charging station
                                dest, dist = self._topo.dist_poi(node, self._charge_G)
                                # Check success
                                is_success = 0
                                if dist>max_dist:
                                    is_success += 1
                                if self._stations[dest]["cap"]==self._stations[dest]["max"]:
                                    is_success += 1
                                is_success = is_success==0
                                # Process success or failure
                                if is_success:
                                    self._stations[dest]["cap"] += 1
                                    self._stations[dest]["users"][user_id] += 1
                                    self._nodes[node]["users"][user_id]["success"] += 1
                                else:
                                    self._nodes[node]["users"][user_id]["fail"] += 1

                # Progress
                sys.stdout.write("Finished day "+progress_form%(week*7+day+1)+"/"+progress_form%(weeks*7)+"...\r")
                sys.stdout.flush()
        print()
