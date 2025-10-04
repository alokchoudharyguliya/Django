# AES MixColumns Transformation with Polynomial Explanation (GF(2^8))

def byte_to_poly(b: int) -> str:
    """Convert a byte (0-255) into its polynomial representation in GF(2^8)."""
    terms = []
    for i in range(7, -1, -1):
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

def show_polynomial_multiplication(a: int, b: int):
    """Show detailed polynomial multiplication step by step."""
    print(f"\nDetailed polynomial multiplication: ({byte_to_poly(a)}) * ({byte_to_poly(b)})")
    
    # Calculate unreduced product manually
    result_bits = [0] * 16  # Can go up to x^14
    
    # For each bit in 'a', multiply by each bit in 'b'
    for i in range(8):
        if a & (1 << i):
            for j in range(8):
                if b & (1 << j):
                    power = i + j
                    result_bits[power] ^= 1  # XOR because we're in GF(2)
    
    # Convert result_bits to integer
    unreduced = 0
    for i in range(15):
        if result_bits[i]:
            unreduced |= (1 << i)
    
    print(f"Unreduced product: {unreduced:04X} = {extended_poly(unreduced, 14)}")
    
    # Show reduction if needed
    if unreduced >= 0x100:  # If degree >= 8
        print("Reduction needed since degree >= 8")
        reduced = unreduced
        
        # Reduce powers >= 8
        for power in range(14, 7, -1):
            if reduced & (1 << power):
                print(f"  x^{power} = x^{power-8} * x^8")
                print(f"  Since x^8 = x^4 + x^3 + x + 1 (mod irreducible polynomial)")
                print(f"  x^{power} = x^{power-8} * (x^4 + x^3 + x + 1)")
                
                # Calculate x^(power-8) * (x^4 + x^3 + x + 1)
                replacement = 0
                base_power = power - 8
                if base_power + 4 < 16:
                    replacement |= (1 << (base_power + 4))  # x^(base+4)
                if base_power + 3 < 16:
                    replacement |= (1 << (base_power + 3))  # x^(base+3)
                if base_power + 1 < 16:
                    replacement |= (1 << (base_power + 1))  # x^(base+1)
                if base_power < 16:
                    replacement |= (1 << base_power)        # x^base
                
                print(f"  x^{power} = {extended_poly(replacement, 14)}")
                reduced ^= (1 << power)  # Remove the high power term
                reduced ^= replacement   # Add the replacement terms
                print(f"  After reduction: {reduced:04X} = {extended_poly(reduced, 14)}")
        
        # Final result (should be < 0x100 now)
        final = reduced & 0xFF
        print(f"Final reduced result: {final:02X} = {byte_to_poly(final)}")
        return final
    else:
        print("No reduction needed")
        return unreduced & 0xFF

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
    if not log:
        # Fast path for non-logged multiplications
        res = 0
        x = a
        y = b
        for i in range(8):
            if y & 1:
                res ^= x
            x = xtime(x)
            y >>= 1
        return res & 0xFF
    
    print(f"\n{'='*60}")
    print(f"GF MULTIPLY: {a:02X} ({byte_to_poly(a)}) * {b:02X} ({byte_to_poly(b)})")
    print(f"{'='*60}")
    
    # Show detailed polynomial multiplication
    theoretical_result = show_polynomial_multiplication(a, b)
    
    print(f"\nVerifying with bit-by-bit algorithm:")
    res = 0
    x = a
    y = b
    
    for i in range(8):
        if y & 1:
            res ^= x
            print(f"  Bit {i} of {b:02X} is 1: Add {x:02X} ({byte_to_poly(x)}) -> Result: {res:02X} ({byte_to_poly(res)})")
        else:
            print(f"  Bit {i} of {b:02X} is 0: Skip")
        
        if i < 7:  # Don't shift on last iteration
            old_x = x
            x = xtime(x, log=(x & 0x80) != 0)  # Show xtime details only if reduction needed
            if not (old_x & 0x80):  # If no reduction was needed
                print(f"    Next x: {old_x:02X} -> {x:02X}")
        y >>= 1
    
    print(f"\nFinal verification: Theoretical = {theoretical_result:02X}, Algorithm = {res:02X}")
    assert theoretical_result == res, f"Mismatch! Theory: {theoretical_result:02X}, Algo: {res:02X}"
    print(f"Results match!")
    
    return res & 0xFF

def mix_single_column(col, log=False):
    """Apply MixColumns to a single 4-byte column with explanation."""
    a0, a1, a2, a3 = col
    if log:
        print(f"\n{'#'*80}")
        print(f"PROCESSING COLUMN: [{', '.join(f'{x:02X}' for x in col)}]")
        print(f"{'#'*80}")
        print("MixColumns Matrix Multiplication:")
        print("+-----+   +------+   +-----+")
        print("| 02  |   |  a0  |   | b0  |")
        print("| 01  | * |  a1  | = | b1  |")  
        print("| 01  |   |  a2  |   | b2  |")
        print("| 03  |   |  a3  |   | b3  |")
        print("+-----+   +------+   +-----+")
        print("\nFormulas:")
        print(" b0 = (02 * a0) XOR (03 * a1) XOR (01 * a2) XOR (01 * a3)")
        print(" b1 = (01 * a0) XOR (02 * a1) XOR (03 * a2) XOR (01 * a3)")
        print(" b2 = (01 * a0) XOR (01 * a1) XOR (02 * a2) XOR (03 * a3)")
        print(" b3 = (03 * a0) XOR (01 * a1) XOR (01 * a2) XOR (02 * a3)")

    # Calculate each output byte with detailed logging
    print(f"\nCalculating b0 = (02 * {a0:02X}) XOR (03 * {a1:02X}) XOR (01 * {a2:02X}) XOR (01 * {a3:02X})")
    term1 = gf_mul(a0, 0x02, log)
    term2 = gf_mul(a1, 0x03, log)
    b0 = term1 ^ term2 ^ a2 ^ a3
    print(f"b0 = {term1:02X} XOR {term2:02X} XOR {a2:02X} XOR {a3:02X} = {b0:02X}")

    print(f"\nCalculating b1 = (01 * {a0:02X}) XOR (02 * {a1:02X}) XOR (03 * {a2:02X}) XOR (01 * {a3:02X})")
    term3 = gf_mul(a1, 0x02, log)
    term4 = gf_mul(a2, 0x03, log)
    b1 = a0 ^ term3 ^ term4 ^ a3
    print(f"b1 = {a0:02X} XOR {term3:02X} XOR {term4:02X} XOR {a3:02X} = {b1:02X}")

    print(f"\nCalculating b2 = (01 * {a0:02X}) XOR (01 * {a1:02X}) XOR (02 * {a2:02X}) XOR (03 * {a3:02X})")
    term5 = gf_mul(a2, 0x02, log)
    term6 = gf_mul(a3, 0x03, log)
    b2 = a0 ^ a1 ^ term5 ^ term6
    print(f"b2 = {a0:02X} XOR {a1:02X} XOR {term5:02X} XOR {term6:02X} = {b2:02X}")

    print(f"\nCalculating b3 = (03 * {a0:02X}) XOR (01 * {a1:02X}) XOR (01 * {a2:02X}) XOR (02 * {a3:02X})")
    term7 = gf_mul(a0, 0x03, log)
    term8 = gf_mul(a3, 0x02, log)
    b3 = term7 ^ a1 ^ a2 ^ term8
    print(f"b3 = {term7:02X} XOR {a1:02X} XOR {a2:02X} XOR {term8:02X} = {b3:02X}")

    if log:
        print(f"\n-> Column Output: [{', '.join(f'{x:02X}' for x in [b0,b1,b2,b3])}]")
    
    return [b0, b1, b2, b3]

def mix_columns(state, log=False):
    """Apply MixColumns to the full 4x4 state matrix."""
    result = []
    for col_idx, col in enumerate(state):
        if log:
            print(f"\n{'*'*100}")
            print(f"PROCESSING COLUMN {col_idx + 1} of 4")
            print(f"{'*'*100}")
        result.append(mix_single_column(col, log))
    return result

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

print("AES MIXCOLUMNS TRANSFORMATION WITH DETAILED POLYNOMIAL ARITHMETIC")
print("="*80)
print("\nInput State (Row-Major):")
for row in state_hex:
    print(" ".join(f"{val:02X}" for val in row))

print("\nInput State (Column-Major for processing):")
for i, col in enumerate(state_cols):
    print(f"Column {i+1}: [{', '.join(f'{x:02X}' for x in col)}]")

# Apply MixColumns with detailed logs - process only first column for demo
mixed_cols = []
mixed_cols.append(mix_single_column(state_cols[0], log=True))

# For remaining columns, use fast processing
for col in state_cols[1:]:
    mixed_cols.append(mix_single_column(col, log=False))

# Convert back to row-major for display
mixed_state = [[mixed_cols[col][row] for col in range(4)] for row in range(4)]
mixed_state_hex = [[f"{val:02X}" for val in row] for row in mixed_state]

print("\n" + "="*80)
print("FINAL RESULT")
print("="*80)
print("Final State After MixColumns:")
for row in mixed_state_hex:
    print(" ".join(row))