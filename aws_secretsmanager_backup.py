#!/usr/bin/env python3
#
# Author: Dan Farmer
# SPDX-License-Identifier: GPL-3.0-only

"""Export or import AWS Secrets Manager Secret names and values."""

import argparse
import logging
import re
import sys
import json
import boto3
from os import getenv

def main():
    """Export or import AWS Secrets Manager Secret names and values."""

    args = parse_args()

    region = args.region or getenv('AWS_REGION')
    profile_name = args.profile or getenv('AWS_PROFILE')

    boto_session = boto3.Session(profile_name=profile_name, region_name=region)
    secrets_client = boto_session.client('secretsmanager')

    regex_filter = None
    if args.filter:
        regex_filter = re.compile(args.filter)

    if args.mode == 'export':
        secrets = {'Secrets': []}
        for secret in sort_secrets(get_secrets(secrets_client), args.sort):
            if regex_filter and not regex_filter.search(secret['Name']):
                continue

            logging.info('Getting SecretString for %s', secret['Name'])
            secret_value = secrets_client.get_secret_value(SecretId=secret['Name'])['SecretString']
            secrets['Secrets'].append({'Name': secret['Name'],
                                       'SecretString': secret_value})
        logging.info('Writing Secrets to outfile %s', args.outfile.name)
        print(json.dumps(secrets, indent=2, sort_keys=True), file=args.outfile)

    elif args.mode == 'import':
        logging.info('Loading Secrets from infile %s', args.infile.name)
        secrets = json.load(args.infile)
        for secret in secrets['Secrets']:
            if regex_filter and not regex_filter.search(secret['Name']):
                continue

            try:
                logging.info('Updating Secret %s with SecretString %s',
                             secret['Name'], secret['SecretString'])
                secrets_client.update_secret(SecretId=secret['Name'],
                                             SecretString=secret['SecretString'])
            except secrets_client.exceptions.ResourceNotFoundException:
                logging.warning('Secret %s does not exist, creating it', secret['Name'])
                logging.info('Creating Secret %s with SecretString %s',
                             secret['Name'], secret['SecretString'])
                secrets_client.create_secret(Name=secret['Name'],
                                             SecretString=secret['SecretString'])

def sort_secrets(secrets, sort_mode):
    sort_key = lambda secret: secret['Name']
    if sort_mode == 'ascending':
        return sorted(secrets, key=sort_key)
    elif sort_mode == 'descending':
        return sorted(secrets, reverse=True, key=sort_key)
        
    return secrets

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

    Return args namespace
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('-m', '--mode', type=str, default='export', choices=['export', 'import'],
                        help='Export secrets (default) or import')
    parser.add_argument('-l', '--loglevel', type=str,
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Logging/output verbosity')
    parser.add_argument('-f', '--filter', type=str, default=None, metavar='REGEX',
                        help='Filter secrets to import/export using a supplied regular expression')
    parser.add_argument('-s', '--sort', type=str, default=None, choices=['ascending', 'descending'],
                        help='Sort secrets to export in ascending or descending order')

    file_group = parser.add_mutually_exclusive_group(required=False)
    file_group.add_argument('-i', '--infile', type=argparse.FileType('r'), default=sys.stdin,
                            help='Filename for import (default: stdin)')
    file_group.add_argument('-o', '--outfile', type=argparse.FileType('w'), default=sys.stdout,
                            help='Filename for export (default: stdout)')

    aws_group = parser.add_argument_group(title='AWS configuration options')
    aws_group.add_argument('-p', '--profile', type=str, default=None,
                           help='Override AWS credentials/configuration profile')
    aws_group.add_argument('-r', '--region', type=str, default=None,
                           help='Override AWS region')

    args = parser.parse_args()

    if args.loglevel:
        logging.basicConfig(level=args.loglevel)

    if args.mode == 'import' and args.outfile is not parser.get_default('outfile'):
        parser.error('--outfile cannot be used with --mode import')
    elif args.mode == 'export' and args.infile is not parser.get_default('infile'):
        parser.error('--infile cannot be used with --mode export')

    return args

if __name__ == '__main__':
    main()
