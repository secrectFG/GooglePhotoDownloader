import os
import io
import shutil
import google.auth
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import pickle

# 修改这里以设置要下载照片的日期范围
start_date = "2023-04-01"
end_date = "2023-04-01"

def get_authenticated_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', 'https://www.googleapis.com/auth/photoslibrary.readonly')
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    try:
        service = build('photoslibrary', 'v1', credentials=creds, static_discovery=False)
        return service
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def download_photos(service):
    if not os.path.exists('google_photos'):
        os.makedirs('google_photos')



    filters = {
        "dateFilter": {
            "ranges": [
                {
                    "startDate": {"year": int(start_date[:4]), "month": int(start_date[5:7]), "day": int(start_date[8:10])},
                    "endDate": {"year": int(end_date[:4]), "month": int(end_date[5:7]), "day": int(end_date[8:10])}
                }
            ]
        }
    }

    nextpagetoken = 'Dummy'
    while nextpagetoken != '':
        nextpagetoken = '' if nextpagetoken == 'Dummy' else nextpagetoken
        results = service.mediaItems().search(
            body={"filters": filters, "pageSize": 100, "pageToken": nextpagetoken}).execute()
        items = results.get('mediaItems', [])
        nextpagetoken = results.get('nextPageToken', '')

        for item in items:
            url = item.get('baseUrl', '')
            filename = item.get('filename', '')
            print(f'Downloading {filename}')
            response = service._http.request(url)
            if response[0].status == 200:
                with open(os.path.join('google_photos', filename), 'wb') as f:
                    f.write(response[1])
            else:
                print(f'An error occurred: {response[0].reason}')


def main():
    service = get_authenticated_service()
    if service:
        download_photos(service)
    else:
        print("Authentication failed. Please check your client_secret.json file and try again.")

if __name__ == '__main__':
    main()