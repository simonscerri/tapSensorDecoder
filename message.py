"""
This is the base message class for the Connit decoder
All messages have to be first created as this object to decode common fields X, Y and Z
X is used to determine the message type which is why this needs to be decoded before the
  final message object can be created.

Contains properties unique to all Message types and a factory method to create the correct object type.
"""

__author__ = 'simon.scerri-taylor'

from decoders import byte


class Message(object):
    def _convert_to_bytes(self, seq):
        """A generator to divide a hex string into byte objects.
        Parameters
        ----------
        :param seq: string
            String containing the sequence to be chunked up

        Returns
        -------
        :rtype : object
            A byte object representing the current byte of the sequence
        """

        while seq:
            yield byte.Byte(int(seq[:2], 16))
            seq = seq[2:]

    def __init__(self, raw_message):
        """The Init class for Message that decodes the incoming string
        Parameters
        ----------
        :param raw_message: string
            Contains the original SIGFOX message as a string

        Returns
        -------

        """
        # Set up our byte array list
        self._byte_array = list(self._convert_to_bytes(raw_message))

    @property
    def message_array(self):
        """
        :return:
        List: the byte array of the original raw message
        """
        return self._byte_array

    @property
    def x(self):
        """
        :return:
        Int: X is easy, it's just the first nibble
        """
        return int(self._byte_array[0].high_nibble, 2)

    @property
    def y(self):
        """
        :return:
        Int: Y is the second nibble divided by two
        """
        return int(self._byte_array[0].low_nibble, 2) / 2

    @property
    def z(self):
        """
        :return:
        Bool: Z depends on if that second nibble is odd or even
        """
        if (int(self._byte_array[0].low_nibble, 2) % 2) == 0:  # Check for an even number
            return False
        else:
            return True

    @property
    def message_type(self):
        """
        :return:
        Str: A human readable text of the message type
        """
        if self.x == 0:
            return "AppInit"
        elif self.x == 1:
            return "AppData"
        elif self.x == 2:
            return "Event"
        elif self.x == 3:
            return "Config"
        else:
            return "Unknown"

    @staticmethod
    def factory(raw_message, device_type, proto_ver=0):
        """The factory class for Message.  It's purpose in life is to return the correct decoder subclass object
        Parameters
        ----------
        :param raw_message: string
            Contains the original SIGFOX message as a string

        :param device_type: string
            A string identifying the sending device type

        :param proto_ver: int
            A integer representing the version of the Connit protocol in use
            Defaults to 0

        Returns
        -------
        :rtype :object
            Returns an object of the appropriate subclass to decode the incoming message
        """
        # import our subclasses from the relevant modules
        if proto_ver == 0:
            from decoders.event import LiveBlackOneEvent, LivePulseBlueEvent
            from decoders.config import LiveBluePulseConfig, LiveBlackOneConfig
            from decoders.app_data import LivePulseBlueAppData
            from decoders.app_init import LiveBlackOneAppInit, LivePulseBlueAppInit
            # The first character (technically the first nibble) of the message defines the message type so grab that
            message_flag = int(raw_message[:1])
            # Do your factory thing
            if message_flag == 0:
                # This is an App Init message
                # This is an Event message
                if device_type == "LPB":
                    return LivePulseBlueAppInit(raw_message)
                elif device_type == "LBO":
                    return LiveBlackOneAppInit(raw_message)
                else:
                    # Some error handling to do with invalid device types here
                    pass
            elif message_flag == 1:
                # This is a App Data message
                return LivePulseBlueAppData(raw_message)
            elif message_flag == 2:
                # This is an Event message
                if device_type == "LPB":
                    return LivePulseBlueEvent(raw_message)
                elif device_type == "LBO":
                    return LiveBlackOneEvent(raw_message)
                else:
                    # Some error handling to do with invalid device types here
                    pass
            elif message_flag == 3:
                # This is a Config message
                if device_type == "LPB":
                    return LiveBluePulseConfig(raw_message)
                elif device_type == "LBO":
                    return LiveBlackOneConfig(raw_message)
                else:
                    # Some error handling to do with invalid device types here
                    pass
        else:
            # Some error handling to do with unknown protocol should occur here
            pass