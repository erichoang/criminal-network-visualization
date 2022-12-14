"""
=================================== LICENSE ==================================
Copyright (c) 2021, Consortium Board ROXANNE
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

Neither the name of the ROXANNE nor the
names of its contributors may be used to endorse or promote products
derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY CONSORTIUM BOARD ROXANNE ``AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL CONSORTIUM BOARD TENCOMPETENCE BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
==============================================================================

 Helpers for authorization """
import jwt
from datetime import datetime, timedelta
from falcon import HTTP_401, HTTP_400
from ..config import config
from ..exceptions import AuthenticationError


class InvalidTokenError(AuthenticationError):
    """ Error in token structure """
    code = "InvalidTokenError"
    response_code = HTTP_400


class TokenExpiredError(AuthenticationError):
    """ Token is expired """
    code = "TokenExpiredError"
    response_code = HTTP_401


ALGORITHM = "HS256"


def create_token(claims: dict):
    """
    Create token with claims. Adds iat and exp claims to token.

    :param claims: claims to be stored in the token
    :returns: str token
    """
    token_payload = {
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=config["JWT_ACCESS_TOKEN_EXPIRES"])
    }
    token_payload.update(claims)
    return jwt.encode(
        token_payload,
        config["JWT_SECRET_KEY"],
        algorithm=ALGORITHM
    ).decode()


def read_token(token, required_claims=None):
    """
    Decode token and get claims

    :param token: token to be decoded and validated
    :param required_claims: claims, that must be present in the token
    :returns: dict of claims from token
    :raises TokenExpiredError: error when token is expired
    :raises InvalidTokenError: error when token could not be decoded, or doesn't have proper claims
    """
    try:
        claims = jwt.decode(token, config["JWT_SECRET_KEY"], algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError as err:
        raise TokenExpiredError(str(err), "token claims")
    except jwt.InvalidTokenError as err:
        raise InvalidTokenError(str(err), "token")
    if required_claims:
        for claim_name in required_claims:
            if claim_name not in claims:
                raise InvalidTokenError(f"Malformed token, claim {claim_name} not found!", "token claims")
    return claims
