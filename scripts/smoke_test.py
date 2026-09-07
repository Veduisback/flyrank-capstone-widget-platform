import requests


BASE_URL = "http://localhost:8000"


def main():
    response = requests.get(
        f"{BASE_URL}/health"
    )

    print("HEALTH:", response.status_code)
    print(response.json())

    assert response.status_code == 200

    print("SMOKE TEST PASSED")


if __name__ == "__main__":
    main()