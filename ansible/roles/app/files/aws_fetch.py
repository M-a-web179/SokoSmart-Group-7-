#!/usr/bin/python3
import base64
import json
import sys
from urllib.parse import quote

import boto3

mode = sys.argv[1]
region = sys.argv[2]

if mode == "ecr-token":
    data = boto3.client("ecr", region_name=region).get_authorization_token()
    token = data["authorizationData"][0]["authorizationToken"]
    print(base64.b64decode(token).decode().split(":", 1)[1])
elif mode == "db-url":
    response = boto3.client("secretsmanager", region_name=region).get_secret_value(SecretId=sys.argv[3])
    secret = json.loads(response["SecretString"])
    user = quote(secret["username"], safe="")
    password = quote(secret["password"], safe="")
    print(f"postgresql://{user}:{password}@{secret['host']}:{secret['port']}/{secret['dbname']}?sslmode=require")
else:
    sys.exit(1)