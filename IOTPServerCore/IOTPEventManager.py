import time

_author_ = "in_soumen"
_date_ = "11-08-2018"


class IOTPEventManager:

    def __init__(self, signals):
        if 0 in signals:
            raise Exception("0 can never be a signal")
        if len(signals) is 0:
            raise Exception("Empty touple is not allowed")
        self.__signals = signals
        self.__all_signals = 0
        self.__info = None
        pass

    " Signal Event, with additional information if required "

    def signal_event(self, signal, info = None):
        if signal in self.__signals:
            self.__all_signals += signal
            self.__info = info


    " Wait for signal -blocking "

    def event_wait(self, signal):
        if signal in self.__signals:
            while True:
                if (self.__all_signals & signal) == signal:
                    break

    " Check for signal -non-blocking "

    def event_check(self, signal):
        if signal in self.__signals:
            return (self.__all_signals & signal) == signal
        return False

    " Clear all events "

    def clear(self):
        self.__all_signals = 0

    " Get extrs information for the host "
    def get_event_extras(self):
        return self.__info
