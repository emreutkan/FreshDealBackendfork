import json
import os

def generate_users():
    """
    Generates exactly 8 users with fixed data:
    - 2 restaurant owners
    - 5 customers
    - 1 support member
    and writes them to ../exported_json/users.json.
    """
    users = [
        # Owners
        {
            "id": 1,
            "name": "Ali Yılmaz",
            "email": "owner1@example.com",
            "phone_number": "+905078905011",
            "password": "scrypt:32768:8:1$1SpMr9j8zZCp6vfr$c436c2aa43572b5b17c63e342636eaf0e64050ed3c30e51e1343b11abaf65dcc2d26e0c0f4dd6570ee4a7707064bd93aeb95c98ee459583aacfc491c866f121f",
            "role": "owner",
            "email_verified": True,
            "reset_token": None,
            "reset_token_expires": None
        },
        {
            "id": 2,
            "name": "Mehmet Kaya",
            "email": "owner2@example.com",
            "phone_number": "+905078905012",
            "password": "scrypt:32768:8:1$1SpMr9j8zZCp6vfr$c436c2aa43572b5b17c63e342636eaf0e64050ed3c30e51e1343b11abaf65dcc2d26e0c0f4dd6570ee4a7707064bd93aeb95c98ee459583aacfc491c866f121f",
            "role": "owner",
            "email_verified": True,
            "reset_token": None,
            "reset_token_expires": None
        },

        # Customers
        {
            "id": 3,
            "name": "Ayşe Demir",
            "email": "customer1@example.com",
            "phone_number": "+905078905010",
            "password": "scrypt:32768:8:1$1SpMr9j8zZCp6vfr$c436c2aa43572b5b17c63e342636eaf0e64050ed3c30e51e1343b11abaf65dcc2d26e0c0f4dd6570ee4a7707064bd93aeb95c98ee459583aacfc491c866f121f",
            "role": "customer",
            "email_verified": True,
            "reset_token": None,
            "reset_token_expires": None
        },
        {
            "id": 4,
            "name": "Fatma Özdemir",
            "email": "customer2@example.com",
            "phone_number": "+905078905013",
            "password": "scrypt:32768:8:1$1SpMr9j8zZCp6vfr$c436c2aa43572b5b17c63e342636eaf0e64050ed3c30e51e1343b11abaf65dcc2d26e0c0f4dd6570ee4a7707064bd93aeb95c98ee459583aacfc491c866f121f",
            "role": "customer",
            "email_verified": True,
            "reset_token": None,
            "reset_token_expires": None
        },
        {
            "id": 5,
            "name": "Kerem Çelik",
            "email": "customer3@example.com",
            "phone_number": "+905078905014",
            "password": "scrypt:32768:8:1$1SpMr9j8zZCp6vfr$c436c2aa43572b5b17c63e342636eaf0e64050ed3c30e51e1343b11abaf65dcc2d26e0c0f4dd6570ee4a7707064bd93aeb95c98ee459583aacfc491c866f121f",
            "role": "customer",
            "email_verified": True,
            "reset_token": None,
            "reset_token_expires": None
        },
        {
            "id": 6,
            "name": "Elif Taş",
            "email": "customer4@example.com",
            "phone_number": "+905078905015",
            "password": "scrypt:32768:8:1$1SpMr9j8zZCp6vfr$c436c2aa43572b5b17c63e342636eaf0e64050ed3c30e51e1343b11abaf65dcc2d26e0c0f4dd6570ee4a7707064bd93aeb95c98ee459583aacfc491c866f121f",
            "role": "customer",
            "email_verified": True,
            "reset_token": None,
            "reset_token_expires": None
        },
        {
            "id": 7,
            "name": "Yusuf Aydın",
            "email": "customer5@example.com",
            "phone_number": "+905078905016",
            "password": "scrypt:32768:8:1$1SpMr9j8zZCp6vfr$c436c2aa43572b5b17c63e342636eaf0e64050ed3c30e51e1343b11abaf65dcc2d26e0c0f4dd6570ee4a7707064bd93aeb95c98ee459583aacfc491c866f121f",
            "role": "customer",
            "email_verified": True,
            "reset_token": None,
            "reset_token_expires": None
        },

        # Support
        {
            "id": 8,
            "name": "Support 1",
            "email": "support1@example.com",
            "phone_number": "+905078905000",
            "password": "scrypt:32768:8:1$1SpMr9j8zZCp6vfr$c436c2aa43572b5b17c63e342636eaf0e64050ed3c30e51e1343b11abaf65dcc2d26e0c0f4dd6570ee4a7707064bd93aeb95c98ee459583aacfc491c866f121f",
            "role": "support",
            "email_verified": True,
            "reset_token": None,
            "reset_token_expires": None
        }
    ]

    os.makedirs('../exported_json', exist_ok=True)
    with open('../exported_json/users.json', 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(users)} users to ../exported_json/users.json")

if __name__ == "__main__":
    generate_users()
