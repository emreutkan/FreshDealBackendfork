import json
import os

def generate_addresses():
    """
    Generates one fixed address per customer (user_id 3–7)
    and writes them to ../exported_json/customeraddresses.json.
    """
    addresses = [
        {
            "id": 1,
            "user_id": 3,
            "title": "Home",
            "longitude": 27.128900,
            "latitude": 38.423300,
            "street": "123 Sokak",
            "neighborhood": "Alsancak",
            "district": "Konak",
            "province": "İzmir",
            "country": "Türkiye",
            "postalCode": "35220",
            "apartmentNo": 12,
            "floor": 3,
            "doorNo": "5",
            "building_name": "Güneş Apt",
            "is_primary": True,
            "delivery_instructions": "Kapıya bırakın"
        },
        {
            "id": 2,
            "user_id": 4,
            "title": "Office",
            "longitude": 27.159700,
            "latitude": 38.420000,
            "street": "45 Cadde",
            "neighborhood": "Bostanlı",
            "district": "Karşıyaka",
            "province": "İzmir",
            "country": "Türkiye",
            "postalCode": "35560",
            "apartmentNo": 8,
            "floor": 5,
            "doorNo": "3",
            "building_name": "Deniz Apt",
            "is_primary": True,
            "delivery_instructions": "Zili çalmayın"
        },
        {
            "id": 3,
            "user_id": 5,
            "title": "Summer House",
            "longitude": 27.053000,
            "latitude": 38.452000,
            "street": "78 Bulvarı",
            "neighborhood": "Çiğli Merkez",
            "district": "Çiğli",
            "province": "İzmir",
            "country": "Türkiye",
            "postalCode": "35600",
            "apartmentNo": 2,
            "floor": 1,
            "doorNo": "1",
            "building_name": None,
            "is_primary": True,
            "delivery_instructions": "Arayın"
        },
        {
            "id": 4,
            "user_id": 6,
            "title": "Parents’ Home",
            "longitude": 27.163500,
            "latitude": 38.362200,
            "street": "10 Sokak",
            "neighborhood": "Atakent",
            "district": "Karşıyaka",
            "province": "İzmir",
            "country": "Türkiye",
            "postalCode": "35550",
            "apartmentNo": 5,
            "floor": 2,
            "doorNo": "7",
            "building_name": "Leylak Apt",
            "is_primary": True,
            "delivery_instructions": "Site güvenliğine bırakın"
        },
        {
            "id": 5,
            "user_id": 7,
            "title": "Gym",
            "longitude": 27.206000,
            "latitude": 38.410000,
            "street": "200 Cadde",
            "neighborhood": "Evka 3",
            "district": "Bornova",
            "province": "İzmir",
            "country": "Türkiye",
            "postalCode": "35100",
            "apartmentNo": 1,
            "floor": 1,
            "doorNo": "A",
            "building_name": "Yıldız Apt",
            "is_primary": True,
            "delivery_instructions": "Kapı numarası kapalı, aranın"
        }
    ]

    os.makedirs('../exported_json', exist_ok=True)
    with open('../exported_json/customeraddresses.json', 'w', encoding='utf-8') as f:
        json.dump(addresses, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(addresses)} addresses to ../exported_json/customeraddresses.json")

if __name__ == "__main__":
    generate_addresses()
