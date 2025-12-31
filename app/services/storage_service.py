import asyncio
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from google.api_core.exceptions import BadRequest
from google.cloud import storage
from google.oauth2 import service_account

from app.core.config import settings


class StorageService:
    async def upload_listing_image(self, file: UploadFile, listing_id: uuid.UUID) -> str:
        raise NotImplementedError


class GCSStorageService(StorageService):
    def __init__(self) -> None:
        credentials = None
        if settings.sa_key_path:
            credentials = service_account.Credentials.from_service_account_file(
                Path(settings.sa_key_path)
            )

        self.client = storage.Client(credentials=credentials)
        self.bucket_name = settings.bucket_name

    async def upload_listing_image(self, file: UploadFile, listing_id: uuid.UUID) -> str:
        if not self.bucket_name:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Storage bucket is not configured",
            )

        destination_path = f"listings/{listing_id}/{uuid.uuid4()}-{file.filename}"
        return await asyncio.to_thread(self._upload_file, file, destination_path)

    def _upload_file(self, file: UploadFile, destination_path: str) -> str:
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(destination_path)

        file.file.seek(0)
        blob.upload_from_file(file.file, content_type=file.content_type)

        if self._bucket_allows_object_acls(bucket):
            try:
                blob.make_public()
            except BadRequest as exc:
                if "uniform bucket-level access" not in str(exc).lower():
                    raise

        return blob.public_url

    def _bucket_allows_object_acls(self, bucket: storage.Bucket) -> bool:
        try:
            bucket.reload()
        except Exception:
            return True

        iam_configuration = bucket.iam_configuration
        return not bool(
            getattr(iam_configuration, "uniform_bucket_level_access_enabled", False)
        )
