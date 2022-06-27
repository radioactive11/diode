from fastapi import APIRouter, Depends, HTTPException

from app.schema.touch import Touch

router = APIRouter()


@router.get("/")
def get_touch():
    return {"hello": "world"}


@router.post("/")
def post_touch(request_body: Touch):
    # return {"foo says": f"{request_body.foo}"}
    return {
        "ssh": r"""ccvjYDYp"6o#k6oE19X89#SgpA/_1xvJ^hcb0yyM6^BMD0_(?le(U14gM#HXPX#aRvsWE%E~~ZdO0v|PtVA^9JN-FBaE7RwZ<538HC)j^&\clw"""
    }
