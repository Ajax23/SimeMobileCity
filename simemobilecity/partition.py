################################################################################
# Paartition Class                                                            #
#                                                                              #
"""Classes for discretization are defined - probability and trajectory."""
################################################################################


import pandas as pd


class P:
    """This class defines a probability object.

    Parameters
    ----------
    p : dictionary, float
        Probability each hour each weekday, either a float for the same
        probability each hour, dictionary of hours for same hour distribution
        for all days, a dictionary of days for the same hour probability for
        different days, or a dictionary of days each with a dictionary of hours
    """
    def __init__(self, p):
        # Process input
        self.set_p(p)


    ##################
    # Representation #
    ##################
    def __repr__(self):
        """Create a pandas table of the probability data.

        Returns
        -------
        repr : String
            Pandas data frame of the probability
        """
        return pd.DataFrame(self._p).to_string()



    ##################
    # Setter Methods #
    ##################
    def set_p(self, p):
        """Set complete probability dictionary.

        Parameters
        ----------
        p : dictionary, float
            Probability each hour each weekday, either a float for the same
            probability each hour, dictionary of hours for same hour
            distribution for all days, a dictionary of days for the same hour
            probability for different days, or a dictionary of days each with a
            dictionary of hours
        """
        if p:
            if isinstance(p, float) or isinstance(p, int):
                self._p = {day: {hour: p for hour in range(24)} for day in range(7)}
            elif isinstance(p, dict):
                if len(p.keys())==7 and 0 in p.keys() and isinstance(p[0], dict) and len(p[0].keys())==24:
                    self._p = p
                elif 23 in p.keys():
                    self._p = {day: {hour: p[hour] for hour in range(24)} for day in range(7)}
                elif 6 in p.keys():
                    self._p = {day: {hour: p[day] for hour in range(24)} for day in range(7)}
                else:
                    print("P: Invalid dictionary input...")
                    self._p = None
            else:
                print("P: Invalid probability input...")
                self._p = None
        else:
            print("P: Dictionary p cannot be empty...")
            self._p = None


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


class T:
    """This class defines a trajectory object. For each hour of a day in a week,
    a dictionary is created for containing the success abnd failures of each
    user type. The failures are differentiated between occupancy **occ** and
    distance **dist**.

    Parameters
    ----------
    num_nodes : integer
        Number of nodes in system
    num_users : integer
        Number of usertypes in system
    num_days : integer, optional
        Number of unique days
    num_hours : integer, optional
        Number of unique hours per days
    failures : list, optional
        List of failure types - by default occupancy **occ** and
        distance **dist**
    node_keys : dictionary, optional
        Dictionary containing the relation of list and osmx ids
    """
    def __init__(self, num_nodes, num_users, num_days=7, num_hours=24, failures=["occ", "dist"], node_keys={}):
        # Initialize
        self._num_days = num_days
        self._num_hours = num_hours
        self._num_nodes = num_nodes
        self._num_users = num_users
        self._failures = failures
        self._node_keys = node_keys

        # Generate data structure
        self._t = []
        for day in range(num_days):
            for hour in range(num_hours):
                for node in range(num_nodes):
                    # Success
                    for u_id in range(num_users):
                        self._t.append(0)
                    # Failure
                    for fail in failures:
                        for u_id in range(num_users):
                            self._t.append(0)

    ###################
    # Private Methods #
    ###################
    def _index(self, day, hour, node, user_id, fail=""):
        """Calculate list index for given settings.

        Parameters
        ----------
        day : integer
            Day index
        hour : integer
            Hour index
        node : node
            Node index
        user_id : integer
            User index
        fail : string, optional
            Failure reason, leave empty for success
        """
        # Process node id
        node = self._node_keys[node] if self._node_keys else node

        # Calcualte
        index = day*self._num_hours*self._num_nodes*self._num_users*(len(self._failures)+1) # day
        index += hour*self._num_nodes*self._num_users*(len(self._failures)+1)               # hour
        index += node*self._num_users*(len(self._failures)+1)                               # nodes
        index += self._num_users*(self._failures.index(fail)+1) if fail else 0              # failure
        index += user_id                                                                    # user

        return index


    ##################
    # Public Methods #
    ##################
    def add_success(self, day, hour, node, user_id):
        """Add a successfull charging instance to given day, hour, node, and
        user_id.

        Parameters
        ----------
        day : integer
            Day index
        hour : integer
            Hour index
        node : node
            Node index
        user_id : integer
            User index
        """
        self._t[self._index(day, hour, node, user_id)] += 1

    def add_success_dist(self, day, hour, node, user_id, dist):
        """Add walking distance of a successfull charging instance to given day,
        hour, node, and user type.

        Parameters
        ----------
        day : integer
            Day index
        hour : integer
            Hour index
        node : node
            Node index
        user_id : integer
            User index
        dist : float
            Walking distance from node to charging station
        """
        self._t[self._index(day, hour, node, user_id)] += dist

    def add_fail(self, day, hour, node, user_id, fail):
        """Add a failed charging instance to given day, hour, node, and user type
        with the given failure reason.

        Parameters
        ----------
        day : integer
            Day index
        hour : integer
            Hour index
        node : node
            Node index
        user_id : integer
            User index
        fail : string
            Failure reason
        """
        self._t[self._index(day, hour, node, user_id, fail)] += 1

    def add_fail_dist(self, day, hour, node, user_id, dist):
        """Add a failed charging instance to given day, hour, node, and user type
        with the given failure reason.

        Parameters
        ----------
        day : integer
            Day index
        hour : integer
            Hour index
        node : node
            Node index
        user_id : integer
            User index
        dist : float
            Walking distance from node to charging station
        """
        self._t[self._index(day, hour, node, user_id, "dist")] += dist

    def extract(self, days, hours, users, is_norm=True):
        """Extract data from trajectory for the given days hours and user types.
        The data for the different values will be combined to one node list with
        percentages for success and failure. The latter will be divided into the
        different failure types.

        Parameters
        ----------
        days : list
            List of day ids to combine
        hours : list
            List of hour ids to combine
        users : list
            List of user ids to combine
        is_norm : bool
            True to noromalize results

        Returns
        -------
        nodes : dictionary
            Dictionary of node ids with amount for success and failure
        """
        # Initialize
        nodes = {}
        node_ids = self._node_keys.keys() if self._node_keys else range(self._num_nodes)

        # Run through nodes
        for node in node_ids:
            # Build structure
            nodes[node] = {"success": 0, "fail": {fail: 0 for fail in self._failures}}

            # Extract values
            for day in days:
                for hour in hours:
                    for user in users:
                        nodes[node]["success"] += self.get_success(day, hour, node, user)
                        for fail in self._failures:
                            nodes[node]["fail"][fail] += self.get_fail(day, hour, node, user, fail)

            # Calculate percentages
            if is_norm:
                normalize = nodes[node]["success"]+sum([nodes[node]["fail"][fail] for fail in self._failures])
                nodes[node]["success"] = nodes[node]["success"]/normalize if normalize else 0
                for fail in self._failures:
                    nodes[node]["fail"][fail] = nodes[node]["fail"][fail]/normalize if normalize else 0

        # Return nodes
        return nodes


    ##################
    # Setter Methods #
    ##################
    def set_success(self, day, hour, node, user_id, val):
        """Set sucess value for given day, hour, node, and user type.

        Parameters
        ----------
        day : integer
            Day index
        hour : integer
            Hour index
        node : node
            Node index
        user_id : integer
            User index
        val : integer
            New entry value
        """
        self._t[self._index(day, hour, node, user_id)] = val

    def set_fail(self, day, hour, node, user_id, fail, val):
        """Set failure value for given day, hour, node, and user type with
        the given failure reason.

        Parameters
        ----------
        day : integer
            Day index
        hour : integer
            Hour index
        node : node
            Node index
        user_id : integer
            User index
        fail : string
            Failure reason
        val : integer
            New entry value
        """
        self._t[self._index(day, hour, node, user_id, fail)] = val


    ##################
    # Getter Methods #
    ##################
    def get_success(self, day, hour, node, user_id):
        """Get sucess value for given day, hour, node, and user type.

        Parameters
        ----------
        day : integer
            Day index
        hour : integer
            Hour index
        node : node
            Node index
        user_id : integer
            User index

        Returns
        -------
        val : integer
            Trajectory value
        """
        return self._t[self._index(day, hour, node, user_id)]


    def get_fail(self, day, hour, node, user_id, fail):
        """Get failure value for given day, hour, node, and user type with
        the given failure reason.

        Parameters
        ----------
        day : integer
            Day index
        hour : integer
            Hour index
        node : node
            Node index
        user_id : integer
            User index
        fail : string
            Failure reason

        Returns
        -------
        val : integer
            Trajectory value
        """
        return self._t[self._index(day, hour, node, user_id, fail)]

    def get_num_days(self):
        """Get number of days.

        Returns
        -------
        val : integer
            Number of days
        """
        return self._num_days

    def get_num_hours(self):
        """Get number of hours.

        Returns
        -------
        val : integer
            Number of hours
        """
        return self._num_hours

    def get_num_users(self):
        """Get number of users.

        Returns
        -------
        val : integer
            Number of users
        """
        return self._num_users

    def get_num_nodes(self):
        """Get number of ndoes.

        Returns
        -------
        val : integer
            Number of nodes
        """
        return self._num_nodes

    def get_node_keys(self):
        """Get number of users.

        Returns
        -------
        val : dictionary
            Node keys dictionary for mapping osmnx index to list index
        """
        return self._node_keys
