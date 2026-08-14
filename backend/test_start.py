import urllib.request
import urllib.error

try:
    req = urllib.request.Request('http://localhost:8000/api/camera/start', method='POST')
    res = urllib.request.urlopen(req)
    print("SUCCESS:", res.read().decode())
except urllib.error.HTTPError as e:
    print("HTTP ERROR CODE:", e.code)
    print("HTTP ERROR BODY:", e.read().decode())
except Exception as e:
    print("OTHER ERROR:", e)
