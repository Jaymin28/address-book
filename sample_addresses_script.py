import json
import sys

import requests

API_BASE_URL = "http://127.0.0.1:8000"

addresses = [
    {
        "name": "Home - Adajan",
        "street": "101 Adajan Road",
        "city": "Surat",
        "state": "Gujarat",
        "country": "India",
        "postal_code": "395009",
        "latitude": 21.2050,
        "longitude": 72.8140
    },
    {
        "name": "Office - Vesu",
        "street": "202 Vesu Main Road",
        "city": "Surat",
        "state": "Gujarat",
        "country": "India",
        "postal_code": "395007",
        "latitude": 21.1535,
        "longitude": 72.7860
    },
    {
        "name": "Friend - City Light",
        "street": "12 City Light Road",
        "city": "Surat",
        "state": "Gujarat",
        "country": "India",
        "postal_code": "395007",
        "latitude": 21.1760,
        "longitude": 72.8015
    },
    {
        "name": "Parents - Varachha",
        "street": "55 Varachha Main Road",
        "city": "Surat",
        "state": "Gujarat",
        "country": "India",
        "postal_code": "395006",
        "latitude": 21.2306,
        "longitude": 72.8410
    },
    {
        "name": "Warehouse - Pandesara",
        "street": "Plot 18, Pandesara GIDC",
        "city": "Surat",
        "state": "Gujarat",
        "country": "India",
        "postal_code": "394221",
        "latitude": 21.1330,
        "longitude": 72.8465
    },
    {
        "name": "Client - Katargam",
        "street": "32 Katargam Road",
        "city": "Surat",
        "state": "Gujarat",
        "country": "India",
        "postal_code": "395004",
        "latitude": 21.2245,
        "longitude": 72.8305
    },
    {
        "name": "Gym - Pal",
        "street": "401 Pal-Adajan Road",
        "city": "Surat",
        "state": "Gujarat",
        "country": "India",
        "postal_code": "395009",
        "latitude": 21.2155,
        "longitude": 72.8000
    },
    {
        "name": "Cafe - Ghod Dod Road",
        "street": "9 Ghod Dod Road",
        "city": "Surat",
        "state": "Gujarat",
        "country": "India",
        "postal_code": "395001",
        "latitude": 21.1775,
        "longitude": 72.8125
    },
    {
        "name": "Shop - Ring Road",
        "street": "78 Ring Road Market",
        "city": "Surat",
        "state": "Gujarat",
        "country": "India",
        "postal_code": "395002",
        "latitude": 21.1930,
        "longitude": 72.8330
    },
    {
        "name": "Relative - Dindoli",
        "street": "5 Dindoli Road",
        "city": "Surat",
        "state": "Gujarat",
        "country": "India",
        "postal_code": "394210",
        "latitude": 21.1480,
        "longitude": 72.8670
    }
]


def main() -> int:
    url = f"{API_BASE_URL}/address"
    headers = {"Content-Type": "application/json"}

    created_ids = []

    for i, addr in enumerate(addresses, start=1):
        print(f"Creating address {i}/{len(addresses)}: {addr['name']} ...", end=" ", flush=True)
        resp = requests.post(url, headers=headers, data=json.dumps(addr))

        if resp.status_code != 201:
            print(f"FAILED (status={resp.status_code})")
            try:
                print("Response:", resp.json())
            except Exception:
                print("Raw response:", resp.text)
            return True

        data = resp.json()
        created_ids.append(data.get("id"))
        print(f"OK (id={data.get('id')})")

    print("\nCreated address IDs:", created_ids)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())