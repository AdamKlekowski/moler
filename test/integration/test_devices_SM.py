__author__ = 'Grzegorz Latuszek'
__copyright__ = 'Copyright (C) 2020, Nokia'
__email__ = 'grzegorz.latuszek@nokia.com'

import pytest
from moler.device import DeviceFactory


def test_adb_remote_device(loaded_adb_device_config, alternative_connection_hops):
    adb_remote = DeviceFactory.get_device(name="ADB_LHOST")
    assert adb_remote.current_state == "UNIX_LOCAL"

    # adb_remote = DeviceFactory.get_device(name="ADB_AT_LOCALHOST", initial_state="UNIX_REMOTE",
    #                                       connection_hops=alternative_connection_hops)
    #
    # assert adb_remote.current_state == "PROXY_PC"

    # adb_remote.goto_state("ADB_SHELL")
    # assert adb_remote.current_state == "ADB_SHELL"


def test_proxy_pc_with_sshshell(loaded_proxy_pc_config):
    dev = DeviceFactory.get_device(name="PROXY")
    assert dev.current_state == "PROXY_PC"
    dev.goto_state("NOT_CONNECTED")
    assert dev.current_state == "NOT_CONNECTED"
    dev.remove()


def test_proxy_pc_with_sshshell_cant_use_unix_local_states(loaded_proxy_pc_config):
    with pytest.raises(ValueError) as err:
        DeviceFactory.get_device(name="PROXY", initial_state="UNIX_LOCAL")
    assert "has no UNIX_LOCAL/UNIX_LOCAL_ROOT states" in str(err.value)
    assert "since it uses following io: ThreadedSshShell" in str(err.value)
    assert 'You need io of type "terminal" to have unix-local states' in str(err.value)


def test_proxy_pc_with_terminal_can_use_unix_local_states(loaded_proxy_pc_config, uxlocal2proxypc_connection_hops):
    # check backward compatibility
    dev = DeviceFactory.get_device(name="PROXY",
                                   initial_state="UNIX_LOCAL",
                                   connection_hops=uxlocal2proxypc_connection_hops,
                                   connection_desc={"io_type": "terminal"})
    assert dev.current_state == "UNIX_LOCAL"
    dev.goto_state("PROXY_PC")
    assert dev.current_state == "PROXY_PC"
    dev.goto_state("UNIX_LOCAL")
    assert dev.current_state == "UNIX_LOCAL"
    dev.goto_state("NOT_CONNECTED")
    assert dev.current_state == "NOT_CONNECTED"
    dev.remove()


def test_unix_remote_with_sshshell_only(loaded_unix_remote_config):
    dev = DeviceFactory.get_device(name="UX_REMOTE")
    assert dev.current_state == "UNIX_REMOTE"
    # dev.goto_state("UNIX_REMOTE_ROOT")  # can't test; need to know root password on CI machine
    # assert dev.current_state == "UNIX_REMOTE_ROOT"
    dev.goto_state("NOT_CONNECTED")
    assert dev.current_state == "NOT_CONNECTED"
    dev.remove()


def test_unix_remote_with_sshshell_via_proxy_pc(loaded_unix_remote_config, proxypc2uxremote_connection_hops):
    dev = DeviceFactory.get_device(name="UX_REMOTE", initial_state="PROXY_PC",
                                   connection_desc={'io_type': 'sshshell',
                                                    'host': 'localhost',
                                                    'username': 'sshproxy',
                                                    'password': 'proxy_password'},
                                   connection_hops=proxypc2uxremote_connection_hops)
    assert dev._use_proxy_pc is True
    assert dev.current_state == "PROXY_PC"
    dev.goto_state("UNIX_REMOTE")
    assert dev.current_state == "UNIX_REMOTE"
    # dev.goto_state("UNIX_REMOTE_ROOT")  # can't test; need to know root password on CI machine
    # assert dev.current_state == "UNIX_REMOTE_ROOT"
    dev.goto_state("PROXY_PC")
    assert dev.current_state == "PROXY_PC"
    dev.goto_state("NOT_CONNECTED")
    assert dev.current_state == "NOT_CONNECTED"
    dev.remove()


def test_unix_remote_with_sshshell_cant_use_unix_local_states(loaded_unix_remote_config):
    with pytest.raises(ValueError) as err:
        DeviceFactory.get_device(name="UX_REMOTE", initial_state="UNIX_LOCAL")
    assert "has no UNIX_LOCAL/UNIX_LOCAL_ROOT states" in str(err.value)
    assert "since it uses following io: ThreadedSshShell" in str(err.value)
    assert 'You need io of type "terminal" to have unix-local states' in str(err.value)


def test_unix_remote_with_terminal_can_use_unix_local_states(loaded_unix_remote_config, uxlocal2uxremote_connection_hops):
    # check backward compatibility
    dev = DeviceFactory.get_device(name="UX_REMOTE",
                                   initial_state="UNIX_LOCAL",
                                   connection_hops=uxlocal2uxremote_connection_hops,
                                   connection_desc={"io_type": "terminal"})
    assert dev.current_state == "UNIX_LOCAL"
    dev.goto_state("PROXY_PC")
    assert dev.current_state == "PROXY_PC"
    dev.goto_state("UNIX_REMOTE")
    assert dev.current_state == "UNIX_REMOTE"
    # dev.goto_state("UNIX_REMOTE_ROOT")  # can't test; need to know root password on CI machine
    # assert dev.current_state == "UNIX_REMOTE_ROOT"
    dev.goto_state("PROXY_PC")
    assert dev.current_state == "PROXY_PC"
    dev.goto_state("UNIX_LOCAL")
    assert dev.current_state == "UNIX_LOCAL"
    dev.goto_state("NOT_CONNECTED")
    assert dev.current_state == "NOT_CONNECTED"
    dev.remove()

# ------------------------------------------------------------


@pytest.fixture
def empty_connections_config():
    import mock
    import moler.config.connections as conn_cfg

    default_variant = {"terminal": "threaded", "sshshell": "threaded"}

    with mock.patch.object(conn_cfg, "default_variant", default_variant):
        with mock.patch.object(conn_cfg, "named_connections", {}):
            yield conn_cfg


@pytest.fixture()
def empty_devices_config():
    import mock
    import moler.config.devices as dev_cfg

    empty_named_devices = {}
    default_connection = {"io_type": "terminal", "variant": "threaded"}

    with mock.patch.object(dev_cfg, "named_devices", empty_named_devices):
        with mock.patch.object(dev_cfg, "default_connection", default_connection):
            yield


@pytest.fixture
def empty_devfactory_config():
    import mock
    from moler.device.device import DeviceFactory as dev_factory

    with mock.patch.object(dev_factory, "_devices", {}):
        with mock.patch.object(dev_factory, "_devices_params", {}):
            with mock.patch.object(dev_factory, "_unique_names", {}):
                with mock.patch.object(dev_factory, "_already_used_names", set()):
                    with mock.patch.object(dev_factory, "_was_any_device_deleted", False):
                        yield


@pytest.fixture
def empty_moler_config(empty_connections_config, empty_devices_config, empty_devfactory_config):
    import mock
    import moler.config as moler_cfg

    empty_loaded_config = ["NOT_LOADED_YET"]

    with mock.patch.object(moler_cfg, "loaded_config", empty_loaded_config):
        yield


@pytest.fixture()
def loaded_adb_device_config(empty_moler_config):
    import yaml
    from moler.config import load_device_from_config

    adb_dev_config_yaml = """
    DEVICES:
        ADB_LHOST:
            DEVICE_CLASS: moler.device.adbremote2.AdbRemote2
            INITIAL_STATE: UNIX_LOCAL  # ADB_SHELL
            CONNECTION_DESC:
                io_type: terminal
                #io_type: sshshell
                #host: localhost
                #username: molerssh         # change to login: to have ssh-cmd parity? username jest paramiko
                #password: moler_password
            CONNECTION_HOPS:
                UNIX_LOCAL:
                    UNIX_REMOTE:
                        execute_command: ssh
                        command_params:
                            host: localhost
                            login: molerssh  # openSSH (linux ssh cmd) uzywa -l login_name
                            password: moler_password
                            expected_prompt: '$'
                UNIX_REMOTE:
                    ADB_SHELL:
                        execute_command: adb_shell
                        command_params:
                            serial_number: '1234567890'
    """
    adb_dev_config = yaml.load(adb_dev_config_yaml, Loader=yaml.FullLoader)
    load_device_from_config(adb_dev_config)


@pytest.fixture()
def loaded_proxy_pc_config(empty_moler_config):
    import yaml
    from moler.config import load_device_from_config

    config_yaml = """
    DEVICES:
        PROXY:
            DEVICE_CLASS: moler.device.proxy_pc2.ProxyPc2
            CONNECTION_DESC:
                io_type: sshshell
                host: localhost
                username: sshproxy         # change to login: to have ssh-cmd parity? username is paramiko naming
                password: proxy_password   # openSSH (linux ssh cmd) uses -l login_name
            # no CONNECTION_HOPS since if using sshshell it jumps NOT_CONNECTED -> PROXY_PC
    """
    dev_config = yaml.load(config_yaml, Loader=yaml.FullLoader)
    load_device_from_config(dev_config)


@pytest.fixture()
def loaded_unix_remote_config(empty_moler_config):
    import yaml
    from moler.config import load_device_from_config

    config_yaml = """
    DEVICES:
        UX_REMOTE:
            DEVICE_CLASS: moler.device.unixremote2.UnixRemote2
            CONNECTION_DESC:
                io_type: sshshell
                host: localhost
                username: molerssh
                password: moler_password
            # using sshshell it jumps NOT_CONNECTED -> REMOTE_UNIX
            CONNECTION_HOPS:
                UNIX_REMOTE:
                    UNIX_REMOTE_ROOT:
                        command_params:
                            password: uteadmin #root_passwd
                            expected_prompt: 'root@\S+#'
    """
    dev_config = yaml.load(config_yaml, Loader=yaml.FullLoader)
    load_device_from_config(dev_config)


@pytest.fixture()
def alternative_connection_hops():
    import yaml

    hops_yaml = """
        UNIX_REMOTE:
            ADB_SHELL:
                execute_command: adb_shell
                command_params:
                    serial_number: '1234567890'
    """
    hops = yaml.load(hops_yaml, Loader=yaml.FullLoader)
    return hops


@pytest.fixture()
def uxlocal2proxypc_connection_hops():
    import yaml

    hops_yaml = """
        UNIX_LOCAL:
            PROXY_PC:
                execute_command: ssh
                command_params:
                    host: localhost
                    login: sshproxy
                    password: proxy_password
                    expected_prompt: 'sshproxy@\S+'
    """
    hops = yaml.load(hops_yaml, Loader=yaml.FullLoader)
    return hops


@pytest.fixture()
def proxypc2uxremote_connection_hops():
    import yaml

    hops_yaml = """
        PROXY_PC:
            UNIX_REMOTE:
                execute_command: ssh
                command_params:
                    host: localhost
                    login: molerssh
                    password: moler_password
                    expected_prompt: 'molerssh@\S+'
        UNIX_REMOTE:
            UNIX_REMOTE_ROOT:
                command_params:
                    password: root_passwd
                    expected_prompt: 'root@\S+#'
    """
    hops = yaml.load(hops_yaml, Loader=yaml.FullLoader)
    return hops


@pytest.fixture()
def uxlocal2uxremote_connection_hops(uxlocal2proxypc_connection_hops, proxypc2uxremote_connection_hops):
    hops = uxlocal2proxypc_connection_hops
    hops.update(proxypc2uxremote_connection_hops)
    return hops
