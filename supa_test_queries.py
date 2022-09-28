
from supabase import create_client, Client
from decouple import config


class supa():
    def __init__(self) -> None:
        self.url = config('URL')
        self.key = config('API_KEY')
        self.client: Client = create_client(self.url, self.key)

    def getRecordsBy(self, table: str = None, column: str = None, value=None):
        query = self.client.table('Products').select(
            '*').filter(column, 'like', value).execute()

        return query


s = supa()
print(s.getRecordsBy())
