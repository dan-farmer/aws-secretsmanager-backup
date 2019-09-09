# aws-secretsmanager-backup
Simple dump/import backup for AWS Secrets Manager Secrets

## Requirements
* Python 3.6+
* [boto3](https://pypi.org/project/boto3/)
* [Configured AWS SDK credentials and default region](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration)
  * [Full documentation of credential configuration methods](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html)

## Usage
```
aws_secretsmanager_backup.py [-h] [-m {export,import}]
                             [-i INFILE | -o OUTFILE]
                             [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]

optional arguments:
  -h, --help            show this help message and exit
  -m {export,import}, --mode {export,import}
                        Export secrets (default) or import
  -i INFILE, --infile INFILE
                        Filename for import (default: stdin)
  -o OUTFILE, --outfile OUTFILE
                        Filename for export (default: stdout)
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Logging/output verbosity
```
