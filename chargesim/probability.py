################################################################################
# Probability Class                                                                   #
#                                                                              #
"""Class defines a probability object."""
################################################################################


class P:
    """This class defines a probability object.

    Parameters
    ----------
    p : dictionary, optional
        Dictionary containing leave probabilities for each day - if empty, all
        hours have the same probability
    base : float, optional
        if probability dictionary is not give, probability list will be generated
        with given value for each hour
    """
    def __init__(self, p={}, base=1/7):
        # Process input
        self._p = p if p else {day: {hour: base for hour in range(24)} for day in range(7)}


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