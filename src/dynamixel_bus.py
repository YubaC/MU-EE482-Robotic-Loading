"""DYNAMIXEL Protocol 2.0 transport; no motion policy or implicit torque writes."""
from dynamixel_sdk import COMM_SUCCESS, PacketHandler, PortHandler


class CommunicationError(RuntimeError):
    """The SDK could not complete a request/reply transaction."""

    def __init__(self, operation, servo_id, address, code, message):
        self.operation, self.servo_id, self.address, self.code = operation, servo_id, address, code
        super().__init__(f'{operation}: ID={servo_id}, address={address}, communication={code}: {message}')


class DeviceError(RuntimeError):
    """The actuator returned an error in its Status Packet."""

    def __init__(self, operation, servo_id, address, code, message):
        self.operation, self.servo_id, self.address, self.code = operation, servo_id, address, code
        super().__init__(f'{operation}: ID={servo_id}, address={address}, device={code}: {message}')


class DynamixelBus:
    """Own one serial port. Use sequentially; do not share across threads.

    read/write use byte lengths 1, 2 or 4. Values are raw register integers.
    Writes are not retried. close() releases the port without changing torque.
    """

    def __init__(self, port, baudrate=1000000):
        self._port = PortHandler(port)
        self._packet = PacketHandler(2.0)
        self.baudrate = baudrate

    @property
    def is_open(self):
        return self._port.is_open

    def open(self):
        if not self.is_open:
            try:
                if not self._port.setBaudRate(self.baudrate):
                    raise RuntimeError(f'Unable to open port at {self.baudrate} baud')
            except Exception:
                self.close()
                raise
        return self

    def close(self):
        if self.is_open:
            self._port.closePort()

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc, traceback):
        self.close()

    def _validate(self, servo_id, address=None, size=None):
        if not self.is_open:
            raise RuntimeError('Bus is not open')
        if type(servo_id) is not int or not 0 <= servo_id <= 252:
            raise ValueError('Individual servo ID must be 0..252; broadcast is not supported here')
        if address is not None:
            if type(address) is not int or not 0 <= address <= 65535:
                raise ValueError('Address must be 0..65535')
            if type(size) is not int or size not in (1, 2, 4):
                raise ValueError('Register size must be 1, 2 or 4 bytes')
            if address + size > 65536:
                raise ValueError('Register extends beyond address space')

    def _check(self, operation, servo_id, address, result, error):
        if result != COMM_SUCCESS:
            raise CommunicationError(operation, servo_id, address, result, self._packet.getTxRxResult(result))
        if error:
            raise DeviceError(operation, servo_id, address, error, self._packet.getRxPacketError(error))

    def ping(self, servo_id):
        """Return Model Number; raise on communication or device error."""
        self._validate(servo_id)
        model, result, error = self._packet.ping(self._port, servo_id)
        self._check('ping', servo_id, None, result, error)
        return model

    def read(self, servo_id, address, size, *, signed=False):
        """Read a raw integer, optionally decoding two's-complement signedness."""
        self._validate(servo_id, address, size)
        value, result, error = getattr(self._packet, f'read{size}ByteTxRx')(self._port, servo_id, address)
        self._check('read', servo_id, address, result, error)
        bits = size * 8
        if signed and value >= 1 << (bits - 1):
            value -= 1 << bits
        return value

    def write(self, servo_id, address, size, value, *, signed=False):
        """Write once and require a Status Packet acknowledgement.

        A timeout does not establish whether the actuator applied the write.
        Register permissions, operating mode and physical limits are the
        caller's responsibility; this method validates integer width only.
        """
        self._validate(servo_id, address, size)
        bits = size * 8
        lower, upper = (-(1 << (bits - 1)), (1 << (bits - 1)) - 1) if signed else (0, (1 << bits) - 1)
        if type(value) is not int or not lower <= value <= upper:
            raise ValueError(f'Value must fit a {bits}-bit {"signed" if signed else "unsigned"} integer')
        encoded = value & ((1 << bits) - 1)
        result, error = getattr(self._packet, f'write{size}ByteTxRx')(self._port, servo_id, address, encoded)
        self._check('write', servo_id, address, result, error)
