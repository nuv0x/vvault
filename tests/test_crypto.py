import pytest
from sololc_vvault.core import crypto

def test_encrypt_decrypt_cycle():
    password = "test-password"
    secret_data = "otpauth://totp/Github:me?secret=ABCDEF"
    
    encrypted = crypto.encrypt_data(secret_data, password)
    assert isinstance(encrypted, str)
    assert encrypted != secret_data.encode()
    
    decrypted = crypto.decrypt_data(encrypted, password)
    assert decrypted == secret_data

def test_wrong_password():
    password = "correct-password"
    wrong_password = "wrong-password"
    encrypted = crypto.encrypt_data("data", password)
    
    with pytest.raises(Exception):
        crypto.decrypt_data(encrypted, wrong_password)