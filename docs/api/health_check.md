# 헬스 체크 API

## 개요

이 API는 Antman 시스템의 상태를 확인하는 데 사용됩니다. 시스템이 정상적으로 작동하는지 확인하기 위한 간단한 엔드포인트입니다.

## 엔드포인트

`GET /health/`

## 요청 파라미터

없음

## 응답

### 성공 응답

**코드:** 200 OK

**내용 예시:**

```json
{
  "status": "ok"
}
```

### 오류 응답

일반적으로 이 엔드포인트는 오류를 반환하지 않습니다. 서버가 응답하지 않을 경우에만 실패합니다.

## 사용 예시

### cURL

```bash
curl -X GET http://localhost:8000/health/
```

### Python (requests)

```python
import requests

response = requests.get('http://localhost:8000/health/')
data = response.json()
print(data)  # {'status': 'ok'}
```

## 참고 사항

- 이 엔드포인트는 CI/CD 파이프라인에서 배포 성공 여부를 확인하는 데 사용됩니다.
- 로드 밸런서 및 쿠버네티스와 같은 컨테이너 오케스트레이션 시스템에서 헬스 체크로 사용됩니다.
- 모니터링 시스템에서 이 엔드포인트를 주기적으로 호출하여 시스템 상태를 확인할 수 있습니다.
