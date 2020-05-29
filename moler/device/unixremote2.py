# -*- coding: utf-8 -*-
"""
Moler's device has 2 main responsibilities:
- be the factory that returns commands of that device
- be the state machine that controls which commands may run in given state
"""

__author__ = 'Grzegorz Latuszek, Marcin Usielski, Michal Ernst'
__copyright__ = 'Copyright (C) 2018-2019, Nokia'
__email__ = 'grzegorz.latuszek@nokia.com, marcin.usielski@nokia.com, michal.ernst@nokia.com'

from moler.device.textualdevice import TextualDevice
from moler.device.unixlocal import UnixLocal
from moler.device.proxy_pc2 import ProxyPc2, PROXY_PC
from moler.helpers import call_base_class_method_with_same_name, mark_to_call_base_class_method_with_same_name


# helper variables to improve readability of state machines
# f.ex. moler.device.textualdevice introduces state TextualDevice.not_connected = "NOT_CONNECTED"
NOT_CONNECTED = TextualDevice.not_connected
CONNECTION_HOPS = TextualDevice.connection_hops
UNIX_LOCAL = UnixLocal.unix_local
UNIX_LOCAL_ROOT = UnixLocal.unix_local_root
UNIX_REMOTE = "UNIX_REMOTE"
UNIX_REMOTE_ROOT = "UNIX_REMOTE_ROOT"


@call_base_class_method_with_same_name
class UnixRemote2(ProxyPc2):
    r"""
    UnixRemote2 device class.

    Example of device in yaml configuration file:
    - with PROXY_PC and io "terminal":
      UNIX_1:
       DEVICE_CLASS: moler.device.unixremote2.UnixRemote2
       CONNECTION_HOPS:
         PROXY_PC:
           UNIX_REMOTE:
             execute_command: ssh # default value
             command_params:
               expected_prompt: unix_remote_prompt
               host: host_ip
               login: login
               password: password
         UNIX_REMOTE:
           PROXY_PC:
             execute_command: exit # default value
             command_params:
               expected_prompt: proxy_pc_prompt
         UNIX_LOCAL:
           PROXY_PC:
             execute_command: ssh # default value
             command_params:
               expected_prompt: proxy_pc_prompt
               host: host_ip
               login: login
               password: password

    - with PROXY_PC and remote-access-io like "sshshell":
      UNIX_1:
       DEVICE_CLASS: moler.device.unixremote2.UnixRemote2
       CONNECTION_DESC:
         io_type: sshshell
         host: host_ip
         username: login
         password: password
       CONNECTION_HOPS:
         PROXY_PC:
           UNIX_REMOTE:
             execute_command: ssh # default value
             command_params:
               expected_prompt: unix_remote_prompt
               host: host_ip
               login: login
               password: password
         UNIX_REMOTE:
           PROXY_PC:
             execute_command: exit # default value
             command_params:
               expected_prompt: proxy_pc_prompt

    -without PROXY_PC and io "terminal":
      UNIX_1:
       DEVICE_CLASS: moler.device.unixremote2.UnixRemote2
       CONNECTION_HOPS:
         UNIX_LOCAL:
           UNIX_REMOTE:
             execute_command: ssh # default value
             command_params:
               expected_prompt: unix_remote_prompt
               host: host_ip
               login: login
               password: password

    -without PROXY_PC and remote-access-io like "sshshell":
      UNIX_1:
       DEVICE_CLASS: moler.device.unixremote2.UnixRemote2
       CONNECTION_DESC:
         io_type: sshshell
         host: host_ip
         username: login
         password: password
       (no need for CONNECTION_HOPS since we jump directly from NOT_CONNECTED to UNIX_REMOTE using sshshell)
    """
    def __init__(self, sm_params, name=None, io_connection=None, io_type=None, variant=None, io_constructor_kwargs=None,
                 initial_state=None):
        """
        Create Unix device communicating over io_connection
        :param sm_params: dict with parameters of state machine for device
        :param name: name of device
        :param io_connection: External-IO connection having embedded moler-connection
        :param io_type: type of connection - tcp, udp, ssh, telnet, ...
        :param variant: connection implementation variant, ex. 'threaded', 'twisted', 'asyncio', ...
                        (if not given then default one is taken)
        :param io_constructor_kwargs: additional parameter into constructor of selected connection type
                        (if not given then default one is taken)
        :param initial_state: name of initial state. State machine tries to enter this state just after creation.
        """
        initial_state = initial_state if initial_state is not None else UNIX_REMOTE
        super(UnixRemote2, self).__init__(name=name, io_connection=io_connection,
                                          io_type=io_type, variant=variant,
                                          io_constructor_kwargs=io_constructor_kwargs,
                                          sm_params=sm_params, initial_state=initial_state)

    @mark_to_call_base_class_method_with_same_name
    def _get_default_sm_configuration_with_proxy_pc(self):
        """
        Return State Machine default configuration with proxy_pc state.
        :return: default sm configuration with proxy_pc state.
        """
        config = {
            CONNECTION_HOPS: {
                PROXY_PC: {  # from
                    UNIX_REMOTE: {  # to
                        "execute_command": "ssh",  # using command
                        "command_params": {  # with parameters
                            "target_newline": "\n"
                        },
                        "required_command_params": [
                            "host",
                            "login",
                            "password",
                            "expected_prompt"
                        ]
                    },
                },
                UNIX_REMOTE: {  # from
                    PROXY_PC: {  # to
                        "execute_command": "exit",  # using command
                        "command_params": {  # with parameters
                            "target_newline": "\n"
                        },
                        "required_command_params": [
                            "expected_prompt"
                        ]
                    },
                    UNIX_REMOTE_ROOT: {  # to
                        "execute_command": "su",  # using command
                        "command_params": {  # with parameters
                            "password": "root_password",
                            "expected_prompt": r'remote_root_prompt',
                            "target_newline": "\n"
                        },
                        "required_command_params": [
                        ]
                    },
                },
                UNIX_REMOTE_ROOT: {  # from
                    UNIX_REMOTE: {  # to
                        "execute_command": "exit",  # using command
                        "command_params": {  # with parameters
                            "target_newline": "\n",
                            "expected_prompt": r'remote_user_prompt'
                        },
                        "required_command_params": [
                        ]
                    }
                }
            }
        }
        return config

    @mark_to_call_base_class_method_with_same_name
    def _get_default_sm_configuration_without_proxy_pc(self):
        """
        Return State Machine default configuration without proxy_pc state.
        :return: default sm configuration without proxy_pc state.
        """
        config = {
            CONNECTION_HOPS: {
                UNIX_LOCAL: {  # from
                    UNIX_REMOTE: {  # to
                        "execute_command": "ssh",  # using command
                        "command_params": {  # with parameters
                            "target_newline": "\n"
                        },
                        "required_command_params": [
                            "host",
                            "login",
                            "password",
                            "expected_prompt"
                        ]
                    },
                },
                UNIX_REMOTE: {  # from
                    UNIX_LOCAL: {  # to
                        "execute_command": "exit",  # using command
                        "command_params": {  # with parameters
                            "expected_prompt": r'^moler_bash#',
                            "target_newline": "\n"
                        },
                        "required_command_params": [
                        ]
                    },
                    UNIX_REMOTE_ROOT: {  # to
                        "execute_command": "su",  # using command
                        "command_params": {  # with parameters
                            "password": "root_password",
                            "expected_prompt": r'remote_root_prompt',
                            "target_newline": "\n"
                        },
                        "required_command_params": [
                        ]
                    },
                },
                UNIX_REMOTE_ROOT: {  # from
                    UNIX_REMOTE: {  # to
                        "execute_command": "exit",  # using command
                        "command_params": {  # with parameters
                            "expected_prompt": r'remote_user_prompt',
                            "target_newline": "\n"
                        },
                        "required_command_params": [
                        ]
                    },
                }
            }
        }
        return config

    @mark_to_call_base_class_method_with_same_name
    def _prepare_transitions_with_proxy_pc(self):
        """
        Prepare transitions to change states with proxy_pc state.
        :return: transitions with proxy_pc state.
        """
        transitions = {
            PROXY_PC: {
                UNIX_REMOTE: {
                    "action": [
                        "_execute_command_to_change_state"
                    ],
                }
            },
            UNIX_REMOTE: {
                PROXY_PC: {
                    "action": [
                        "_execute_command_to_change_state"
                    ],
                },
                UNIX_REMOTE_ROOT: {
                    "action": [
                        "_execute_command_to_change_state"
                    ],
                }
            },
            UNIX_REMOTE_ROOT: {
                UNIX_REMOTE: {
                    "action": [
                        "_execute_command_to_change_state"
                    ],
                }
            }
        }
        return transitions

    @mark_to_call_base_class_method_with_same_name
    def _prepare_transitions_without_proxy_pc(self):
        """
        Prepare transitions to change states without proxy_pc state.
        :return: transitions without proxy_pc state.
        """
        transitions = {
            UNIX_REMOTE: {
                UNIX_LOCAL: {
                    "action": [
                        "_execute_command_to_change_state"
                    ],
                },
                UNIX_REMOTE_ROOT: {
                    "action": [
                        "_execute_command_to_change_state"
                    ],
                }
            },
            UNIX_LOCAL: {
                UNIX_REMOTE: {
                    "action": [
                        "_execute_command_to_change_state"
                    ],
                }
            },
            UNIX_REMOTE_ROOT: {
                UNIX_REMOTE: {
                    "action": [
                        "_execute_command_to_change_state"
                    ],
                }
            }
        }
        return transitions

    @mark_to_call_base_class_method_with_same_name
    def _prepare_state_prompts_with_proxy_pc(self):
        """
        Prepare textual prompt for each state for State Machine with proxy_pc state.
        :return: textual prompt for each state with proxy_pc state.
        """
        hops_cfg = self._configurations[CONNECTION_HOPS]
        state_prompts = {
            UNIX_REMOTE:
                hops_cfg[PROXY_PC][UNIX_REMOTE]["command_params"]["expected_prompt"],
            UNIX_REMOTE_ROOT:
                hops_cfg[UNIX_REMOTE][UNIX_REMOTE_ROOT]["command_params"]["expected_prompt"],
        }
        return state_prompts

    @mark_to_call_base_class_method_with_same_name
    def _prepare_state_prompts_without_proxy_pc(self):
        """
        Prepare textual prompt for each state for State Machine without proxy_pc state.
        :return: textual prompt for each state without proxy_pc state.
        """
        hops_cfg = self._configurations[CONNECTION_HOPS]
        state_prompts = {
            UNIX_REMOTE:
                hops_cfg[UNIX_LOCAL][UNIX_REMOTE]["command_params"]["expected_prompt"],
            UNIX_REMOTE_ROOT:
                hops_cfg[UNIX_REMOTE][UNIX_REMOTE_ROOT]["command_params"]["expected_prompt"],
            UNIX_LOCAL:
                hops_cfg[UNIX_REMOTE][UNIX_LOCAL]["command_params"]["expected_prompt"],
        }
        return state_prompts

    @mark_to_call_base_class_method_with_same_name
    def _prepare_newline_chars_with_proxy_pc(self):
        """
        Prepare newline char for each state for State Machine with proxy_pc state.
        :return: newline char for each state with proxy_pc state.
        """
        hops_cfg = self._configurations[CONNECTION_HOPS]
        newline_chars = {
            UNIX_REMOTE:
                hops_cfg[PROXY_PC][UNIX_REMOTE]["command_params"]["target_newline"],
            UNIX_REMOTE_ROOT:
                hops_cfg[UNIX_REMOTE][UNIX_REMOTE_ROOT]["command_params"]["target_newline"],
        }
        return newline_chars

    @mark_to_call_base_class_method_with_same_name
    def _prepare_newline_chars_without_proxy_pc(self):
        """
        Prepare newline char for each state for State Machine without proxy_pc state.
        :return: newline char for each state without proxy_pc state.
        """
        hops_cfg = self._configurations[CONNECTION_HOPS]
        newline_chars = {
            UNIX_REMOTE:
                hops_cfg[UNIX_LOCAL][UNIX_REMOTE]["command_params"]["target_newline"],
            UNIX_LOCAL:
                hops_cfg[UNIX_REMOTE][UNIX_LOCAL]["command_params"]["target_newline"],
            UNIX_REMOTE_ROOT:
                hops_cfg[UNIX_REMOTE][UNIX_REMOTE_ROOT]["command_params"]["target_newline"],
        }
        return newline_chars

    @mark_to_call_base_class_method_with_same_name
    def _prepare_state_hops_with_proxy_pc(self):
        """
        Prepare non direct transitions for each state for State Machine with proxy_pc state.
        :return: non direct transitions for each state with proxy_pc state.
        """
        state_hops = {
            NOT_CONNECTED: {
                UNIX_REMOTE: UNIX_LOCAL,
                PROXY_PC: UNIX_LOCAL,
                UNIX_LOCAL_ROOT: UNIX_LOCAL,
                UNIX_REMOTE_ROOT: UNIX_LOCAL
            },
            UNIX_REMOTE: {
                NOT_CONNECTED: PROXY_PC,
                UNIX_LOCAL: PROXY_PC,
                UNIX_LOCAL_ROOT: PROXY_PC
            },
            UNIX_LOCAL_ROOT: {
                UNIX_REMOTE: UNIX_LOCAL,
                UNIX_REMOTE_ROOT: UNIX_LOCAL
            },
            PROXY_PC: {
                NOT_CONNECTED: UNIX_LOCAL,
                UNIX_LOCAL_ROOT: UNIX_LOCAL,
                UNIX_REMOTE_ROOT: UNIX_REMOTE
            },
            UNIX_LOCAL: {
                UNIX_REMOTE: PROXY_PC,
                UNIX_REMOTE_ROOT: PROXY_PC
            },
            UNIX_REMOTE_ROOT: {
                NOT_CONNECTED: UNIX_REMOTE,
                UNIX_LOCAL: UNIX_REMOTE,
                UNIX_LOCAL_ROOT: UNIX_REMOTE,
                PROXY_PC: UNIX_REMOTE,
            }
        }
        return state_hops

    @mark_to_call_base_class_method_with_same_name
    def _prepare_state_hops_without_proxy_pc(self):
        """
        Prepare non direct transitions for each state for State Machine without proxy_pc state.
        :return: non direct transitions for each state without proxy_pc state.
        """
        state_hops = {
            NOT_CONNECTED: {
                UNIX_REMOTE: UNIX_LOCAL,
                UNIX_LOCAL_ROOT: UNIX_LOCAL,
                UNIX_REMOTE_ROOT: UNIX_LOCAL,
            },
            UNIX_LOCAL: {
                UNIX_REMOTE_ROOT: UNIX_REMOTE
            },
            UNIX_LOCAL_ROOT: {
                UNIX_REMOTE: UNIX_LOCAL,
                UNIX_REMOTE_ROOT: UNIX_LOCAL
            },
            UNIX_REMOTE: {
                NOT_CONNECTED: UNIX_LOCAL,
                UNIX_LOCAL_ROOT: UNIX_LOCAL
            },
            UNIX_REMOTE_ROOT: {
                NOT_CONNECTED: UNIX_REMOTE,
                UNIX_LOCAL: UNIX_REMOTE,
                UNIX_LOCAL_ROOT: UNIX_REMOTE,
                PROXY_PC: UNIX_REMOTE,
            }
        }
        return state_hops

    def _configure_state_machine(self, sm_params):
        """
        Configure device State Machine.
        :param sm_params: dict with parameters of state machine for device.
        :return: Nothing.
        """
        super(UnixRemote2, self)._configure_state_machine(sm_params)

        hops_cfg = self._configurations[CONNECTION_HOPS]
        if self._use_proxy_pc:
            hops_cfg[UNIX_REMOTE_ROOT][UNIX_REMOTE]["command_params"]["expected_prompt"] = \
                hops_cfg[PROXY_PC][UNIX_REMOTE]["command_params"]["expected_prompt"]
        else:
            hops_cfg[UNIX_REMOTE_ROOT][UNIX_REMOTE]["command_params"]["expected_prompt"] = \
                hops_cfg[UNIX_LOCAL][UNIX_REMOTE]["command_params"]["expected_prompt"]

    def _get_packages_for_state(self, state, observer):
        """
        Get available packages contain cmds and events for each state.
        :param state: device state.
        :param observer: observer type, available: cmd, events
        :return: available cmds or events for specific device state.
        """
        available = super(UnixRemote2, self)._get_packages_for_state(state, observer)

        if not available:
            if state == UNIX_REMOTE or state == UNIX_REMOTE_ROOT:
                available = {UnixRemote2.cmds: ['moler.cmd.unix'],
                             UnixRemote2.events: ['moler.events.shared', 'moler.events.unix']}
            if available:
                return available[observer]

        return available
