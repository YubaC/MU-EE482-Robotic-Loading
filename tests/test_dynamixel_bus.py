"""Offline transport checks: no hardware access."""
import unittest
from unittest.mock import Mock, patch
from src.dynamixel_bus import DynamixelBus, CommunicationError, DeviceError


class BusTests(unittest.TestCase):
    def setUp(self):
        self.port = Mock(is_open=False)
        self.packet = Mock()
        self.port.setBaudRate.side_effect = self.open_port
        self.port.closePort.side_effect = lambda: setattr(self.port, 'is_open', False)
        self.port_patch = patch('src.dynamixel_bus.PortHandler', return_value=self.port)
        self.packet_patch = patch('src.dynamixel_bus.PacketHandler', return_value=self.packet)
        self.port_patch.start()
        self.packet_patch.start()
        self.addCleanup(self.port_patch.stop)
        self.addCleanup(self.packet_patch.stop)
        self.bus = DynamixelBus('FAKE')

    def open_port(self, baud):
        self.port.is_open = True
        return True

    def test_signed_feedback_and_write_encoding(self):
        with self.bus:
            self.packet.read2ByteTxRx.return_value = (65535, 0, 0)
            self.packet.read4ByteTxRx.return_value = (2147483648, 0, 0)
            self.assertEqual(self.bus.read(15, 126, 2, signed=True), -1)
            self.assertEqual(self.bus.read(11, 132, 4, signed=True), -2147483648)
            self.assertEqual(self.bus.read(15, 126, 2), 65535)
            self.packet.write2ByteTxRx.return_value = (0, 0)
            self.bus.write(15, 102, 2, -50, signed=True)
            self.packet.write2ByteTxRx.assert_called_once_with(self.port, 15, 102, 65486)

    def test_write_timeout_is_not_retried(self):
        with self.bus:
            self.packet.write4ByteTxRx.return_value = (-3001, 0)
            with self.assertRaises(CommunicationError) as caught:
                self.bus.write(11, 116, 4, 299)
            self.assertEqual(caught.exception.address, 116)
            self.packet.write4ByteTxRx.assert_called_once()

    def test_device_error_is_distinct(self):
        with self.bus:
            self.packet.read1ByteTxRx.return_value = (0, 0, 128)
            with self.assertRaises(DeviceError):
                self.bus.read(11, 70, 1)

    def test_invalid_requests_do_not_reach_sdk(self):
        with self.bus:
            for value in (-1, 256):
                with self.assertRaises(ValueError):
                    self.bus.write(11, 64, 1, value)
            with self.assertRaises(ValueError):
                self.bus.read(254, 132, 4)
            self.packet.assert_not_called()
            self.assertEqual(self.packet.method_calls, [])

    def test_cleanup_on_exception_never_changes_torque(self):
        with self.assertRaises(RuntimeError):
            with self.bus:
                raise RuntimeError('application failure')
        self.assertFalse(self.bus.is_open)
        self.port.closePort.assert_called_once()
        self.assertEqual(self.packet.method_calls, [])


if __name__ == '__main__':
    unittest.main()
