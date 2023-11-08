import datetime
import logging
import os
from azure.storage.blob import BlobServiceClient

import azure.functions as func

def move_files(blob_service_client, src_container, dest_container, extensions):
    src_container_client = blob_service_client.get_container_client(src_container)
    dest_container_client = blob_service_client.get_container_client(dest_container)

    for blob in src_container_client.list_blobs():
        if any(blob.name.endswith(ext) for ext in extensions):
            src_blob_client = src_container_client.get_blob_client(blob.name)
            dest_blob_client = dest_container_client.get_blob_client(blob.name)
            dest_blob_client.start_copy_from_url(src_blob_client.url)
            src_blob_client.delete_blob()

def delete_files(blob_service_client, container, days, extensions):
    container_client = blob_service_client.get_container_client(container)

    for blob in container_client.list_blobs():
        if any(blob.name.endswith(ext) for ext in extensions):
            blob_properties = container_client.get_blob_client(blob.name).get_blob_properties()
            blob_last_modified = blob_properties['metadata']['Last-Modified']
            blob_last_modified_datetime = datetime.datetime.strptime(blob_last_modified, "%a, %d %b %Y %H:%M:%S GMT")
            age = datetime.datetime.utcnow() - blob_last_modified_datetime
            if age.days > days:
                container_client.get_blob_client(blob.name).delete_blob()

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    connection_string = "DefaultEndpointsProtocol=https;AccountName=okikisacc;AccountKey=eX1gHzJpMbBY2zTuefgNEEx/q9QsrPFmOCftmcGRQqXpYGYEOSzhgSyiszgPy49gYhFSu/FI2vCz+AStdTV7XA==;EndpointSuffix=core.windows.net"
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    move_files(blob_service_client, "primary", "secondary", ('.yml', '.xml'))
    delete_files(blob_service_client, "primary", 7, ('.yml', '.xml'))
