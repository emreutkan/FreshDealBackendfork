#!/usr/bin/env python3
import os
import json
import random
from datetime import datetime, timedelta, timezone

def generate_listings():
    """
    Generates 4 deterministic, meaningful listings for each of the 10 restaurants,
    with manual image-URL overrides, consume_within between 24 and 72 hours,
    fresh_score ≥70, varying count, and writes them to ../exported_json/listings.json.
    """

    # --- Manual overrides: put exact image URLs here by title ---
    IMAGE_URL_OVERRIDES = {
        "Simit & Çay": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2Fsimit.jpg?alt=media&token=f4285268-b312-4d55-9bb7-17370c50c3c0",
        "Poğaça Çeşitleri": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2Fborek.jpg?alt=media&token=1ca715f9-3ade-438a-950e-fc2f227e52b7",
        "Börek Tabağı": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2Fhattena-borek-tabagi-551.png?alt=media&token=daa41c52-d967-49c2-acef-7e4fcf510f94",
        "Revani": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2F4.jpg?alt=media&token=650ed242-3994-4015-9334-b506681e8c2c",

        "Menemen": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2F5.jpg?alt=media&token=dedcb6c7-d4ec-49a8-bc45-a2973e367de1",
        "French Toast": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2Ffrench_toast.jpg?alt=media&token=00a84870-65ff-4d4f-91c4-f4b24f736220",
        "Smoothie Kasesi": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2F7.jpg?alt=media&token=24955d31-0f39-4731-bb58-33ccf33e536a",
        "Simit Tabağı": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2F8.jpg?alt=media&token=bae6583f-da69-4843-8da7-097736c5a92e",

        "Adana Kebap": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2F10.jpg?alt=media&token=34ee0830-60fe-499b-81c2-6edc880f65aa",
        "Urfa Kebap": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2Fadanakebap.webp?alt=media&token=6d374515-5a38-45cd-abb6-cbc37f6a8910",
        "Lahmacun": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2Flahmacun.jpg?alt=media&token=86261b13-8b9a-4a74-8945-d65512ce8065",
        "Şiş Köfte": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2Fsebzeli-sis-kofte-yemekcom.jpg?alt=media&token=9c0b58a2-bd71-422d-b7a3-c6d32ffd3383",

        "Tavuk Dürüm": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2Ftavuk_doner.jpg?alt=media&token=afc8e42c-9336-4c24-87fa-516befecd572",
        "Et Dürüm": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2Fet_doner.jpg?alt=media&token=019de350-0714-4599-8f57-f72351a7ee90",
        "Sebzeli Dürüm": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2Fsebzeli_durum.jpg?alt=media&token=414dc051-0959-4b21-9d49-18221404e8fe",
        "Patates Kızartması": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2Fpatates_kizartmasi.jpg?alt=media&token=a75d0331-d316-4e3a-9f69-d51ddb3f03b7",

        "Izgara Levrek": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2Fizgara_levrek.jpg?alt=media&token=de4831d0-d90e-4ee1-a9bc-e06ce019b132",
        "Kalamar Tava": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2Fkalamar-tek.jpg?alt=media&token=fc841e63-f640-4d85-8165-a24198d6a4cc",
        "Karides Güveç": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2Fkarides_guvec.jpeg?alt=media&token=cd2c92b0-a9f2-4ab6-b23f-b86274bea978",
        "Balık Çorbası": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2Fbalik-corbasi.webp?alt=media&token=9cc07f0e-a350-40e3-ac46-ceb4642e783c",

        "Mercimek Çorbası": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2Fmercimek_corbasi.jpg?alt=media&token=fda93aac-d2f4-4b35-a516-003814c67944",
        "Izgara Köfte": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2FIzgara_Kofte-1260x839.webp?alt=media&token=d10b3602-3de7-46c6-8c9a-555b6eaf58ea",
        "Pilav Üstü Tavuk": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2Fpilav_ustu_tavuk.jpg?alt=media&token=c4fe68de-0bad-4f26-a722-16e01122fe6f",
        "Taze Fasulye": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2Ftaze_fasulye.webp?alt=media&token=e3152586-2259-475e-85d8-caac7157030f",

        "Kıymalı Pide": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2Fkiymali-pide-24.webp?alt=media&token=2a90783f-8e9b-405f-bb96-6867718fe21f",
        "Kaşarlı Pide": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2Fkasarli_pide.jpg?alt=media&token=4a2c439a-d7a3-4e5a-9461-989e72e7ce0b",
        "Karışık Pide": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2F27.jpg?alt=media&token=c8db9e7c-554a-4c5a-84f2-c6e7b03723ba",
        # "Lahmacun" already covered above

        "Adana Kebap Tabağı": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2F10.jpg?alt=media&token=34ee0830-60fe-499b-81c2-6edc880f65aa",
        "Urfa Kebap Tabağı": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2Furfa-kebap.jpg?alt=media&token=0f5d7901-8e74-4492-8608-c5c32f77ed5c",
        "Şalgam": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2F31.jpg?alt=media&token=3d82b60f-2ede-46bb-a8f6-e94c1fb1ea28",
        # "Lahmacun" reusable

        "California Roll": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2F33.jpg?alt=media&token=8dbdae4a-9091-4dbe-a009-866b702469ba",
        "Nigiri Somon": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2F34.jpg?alt=media&token=a4e01d64-ac4b-4683-a7b1-214a4ab39408",
        "Sashimi Çeşitleri": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2F35.jpg?alt=media&token=c17ca923-b261-477f-9563-6e4c15e9714f",
        "Gyudon": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2F36.jpg?alt=media&token=fa106384-272b-46c3-8410-300011b35996",

        "Enginar Tabağı": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2F37.jpg?alt=media&token=37d0a4a2-9dea-4ef9-8d07-29f6088790fe",
        "Falafel Menü": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2F38.jpg?alt=media&token=3f59ac05-0631-4283-8c65-e3dd14864091",
        "Quinoa Salatası": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2F39.jpg?alt=media&token=05296efe-3a02-4b86-8383-48e99f305701",
        "Humus & Lavaş": "https://firebasestorage.googleapis.com/v0/b/freshdeal-d691b.firebasestorage.app/o/listings%2F40.webp?alt=media&token=4aa5daff-36b6-4bea-afe8-703374c6d266"
    }

    # load restaurants
    with open('../exported_json/restaurants.json', 'r', encoding='utf-8') as f:
        restaurants = {r['id']: r for r in json.load(f)}

    # predefined menu items per restaurant: (title, description, base_count)
    items_map = {
        1: [("Simit & Çay",       "Geleneksel susamlı simit ve taze çay",          20),
            ("Poğaça Çeşitleri",   "Zeytinli, peynirli ve patatesli poğaça tabağı", 16),
            ("Börek Tabağı",       "Ispanaklı ve kıymalı börek karışık tabak",      12),
            ("Revani",             "İrmikli şerbetli revani tatlısı",               14)],
        2: [("Menemen",           "Domatesli, biberli bol yumurtalı menemen",      15),
            ("French Toast",       "Çilek soslu ve pudra şekerli Fransız tostu",    10),
            ("Smoothie Kasesi",    "Meyve ve granola ile hazırlanan smoothie kasesi", 8),
            ("Simit Tabağı",       "Farklı susam çeşitleriyle sunulan simit tabağı", 20)],
        # ... repeat for 3–10 exactly as you had, dropping the old price ...
        3: [("Adana Kebap",        "Acılı kıyma ile hazırlanmış Adana kebap",       10),
            ("Urfa Kebap",         "Baharatlı ama acısız Urfa kebap",               10),
            ("Lahmacun",           "Kıymalı ince hamur lahmacun",                   30),
            ("Şiş Köfte",          "Izgarada pişirilmiş nefis şiş köfte",          12)],
        4: [("Tavuk Dürüm",        "Izgara tavuk etli dürüm, domates ve marul",     15),
            ("Et Dürüm",           "Izgara dana eti, biber ve patlıcanlı dürüm",    12),
            ("Sebzeli Dürüm",      "Izgara sebzelerle hazırlanan hafif dürüm",      10),
            ("Patates Kızartması", "Sıcak ve çıtır patates kızartması",             20)],
        5: [("Izgara Levrek",      "Zeytinyağlı, limonlu ızgara levrek",           8),
            ("Kalamar Tava",       "Çıtır kalamar halkaları ve sarımsaklı mayo",    10),
            ("Karides Güveç",      "Baharatlı karides güveç, üzeri kaşarlı",       8),
            ("Balık Çorbası",      "Sıcak, kremalı balık çorbası",                  15)],
        6: [("Mercimek Çorbası",   "Klasik Anadolu mercimek çorbası",              20),
            ("Izgara Köfte",       "Ege usulü yoğurtlu ızgara köfte",              12),
            ("Pilav Üstü Tavuk",   "Terbiyeli tavuklu pilav",                      10),
            ("Taze Fasulye",       "Zeytinyağlı geleneksel taze fasulye",          15)],
        7: [("Kıymalı Pide",       "Kıymalı peynirli pide",                        15),
            ("Kaşarlı Pide",       "Bol kaşarlı klasik pide",                       15),
            ("Karışık Pide",       "Sucuk, kıyma ve kaşar karışık pide",            10),
            ("Lahmacun",           "El açması ince hamur lahmacun",                 30)],
        8: [("Adana Kebap Tabağı", "Acılı Adana kebap, lavaş ve salata",            10),
            ("Urfa Kebap Tabağı",  "Baharatlı Urfa kebap, lavaş ve salata",         10),
            ("Şalgam",             "Ev yapımı şalgam suyu",                         20),
            ("Lahmacun",           "Kıymalı ince hamur lahmacun",                   30)],
        9: [("California Roll",    "Surimi, avokado ve salatalıklı California roll",12),
            ("Nigiri Somon",       "Taze somon dilimi üzerinde pirinç nigiri",       10),
            ("Sashimi Çeşitleri",  "Somon ve ton balıklı sashimi tabağı",           8),
            ("Gyudon",             "Etli pirinç üstü Japon usulü gyudon",           10)],
        10:[("Enginar Tabağı",     "Zeytinyağlı enginar, dereotu ve limon",         12),
            ("Falafel Menü",       "Humus, falafel ve taze salata",                10),
            ("Quinoa Salatası",    "Sebzeli sağlıklı quinoa salatası",             8),
            ("Humus & Lavaş",      "Ev yapımı humus ve taze lavaş",                 15)],
    }

    consume_hours = [24, 36, 48, 72]
    fresh_scores   = [100.0, 90.0, 80.0, 70.0]

    listings = []
    listing_id = 1
    now = datetime.now(timezone.utc)
    created_at = now.strftime("%Y-%m-%d %H:%M:%S")

    for rest_id, menu_items in items_map.items():
        rest = restaurants[rest_id]
        for idx, (title, desc, base_count) in enumerate(menu_items):
            # 1) Pricing
            # pickup between 100–200
            if rest["pickup"]:
                pu = round(random.uniform(100, 200), 2)
            else:
                pu = None

            # delivery ~5–15% more
            if rest["delivery"] and pu is not None:
                dl = round(pu * random.uniform(1.05, 1.15), 2)
            else:
                dl = None

            # original at least 1.3× pickup, clamped to [250, 500]
            if pu is not None:
                orig_min = max(pu * 1.3, 250.0)
                op = round(random.uniform(orig_min, 500.0), 2)
            else:
                op = round(random.uniform(250.0, 500.0), 2)

            # 2) expire / freshness
            cw      = consume_hours[idx]
            expires = (now + timedelta(hours=cw)).strftime("%Y-%m-%d %H:%M:%S")
            fs      = fresh_scores[idx]

            # 3) count
            cnt = base_count + rest_id

            # 4) image URL override?
            manual = IMAGE_URL_OVERRIDES.get(title)
            if manual:
                img_url = manual
            else:
                img_url = f"https://example.com/images/listings/{listing_id}.jpg"

            # assemble
            listings.append({
                "id":                      listing_id,
                "restaurant_id":           rest_id,
                "title":                   title,
                "description":             desc,
                "image_url":               img_url,
                "count":                   cnt,
                "original_price":          op,
                "pick_up_price":           pu,
                "delivery_price":          dl,
                "consume_within":          cw,
                "consume_within_type":     "HOURS",
                "expires_at":              expires,
                "created_at":              created_at,
                "update_count":            0,
                "fresh_score":             fs,
                "available_for_pickup":    rest["pickup"],
                "available_for_delivery":  rest["delivery"],
            })

            listing_id += 1

    # write out
    os.makedirs('../exported_json', exist_ok=True)
    out = '../exported_json/listings.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(listings, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(listings)} listings to {out}")

if __name__ == "__main__":
    random.seed(42)   # reproducible
    generate_listings()
