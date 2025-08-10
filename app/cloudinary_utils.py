# import cloudinary
# import cloudinary.uploader
import cloudinary
import cloudinary.uploader
from .config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

def upload_resume_file(file_obj, filename):
    # file_obj is starlette UploadFile .file
    res = cloudinary.uploader.upload_large(file_obj, resource_type="raw", public_id=filename)
    return res.get("secure_url")
