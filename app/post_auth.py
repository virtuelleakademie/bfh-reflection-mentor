# Required for JWT authentication
import jwt
from dotmap import DotMap
import asyncio
from typing import Optional
from starlette.requests import Request
import chainlit as cl

def post_auth_cb(request: Request) -> Optional[cl.User]:
    if not request:
        return None

    async def get_form():
        form = await request.form()
        return form

    async def get_json():
        json = await request.json()
        return json

    contentType = request.headers.get('Content-Type')

    if contentType == 'application/json':
        json = asyncio.run(get_json())
        result = json.get('formData')
    else:
        result = asyncio.run(get_form())

    if not result.get('token'):
        return None

    try:
        token = result.get('token')
        # Read rsa public key
        file = open('rs256.rsa.pub', mode='r')
        key = file.read()
        file.close()
        payload = jwt.decode(token, key, algorithms=["RS256"])
        payload = DotMap(payload)
        adminRoleKey = 'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Administrator'
        isAdmin = adminRoleKey in payload.platformContext.roles
        role = 'admin' if isAdmin else 'student'
        return cl.User(identifier=payload.user, metadata={"user": payload.user, "role": role, "provider": "header", "platform-id": payload.platformId, "courseid": payload.platformContext.context.id})
    except:
        print("JWT decode failed")
        return None
