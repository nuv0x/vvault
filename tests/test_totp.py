from sololc_vvault.core import vault, totp

def test_totp_generation():
   
    secret = "JBSWY3DPEHPK3PXP" 
    code = totp.generate_code(secret)
    
    assert len(code) == 6
    assert code.isdigit()

def test_url_parsing():
    url = "otpauth://totp/Google:user@gmail.com?secret=JBSWY3DPEHPK3PXP&issuer=Google"
    account = vault.parse_otpauth_url(url)
    
    assert account["name"] == "user@gmail.com"
    assert account["issuer"] == "Google"
    assert account["secret"] == "JBSWY3DPEHPK3PXP"