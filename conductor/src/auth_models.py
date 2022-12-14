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

 Code to mange user authentification and authorization """
import re
from falcon import HTTP_400, HTTP_409, HTTP_404
import hashlib
import binascii
import os
import shutil
from .config import config
from .exceptions import AuthenticationError, ValidationError, ErrorDetail, DatasetError
from .graph import data_manager


class AlreadyExistsError(AuthenticationError):
    """ Auth record already exists """
    code = "AlreadyExistsError"
    response_code = HTTP_400


class AuthRecordNotFoundError(AuthenticationError):
    """ Record not found """
    code = "AuthRecordNotFoundError"
    response_code = HTTP_400


class WrongPasswordError(AuthenticationError):
    """ Passwords didn't match """
    code = "WrongPasswordError"
    response_code = HTTP_400


class PasswordValidationError(ValidationError):
    """ Password doesn't match required parameters """
    code = "PasswordValidationError"
    response_code = HTTP_400


class DatasetRemovalError(DatasetError):
    """ Error removing dataset """
    code = "DatasetRemovalError"
    response_code = HTTP_409


class DatasetCreationError(DatasetError):
    """ Error creating dataset """
    code = "DatasetCreationError"
    response_code = HTTP_409


class DatasetDoesNotExistError(DatasetError):
    """ Error getting dataset """
    code = "DatasetDoesNotExistError"
    response_code = HTTP_404


def hash_password(password):
    """ Hash password using salt in Flask """
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("ascii")
    pwdhash = hashlib.pbkdf2_hmac(
        "sha512",
        password.encode("utf-8"),
        salt,
        100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode("ascii")


def verify_password(password, check_password):
    """ Verify stored password against given """
    salt = password[:64]
    stored_password = password[64:]
    pwdhash = hashlib.pbkdf2_hmac(
        "sha512",
        check_password.encode("utf-8"),
        salt.encode("ascii"),
        100000)
    pwdhash = binascii.hexlify(pwdhash).decode("ascii")
    return pwdhash == stored_password


def check_password(password):
    """
    Check if password has at least 8 latin characters or digits and at least one capital letter

    :param password: password string
    :raises PasswordValidationError: if password desn't match the rules
    """
    description = None
    if len(password) < 8:
        description = ErrorDetail("NotEnoughCharacters", "password", "Password must have at least 8 characters")
    if not re.search("[0-9]", password):
        description = ErrorDetail("NotEnoughCharacters", "password", "Password must have at least one number")
    if not re.search("[A-Z]", password):
        description = ErrorDetail("NotEnoughCharacters", "password", "Password must have at least one capital letter")
    if description:
        raise PasswordValidationError("Password isn't secure enough!", "user password", [description])


class Role(object):
    """ Role model """

    def __init__(self, dataset):
        self.dataset = dataset
        self._vertex = None

    def get_role_vertex(self, name):
        """ Find role vertex by name """
        result = self.dataset.search_nodes([name])
        if len(result["not_found"]):
            raise AuthRecordNotFoundError("Role not found by name: " + name, "Role")
        self._vertex = result["found"][0]["properties"]
        return self

    def set_role_vertex(self, vertex):
        """ Sets a vertex for the role """
        self._vertex = vertex
        return self

    def get_rank(self):
        """ Get rank of the role """
        return self._vertex["rank"]

    def get_name(self):
        """ Get name of the role """
        return self._vertex["name"]

    def set_rank(self, rank):
        """ Set role's rank """
        self._vertex["rank"] = rank

    def set_name(self, name):
        """ Set role's name """
        self._vertex["name"] = name

    @classmethod
    def get_user_role(cls, dataset, username):
        """ Find role of user vertex """
        search_result = dataset.get_neighbors([username])
        if search_result["found"]:
            return cls(dataset).get_role_vertex(search_result["found"][0]["neighbors"][0]["neighbor_id"])
        raise AuthRecordNotFoundError(f"Role for user {username} not found!", "Role")

    @classmethod
    def get_all(cls, dataset):
        """ Get all roles """
        result = dataset.search_nodes(None, {"type": "Role"})
        if not len(result["found"]):
            raise AuthRecordNotFoundError("No Roles found!", "Role")
        return [cls(dataset).set_role_vertex(v["properties"]) for v in result["found"]]

    def add_role(self, name, rank):
        """ Commit role to the datastore or update its rank """
        try:
            self.get_role_vertex(name)
            raise AlreadyExistsError("Role already exists", "role name")
        except AuthRecordNotFoundError:
            self.dataset.save_nodes({name: {"name": name, "rank": rank, "type": "Role"}})
            self.get_role_vertex(name)
            return self


class User(object):
    """ User model """

    def __init__(self, dataset):
        self.dataset = dataset
        self._vertex = None
        self.role = None

    def get_username(self):
        """ Return user's username """
        return self._vertex["username"]

    def get_password(self):
        """ Return user's password """
        return self._vertex["password"]

    def get_role(self):
        """ Return user's role """
        if not self.role:
            self.role = Role.get_user_role(self.dataset, self.get_username())
        return self.role

    def get_folder_path(self):
        """ Get User's workspace folder path """
        username = self.get_username()
        return config["temp_file_folder"] / hashlib.md5(username.encode("utf-8")).hexdigest()

    def set_username(self, username):
        """ Set new username for user """
        if self.dataset.nodes.get(username):
            raise AlreadyExistsError(f"User by the name {username} already exists!", "User")
        del self.dataset.nodes[self.get_username()]
        temp_adj = self.dataset.adj_list[self.get_username()]
        del self.dataset.adj_list[self.get_username()]
        self.dataset.adj_list[username] = temp_adj
        for edge in temp_adj:
            self.dataset.edges[edge]["source"] = username
        self.dataset.nodes[username] = self._vertex
        return self

    def set_password(self, password):
        """ Set new password for user """
        self._vertex["password"] = hash_password(password)
        return self

    def set_role(self, role_name):
        """ Set new role for user """
        current_role = self.get_role()
        new_role = Role(self.dataset).get_role_vertex(role_name)
        found_edges = self.dataset.get_network([self.get_username(), current_role.get_name()])["edges"]
        if found_edges:
            found_edges[0]["target"] = role_name
        else:
            self.dataset.save_edges(
                [{"source": self.get_username(), "target": role_name, "properties": {"type": "has_privilege"}}])
        self.role = new_role
        return self

    @classmethod
    def get_all(cls, dataset):
        """ Get all users """
        found_users = dataset.search_nodes(None, {"type": "User"})
        initialized_users = []
        for user_vertex in found_users["found"]:
            temp_user = cls(dataset)
            temp_user._vertex = user_vertex["properties"]
            temp_user.get_role()
            initialized_users.append(temp_user)
        return initialized_users

    def store_user(self, username, password, role_name):
        """ Create new user and store him """
        found_vertex = self.dataset.search_nodes([username], {"type": "User"})
        if found_vertex["found"]:
            raise AlreadyExistsError(f"User by username {username} already exists!", "User")
        check_password(password)
        hashed_password = hash_password(password)
        self.dataset.save_nodes({
            username: {
                "username": username,
                "password": hashed_password,
                "datasets": set(),
                "type": "User"
            }
        })
        self._vertex = self.dataset.search_nodes([username], {"type": "User"})["found"][0]["properties"]
        self.role = Role(self.dataset).get_role_vertex(role_name)
        self.set_role(role_name)
        try:
            os.mkdir(self.get_folder_path())
        except FileExistsError:
            pass
        return self

    def authenticate(self, username, password):
        """ Find user and match password """
        self.identify(username)
        if not verify_password(self.get_password(), password):
            raise WrongPasswordError("Wrong password!", "User")
        return self

    def identify(self, username):
        """ Get user record by username """
        try:
            self._vertex = self.dataset.search_nodes([username], {"type": "User"})["found"][0]["properties"]
        except IndexError:
            raise AuthRecordNotFoundError(f"User by username {username} not found!", "username")
        self.get_role()
        return self

    def create_dataset(self, dataset_name, dataset_description, file_name, from_file=False):
        """ Creates a dataset for a user """
        result = data_manager.add_dataset(
            self.get_username() + dataset_name,
            dataset_description,
            str(self.get_folder_path() / file_name) if file_name else None,
            from_file=from_file)
        self._vertex["datasets"].add(dataset_name)
        if result["success"] == 0:
            raise DatasetCreationError.from_dataset_message(result)

    def remove_dataset(self, dataset_name):  # TODO implement dataset removal in manager
        """ Removes a dataset from user """
        try:
            del data_manager.datasets[self.get_username() + dataset_name]
            self._vertex["datasets"].remove(dataset_name)
        except KeyError:
            raise DatasetRemovalError(f"Couldn't find dataset by name {dataset_name}", "dataset name")

    def list_datasets(self):
        """ List all user's datasets """
        return list(self._vertex["datasets"])

    def get_dataset(self, dataset_name):
        """ Get dataset by name """
        try:
            return data_manager.datasets[self.get_username() + dataset_name]["data"]
        except KeyError:
            raise DatasetDoesNotExistError(f"Couldn't find dataset by name {dataset_name}", "dataset name")

    def delete(self):
        """ Delete user from datastore """
        shutil.rmtree(self.get_folder_path())
        result = self.dataset.delete_edges([(self.get_username(), self.get_role().get_name())], False)
        if result:
            raise AuthRecordNotFoundError("Relationship not found", "user")
        result = self.dataset.delete_nodes([self.get_username()])
        if result:
            raise AuthRecordNotFoundError("No user found", "username")
