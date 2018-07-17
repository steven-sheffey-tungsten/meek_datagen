import logging
import os
from pathlib import Path
import typing

from stem import process as stem_process

class Proxy():
    def __init__(self, config, tbb_path):
        # Get the logger
        self.logger = logging.getLogger(config["log"]["name"])
        # Get mode from the config
        self.mode = config["mode"]
        # Only do proxy config in tor mode
        if self.mode == "tor":
            self.tor_init(config, tbb_path)
    def tor_init(self, config, tbb_path):
        """
        Constructor for the proxy when the mode is tor
        """
        # Take path to tor browser bundle
        # self.tbb_path = Path(config["tor"]["tbb_path"])
        self.tbb_path = tbb_path
        # Get path to tor folder
        tor_path = tbb_path / "Browser" / "TorBrowser" / "Tor"
        # Path to the tor daemon
        self.tor_executable_path = str(tor_path / "tor")
        # Meek client
        meek_client_path = tor_path / "PluggableTransports" / "meek-client"
        # Meek client helper
        meek_client_tb_path = tor_path / "PluggableTransports" / "meek-client-torbrowser"
        # Set the bridge
        # Build the config
        self.tor_config = {
            "UseBridges": "1",
            "ClientTransportPlugin": "meek exec {} --log helper.log -- {} --log meek.log".format(
                meek_client_tb_path.absolute(),
                meek_client_path.absolute()
            ),
            "Bridge": config["tor"]["bridge"],
            'Log': [
              'NOTICE stdout',
              'ERR file /tmp/tor_error_log',
            ]
        }
        # Set environment to use tor directory for dynamic libs
        if "LD_LIBRARY_PATH" in os.environ:
            os.environ["LD_LIBRARY_PATH"] = os.environ["LD_LIBRARY_PATH"] + ":" + str(tor_path)
        else: 
            os.environ["LD_LIBRARY_PATH"] = str(tor_path)
        # No tor process on construction
        self.tor_process = None
        # Whether tor has not already been started once
        self.first_run = True
        # Store the timeouts
        self.tor_timeouts = config["tor"]["timeout"]

    def __enter__(self):
        """
        Run at the beginning of `with`

        Starts tor
        """
        # Start tor
        if self.mode == "tor":
            # Calculate the timeout based on which run
            # If the first run flag is set, unset it
            timeout = None
            if self.first_run:
                timeout = self.tor_timeouts["initial"]
                self.first_run = False
            else:
                timeout = self.tor_timeouts["regular"]
            # Launch the tor process
            self.tor_process = stem_process.launch_tor_with_config(
                config = self.tor_config,
                tor_cmd = self.tor_executable_path,
                timeout = timeout,
                take_ownership = True,
                # init_msg_handler = print
            )
        # Return nothing
        return self
    def __exit__(self, typ, value, traceback):
        """
        Run at the end of `with`

        Kills tor
        """
        if self.mode == "tor":
            if self.tor_process is None:
                self.logger.warn("Cannot kill tor process that does not exist")
            else:
                # Kill tor
                self.tor_process.kill()
                # Clear the process variable
                self.tor_process = None

class NullProxy():
    def __init__(self):
        pass
    def __enter__(self):
        pass
    def __exit__(self, typ, value, traceback):
        pass
