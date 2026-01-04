import jwt

from core.config import SECRET_JWT_KEY
print(SECRET_JWT_KEY)


ControllerPermissions = {"dashboardadmin": ["admin"]}

def getPermissions(token):
    context = {}
    flag = False

    try:
        decoded_token = jwt.decode(
            token,
            SECRET_JWT_KEY,
            algorithms=["HS256"]
        )
        flag = True

    except jwt.ExpiredSignatureError:
        context["error"] = "Token expired"

    except jwt.InvalidTokenError:
        context["error"] = "Invalid token"

    return flag, context

def canAccessController(token, controller_name):
    has_permission = False
    flag, context = getPermissions(token)
    if controller_name not in ControllerPermissions:
        return True
    if flag:
        decoded_token = jwt.decode(
            token,
            SECRET_JWT_KEY,
            algorithms=["HS256"]
        )
        role = decoded_token["role"]
        if controller_name in ControllerPermissions:
            if role in ControllerPermissions[controller_name]:
                has_permission = True

    return has_permission


print(canAccessController("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc1NTkzOTIsInVzZXJuYW1lIjoiWW9zZWYiLCJyb2xlIjoiYWRtaW4ifQ.Jv_qdLT4uHsOeWw1taZCWXTXxLWEisIR1Ca50BnU4Kk", "dashboardadmin"))
