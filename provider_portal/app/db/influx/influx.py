from datetime import timezone, timedelta
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from config import config


class InfluxDB:
    def __init__(self):
        self._token = config.InfluxConfig.INFLUX_TOKEN
        self._bucket = config.InfluxConfig.INFLUX_BUCKET
        self._provider = config.InfluxConfig.INFLUX_PROVIDER
        self._url = config.InfluxConfig.INFLUX_URL
        self._client = InfluxDBClient(url=self._url, token=self._token, org=self._provider)

        bucket_api = self._client.buckets_api()
        if not bucket_api.find_bucket_by_name(self._bucket):
            bucket_api.create_bucket(bucket_name=self._bucket, org=self._provider)

    def read(self, start_time, end_time, interval, uid, measurement):
        query = f'''
                    from(bucket: "{self._bucket}")
                    |> range(start: {start_time}, stop: {end_time})
                    |> filter(fn: (r) => r["_measurement"] == "{measurement}" and r["uid"] == "{uid}")
                    |> aggregateWindow(every: {interval}, fn: mean)
                    |> fill(column: "_value", usePrevious: true)
                '''
        query_api = self._client.query_api()
        tables = query_api.query(org=self._provider, query=query)

        data = []

        for table in tables:
            for record in table.records:
                data.append({
                    "time": record.get_time().isoformat(),
                    "value": record.get_value(),
                })

        return data

    def write(self, timestamp, value, uid, measurement):
        point = {
            "measurement": measurement,
            "tags": {
                "uid": uid
            },
            "time": timestamp,
            "fields": {
                "float_value": value
            },
        }
        try:
            write_api = self._client.write_api(write_options=SYNCHRONOUS)
            write_api.write(self._bucket, self._provider, point)
            return True
        except:
            return False

    '''
    def delete(self, uid):
        try:
            delete_api = self._client.delete_api()

            # Get the current time
            current_time = datetime.now()
            new_time = current_time + timedelta(minutes=60)
            rfc3339_format = '%Y-%m-%dT%H:%M:%SZ'
            new_time_rfc3339 = new_time.strftime(rfc3339_format)
            print(new_time_rfc3339, file=sys.stderr)

            # Executing delete request
            delete_api.delete("1970-01-01T00:00:00Z", new_time_rfc3339, '_measurement="consumption"', f'uid="{uid}"', org=self._provider, bucket=self._bucket)

            return True
        except Exception as e:
            print(f"Error deleting data: {e}")
            return False
    '''