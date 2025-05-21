def print_response_debug(response, endpoint_name=""):
    """Helper function to print detailed debug information about a response"""
    print(f"\n=== {endpoint_name} Response Debug ===")
    print(f"Status Code: {response.status_code}")
    print("Headers:", dict(response.headers))
    print("Response Data:", response.data.decode('utf-8'))
    try:
        json_data = response.get_json()
        print("JSON Data:", json_data)
    except Exception as e:
        print("Could not parse JSON:", str(e))
    print("=" * 50)