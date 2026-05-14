import sys

def crc16_ccitt(data: bytes):
    crc = 0xFFFF
    for b in data:
        crc ^= (b << 8)
        for _ in range(8):
            if (crc & 0x8000):
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc

# 파일 열기
with open("eep.bin", "rb") as f:
    data = bytearray(f.read())

# 🔍 패턴 찾기 (P07B700)
pattern = bytes([0x07, 0xB7, 0x00, 0x27])

offsets = []
for i in range(len(data) - 4):
    if data[i:i+4] == pattern:
        offsets.append(i)

print("DTC found at:", offsets)

# 🔧 수정 (freeze 영역 0 처리)
for off in offsets:
    data[off+6] = 0x00
    data[off+7] = 0x00
    data[off+8] = 0x00

# ⚠️ 블록 크기 (일반적으로 0x4000)
BLOCK_SIZE = 0x4000

for block_start in range(0, len(data), BLOCK_SIZE):
    block_end = block_start + BLOCK_SIZE

    if block_end > len(data):
        break

    block = data[block_start:block_end-2]

    crc = crc16_ccitt(block)

    # Big endian 저장
    data[block_end-2] = (crc >> 8) & 0xFF
    data[block_end-1] = crc & 0xFF

    print(f"Block {hex(block_start)} CRC: {hex(crc)}")

# 저장
with open("patched.bin", "wb") as f:
    f.write(data)

print("완료: patched.bin 생성됨")