#!/usr/bin/env bash
#
# Ch 2 - Lab 2: PGP demo (GnuPG)
#
# Simulates how a public-key cryptosystem provides confidentiality:
#   1. Generate a key pair (public + private key)
#   2. Encrypt a message with the PUBLIC key
#   3. Decrypt the ciphertext with the PRIVATE key
#
# Uses a throwaway keyring in ./gpg_demo_home so your real keys are untouched.
# Usage: ./pgp_demo.sh | tee pgp_demo_output.txt

set -euo pipefail

export GNUPGHOME="$(pwd)/gpg_demo_home"
rm -rf "$GNUPGHOME" && mkdir -m 700 "$GNUPGHOME"

NAME="Lab Student"
EMAIL="student@example.com"
PASS="lab2-passphrase"

step() { echo; echo "===== $* ====="; }

step "GnuPG version"
gpg --version | head -n 2

step "Step 1: Generate RSA 3072-bit key pair"
gpg --batch --pinentry-mode loopback --passphrase "$PASS" \
    --quick-generate-key "$NAME <$EMAIL>" rsa3072 encrypt,sign 1y 2>&1
gpg --list-keys "$EMAIL"

step "Export public key (what you would share with others)"
gpg --armor --export "$EMAIL" > public_key.asc
head -n 3 public_key.asc; echo "..."

step "Step 2: Plaintext message"
echo "Meet me after the party. This message is confidential." > message.txt
cat message.txt

step "Encrypt with the recipient's PUBLIC key"
gpg --batch --yes --armor --trust-model always \
    --recipient "$EMAIL" --output message.txt.asc --encrypt message.txt
cat message.txt.asc

step "Step 3: Decrypt with the PRIVATE key (requires passphrase)"
gpg --batch --yes --pinentry-mode loopback --passphrase "$PASS" \
    --output decrypted.txt --decrypt message.txt.asc 2>&1
cat decrypted.txt

step "Verify decrypted text matches original"
if diff -q message.txt decrypted.txt >/dev/null; then
    echo "SUCCESS: decrypted.txt is identical to message.txt"
else
    echo "FAILURE: files differ"; exit 1
fi

# Clean up generated files (keep only the transcript produced via tee)
rm -rf "$GNUPGHOME" public_key.asc message.txt message.txt.asc decrypted.txt
