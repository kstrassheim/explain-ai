from django.http import JsonResponse
from django.urls import path, re_path
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async
from azure.storage.blob import BlobServiceClient, ContainerClient
import json_lines
import json
import io
from dateutil.parser import isoparse
from datetime import datetime
from .auth import get_access_token_from_request, process_authorization
from os import path as ospath, makedirs

urls = [] 
from os import getenv
AZURE_STORAGE_CONNECTION_STRING=getenv("WEBAPP_AZURE_STORAGE_CONNECTION_STRING", None)
AZURE_STORAGE_CONTAINER_NAME=getenv("WEBAPP_AZURE_STORAGE_CONTAINER_NAME", None)
ITEMS_LIST_NAME = "items"
DELETED_IDS_LIST_NAME = 'deleted_ids'
LOCAL_STORAGE_FOLDER = ospath.join(ospath.abspath(ospath.join(ospath.dirname(__file__),"..")), 'db')

# cloud file read operations
def getCloudStorageDictObjects(path):
    blob_name = f'{path.lower()}.jsonl'
    blob_list_raw = ContainerClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING, container_name=AZURE_STORAGE_CONTAINER_NAME).list_blobs()
    blob_list = [b.name for b in blob_list_raw]
    if blob_name in blob_list:
        blob_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING).get_blob_client(container=AZURE_STORAGE_CONTAINER_NAME, blob=blob_name)
        byt = io.BytesIO() 
        byt.write(blob_client.download_blob().readall())
        byt.seek(0)
        items = json_lines.reader(byt)
        return [o for o in items]
    else:
        return []

def getLocalStorageDictObjects(path):
    file_name = ospath.join(LOCAL_STORAGE_FOLDER, f'{path.lower()}.jsonl') 
    if ospath.isfile(file_name):
        with open(file_name, 'rb') as file:
            byt = io.BytesIO() 
            byt.write(file.read())
            byt.seek(0)
            items = json_lines.reader(byt)
            return [o for o in items]
    else:
        return []

def appendDictObjectToCloudStorage(path, obj):
    obj_json_string = json.dumps(obj)
    # Create the BlobServiceClient object which will be used to create a container client
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=AZURE_STORAGE_CONTAINER_NAME, blob=f'{path.lower()}.jsonl')
    blob_client.upload_blob(f"{obj_json_string}\n", blob_type="AppendBlob")

def appendDictObjectToLocalStorage(path, obj):
    obj_json_string = json.dumps(obj)

    if not ospath.exists(LOCAL_STORAGE_FOLDER):
        makedirs(LOCAL_STORAGE_FOLDER)

    file_name = ospath.join(LOCAL_STORAGE_FOLDER, f'{path.lower()}.jsonl') 
    with open(file_name, "a+") as file_object:
        # Move read cursor to the start of file.
        file_object.seek(0)

        # Append text at the end of file
        file_object.write(obj_json_string)
        file_object.write("\n")

def appendItem(item):
    if AZURE_STORAGE_CONNECTION_STRING is not None:
        appendDictObjectToCloudStorage(ITEMS_LIST_NAME, item)
    else:
        appendDictObjectToLocalStorage(ITEMS_LIST_NAME, item)

def deleteItem(item):
    if item["id"] != None and item["id"] != -1:
        if AZURE_STORAGE_CONNECTION_STRING is not None:
            appendDictObjectToCloudStorage(DELETED_IDS_LIST_NAME, item["id"])
        else:
            appendDictObjectToLocalStorage(DELETED_IDS_LIST_NAME, item["id"])

def load_items():
    # get items from storage
    items = getCloudStorageDictObjects(ITEMS_LIST_NAME) if AZURE_STORAGE_CONNECTION_STRING else getLocalStorageDictObjects(ITEMS_LIST_NAME)
    deletedIds = getCloudStorageDictObjects(DELETED_IDS_LIST_NAME) if AZURE_STORAGE_CONNECTION_STRING else getLocalStorageDictObjects(DELETED_IDS_LIST_NAME)

    # sort by modified date
    items.sort(key=lambda o: isoparse(o["modified"]), reverse=True)

    # distinct and filter list
    newItems = []
    newIds = []
    for o in items:
        if o["id"] not in newIds and o["id"] not in deletedIds:
            newItems.append(o)
            newIds.append(o["id"])
    return newItems

# Remark the overloading of string parameter over same url
async def get_items(request):
    if request.method == "POST":
        access_token = get_access_token_from_request(request)
        login_name = process_authorization(access_token)["login"]
        # get params
        items = load_items()
        return await sync_to_async(JsonResponse)(items, safe=False)
    else:
        raise Exception(f"Method {request.method} not allowed")
urls+=[path('api/items', get_items)]

# Remark the overloading of string parameter over same url
async def get_item(request):
    if request.method == "POST":
        access_token = get_access_token_from_request(request)
        login_name = process_authorization(access_token)["login"]
        # get params
        post_data = json.loads(request.body.decode("utf-8"))
        id = post_data.get("id")
        items = [ o for o in load_items() if o["id"] == id]

        if len(items) > 0:
            return await sync_to_async(JsonResponse)(items[0], safe=False)
        else:
            raise Exception(f"Item not found")
    else:
        raise Exception(f"Method {request.method} not allowed")
urls+=[path('api/item', get_item)]

# Remark the overloading of string parameter over same url
async def delete_item(request):
    if request.method == "POST":
        access_token = get_access_token_from_request(request)
        login_name = process_authorization(access_token)["login"]
        # get params
        post_data = json.loads(request.body.decode("utf-8"))
        item = post_data.get("item")

        if item["id"] != None and item["id"] != -1:
            #ADD to deleted list
            if AZURE_STORAGE_CONNECTION_STRING is not None:
                appendDictObjectToCloudStorage(DELETED_IDS_LIST_NAME, item["id"])
            else:
                appendDictObjectToLocalStorage(DELETED_IDS_LIST_NAME, item["id"])
            #change also modified status to know who deleted this
            item["modified"] = datetime.now().isoformat()
            item["modifiedBy"] = login_name
            if AZURE_STORAGE_CONNECTION_STRING is not None:
                appendDictObjectToCloudStorage(ITEMS_LIST_NAME, item)
            else:
                appendDictObjectToLocalStorage(ITEMS_LIST_NAME, item)

            # send info to other clients
            await get_channel_layer().group_send("item", {
                "type": "item.info",
                "operation": "delete",
                "user": login_name,
                "item": item
            })
            return await sync_to_async(JsonResponse)(item)
        else:
            raise Exception(f"Deleting an empty item id is not possible")
    else:
        raise Exception(f"Method {request.method} not allowed")
urls+=[path('api/deleteitem', delete_item)]


