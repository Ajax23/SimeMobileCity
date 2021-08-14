################################################################################
# User Class                                                                   #
#                                                                              #
"""Class defining user types."""
################################################################################


class User:
    """This class defines a user.

    Parameters
    ----------
    probability : dictionary, optional
        Dictionary containing leave probabilities for each day - if empty, all
        hours have the same probability
    ident : string, optional
        Optional user name
    """
    def __init__(self, probability={}, ident=""):
        # Process input
        self._ident = ident
        self._p = probability
        if not self._p:
            for day in range(7):
                self._p[day] = {}
                for hour in range(24):
                    self._p[day][hour] = 1/7


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

    def set_ident(self, val):
        """Set user name.

        Parameters
        ----------
        val : string
            User name
        """
        self._ident = val


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

    def get_ident(self):
        """Return user name.

        Returns
        -------
        val : string
            User name
        """
        return self._ident
