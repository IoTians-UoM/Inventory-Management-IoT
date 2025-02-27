import socket


class NetworkChecker:
    """Class to check if the network is connected."""

    @staticmethod
    def is_connected(host="8.8.8.8", port=53, timeout=3) -> bool:
        """
        Check if the machine is connected to the internet.

        :param host: Host to connect to (default is Google's DNS).
        :param port: Port to connect on (53 is for DNS).
        :param timeout: Timeout for the connection attempt in seconds.
        :return: True if connected, False otherwise.
        """
        try:
            socket.setdefaulttimeout(timeout)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((host, port))
            return True
        except OSError:
            return False