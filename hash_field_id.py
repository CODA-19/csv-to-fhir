import hashlib

PATIENT_SITE_SALT = "YOUR_RANDOM_SITE_SALT"

def hash_field_id(field_id):
  
  field_id = str(field_id)

  return hashlib.pbkdf2_hmac('sha512', 
    field_id.encode('utf-8'), 
    PATIENT_SITE_SALT.encode('utf-8'), 100000).hex()
