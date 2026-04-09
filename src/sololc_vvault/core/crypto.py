import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id

# Security constants for Vvault
SALT_SIZE = 16
NONCE_SIZE = 12  # Standard for AES-GCM
KEY_LENGTH = 32  # 256-bit key

def derive_key(password: str, salt: bytes) -> bytes:
    """
    KDF(password) -> key
    Uses Argon2id (via the Argon2 class) to derive a secure 32-byte key.
    """
    # Argon2 settings: memory_cost (64MB), time_cost (3 iterations)
    kdf = Argon2id(
        salt=salt,
        length=32,
        iterations=3,       
        memory_cost=65536,  
        lanes=4,     
    )
    return kdf.derive(password.encode())

def encrypt_data(data: str, password: str) -> str:
    """
    KDF(password) -> key -> AES-GCM Encrypt
    Returns: base64(salt + nonce + ciphertext)
    """
    salt = os.urandom(SALT_SIZE)
    nonce = os.urandom(NONCE_SIZE)
    key = derive_key(password, salt)
    
    aesgcm = AESGCM(key)
    # Encrypting the plaintext string
    ciphertext = aesgcm.encrypt(nonce, data.encode(), None)
    
    # Bundle components: salt(16) + nonce(12) + encrypted_data(...)
    bundle = salt + nonce + ciphertext
    return base64.b64encode(bundle).decode('utf-8')

def decrypt_data(bundle_b64: str, password: str) -> str:
    """
    Base64 Decode -> Extract Salt/Nonce -> Derive Key -> AES-GCM Decrypt
    """
    try:
        bundle = base64.b64decode(bundle_b64)
        
        # Exact slicing of the binary bundle
        salt = bundle[:SALT_SIZE]
        nonce = bundle[SALT_SIZE:SALT_SIZE + NONCE_SIZE]
        ciphertext = bundle[SALT_SIZE + NONCE_SIZE:]
        
        key = derive_key(password, salt)
        aesgcm = AESGCM(key)
        
        decrypted_data = aesgcm.decrypt(nonce, ciphertext, None)
        return decrypted_data.decode('utf-8')
    except Exception:
        # Standard security practice: do not reveal if the error 
        # was a wrong password or corrupted data.
        raise ValueError("Decryption failed. Please check your master password.")