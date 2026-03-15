from werkzeug.security import generate_password_hash

password = "Admin@27"

hash_value = generate_password_hash(
    password,
    method="scrypt",
    salt_length=16
)

print(hash_value)
