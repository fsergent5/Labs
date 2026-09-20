"""
Caesar Cipher - Brute Force Decryption

Reads a ciphertext from input.txt and, since the shift key k is unknown,
tries every possible k (1-25) and prints the resulting plaintext for each.

Decryption formula: p = (c - k) mod 26
  where c = numerical value of ciphertext letter (A=0, B=1, ..., Z=25)
        p = numerical value of plaintext letter
"""


def decrypt(ciphertext, k):
    """Decrypt ciphertext using shift key k and return the plaintext."""
    plaintext = []
    for ch in ciphertext:
        if ch.isalpha():
            c = ord(ch.upper()) - ord('A')       # letter -> numerical value
            p = (c - k) % 26                     # decryption formula
            plaintext.append(chr(p + ord('A')))
        else:
            plaintext.append(ch)                 # keep spaces/punctuation as-is
    return ''.join(plaintext)


def main():
    with open('input.txt', 'r') as f:
        ciphertext = f.read().strip()

    print(f"Ciphertext: {ciphertext}\n")
    print("All possible plaintexts:")
    for k in range(1, 26):
        plaintext = decrypt(ciphertext, k)
        print(f"k={k:2d}: {plaintext}")


if __name__ == '__main__':
    main()
