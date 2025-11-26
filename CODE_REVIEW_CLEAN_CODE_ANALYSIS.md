# 📋 CODE REVIEW - CLEAN CODE ANALYSIS

## 🔍 PHÂN TÍCH CODE THỪA & ĐỀ XUẤT TỐI ƯU

---

## 1️⃣ **JWT SERVICE - Code Thừa & Lặp Lại**

### 📍 Vị trí: `jwt_shared/jwt.py` & `Billing/service/jwt.py`

#### 🚨 **Vấn đề:**
- **Lặp lại code**: `jwt.py` được định nghĩa ở **2 chỗ**:
  - `jwt_shared/jwt.py` (version chính)
  - `Billing/service/jwt.py` (version lỗi thời)
- **Billing/service/jwt.py bị cắt ngắn**: Thiếu method `create_access_token()` và `decode_access_token()`
- Mọi service import từ `jwt_shared` nhưng `Billing` chứa bản sao không hoàn chỉnh

#### ✅ **Giải pháp:**
1. Xóa `Billing/service/jwt.py`
2. Tất cả service sử dụng: `from jwt_shared.jwt import jwt_services`
3. Cơ bản hóa JWT configuration trong `jwt_shared/jwt.py`

```python
# ✅ RECOMMENDED: jwt_shared/jwt.py
class jwt_services:
    # Load từ environment variables thay vì hardcode
    SECRET_KEY = os.getenv("SECRET_KEY", "SECRET_KEY_SOA")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "120"))
    
    # ... rest of code
```

---

## 2️⃣ **GET_CURRENT_USER - Code Thừa Ở Mọi Controller**

### 📍 Vị trí: 
- `Booking/controller/main.py`
- `Court/controller/main.py`
- `Facility/controller/main.py`
- `Notification/controller/main.py`
- `Report/controller/main.py`

#### 🚨 **Vấn đề:**
```python
# ❌ REPEATED 5+ TIMES ACROSS PROJECT
def get_current_user(token: str = Depends(jwt_services.oauth2_scheme)):
    try:
        payload = jwt_services.decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
```

#### ✅ **Giải pháp - Tạo Shared Utils:**
```python
# ✅ jwt_shared/dependencies.py (NEW FILE)
from fastapi import Depends, HTTPException
from jwt_shared.jwt import jwt_services

_jwt_service = jwt_services()

def get_current_user(token: str = Depends(_jwt_service.oauth2_scheme)):
    """Centralized user authentication dependency"""
    try:
        payload = _jwt_service.decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

# Usage trong controller:
from jwt_shared.dependencies import get_current_user

@app.get("/booking")
def list_bookings(user: dict = Depends(get_current_user)):
    # ...
```

---

## 3️⃣ **AUTH SERVICE - Duplicate Hash Password**

### 📍 Vị trí: `Auth/service/auth_ser.py` (Line 27)

#### 🚨 **Vấn đề:**
```python
# ❌ PASSWORD HASHING CALLED TWICE!
pass_hashed = self.jwt_service.get_hash(user.password)
new_user = user.copy()
pass_hashed = self.jwt_service.get_hash(user.password)  # ⬅️ DUPLICATE!
```

#### ✅ **Giải pháp:**
```python
# ✅ CLEAN CODE
def create_user(self, user: New_User_infor):
    try:
        user_exists = self.repo.get_user_by_email(user.email)
        if user_exists:
            raise Exception("User with this email already exists")
        
        pass_hashed = self.jwt_service.get_hash(user.password)
        self.repo.insert_user(user, pass_hashed)
        return {"status": "success", "message": "User created successfully"}
    except Exception as e:
        raise Exception(f"{e} -- from auth service")
```

---

## 4️⃣ **BOOKING SERVICE - Duplicate "Booking Not Found" Checks**

### 📍 Vị trí: `Booking/service/booking_service.py`

#### 🚨 **Vấn đề:**
```python
# ❌ DUPLICATE CHECK PATTERN
def delete_booking(self, booking_id: int) -> None:
    booking = self.repo.get_booking(booking_id)          # ⬅️ Check 1
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    deleted = self.repo.delete_booking(booking_id)
    if not deleted:                                        # ⬅️ Check 2 (REDUNDANT)
        raise HTTPException(status_code=404, detail="Booking not found")
```

#### ✅ **Giải pháp:**
```python
# ✅ CLEAN - Trust repository deletion response
def delete_booking(self, booking_id: int) -> None:
    booking = self.repo.get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Repository should handle deletion, just verify success
    deleted = self.repo.delete_booking(booking_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete booking")
```

---

## 5️⃣ **BOOKING SERVICE - Unused Event Emission**

### 📍 Vị trí: `Booking/service/booking_service.py` Line ~210

#### 🚨 **Vấn đề:**
```python
# ❌ COMMENTED CODE (DEAD CODE)
def _emit_booking_confirmed(self, booking: Booking) -> None:
    try:
        event_payload = { ... }
        # send_event("BOOKING_CONFIRMED", event_payload)  # ⬅️ COMMENTED!
    except Exception:
        pass
```

#### ✅ **Giải pháp:**
1. Nếu không dùng: **Xóa hoàn toàn**
2. Nếu cần dùng: **Uncomment và test**
3. **Không** để commented code trong production

---

## 6️⃣ **BOOKING SERVICE - Git Merge Conflict Markers**

### 📍 Vị trí: `Booking/service/booking_service.py` Line ~238

#### 🚨 **Vấn đề:**
```python
# ❌ GIT MERGE CONFLICT - NEVER SHOULD BE IN CODE!
<<<<<<< HEAD
    def get_time_slots_by_court(self, court_id: int) -> List[dict]:
=======
    def get_time_slots_by_court(self, court_id: int, user_id: int) -> List[dict]:
>>>>>>> 7f3ffaacc95ad918698a4d53a6a3079a1216f6d3
```

#### ✅ **Giải pháp:**
```python
# ✅ RESOLVE - Decide which signature to keep
def get_time_slots_by_court(self, court_id: int) -> List[dict]:
    try:
        slots = self.repo.get_time_slots_by_court(court_id)
        return slots
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 7️⃣ **NOTIFICATION SERVICE - Unused Instance Variable**

### 📍 Vị trí: `Notification/service/notification_service.py` Line 17

#### 🚨 **Vấn đề:**
```python
# ❌ UNUSED INSTANCE VARIABLE
def __init__(self):
    self._log = NotificationLog(  # ⬅️ NEVER USED!
        notification_id=1,
        user_email="demo@example.com",
        channel="email",
        status="sent",
        sent_at="2024-06-20T08:00:00Z",
    )

url = {
    "auth": "http://auth_service:8001"  # ⬅️ ALSO NEVER USED!
}
```

#### ✅ **Giải pháp:**
```python
# ✅ CLEAN
class NotificationService:
    """Stub notification service."""
    
    def __init__(self):
        pass  # Remove unused initialization
    
    @staticmethod
    def send_email_verify_register(user: dict):
        # ...
```

---

## 8️⃣ **NOTIFICATION SERVICE - Incorrect Return Statement**

### 📍 Vị trí: `Notification/controller/main.py` Line 37

#### 🚨 **Vấn đề:**
```python
# ❌ WRONG - Tuple instead of dict
try:
    return service.send_email_verify_register(user), {"status": "success"}
    # ⬆️ Returns tuple: (service_result, status_dict) instead of dict
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

#### ✅ **Giải pháp:**
```python
# ✅ CORRECT
@app.post("/notification/send-email-verify-register")
def send_email_verify_register(
    service: NotificationService = Depends(get_service),
    user: dict = Body(...)
):
    try:
        result = service.send_email_verify_register(user)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 9️⃣ **SESSION SERVICE - Complete Stub (No DB Integration)**

### 📍 Vị trí: `Session/service/session_service.py`

#### 🚨 **Vấn đề:**
```python
# ❌ ALL METHODS RETURN FAKE DATA
class SessionService:
    def __init__(self):
        self._sample = SessionInfo(...)  # Fake data
    
    def create_session(self, payload: SessionCreate) -> SessionInfo:
        return SessionInfo(session_id=55, ...)  # ⬅️ Hardcoded ID!
    
    def list_by_user(self, user_id: int) -> List[SessionInfo]:
        return [self._sample.copy(...), ...]  # ⬅️ Fake list!
```

#### ✅ **Giải pháp:**
**TODO**: Implement real database integration hoặc:
1. Có comment rõ ràng "STUB - Not implemented"
2. Hoặc implement properly với SessionRepository

```python
# ✅ BETTER - At least add comments
class SessionService:
    """Stub session management - TODO: Implement DB integration"""
    
    def __init__(self):
        # TODO: Implement real session repository
        pass
```

---

## 🔟 **COURT/FACILITY/REPORT - Duplicate Health Check**

### 📍 Vị trí: Mọi controller

#### 🚨 **Vấn đề:**
```python
# ❌ REPEATED IN EVERY SERVICE
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "court"}

@app.get("/db-test")
def db_test():
    if db.test_query():
        return {"status": "success", "message": "Database connection successful"}
    raise HTTPException(status_code=500, detail="Database connection failed")
```

#### ✅ **Giải pháp:**
```python
# ✅ shared_routes.py (NEW FILE)
def create_health_routes(app, service_name: str, db=None):
    @app.get("/health")
    def health_check():
        return {"status": "ok", "service": service_name}
    
    if db:
        @app.get("/db-test")
        def db_test():
            if db.test_query():
                return {"status": "success", "message": "Database connection successful"}
            raise HTTPException(status_code=500, detail="Database connection failed")

# Usage:
from jwt_shared.routes import create_health_routes
app = FastAPI()
db = connDB()
create_health_routes(app, "court", db)
```

---

## 1️⃣1️⃣ **BOOKING SERVICE - Exception Handling Too Generic**

### 📍 Vị trị: `Booking/service/booking_service.py`

#### 🚨 **Vấn đề:**
```python
# ❌ SWALLOW ALL EXCEPTIONS
def _emit_booking_confirmed(self, booking: Booking) -> None:
    try:
        # ...
    except Exception:  # ⬅️ Too broad!
        pass  # ⬅️ Silent failure

def _verify_facility_and_courts(...):
    except HTTPException:
        raise
    except Exception as exc:  # ⬅️ Generic catch
        raise HTTPException(status_code=502, detail=f"Cannot reach court service: {exc}")
```

#### ✅ **Giải pháp:**
```python
# ✅ SPECIFIC EXCEPTIONS
import logging

logger = logging.getLogger(__name__)

def _emit_booking_confirmed(self, booking: Booking) -> None:
    try:
        # ...
    except Exception as e:
        logger.warning(f"Failed to emit booking event: {e}")
        # Don't silently swallow - at least log it!

def _verify_facility_and_courts(...):
    try:
        # ...
    except httpx.TimeoutException as e:
        raise HTTPException(status_code=504, detail="Service timeout")
    except httpx.ConnectError as e:
        raise HTTPException(status_code=502, detail="Cannot reach service")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

---

## 1️⃣2️⃣ **REPORT SERVICE - Hardcoded URL & Poor Error Handling**

### 📍 Vị trí: `Report/service/report_service.py`

#### 🚨 **Vấn đề:**
```python
# ❌ HARDCODED URL - NO ENV VARIABLE
url = f"http://booking_api:8003/manager/court_id={court_id}/time_slots"

# ❌ GENERIC ERROR HANDLING
except ValueError:
    print("Response is not JSON")  # ⬅️ Print instead of logger
    return {}
```

#### ✅ **Giải pháp:**
```python
# ✅ CLEAN
import os
import logging

logger = logging.getLogger(__name__)

class ReportService:
    def __init__(self):
        self.booking_service_url = os.getenv("BOOKING_SERVICE_URL", "http://booking_api:8003")
    
    def get_day_playTime_report(self, court_id: int, token: str) -> Dict[str, float]:
        url = f"{self.booking_service_url}/manager/court_id={court_id}/time_slots"
        # ...
        except ValueError as e:
            logger.error(f"Invalid JSON response: {e}")
            return {}
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise HTTPException(status_code=502, detail="Booking service unavailable")
```

---

## 1️⃣3️⃣ **BILLING SERVICE - Multiple Return Formats**

### 📍 Vị trí: `Billing/service/billing_service.py`

#### 🚨 **Vấn đề:**
```python
# ❌ INCONSISTENT RETURN FORMATS
def initiate_payment(self, invoice_id: int, payload: PaymentRequest) -> dict:
    return {
        "invoice_id": invoice_id,
        "payment_method": payload.method,
        "status": "paid",
        "message": "Invoice marked as paid",
    }

def create_sepay_payment(self, invoice_id: int, payload: SePayCreatePaymentRequest) -> dict:
    result = self.sepay_service.create_payment(...)
    result["invoice_id"] = invoice_id
    return result  # Different structure!

def handle_sepay_return(self, query_params: Dict[str, str]) -> dict:
    return {
        "success": bool,
        "redirect_url": str,
        # ... different keys again
    }
```

#### ✅ **Giải pháp:**
```python
# ✅ USE PYDANTIC MODELS FOR CONSISTENT RESPONSES
from pydantic import BaseModel

class PaymentResponse(BaseModel):
    invoice_id: int
    status: str
    payment_url: Optional[str] = None
    transaction_id: Optional[str] = None
    message: str

def initiate_payment(self, ...) -> PaymentResponse:
    return PaymentResponse(
        invoice_id=invoice_id,
        status="paid",
        message="Invoice marked as paid"
    )
```

---

## 1️⃣4️⃣ **FACILITY SERVICE - Generic Exception Handling**

### 📍 Vị trí: `Facility/service/facility_service.py` Line 37

#### 🚨 **Vấn đề:**
```python
# ❌ TOO GENERIC
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
```

#### ✅ **Giải pháp:**
```python
# ✅ SPECIFIC HANDLING
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

except IntegrityError as e:
    raise HTTPException(status_code=400, detail="Duplicate entry or constraint violation")
except SQLAlchemyError as e:
    logger.error(f"Database error: {e}")
    raise HTTPException(status_code=500, detail="Database operation failed")
except ValueError as e:
    raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
```

---

## 📊 **SUMMARY TABLE**

| Issue | Location | Severity | Fix |
|-------|----------|----------|-----|
| Duplicate JWT | `Billing/service/jwt.py` | HIGH | Delete file |
| Repeated `get_current_user` | 5+ controllers | HIGH | Extract to `jwt_shared/dependencies.py` |
| Duplicate hash call | `Auth/service/auth_ser.py:27` | MEDIUM | Remove duplicate line |
| Redundant null check | `Booking/service/booking_service.py` | LOW | Remove redundant check |
| Commented code | `Booking/service/booking_service.py:210` | MEDIUM | Delete dead code |
| Git merge markers | `Booking/service/booking_service.py:238` | CRITICAL | Resolve conflict |
| Unused variables | `Notification/service/notification_service.py` | LOW | Remove |
| Wrong return type | `Notification/controller/main.py:37` | MEDIUM | Fix tuple return |
| Stub services | `Session/service/session_service.py` | HIGH | Add comments or implement |
| Duplicate health check | All controllers | MEDIUM | Extract to shared utility |
| Generic exceptions | Multiple services | MEDIUM | Use specific exception types |
| Hardcoded URLs | `Report/service/report_service.py` | HIGH | Use environment variables |
| Inconsistent responses | `Billing/service/billing_service.py` | MEDIUM | Use Pydantic models |

---

## 🎯 **ACTION PLAN - Priority Order**

### 🔴 **CRITICAL (Fix Immediately)**
1. ✅ Resolve Git merge conflict in `Booking/service/booking_service.py`
2. ✅ Delete `Billing/service/jwt.py` (duplicate)

### 🟠 **HIGH (Fix Soon)**
3. ✅ Extract `get_current_user()` to `jwt_shared/dependencies.py`
4. ✅ Replace hardcoded URLs with environment variables
5. ✅ Implement real Session service or document as stub

### 🟡 **MEDIUM (Clean Up)**
6. ✅ Remove duplicate hash call in Auth service
7. ✅ Fix Notification controller return type
8. ✅ Remove unused variables/commented code
9. ✅ Use Pydantic models for consistent responses
10. ✅ Add specific exception handling

### 🟢 **LOW (Nice to Have)**
11. ✅ Extract health check routes
12. ✅ Add logging instead of print statements
13. ✅ Add type hints consistently

---

## 💡 **BEST PRACTICES TO IMPLEMENT**

✅ **DRY (Don't Repeat Yourself)**
- Extract shared code to utility modules

✅ **Single Responsibility**
- Each service handles one concern

✅ **Explicit Error Handling**
- Use specific exceptions, not generic `Exception`

✅ **Configuration Management**
- Use environment variables for URLs, secrets

✅ **Consistent Response Format**
- Use Pydantic models for all API responses

✅ **Logging**
- Log errors properly, don't use `print()`

✅ **Code Cleanup**
- No commented code or dead code

✅ **Type Hints**
- Use consistent type hints across project

---

**Generated**: 2024
**Status**: Code Review Complete ✅
