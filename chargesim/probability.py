################################################################################
# Probability Class                                                                   #
#                                                                              #
"""Class defines a probability object."""
################################################################################


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
