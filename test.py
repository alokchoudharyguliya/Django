# # # # # AES MixColumns Transformation in Python

# # # # def xtime(a: int) -> int:
# # # #     """Multiply by x (i.e., 2) in GF(2^8) with AES irreducible polynomial 0x11B."""
# # # #     a <<= 1
# # # #     if a & 0x100:
# # # #         a ^= 0x11B
# # # #     return a & 0xFF

# # # # def gf_mul(a: int, b: int) -> int:
# # # #     """Multiply two numbers in GF(2^8)."""
# # # #     res = 0
# # # #     x = a & 0xFF
# # # #     y = b & 0xFF
# # # #     for _ in range(8):
# # # #         if y & 1:
# # # #             res ^= x
# # # #         x = xtime(x)
# # # #         y >>= 1
# # # #     return res & 0xFF

# # # # def mix_single_column(col):
# # # #     """Apply MixColumns to a single 4-byte column."""
# # # #     a0, a1, a2, a3 = col
# # # #     return [
# # # #         gf_mul(a0, 0x02) ^ gf_mul(a1, 0x03) ^ a2 ^ a3,
# # # #         a0 ^ gf_mul(a1, 0x02) ^ gf_mul(a2, 0x03) ^ a3,
# # # #         a0 ^ a1 ^ gf_mul(a2, 0x02) ^ gf_mul(a3, 0x03),
# # # #         gf_mul(a0, 0x03) ^ a1 ^ a2 ^ gf_mul(a3, 0x02),
# # # #     ]

# # # # def mix_columns(state):
# # # #     """Apply MixColumns to the full 4x4 state matrix."""
# # # #     return [mix_single_column(col) for col in state]

# # # # # -------------------------------
# # # # # Input State (row-major order)
# # # # # -------------------------------
# # # # state_hex = [
# # # #     [0x63, 0xC9, 0xFE, 0x30],
# # # #     [0xF2, 0x63, 0x26, 0xF2],
# # # #     [0x7D, 0xD4, 0xC9, 0xC9],
# # # #     [0xD4, 0xFA, 0x63, 0x82],
# # # # ]

# # # # # Convert to column-major (AES state representation)
# # # # state_cols = [[state_hex[row][col] for row in range(4)] for col in range(4)]

# # # # # Apply MixColumns
# # # # mixed_cols = mix_columns(state_cols)

# # # # # Convert back to row-major for display
# # # # mixed_state = [[mixed_cols[col][row] for col in range(4)] for row in range(4)]
# # # # mixed_state_hex = [[f"{val:02X}" for val in row] for row in mixed_state]

# # # # # Print result
# # # # print("Input State:")
# # # # for row in state_hex:
# # # #     print(" ".join(f"{val:02X}" for val in row))

# # # # print("\nAfter MixColumns:")
# # # # for row in mixed_state_hex:
# # # #     print(" ".join(row))


# # # # AES MixColumns Transformation with Step-by-Step Logging

# # # def xtime(a: int) -> int:
# # #     """Multiply by x (i.e., 2) in GF(2^8)."""
# # #     a <<= 1
# # #     if a & 0x100:  # If overflow beyond 8 bits
# # #         a ^= 0x11B  # Reduce modulo AES polynomial
# # #     return a & 0xFF

# # # def gf_mul(a: int, b: int, log=False) -> int:
# # #     """Multiply two numbers in GF(2^8)."""
# # #     res = 0
# # #     x = a & 0xFF
# # #     y = b & 0xFF
# # #     if log:
# # #         print(f"\n--- GF Multiply: {a:02X} * {b:02X} ---")
# # #     for i in range(8):
# # #         if y & 1:
# # #             res ^= x
# # #             if log:
# # #                 print(f"  bit {i}: res ^= {x:02X} → {res:02X}")
# # #         x = xtime(x)
# # #         if log:
# # #             print(f"  xtime → {x:02X}")
# # #         y >>= 1
# # #     if log:
# # #         print(f"Result = {res:02X}")
# # #     return res & 0xFF

# # # def mix_single_column(col, log=False):
# # #     """Apply MixColumns to a single 4-byte column with explanation."""
# # #     a0, a1, a2, a3 = col
# # #     if log:
# # #         print(f"\n=== Processing Column: {[f'{x:02X}' for x in col]} ===")
# # #         print("Formula:")
# # #         print(" b0 = 2*a0 ⊕ 3*a1 ⊕ 1*a2 ⊕ 1*a3")
# # #         print(" b1 = 1*a0 ⊕ 2*a1 ⊕ 3*a2 ⊕ 1*a3")
# # #         print(" b2 = 1*a0 ⊕ 1*a1 ⊕ 2*a2 ⊕ 3*a3")
# # #         print(" b3 = 3*a0 ⊕ 1*a1 ⊕ 1*a2 ⊕ 2*a3")

# # #     b0 = gf_mul(a0, 0x02, log) ^ gf_mul(a1, 0x03, log) ^ a2 ^ a3
# # #     b1 = a0 ^ gf_mul(a1, 0x02, log) ^ gf_mul(a2, 0x03, log) ^ a3
# # #     b2 = a0 ^ a1 ^ gf_mul(a2, 0x02, log) ^ gf_mul(a3, 0x03, log)
# # #     b3 = gf_mul(a0, 0x03, log) ^ a1 ^ a2 ^ gf_mul(a3, 0x02, log)

# # #     if log:
# # #         print(f" Output Column: {[f'{x:02X}' for x in [b0,b1,b2,b3]]}")
# # #     return [b0, b1, b2, b3]

# # # def mix_columns(state, log=False):
# # #     """Apply MixColumns to the full 4x4 state matrix."""
# # #     return [mix_single_column(col, log) for col in state]

# # # # -------------------------------
# # # # Input State (row-major order)
# # # # -------------------------------
# # # state_hex = [
# # #     [0x63, 0xC9, 0xFE, 0x30],
# # #     [0xF2, 0x63, 0x26, 0xF2],
# # #     [0x7D, 0xD4, 0xC9, 0xC9],
# # #     [0xD4, 0xFA, 0x63, 0x82],
# # # ]

# # # # Convert to column-major (AES state representation)
# # # state_cols = [[state_hex[row][col] for row in range(4)] for col in range(4)]

# # # print("Input State (Row-Major):")
# # # for row in state_hex:
# # #     print(" ".join(f"{val:02X}" for val in row))

# # # # Apply MixColumns with detailed logs
# # # mixed_cols = mix_columns(state_cols, log=True)

# # # # Convert back to row-major for display
# # # mixed_state = [[mixed_cols[col][row] for col in range(4)] for row in range(4)]
# # # mixed_state_hex = [[f"{val:02X}" for val in row] for row in mixed_state]

# # # print("\nFinal State After MixColumns:")
# # # for row in mixed_state_hex:
# # #     print(" ".join(row))



# # # AES MixColumns Transformation with Polynomial Explanation (GF(2^8))

# # def byte_to_poly(b: int) -> str:
# #     """Convert a byte (0-255) into its polynomial representation in GF(2^8)."""
# #     terms = []
# #     for i in range(8, -1, -1):
# #         if b & (1 << i):
# #             if i == 0:
# #                 terms.append("1")
# #             elif i == 1:
# #                 terms.append("x")
# #             else:
# #                 terms.append(f"x^{i}")
# #     return " + ".join(terms) if terms else "0"

# # def xtime(a: int, log=False) -> int:
# #     """Multiply by x (2) in GF(2^8) with reduction modulo 0x11B."""
# #     carry = a & 0x80  # check if highest bit is set (x^7 term -> x^8)
# #     res = (a << 1) & 0xFF
# #     if carry:
# #         res ^= 0x1B  # reduction by (x^8 + x^4 + x^3 + x + 1)
# #     if log:
# #         print(f" xtime({a:02X}) → {res:02X} | {byte_to_poly(a)} * x = {byte_to_poly(res)}")
# #     return res

# # def gf_mul(a: int, b: int, log=False) -> int:
# #     """Multiply a * b in GF(2^8) with polynomial explanation."""
# #     res = 0
# #     x = a
# #     y = b
# #     if log:
# #         print(f"\n--- GF Multiply: {a:02X} ({byte_to_poly(a)}) * {b:02X} ({byte_to_poly(b)}) ---")
# #     for i in range(8):
# #         if y & 1:
# #             res ^= x
# #             if log:
# #                 print(f"  Add {x:02X} ({byte_to_poly(x)}) to result → {res:02X} ({byte_to_poly(res)})")
# #         x = xtime(x, log)
# #         y >>= 1
# #     if log:
# #         print(f" Result = {res:02X} ({byte_to_poly(res)})")
# #     return res & 0xFF

# # def mix_single_column(col, log=False):
# #     """Apply MixColumns to a single 4-byte column with explanation."""
# #     a0, a1, a2, a3 = col
# #     if log:
# #         print(f"\n=== Processing Column: {[f'{x:02X}' for x in col]} ===")
# #         print("Formula:")
# #         print(" b0 = (2 * a0) ⊕ (3 * a1) ⊕ (1 * a2) ⊕ (1 * a3)")
# #         print(" b1 = (1 * a0) ⊕ (2 * a1) ⊕ (3 * a2) ⊕ (1 * a3)")
# #         print(" b2 = (1 * a0) ⊕ (1 * a1) ⊕ (2 * a2) ⊕ (3 * a3)")
# #         print(" b3 = (3 * a0) ⊕ (1 * a1) ⊕ (1 * a2) ⊕ (2 * a3)")

# #     b0 = gf_mul(a0, 0x02, log) ^ gf_mul(a1, 0x03, log) ^ a2 ^ a3
# #     b1 = a0 ^ gf_mul(a1, 0x02, log) ^ gf_mul(a2, 0x03, log) ^ a3
# #     b2 = a0 ^ a1 ^ gf_mul(a2, 0x02, log) ^ gf_mul(a3, 0x03, log)
# #     b3 = gf_mul(a0, 0x03, log) ^ a1 ^ a2 ^ gf_mul(a3, 0x02, log)

# #     if log:
# #         print(f"→ Output Column: {[f'{x:02X}' for x in [b0,b1,b2,b3]]}")
# #     return [b0, b1, b2, b3]

# # def mix_columns(state, log=False):
# #     """Apply MixColumns to the full 4x4 state matrix."""
# #     return [mix_single_column(col, log) for col in state]

# # # -------------------------------
# # # Input State (row-major order)
# # # -------------------------------
# # state_hex = [
# #     [0x63, 0xC9, 0xFE, 0x30],
# #     [0xF2, 0x63, 0x26, 0xF2],
# #     [0x7D, 0xD4, 0xC9, 0xC9],
# #     [0xD4, 0xFA, 0x63, 0x82],
# # ]

# # # Convert to column-major (AES state representation)
# # state_cols = [[state_hex[row][col] for row in range(4)] for col in range(4)]

# # print("🔹 Input State (Row-Major):")
# # for row in state_hex:
# #     print(" ".join(f"{val:02X}" for val in row))

# # # Apply MixColumns with detailed logs
# # mixed_cols = mix_columns(state_cols, log=True)

# # # Convert back to row-major for display
# # mixed_state = [[mixed_cols[col][row] for col in range(4)] for row in range(4)]
# # mixed_state_hex = [[f"{val:02X}" for val in row] for row in mixed_state]

# # print("\n🔹 Final State After MixColumns:")
# # for row in mixed_state_hex:
# #     print(" ".join(row))



# # AES MixColumns Transformation with Polynomial Explanation (GF(2^8))

# def byte_to_poly(b: int) -> str:
#     """Convert a byte (0-255) into its polynomial representation in GF(2^8)."""
#     terms = []
#     for i in range(8, -1, -1):
#         if b & (1 << i):
#             if i == 0:
#                 terms.append("1")
#             elif i == 1:
#                 terms.append("x")
#             else:
#                 terms.append(f"x^{i}")
#     return " + ".join(terms) if terms else "0"

# def xtime(a: int, log=False) -> int:
#     """Multiply by x (2) in GF(2^8) with reduction modulo 0x11B."""
#     carry = a & 0x80  # check if highest bit is set (x^7 term -> x^8)
#     res = (a << 1) & 0xFF
#     if carry:
#         res ^= 0x1B  # reduction by (x^8 + x^4 + x^3 + x + 1)
#     if log:
#         print(f" xtime({a:02X}) -> {res:02X} | {byte_to_poly(a)} * x = {byte_to_poly(res)}")
#     return res

# def gf_mul(a: int, b: int, log=False) -> int:
#     """Multiply a * b in GF(2^8) with polynomial explanation."""
#     res = 0
#     x = a
#     y = b
#     if log:
#         print(f"\n--- GF Multiply: {a:02X} ({byte_to_poly(a)}) * {b:02X} ({byte_to_poly(b)}) ---")
#     for i in range(8):
#         if y & 1:
#             res ^= x
#             if log:
#                 print(f"  Add {x:02X} ({byte_to_poly(x)}) to result -> {res:02X} ({byte_to_poly(res)})")
#         x = xtime(x, log)
#         y >>= 1
#     if log:
#         print(f" Result = {res:02X} ({byte_to_poly(res)})")
#     return res & 0xFF

# def mix_single_column(col, log=False):
#     """Apply MixColumns to a single 4-byte column with explanation."""
#     a0, a1, a2, a3 = col
#     if log:
#         print(f"\n=== Processing Column: {[f'{x:02X}' for x in col]} ===")
#         print("Formula:")
#         print(" b0 = (2 * a0) XOR (3 * a1) XOR (1 * a2) XOR (1 * a3)")
#         print(" b1 = (1 * a0) XOR (2 * a1) XOR (3 * a2) XOR (1 * a3)")
#         print(" b2 = (1 * a0) XOR (1 * a1) XOR (2 * a2) XOR (3 * a3)")
#         print(" b3 = (3 * a0) XOR (1 * a1) XOR (1 * a2) XOR (2 * a3)")

#     b0 = gf_mul(a0, 0x02, log) ^ gf_mul(a1, 0x03, log) ^ a2 ^ a3
#     b1 = a0 ^ gf_mul(a1, 0x02, log) ^ gf_mul(a2, 0x03, log) ^ a3
#     b2 = a0 ^ a1 ^ gf_mul(a2, 0x02, log) ^ gf_mul(a3, 0x03, log)
#     b3 = gf_mul(a0, 0x03, log) ^ a1 ^ a2 ^ gf_mul(a3, 0x02, log)

#     if log:
#         print(f"-> Output Column: {[f'{x:02X}' for x in [b0,b1,b2,b3]]}")
#     return [b0, b1, b2, b3]

# def mix_columns(state, log=False):
#     """Apply MixColumns to the full 4x4 state matrix."""
#     return [mix_single_column(col, log) for col in state]

# # -------------------------------
# # Input State (row-major order)
# # -------------------------------
# state_hex = [
#     [0x63, 0xC9, 0xFE, 0x30],
#     [0xF2, 0x63, 0x26, 0xF2],
#     [0x7D, 0xD4, 0xC9, 0xC9],
#     [0xD4, 0xFA, 0x63, 0x82],
# ]

# # Convert to column-major (AES state representation)
# state_cols = [[state_hex[row][col] for row in range(4)] for col in range(4)]

# print("Input State (Row-Major):")
# for row in state_hex:
#     print(" ".join(f"{val:02X}" for val in row))

# # Apply MixColumns with detailed logs
# mixed_cols = mix_columns(state_cols, log=True)

# # Convert back to row-major for display
# mixed_state = [[mixed_cols[col][row] for col in range(4)] for row in range(4)]
# mixed_state_hex = [[f"{val:02X}" for val in row] for row in mixed_state]

# print("\nFinal State After MixColumns:")
# for row in mixed_state_hex:
#     print(" ".join(row))

# AES MixColumns Transformation with Polynomial Explanation (GF(2^8))

def byte_to_poly(b: int) -> str:
    """Convert a byte (0-255) into its polynomial representation in GF(2^8)."""
    terms = []
    for i in range(8, -1, -1):
        if b & (1 << i):
            if i == 0:
                terms.append("1")
            elif i == 1:
                terms.append("x")
            else:
                terms.append(f"x^{i}")
    return " + ".join(terms) if terms else "0"

def extended_poly(b: int, max_power: int = 15) -> str:
    """Convert to polynomial with powers up to max_power for showing reduction."""
    terms = []
    for i in range(max_power, -1, -1):
        if b & (1 << i):
            if i == 0:
                terms.append("1")
            elif i == 1:
                terms.append("x")
            else:
                terms.append(f"x^{i}")
    return " + ".join(terms) if terms else "0"

def xtime(a: int, log=False) -> int:
    """Multiply by x (2) in GF(2^8) with reduction modulo 0x11B."""
    carry = a & 0x80  # check if highest bit is set (x^7 term -> x^8)
    res = (a << 1) & 0xFF
    if carry:
        res ^= 0x1B  # reduction by (x^8 + x^4 + x^3 + x + 1)
    if log:
        if carry:
            print(f"    xtime({a:02X}) -> shift left: {(a << 1) & 0x1FF:03X}")
            print(f"    Reduction needed: {(a << 1) & 0x1FF:03X} XOR 11B = {res:02X}")
            print(f"    {extended_poly((a << 1) & 0x1FF, 8)} mod (x^8 + x^4 + x^3 + x + 1) = {byte_to_poly(res)}")
        else:
            print(f"    xtime({a:02X}) -> {res:02X} | {byte_to_poly(a)} * x = {byte_to_poly(res)}")
    return res

def gf_mul(a: int, b: int, log=False) -> int:
    """Multiply a * b in GF(2^8) with detailed polynomial reduction explanation."""
    res = 0
    x = a
    y = b
    if log:
        print(f"\n--- GF Multiply: {a:02X} ({byte_to_poly(a)}) * {b:02X} ({byte_to_poly(b)}) ---")
        if a == 0x03 and b == 0xF2:
            print("Special case: 03 * F2 - showing detailed polynomial multiplication and reduction")
            print(f"({byte_to_poly(a)}) * ({byte_to_poly(b)})")
            
            # Show manual polynomial multiplication
            print("\nStep-by-step polynomial multiplication:")
            print("(x + 1) * (x^7 + x^6 + x^5 + x^4 + x)")
            print("= x * (x^7 + x^6 + x^5 + x^4 + x)")
            print("  + 1 * (x^7 + x^6 + x^5 + x^4 + x)")
            print("= (x^8 + x^7 + x^6 + x^5 + x^2)")
            print("  + (x^7 + x^6 + x^5 + x^4 + x)")
            print("= x^8 + x^7 + x^6 + x^5 + x^2 + x^7 + x^6 + x^5 + x^4 + x")
            print("= x^8 + x^4 + x^2 + x  (after XOR combining like terms)")
            
            unreduced = 0x100 | 0x10 | 0x04 | 0x02  # x^8 + x^4 + x^2 + x
            print(f"Unreduced result: {unreduced:03X} = {extended_poly(unreduced, 8)}")
            print(f"Since we have x^8 term, we need reduction modulo (x^8 + x^4 + x^3 + x + 1)")
            print(f"x^8 mod (x^8 + x^4 + x^3 + x + 1) = x^4 + x^3 + x + 1")
            print(f"So: x^8 + x^4 + x^2 + x")
            print(f"  = (x^4 + x^3 + x + 1) + x^4 + x^2 + x")
            print(f"  = x^4 + x^3 + x + 1 + x^4 + x^2 + x")
            print(f"  = x^3 + x^2 + 1  (after XOR)")
            final_result = 0x0C | 0x01  # x^3 + x^2 + 1
            print(f"Final result: {final_result:02X} = {byte_to_poly(final_result)}")
            print()
    
    for i in range(8):
        if y & 1:
            res ^= x
            if log:
                print(f"  bit {i}: Add {x:02X} ({byte_to_poly(x)}) to result -> {res:02X} ({byte_to_poly(res)})")
        if i < 7:  # Don't shift on last iteration
            x = xtime(x, log and (a == 0x03 and b == 0xF2))
        y >>= 1
    
    if log:
        print(f" Final Result = {res:02X} ({byte_to_poly(res)})")
    return res & 0xFF

def mix_single_column(col, log=False):
    """Apply MixColumns to a single 4-byte column with explanation."""
    a0, a1, a2, a3 = col
    if log:
        print(f"\n=== Processing Column: {[f'{x:02X}' for x in col]} ===")
        print("Formula:")
        print(" b0 = (2 * a0) XOR (3 * a1) XOR (1 * a2) XOR (1 * a3)")
        print(" b1 = (1 * a0) XOR (2 * a1) XOR (3 * a2) XOR (1 * a3)")
        print(" b2 = (1 * a0) XOR (1 * a1) XOR (2 * a2) XOR (3 * a3)")
        print(" b3 = (3 * a0) XOR (1 * a1) XOR (1 * a2) XOR (2 * a3)")

    b0 = gf_mul(a0, 0x02, log) ^ gf_mul(a1, 0x03, log) ^ a2 ^ a3
    b1 = a0 ^ gf_mul(a1, 0x02, log) ^ gf_mul(a2, 0x03, log) ^ a3
    b2 = a0 ^ a1 ^ gf_mul(a2, 0x02, log) ^ gf_mul(a3, 0x03, log)
    b3 = gf_mul(a0, 0x03, log) ^ a1 ^ a2 ^ gf_mul(a3, 0x02, log)

    if log:
        print(f"-> Output Column: {[f'{x:02X}' for x in [b0,b1,b2,b3]]}")
    return [b0, b1, b2, b3]

def mix_columns(state, log=False):
    """Apply MixColumns to the full 4x4 state matrix."""
    return [mix_single_column(col, log) for col in state]

# -------------------------------
# Input State (row-major order)
# -------------------------------
state_hex = [
    [0x63, 0xC9, 0xFE, 0x30],
    [0xF2, 0x63, 0x26, 0xF2],
    [0x7D, 0xD4, 0xC9, 0xC9],
    [0xD4, 0xFA, 0x63, 0x82],
]

# Convert to column-major (AES state representation)
state_cols = [[state_hex[row][col] for row in range(4)] for col in range(4)]

print("Input State (Row-Major):")
for row in state_hex:
    print(" ".join(f"{val:02X}" for val in row))

# Apply MixColumns with detailed logs
mixed_cols = mix_columns(state_cols, log=True)

# Convert back to row-major for display
mixed_state = [[mixed_cols[col][row] for col in range(4)] for row in range(4)]
mixed_state_hex = [[f"{val:02X}" for val in row] for row in mixed_state]

print("\nFinal State After MixColumns:")
for row in mixed_state_hex:
    print(" ".join(row))