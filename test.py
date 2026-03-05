from export_builder import build_export_zip

class S3StorageMock:
    def get_bytes(self, key: str) -> bytes:
        return b"This is a mock image content from " + key.encode("utf-8")

incidents_data = [
    {"id": "INC-001", "branch": "강남본점", "status": "접수", "created_by": "홍길동", "service_no": "SV001"},
    {"id": "INC-002", "branch": "서초지점", "status": "해결완료", "created_by": "김철수", "service_no": "SV002"},
    {"id": "INC-003", "branch": "서초지점", "status": "접수", "created_by": "박영희", "service_no": "SV003"},
    {"id": "INC-004", "branch": "강남본점", "status": "해결완료", "created_by": "이민수", "service_no": "SV004"},
    {"id": "INC-005", "branch": "잠실지점", "status": "진행중", "created_by": "최성호", "service_no": "SV005"},
]

files_data = [
    {"storage_key": "s3://bucket/photo1.jpg", "incident_id": "INC-001", "category": "OUTSIDE", "original_name": "front.jpg"},
    {"storage_key": "s3://bucket/photo2.jpg", "incident_id": "INC-001", "category": "METER", "original_name": "meter.jpg"},
    {"storage_key": "s3://bucket/photo3.jpg", "incident_id": "INC-002", "category": "SCENE", "original_name": "broken.png"},
]

storage = S3StorageMock()

print("Generating ZIP...")
tmp_zip_file = build_export_zip(incidents_data, files_data, storage, categories_path="categories.yaml")

with open("export_complete.zip", "wb") as f_out:
    while True:
        chunk = tmp_zip_file.read(8192)
        if not chunk: break
        f_out.write(chunk)
tmp_zip_file.close()

print("ZIP generated successfully: export_complete.zip")
