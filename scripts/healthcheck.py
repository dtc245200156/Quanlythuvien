import urllib.request
import urllib.error
import sys
import json
import os

def check_health():
    port = os.getenv('APP_PORT', '5000')
    url = f"http://127.0.0.1:{port}/health"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Docker-HealthCheck/1.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                if data.get('status') == 'healthy':
                    print("OK: Application and database are healthy.")
                    sys.exit(0)
                else:
                    print(f"DEGRADED: {data}")
                    sys.exit(1)
            else:
                print(f"FAILED: HTTP status {response.status}")
                sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Cannot connect to {url}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
        sys.exit(1)

if __name__ == '__main__':
    check_health()
