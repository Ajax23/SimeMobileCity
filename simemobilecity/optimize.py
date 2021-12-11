################################################################################
# Optimize Class                                                               #
#                                                                              #
"""Optimization class for predicting charging station placement."""
################################################################################


import sys
import random

import simemobilecity.utils as utils


class Optimize:
    """Run optimization

    Parameters
    ----------
    topo : Topology
        Topology object
    """
    def __init__(self, topo):
        # Initialize
        self._topo = topo


    ##################
    # Public Methods #
    ##################
    def run(self, traj, cap={}, crit={"dist": 0.5, "occ": 0.5}):
        """Run optimization.

        Parameters
        ----------
        traj : dictionary
            Simulation trajectory of the mc code - includes the **cs** and
            **dist** entry
        cap : dictionary, optional
            Charging station capacities
        crit : dictionary, optional
            Critical values of failures at which to optimize
        """
        # Initialize
        num_days = traj["cs"].get_num_days()
        num_hours = traj["cs"].get_num_hours()
        num_users = traj["cs"].get_num_users()
        num_nodes = traj["cs"].get_num_nodes()

        progress_form = "%"+str(len(str(num_nodes)))+"i"

        # Process charging station capacities
        cap = self._topo.charging_station()[1] if not cap else cap

        # Extract failing probabilities
        extract = traj["cs"].extract(range(num_days), range(num_hours), range(num_users), is_norm=False)
        distances = traj["dist"].extract(range(num_days), range(num_hours), range(num_users), is_norm=False)

        # Warning for missing charging station capacities
        if not len(cap)==traj["cs"].get_num_nodes():
            print("Warning - Number of charging station capcity list is not equal to number of charging stations in given trajectory. Missing ones will be ignores.")

        # Run through nodes
        run_id = 0
        for node, data in extract.items():
            run_id += 1
            for failure, thresh in crit.items():
                # Check if critical value is reached
                tot_sessions = data["fail"][failure]+data["success"]
                fail_prob = data["fail"][failure]/tot_sessions if data["fail"][failure] else 0
                if fail_prob > thresh:
                    # Occupancy optimization - Add for charging points
                    if failure=="occ":
                        if node in cap.keys():
                            # Add charging points with number of mean failures
                            cap[node] += int(data["fail"][failure]/(num_days*num_hours))

                    # Distance fail - Add
                    elif failure=="dist":
                        mean_dist = distances[node]["fail"]["dist"]/tot_sessions if data["fail"][failure] else 0
                        # print(mean_dist, cap[node])
                        # print(node, cap[node])

            # Progress
            sys.stdout.write("Finished node "+progress_form%(run_id)+"/"+progress_form%(num_nodes)+"...\r")
            sys.stdout.flush()
        print()
