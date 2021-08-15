################################################################################
# Car Class                                                                    #
#                                                                              #
"""Class defining car types."""
################################################################################


class Car:
    """This class defines a car.

    Parameters
    ----------
    size : float
        Battery size in kWh
    ident : string, optional
        Optional car name
    """
    def __init__(self, size, ident=""):
        # Process input
        self._size = size
        self._ident = ident


    ##################
    # Setter Methods #
    ##################
    def set_size(self, val):
        """Set battery size.

        Parameters
        ----------
        val : float
            Battery size in kWh
        """
        self._size = val

    def set_ident(self, val):
        """Set car name.

        Parameters
        ----------
        val : string
            Car name
        """
        self._ident = val


    ##################
    # Getter Methods #
    ##################
    def get_size(self):
        """Return battery size.

        Returns
        -------
        val : float
            battery size in kWh
        """
        return self._size

    def get_ident(self):
        """Return car name.

        Returns
        -------
        val : string
            Car name
        """
        return self._ident
