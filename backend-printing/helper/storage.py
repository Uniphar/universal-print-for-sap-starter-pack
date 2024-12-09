"""Storage client to interact with the Azure Storage Account."""

import os
from uuid import uuid4
import json
from azure.storage.queue import QueueMessage
from helper.azure_client import AzureClient
from helper.constants import MAX_ITEMS_TO_FETCH, MESSAGE_EXPIRY_TIME


class StorageQueueClient(AzureClient):
    def _store_document_to_blob(self, blob_guid, message):
        """Store the document to the blob

        Args:
            blob_guid (string): container guid
            document (dict): document to store
        """
        try:
            blob_client = self.get_blob_client(blob_guid)
            blob_client.upload_blob(data=json.dumps(message).encode("utf-8"))
            return blob_client.url
        except Exception as e:
            raise e

    def _get_document_from_blob(self, message_content):
        """Get the document from the blob

        Args:
            message_content (dict): blob guid and url
        """
        try:
            blob_url, blob_guid = (
                message_content["blob_url"],
                message_content["blob_guid"],
            )
            blob_client = self.get_blob_client(blob_guid)
            blob_client.from_blob_url(blob_url)
            return blob_client.download_blob().readall()
        except Exception as e:
            raise e

    def send_message(self, message):
        """Send a message to the queue

        Args:
            message (string): message to send
        """
        try:
            encoded_message = json.dumps(message).encode("utf-8")
            # if message size is greater than 60KB, store it in blob
            # and send the blob url in the message
            if len(encoded_message) > 60 * 1024:
                blob_guid = str(uuid4())
                blob_url = self._store_document_to_blob(blob_guid, message)
                encoded_message = json.dumps(
                    {"blob_guid": blob_guid, "blob_url": blob_url}
                ).encode("utf-8")
            send_message_response = self.storage_queue_client.send_message(
                content=encoded_message,
                time_to_live=MESSAGE_EXPIRY_TIME,
            )
            return send_message_response
        except Exception as e:
            raise Exception(f"Error occurred while sending message: {e}")

    def receive_messages(self) -> list[dict]:
        """Receive messages from the queue

        Returns:
            list[QueueMessage]: list of messages
        """
        return_messages = []
        try:
            raw_messages = self.storage_queue_client.receive_messages(
                max_messages=MAX_ITEMS_TO_FETCH
            )
            for messages in raw_messages.by_page():
                for message in messages:
                    message_content = json.loads(
                        message.content.decode("utf-8").replace("'", '"')
                    )
                    if "blob_guid" in message_content:
                        blob_data = self._get_document_from_blob(message_content)
                        message_content = json.loads(
                            blob_data.decode("utf-8").replace("'", '"')
                        )
                    return_messages.append((message, message_content))
            return return_messages
        except Exception as e:
            raise Exception(f"Error occurred while receiving messages: {e}")

    def delete_message(self, message):
        """Delete a message from the queue

        Args:
            message (QueueMessage): message to delete
        """
        try:
            return self.storage_queue_client.delete_message(
                pop_receipt=message.pop_receipt, message=message
            )
        except Exception as e:
            raise Exception(f"Error occurred while deleting message: {e}")


class TableStorageClient(AzureClient):
    def put_entity(self, table_name, entity):
        """Put an entity to the table

        Args:
            table_name (string): table name
            entity (dict): entity to put
        """
        try:
            return self.table_service_client.upsert_entity(entity=entity)
        except Exception as e:
            raise Exception(f"Error occurred while putting entity: {e}")
