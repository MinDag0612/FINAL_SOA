from fastapi import FastAPI, Request
import httpx

app = FastAPI()

# Định nghĩa các service backend
SERVICE_URLS = {
    "auth": "http://auth_api:8001",
    "session": "http://session_api:8006",
    "billing": "http://billing_api:8002",
    "booking": "http://booking_api:8003",
    "court": "http://court_api:8004",
    "facility": "http://facility_api:8005"
}

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(service: str, path: str, request: Request):
    """
    Proxy tất cả request tới service tương ứng.
    """
    if service not in SERVICE_URLS:
        return {"error": f"Service {service} not found"}

    # Lấy URL backend
    url = f"{SERVICE_URLS[service]}/{path}"

    # Lấy method, headers, body từ request gốc
    method = request.method
    headers = dict(request.headers)
    body = await request.body()

    # Gửi request tới service backend
    async with httpx.AsyncClient() as client:
        resp = await client.request(method, url, headers=headers, content=body)

    # Trả response về client
    return resp.json()
