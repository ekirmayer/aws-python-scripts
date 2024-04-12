import os
import boto3
from datetime import datetime
import logging

maxPushDays = os.getenv("MAXPUSHDAYS", 90)
maxPullDays = os.getenv("MAXPULLDAYS", 90)
dryRun = os.getenv("DRYRUN", "True")
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
client = boto3.client('ecr')


def clean_registry():
    repo_paginator = client.get_paginator('describe_repositories')
    repo_page_iterator = repo_paginator.paginate()
    for repos in repo_page_iterator:
        for repository in repos["repositories"]:
            try:
                logger.info(f'Clean repository {repository}')
                clean_repository(repository["registryId"], repository["repositoryName"])
            except Exception as e:
                logger.error(f'Error cleaning repository {repository} =>> {e}')


def clean_repository(registry_id, repository_name):
    paginator = client.get_paginator('list_images')
    page_iterator = paginator.paginate(
        registryId=registry_id,
        repositoryName=repository_name,
        maxResults=99,
    )

    for page in page_iterator:
        if len(page['imageIds']) == 0:
            continue
        image_data = client.describe_images(
            registryId=registry_id,
            repositoryName=repository_name,
            imageIds=page['imageIds']
        )
        if len(image_data) > 0:
            image_ids_to_delete = get_images_to_delete(image_data)

            if len(image_ids_to_delete) > 0 and (dryRun.lower() == "false"):
                response = client.batch_delete_image(
                    registryId=registry_id,
                    repositoryName=repository_name,
                    imageIds=image_ids_to_delete
                )

                print(response)
            else:
                logger.info(len(image_ids_to_delete))


def get_images_to_delete(image_data):
    image_ids_to_delete = []
    for image in image_data['imageDetails']:
        time_between_insertion = datetime.now() - image["imagePushedAt"].replace(tzinfo=None)
        time_last_pull = datetime.now()
        image_pulled = True
        if 'lastRecordedPullTime' in image.keys():
            time_last_pull = datetime.now() - image["lastRecordedPullTime"].replace(tzinfo=None)
            logger.debug(f'Image {image["imageDigest"]}, Pushed at {image["imagePushedAt"]}, last pull time:  '
                        f'{image["lastRecordedPullTime"]}')
        else:
            image_pulled = False
            logger.debug(f'Image {image["imageDigest"]}, Pushed at {image["imagePushedAt"]}, last pull time: Never')

        if time_between_insertion.days > maxPushDays:
            if (not image_pulled) or (time_last_pull.days > maxPullDays):
                if "imageTags" in image.keys():
                    logger.info(f'Delete image {image["imageTags"]} The insertion and pull date are older than 30 days')
                else:
                    logger.info(f'Delete image {image["imageDigest"]} The insertion and pull date are older than 30 days')
                image_ids_to_delete.append({
                    'imageDigest': image['imageDigest']
                })

    return image_ids_to_delete


if __name__ == '__main__':
    logger.info(f'Run id Dry mode: {dryRun}')
    clean_registry()
