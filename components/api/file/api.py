from pydantic import BaseModel

import os
from xmlrpc.client import boolean
import cv2
import logging
import secrets
import base64

from fastapi import APIRouter, File, status, UploadFile
from fastapi.responses import JSONResponse
from typing import List

from components.utils.file import createDirectory, deletefolder, expiration_date
from components.utils.exception import FailExceptionHandler
from components.triton.inference import ModelInferencer
from components.core.config import SERVER_IP, SERVER_PORT
# from app.api.errors.exception import SuccessSrFolder, FolderInNoFile, NoExistFolderPass


log = logging.getLogger("uvicorn")
router = APIRouter(prefix="/esp/sync_api/v2", tags=["SR"])


@router.post(
    "/SR_start",
    summary="파일 업로드 -> 로컬 저장 -> SR -> Return SR URL ",
    status_code=200,
)
async def create_upload_files(files: List[UploadFile] = File(...)):
    download_filelist = []
    event_key = secrets.token_hex(nbytes=16)
    origin_image_path = f"/app/static/origin_images/{event_key}"
    sr_image_path = f"/app/static/sr_images/{event_key}"

    createDirectory(origin_image_path)
    createDirectory(sr_image_path)

    expiration_date('/app/static/origin_images')
    expiration_date('/app/static/sr_images')

    trtis_server = ModelInferencer("localhost:8001")

    if len(files) != 0:
        for file in files:

            file_path = os.path.join(origin_image_path, file.filename)
            output_file_name = f"{file.filename.split('.')[0]}_SR.{file.filename.split('.')[-1]}"

            if file.filename.split('.')[-1].lower().endswith(
                ("png", "jpg")
            ):

                try:
                    contents = await file.read()
                    with open(file_path, "wb") as fp:
                        fp.write(contents)
                except:
                   deletefolder(origin_image_path)
                   return FailExceptionHandler(f'{file.filename} 파일 업로드 요청에 실패하였습니다.', '파일 업로드 실패.', 500)

                try:
                    image = cv2.imread(file_path)
                except:
                    deletefolder(origin_image_path)
                    return FailExceptionHandler(f'{file.filename} 파일 로드에 실패하였습니다.', '파일 로드 실패.', 500)

                try:
                    output_data = trtis_server.infer(image)
                except:
                    deletefolder(origin_image_path)
                    return FailExceptionHandler(f'{file.filename} 파일의 SR 요청에 실패하였습니다.', 'Super Resolution 요청에 실패.', 500)

                try:
                    cv2.imwrite(
                        f"{sr_image_path}/{output_file_name}", output_data)

                    _, buffer = cv2.imencode(os.path.splitext(file.filename)[1], output_data)
                    binary = base64.b64encode(buffer)
                    
                    filelist = {
                        "filename": file.filename,
                        "file": str(binary)
                    }

                    download_filelist.append(filelist)
                except:
                    deletefolder(origin_image_path)
                    deletefolder(sr_image_path)
                    return FailExceptionHandler(f'{file.filename} SR 완료된 파일의 업로드 요청에 실패하였습니다.', 'SR 완료된 파일의 업로드 요청에 실패.', 500)

            else:
                return FailExceptionHandler(f"현재 업로드된 파일형식({file.filename.split('.')[-1]}), 지원 가능한 확장자(jpg, png).", '파일 형식이 맞지 않습니다.', 500)

    return JSONResponse(content=download_filelist)
