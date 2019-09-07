#!/usr/bin/env python3
#
# Author: Dan Farmer
# SPDX-License-Identifier: GPL-3.0-only

"""Dump AWS Secrets Manager Secret names and values to stdout."""

import argparse
import logging
import boto3

def main():
    """Dump AWS Secrets Manager Secret names and values to stdout."""

    args = parse_args()
    if args.loglevel:
        logging.basicConfig(level=args.loglevel)

    secrets_client = boto3.client('secretsmanager')

    for secret in get_secrets(secrets_client):
        print(secret['Name'])

def get_secrets(secrets_client):
    """Iterator for secrets.

    Yield secrets
    """
    secrets_paginator = secrets_client.get_paginator('list_secrets')
    pages = secrets_paginator.paginate()
    for page in pages:
        for secret in page['SecretList']:
            yield secret

def parse_args():
    """Create arguments and populate variables from args.

    Return args namespace"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--loglevel', type=str,
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Logging/output verbosity')
    return parser.parse_args()

if __name__ == '__main__':
    main()
