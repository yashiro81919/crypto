from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import os, questionary

# Generate a key based on a passphrase and salt using PBKDF2
def generate_key(passphrase: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(passphrase.encode())

# AES-256-GCM encode function
def aes256gcm_encode(data: bytes, passphrase: str) -> bytes:
    # Generate a random salt and nonce
    salt = os.urandom(16)   # Salt for key derivation
    nonce = os.urandom(12)   # Nonce for AES-GCM (recommended size for GCM)

    # Derive a 256-bit key from the passphrase and salt
    key = generate_key(passphrase, salt)

    # Initialize AES-GCM cipher
    encryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(nonce),
        backend=default_backend()
    ).encryptor()

    # Encrypt data and get the authentication tag
    ciphertext = encryptor.update(data) + encryptor.finalize()
    tag = encryptor.tag

    # Return salt, nonce, tag, and ciphertext concatenated
    return salt + nonce + tag + ciphertext

# AES-256-GCM decode function
def aes256gcm_decode(encoded_data: bytes, passphrase: str) -> bytes:
    # Extract salt, nonce, tag, and ciphertext from encoded data
    salt = encoded_data[:16]
    nonce = encoded_data[16:28]
    tag = encoded_data[28:44]
    ciphertext = encoded_data[44:]

    # Derive the key from the passphrase and salt
    key = generate_key(passphrase, salt)

    # Initialize AES-GCM cipher for decryption
    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(nonce, tag),
        backend=default_backend()
    ).decryptor()

    # Decrypt and return the plaintext
    return decryptor.update(ciphertext) + decryptor.finalize()

# Example usage
if __name__ == "__main__":
    action1 = questionary.Choice(title="encrypt text", value=0)
    action2 = questionary.Choice(title="decrypt from text", value=1)
    action3 = questionary.Choice(title="decrypt from file", value=2)
    step = questionary.select("Choose your action: ", choices=[action1, action2, action3]).ask()
    passphrase = questionary.password("Passphrase: ", validate=lambda text: len(text) > 0).ask()

    if step == 0:
        plaintext = questionary.text("Text to be encrypted: ", validate=lambda text: len(text) > 0).ask()
        # Encrypt the data
        encrypted_data = aes256gcm_encode(bytes(plaintext, "utf-8"), passphrase)
        print(f"Encrypted data: {encrypted_data.hex()}")
    elif step == 1:
        plaintext = questionary.text("Text to be decrypted: ", validate=lambda text: len(text) > 0).ask()
        # Decrypt the data
        decrypted_data = aes256gcm_decode(bytes.fromhex(plaintext), passphrase)
        print(f"Decrypted data: {decrypted_data}")    
    elif step == 2:
        file_name = questionary.text("File name to be decrypted: ", validate=lambda text: len(text) > 0).ask()
        # Decrypt the data from file
        with open(file_name, 'r') as file:
            content = file.read()        
        decrypted_data = aes256gcm_decode(bytes.fromhex(content), passphrase)
        print(f"Decrypted data: {decrypted_data}")