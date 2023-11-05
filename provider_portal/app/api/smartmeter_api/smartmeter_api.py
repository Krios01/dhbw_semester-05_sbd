import cryptography
from cryptography import x509
from cryptography.hazmat._oid import NameOID
from app.db.influx.influx import InfluxDB


class SmartmeterAPI:
    def __init__(self, raw_cert, uid):
        self._uid = uid
        self._raw_cert = raw_cert

    @staticmethod
    def _get_common_name(cert):
        return cert[0].subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value

    def authenticate_smartmeter(self):
        try:
            client_cert = cryptography.x509.load_pem_x509_certificates(self._raw_cert.encode("utf-8"))
            common_name = self._get_common_name(client_cert)
            if common_name == self._uid:
                return True
            else:
                return False
        except:
            return False

    def add_measurements(self, datapoints):
        for datapoint in datapoints:
            timestamp = datapoint["timestamp"]
            value = datapoint["value"]
            uid = self._uid
            measurement = "consumption"
            influxdb = InfluxDB()
            influxdb.write(timestamp, value, uid, measurement)

        pass
