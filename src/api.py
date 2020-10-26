import abc


class CoffeeMakerApi(abc.ABC):
    WARMER_EMPTY = 0
    POT_EMPTY = 1
    POT_NOT_EMPTY = 2

    @property
    @abc.abstractmethod
    def warmer_plate_status(self) -> int:
        """
        This function returns the status of the warmer-plate
        sensor. This sensor detects the presence of the pot
        and whether it has coffee in it.
        """
        pass

    BOILER_EMPTY = 0
    BOILER_NOT_EMPTY = 1

    @property
    @abc.abstractmethod
    def boiler_status(self) -> int:
        """
        This function returns the status of the boiler switch.
        The boiler switch is a float switch that detects if
        there is more than 1/2 cup of water in the boiler.
        """
        pass

    BREW_BUTTON_PUSHED = 0
    BREW_BUTTON_NOT_PUSHED = 1

    @property
    @abc.abstractmethod
    def brew_button_status(self) -> int:
        """
        This function returns the status of the brew button.
        The brew button is a momentary switch that remembers
        its state. Each call to this function returns the
        remembered state and then resets that state to
        BREW_BUTTON_NOT_PUSHED.

        Thus, even if this function is polled at a very slow
        rate, it will still detect when the brew button is
        pushed.
        """
        pass

    BOILER_ON = 0
    BOILER_OFF = 1

    @abc.abstractmethod
    def set_boiler_state(self, boiler_status: int):
        """
        This function turns the heating element in the boiler
        on or off.
        """
        pass

    WARMER_ON = 0
    WARMER_OFF = 1

    @abc.abstractmethod
    def set_warmer_state(self, warmer_state: int):
        """
        This function turns the heating element in the warmer
        plate on or off.
        """
        pass

    INDICATOR_ON = 0
    INDICATOR_OFF = 1

    @abc.abstractmethod
    def set_indicator_state(self, indicator_state: int):
        """
        This function turns the indicator light on or off.
        The indicator light should be turned on at the end
        of the brewing cycle. It should be turned off when
        the user presses the brew button.
        """
        pass

    VALVE_OPEN = 0
    VALVE_CLOSED = 1

    @abc.abstractmethod
    def set_relief_valve_state(self, relief_valve_state: int):
        """
        This function opens and closes the pressure-relief
        valve. When this valve is closed, steam pressure in
        the boiler will force hot water to spray out over
        the coffee filter. When the valve is open, the steam
        in the boiler escapes into the environment, and the
        water in the boiler will not spray out over the filter.
        """
        pass
