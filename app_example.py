import os
import io
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from export_builder import build_export_zip

app = FastAPI(
    title="사건사고 다운로드 서버",
    description="관리자용 사건사고 데이터를 ZIP 형태로 비동기 압축하여 스트리밍합니다."
)

# ---- S3 Mock Class (Replace with actual Boto3 implementation) ----
class S3StorageMock:
    def get_bytes(self, key: str) -> bytes:
        return b"This is a mock image content from " + key.encode("utf-8")

@app.get("/api/export/incidents")
async def export_incidents_zip():
    """
    모든 데이터베이스 데이터를 긁어와서 incidents.xlsx 와 해당 사건의 
    카테고리별 S3 사진 파일들을 ZIP으로 묶어서 스트리밍합니다.
    (브라우저에서 바로 파일 다운로드가 시작됩니다.)
    """
    # 1. DB에서 데이터 조회 (예시)
    incidents_data = [
        {"id": "INC-001", "branch": "강남본점", "status": "접수", "created_by": "홍길동", "service_no": "SV001"},
        {"id": "INC-002", "branch": "서초지점", "status": "해결완료", "created_by": "김철수", "service_no": "SV002"},
        {"id": "INC-003", "branch": "서초지점", "status": "접수", "created_by": "박영희", "service_no": "SV003"},
        {"id": "INC-004", "branch": "강남본점", "status": "해결완료", "created_by": "이민수", "service_no": "SV004"},
        {"id": "INC-005", "branch": "잠실지점", "status": "진행중", "created_by": "최성호", "service_no": "SV005"},
    ]
    
    # 2. 사진 파일 목록 조회 (예시)
    files_data = [
        {"storage_key": "s3://bucket/photo1.jpg", "incident_id": "INC-001", "category": "OUTSIDE", "original_name": "front.jpg"},
        {"storage_key": "s3://bucket/photo2.jpg", "incident_id": "INC-001", "category": "METER", "original_name": "meter.jpg"},
        {"storage_key": "s3://bucket/photo3.jpg", "incident_id": "INC-002", "category": "SCENE", "original_name": "broken.png"},
    ]
    
    storage = S3StorageMock()

    # 3. 디스크/메모리 하이브리드 스트리밍 파일(SpooledTemporaryFile) 생성
    # 이 작업은 스레드풀을 통해 병렬로 S3 다운로드를 수행하므로 속도가 빠릅니다.
    temp_zip = build_export_zip(incidents_data, files_data, storage, categories_path="categories.yaml")

    # 4. 스트리밍 제너레이터 
    # (메모리에 다 올리지 않고 청크 단위로 클라이언트에 전송)
    def iter_file():
        with temp_zip as f:
            while chunk := f.read(8192):
                yield chunk

    # 5. 브라우저 응답 헤더 설정
    headers = {
        'Content-Disposition': 'attachment; filename="incidents_export.zip"'
    }

    return StreamingResponse(
        iter_file(), 
        media_type="application/x-zip-compressed", 
        headers=headers
    )

if __name__ == "__main__":
    print("🚀 서버 실행: http://127.0.0.1:8000")
    print("👉 다운로드 테스트: http://127.0.0.1:8000/api/export/incidents")
    uvicorn.run("app_example:app", host="127.0.0.1", port=8000, reload=True)
