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

 Test authorization helpers """
import jwt
import pytest
from datetime import datetime, timedelta
from ....conductor.src.helpers.auth_helpers import create_token, read_token, ALGORITHM, InvalidTokenError, TokenExpiredError
from ....conductor.src.config import config


def test_create_token_should_create_token_with_given_claims():
    """ passed claims into create_token should be in token """
    claim_name = "user_id"
    claims = {
        claim_name: 123
    }
    token = create_token(claims)
    decoded_claims = jwt.decode(token, config["JWT_SECRET_KEY"], algorithms=[ALGORITHM])
    assert claim_name in decoded_claims
    assert claims[claim_name] == decoded_claims[claim_name]


def test_create_token_should_add_issue_date_to_token():
    """ create_token should create iat claim """
    token = create_token({})
    decoded_claims = jwt.decode(token, config["JWT_SECRET_KEY"], algorithms=[ALGORITHM])
    assert "iat" in decoded_claims


def test_create_token_should_add_expiration_date_to_token():
    """ create_token should add exp claim """
    token = create_token({})
    decoded_claims = jwt.decode(token, config["JWT_SECRET_KEY"], algorithms=[ALGORITHM])
    assert "exp" in decoded_claims


def test_read_token_should_decode_token_and_return_dictionary_of_claims():
    """ read_token should return decoded claims """
    payload = {
        "user_id": 123
    }
    token = jwt.encode(payload, config["JWT_SECRET_KEY"], algorithm=ALGORITHM)
    decoded_claims = read_token(token)
    assert payload == decoded_claims


def test_read_token_should_raise_TokenExpiredError_if_token_expired():
    """ read_token should raise TokenExpiredError when exp > iat """
    payload = {
        "user_id": 123,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() - timedelta(minutes=10)
    }
    token = jwt.encode(payload, config["JWT_SECRET_KEY"], algorithm=ALGORITHM)
    with pytest.raises(TokenExpiredError):
        decoded_claims = read_token(token)


def test_read_token_should_raise_InvalidTokenError_if_token_improperly_signed():
    """ read_token should raise InvalidTokenError when different properties used during encoding """
    payload = {
        "user_id": 123,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=10)
    }
    token = jwt.encode(payload, "", algorithm=ALGORITHM)
    with pytest.raises(InvalidTokenError):
        decoded_claims = read_token(token)


def test_read_token_should_raise_InvalidTokenError_if_token_doesnt_have_required_claims():
    """ read_token should raise InvalidTokenError if required claim not found """
    payload = {
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=10)
    }
    token = jwt.encode(payload, config["JWT_SECRET_KEY"], algorithm=ALGORITHM)
    with pytest.raises(InvalidTokenError):
        read_token(token, ["user_id"])
