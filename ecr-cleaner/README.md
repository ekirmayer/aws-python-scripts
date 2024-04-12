# ECR Cleaner

Provide a temporary solution to clean un-used images based on age and last pull time.

This solution is required until AWS provide better ECR lifecycle management for repositories


## How to run 

By default, the script runs in Dry-Mode. To run in cleanup mode set DRYRUN=false

### Usind Docker

1. Build the image
    ```shell
    docker build -t ecr-cleaner .
    ```
1. Run the script
    ```shell
    docker run -it --rm -v ~/.aws:/home/nonroot/.aws -e AWS_DEFAULT_PROFILE=<profile> ecr-cleaner
    ```

### Change Settings

To change the settings, update these environment variables

| Name | Description | Default |
| ---- | ----------- | ------- |
| MAXPUSHDAYS | Check for images pushed before this amount of days | 90 |
| MAXPULLDAYS | Delete images which were not pull this mount of days| 90 |
| DRYRUN | Run in DRY-Mode| true |