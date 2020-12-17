import abc
import time
from dataclasses import dataclass
from datetime import timedelta
from typing import List

from src.api import CoffeeMakerApi


class IObserver(abc.ABC):
    @abc.abstractmethod
    def on_observe(self, new_status: int):
        pass


class IStatusPublisher(abc.ABC):
    def __init__(self, observers: List[IObserver]):
        self._observers = observers

    def check_status(self):
        new_status = self._get_status()
        for o in self._observers:
            o.on_observe(new_status)

    def add_observer(self, observer: IObserver):
        self._observers.append(observer)

    @abc.abstractmethod
    def _get_status(self) -> int:
        pass


class WarmerPlateSensor(IStatusPublisher):
    def __init__(self, observers: List[IObserver], api: CoffeeMakerApi):
        super().__init__(observers)
        self._api = api

    def _get_status(self) -> int:
        return self._api.warmer_plate_status

    @property
    def pot_present(self) -> bool:
        return self._get_status() != self._api.WARMER_EMPTY


class BoilerSensor(IStatusPublisher):
    def __init__(self, observers: List[IObserver], api: CoffeeMakerApi):
        super().__init__(observers)
        self._api = api

    def _get_status(self) -> int:
        return self._api.boiler_status

    @property
    def is_empty(self) -> bool:
        return self._get_status() == self._api.BOILER_EMPTY


class ButtonSensor(IStatusPublisher):
    def __init__(self, observers: List[IObserver], api: CoffeeMakerApi):
        super().__init__(observers)
        self._api = api

    def _get_status(self) -> int:
        return self._api.brew_button_status


class WarmerPlate:
    def __init__(self, api: CoffeeMakerApi):
        self._api = api

    def on_observe_warmer_plate(self, new_status: int):
        if new_status == self._api.POT_NOT_EMPTY:
            self.turn_on()
        else:
            self.turn_off()

    def turn_on(self):
        self._api.set_warmer_state(self._api.WARMER_ON)

    def turn_off(self):
        self._api.set_warmer_state(self._api.WARMER_OFF)


@dataclass
class WarmerPlateObserver(IObserver):
    warmer_plate: WarmerPlate

    def on_observe(self, new_status: int):
        self.warmer_plate.on_observe_warmer_plate(new_status)


class Valve:
    def __init__(self, api: CoffeeMakerApi):
        self._api = api

    def open(self):
        self._api.set_relief_valve_state(self._api.VALVE_OPEN)

    def close(self):
        self._api.set_relief_valve_state(self._api.VALVE_CLOSED)


@dataclass
class WarmerPlateStatusValveObserver(IObserver):
    valve: Valve

    def on_observe(self, new_status: int):
        if new_status == CoffeeMakerApi.WARMER_EMPTY:
            self.valve.open()
        else:
            self.valve.close()


class Boiler:
    def __init__(
        self, api: CoffeeMakerApi, boiler_sensor: BoilerSensor, warmer_plate_sensor: WarmerPlateSensor, valve: Valve
    ):
        self._api = api
        self._boiler_sensor = boiler_sensor
        self._warmer_plate_sensor = warmer_plate_sensor
        self._valve = valve

        self._is_on = False

    def turn_on(self):
        can_turn_on = not self._boiler_sensor.is_empty and self._warmer_plate_sensor.pot_present
        if can_turn_on:
            self._valve.close()
            self._api.set_boiler_state(self._api.BOILER_ON)
            self._is_on = True

    def turn_off(self):
        self._api.set_boiler_state(self._api.BOILER_OFF)
        self._is_on = False

    @property
    def is_on(self) -> bool:
        return self._is_on


@dataclass
class BoilerSensorObserver(IObserver):
    boiler: Boiler

    def on_observe(self, new_status: int):
        if new_status == CoffeeMakerApi.BOILER_EMPTY:
            self.boiler.turn_off()


@dataclass
class BoilerButtonStatusObserver(IObserver):
    boiler: Boiler

    def on_observe(self, new_status: int):
        if new_status == CoffeeMakerApi.BREW_BUTTON_PUSHED:
            self.boiler.turn_on()


class IndicatorLight:
    def __init__(self, api: CoffeeMakerApi):
        self._api = api

    def _turn_on(self):
        self._api.set_indicator_state(self._api.INDICATOR_ON)

    def _turn_off(self):
        self._api.set_indicator_state(self._api.INDICATOR_OFF)

    def on_warmer_plate_status(self, status: int):
        if status == self._api.POT_NOT_EMPTY:
            self._turn_on()
        else:
            self._turn_off()


@dataclass
class IndicatorLightWarmerPlateObserver(IObserver):
    indicator_light: IndicatorLight

    def on_observe(self, new_status: int):
        self.indicator_light.on_warmer_plate_status(new_status)


def run_event_loop(
    interval: timedelta, publishers: List[IStatusPublisher],
):
    while True:
        for publisher in publishers:
            publisher.check_status()

        time.sleep(interval.total_seconds())


def set_up_and_run(api: CoffeeMakerApi):
    warmer_plate_sensor = WarmerPlateSensor([], api)
    boiler_sensor = BoilerSensor([], api)
    button_sensor = ButtonSensor([], api)

    valve = Valve(api)
    warmer_plate_valve_observer = WarmerPlateStatusValveObserver(valve)
    warmer_plate_sensor.add_observer(warmer_plate_valve_observer)

    boiler = Boiler(api, boiler_sensor=boiler_sensor, warmer_plate_sensor=warmer_plate_sensor, valve=valve)
    boiler_sensor_observer = BoilerSensorObserver(boiler)
    boiler_sensor.add_observer(boiler_sensor_observer)
    boiler_button_status_observer = BoilerButtonStatusObserver(boiler)
    button_sensor.add_observer(boiler_button_status_observer)

    warmer_plate = WarmerPlate(api)
    warmer_plate_sensor.add_observer(WarmerPlateObserver(warmer_plate))

    indicator_light = IndicatorLight(api)
    warmer_plate_sensor.add_observer(IndicatorLightWarmerPlateObserver(indicator_light))

    run_event_loop(timedelta(seconds=1), publishers=[warmer_plate_sensor, boiler_sensor, button_sensor])


if __name__ == "__main__":
    # Assume we're making coffee
    # https://files.meetup.com/10912822/CoffeeMaker.pdf
    set_up_and_run(api)
