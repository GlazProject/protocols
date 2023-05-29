def byte_at(value: int, bit_position: int, bits_count: int):
    sequence = value.to_bytes((value.bit_length() + 7) // 8, 'big')
    byte = sequence[bit_position // 8]
    bit_position %= 8
    mask = 0
    for i in range(bit_position, bit_position + bits_count):
        mask |= 1 << 7 - i
    value = byte & mask
    return value >> 8 - (bit_position + bits_count)
