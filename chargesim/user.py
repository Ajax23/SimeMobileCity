################################################################################
# User Class                                                                   #
#                                                                              #
"""Class defining user types."""
################################################################################


from chargesim.probability import P


class User(P):
    """This class defines a user.

    Parameters
    ----------
    p : dictionary, float
        Probability each hour each weekday, either a float for the same
        probability each hour, dictionary of hours for same hour distribution
        for all days, a dictionary of days for the same hour probability for
        different days, or a dictionary of days each with a dictionary of hours
    ident : string, optional
        Optional user name
    """
    def __init__(self, p, ident=""):
        # Call super class
        super(User, self).__init__(p)

        # Process input
        self._ident = ident


    ##################
    # Setter Methods #
    ##################
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
    def get_ident(self):
        """Return user name.

        Returns
        -------
        val : string
            User name
        """
        return self._ident
