import json


class HarFile():
    """
    Har File Spec - http://www.softwareishard.com/blog/har-12-spec/
    """
    def __init__(self):
        self.map = {
            "log": {
                "version": "1.2",
                "creator": {
                    "name": "urrlib2 interceptor",
                    "version": "0.0.1",
                    "comment": "hic est dracones"
                },
                "entries": []
            }
        }

    def _serialize_request_headers(self, request):
        headerEntries = []
        for key, value in request.header_items():
            headerEntries.append({
                "name": key,
                "value": value
            })
        return headerEntries

    def _serialize_response_headers(self, response):
        headerEntries = []
        for key, value in response.headers.dict.items():
            headerEntries.append({
                "name": key,
                "value": value
            })
        return headerEntries

    def _serialize_content(self, response):
        raw_data = response.read()
        info = response.info()
        return {
            "size": len(raw_data),
            "mimeType": info.getheader("Content-Type", "text/plain"),
            "text": raw_data
        }

    def _serialize_post_data(self, request):
        data = request.get_data()
        content_type = request.get_header("Content-Type", "text/plain")
        return {
            "mimeType": content_type,
            "params": [],
            "text": data,

        }

    def add_entry(self, request, response, startDate, time):
        entry = {
            "startedDateTime": startDate,
            "time": time,
            "request": {
                "method": request.get_method(),
                "url": request.get_full_url(),
                "httpVersion": "HTTP/1.1",
                "cookies": [],
                "headers": self._serialize_request_headers(request),
                "queryString": [],
                "postData": self._serialize_post_data(request),
                "headersSize": -1,
                "bodySize": -1,
            },
            "response": {
                "status": response.code,
                "statusText": response.msg,
                "httpVersion": "HTTP/1.1",
                "cookies": [],
                "headers": self._serialize_response_headers(response),
                "content": self._serialize_content(response),
                "redirectURL": "",
                "headersSize": -1,
                "bodySize": -1,
            },
            "cache": {},
            "timings": {},
        }
        self.map["log"]["entries"].append(entry)

    def contents(self):
        return json.dumps(self.map)

    def write_to_file(self, filepath):
        file = open(filepath, "w")
        file.write(self.contents())
        file.close()
