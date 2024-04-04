import mmap
import os
import sys

TARGET_ADDR = 0x40000000
MAP_LENGTH = 4096
new_byte = bytes.fromhex(sys.argv[1])  # Convert first argument from hex string to byte

if len(new_byte) != 1:
    raise ValueError("Please provide exactly one byte to write.")

mem_fd = os.open("/dev/mem", os.O_RDWR | os.O_SYNC)  # Open with read-write permissions
try:
    with mmap.mmap(fileno=mem_fd, length=MAP_LENGTH, offset=TARGET_ADDR, access=mmap.ACCESS_WRITE) as mm:
        mm.seek(0)  # Go to the beginning of the mmap
        first_byte = mm.read(1)
        print(f"Current byte at 0x{TARGET_ADDR:X}: {first_byte.hex()}")
        mm.seek(0)  # Go back to the beginning to write
        mm.write(new_byte)  # Write the new byte
        print(f"Written byte: {new_byte.hex()} to address 0x{TARGET_ADDR:X}")
finally:
    os.close(mem_fd)
