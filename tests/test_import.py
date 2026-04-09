import qrcode
from PIL import Image
from pyzbar.pyzbar import decode
from pathlib import Path

def test_qr_decode_logic(tmp_path):
    test_data = "otpauth://totp/Test:User?secret=GEZDGNBVGY3TQOJQ"
    qr_path = tmp_path / "test_qr.png"
    img = qrcode.make(test_data)
    img.save(qr_path)
    
    with Image.open(qr_path) as test_img:
        results = decode(test_img)
        decoded_text = results[0].data.decode("utf-8")
    
    assert decoded_text == test_data