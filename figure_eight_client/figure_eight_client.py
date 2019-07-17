import json
from time import sleep

import requests

try:
    # python 2 optimization
    from cStringIO import StringIO
except:
    try:
        # python 2 fallback
        from StringIO import StringIO
    except:
        # python 3 fallback
        from io import StringIO

from zipfile import ZipFile


class FigureEightClient:
    endpoint = "https://api.figure-eight.com/v1/{path}?key={api_key}"
    api_key = ""

    def __init__(self, api_key, endpoint=None):
        if api_key is None or api_key is '':
            raise Exception("api_key not valid")

        self.api_key = api_key

        if endpoint:
            self.endpoint = endpoint

    @staticmethod
    def __check_response_status_code(res, path):
        if res.status_code > 299 or res.status_code < 200:
            raise Exception("Got status code {status} to {path}: {reason}".format(status=res.status_code, path=path,
                                                                                  reason=res.reason))

    def set_job_title(self, job_id, title):
        path = "jobs/{}.json".format(job_id)
        url = self.endpoint.format(path=path, api_key=self.api_key)

        res = requests.post(url, data={"job[title]": title})
        self.__check_response_status_code(res, path)

        return res.json()

    def set_job_price_in_cents_per_page(self, job_id, price_in_cents):
        path = "jobs/{}.json".format(job_id)
        url = self.endpoint.format(path=path, api_key=self.api_key)

        res = requests.post(url, data={"job[payment_cents]": price_in_cents})
        self.__check_response_status_code(res, path)

        return res.json()

    def copy_job(self, job_id, all_units=True):
        path = "jobs/{}/copy.json".format(job_id)
        url = self.endpoint.format(path=path, api_key=self.api_key)

        if all_units:
            url += "&all_units=true"

        res = requests.get(url)
        self.__check_response_status_code(res, path)

        return res.json()

    def copy_job_without_rows(self, job_id):
        return self.copy_job(job_id, all_units=False)

    def add_tag_to_job(self, job_id, tag):
        path = "jobs/{}/tags".format(job_id)
        url = self.endpoint.format(path=path, api_key=self.api_key)

        res = requests.post(url, params={'tags': tag})
        self.__check_response_status_code(res, path)

        return res.json()

    def upload_csv_to_job(self, job_id, data):
        path = "jobs/{}/upload.json".format(job_id)
        url = self.endpoint.format(path=path, api_key=self.api_key)
        url += "&force=true"

        res = requests.put(url, headers={'Content-Type': 'text/csv'}, data=data)
        self.__check_response_status_code(res, path)

        return res.json()

    def launch_job(self, job_id, units_count, channel='on_demand', retry_limit=5, retry_timeout=60):
        path = "jobs/{}/orders.json".format(job_id)
        url = self.endpoint.format(path=path, api_key=self.api_key)

        retry = 0
        while 1:
            try:
                res = requests.post(url, data={"channels[0]": channel, "debit[units_count]": units_count})
                self.__check_response_status_code(res, path)
                return res.json()
            except Exception as e:
                retry += 1
                if retry > retry_limit:
                    raise Exception("Max retries ({}) exceeded: {}".format(retry_limit, str(e)))

                sleep(retry_timeout)

    def find_jobs_by_support_email(self, support_email, team_id=None):
        path = "jobs.json"
        url = self.endpoint.format(path=path, api_key=self.api_key)

        if team_id:
            url += "&team_id=" + team_id

        res = requests.get(url)
        self.__check_response_status_code(res, path)

        jobs = [job for job in res.json() if job['support_email'] == support_email]

        return jobs

    def get_judgements_by_job_id(self, job_id):
        path = "jobs/{}/judgments.json".format(job_id)
        url = self.endpoint.format(path=path, api_key=self.api_key)
        url += "&page={}"

        results = []
        page = 1

        res = requests.get(url.format(page))
        self.__check_response_status_code(res, path)

        judgements = res.json()
        while len(judgements):
            results += judgements.values()
            page += 1

            res = requests.get(url.format(page))
            self.__check_response_status_code(res, path)

            judgements = res.json()

        return results

    def get_json_results_by_job_id(self, job_id, retry_limit=5, retry_timeout=60):
        path = "jobs/{}.csv".format(job_id)
        url = self.endpoint.format(path=path, api_key=self.api_key)
        url += "&type=json"

        retry = 0
        while 1:
            try:
                res = requests.get(url)
                if res.status_code > 302 or res.status_code < 200:
                    raise Exception(
                        "Got status code {status} (expected 302 or 200) to {path}: {reason}".format(
                            status=res.status_code,
                            path=path,
                            reason=res.reason))

                res = requests.get(url)
                self.__check_response_status_code(res, path)

                zip = ZipFile(StringIO(res.content))
                if len(zip.filelist) == 0:
                    raise Exception("No result file found in zip report")

                report = zip.read(zip.filelist[0].filename)

                json_data = [json.loads(line) for line in report.split('\n') if line]

                return json_data
            except Exception as e:
                retry += 1
                if retry > retry_limit:
                    raise Exception("Max retries ({}) exceeded: {}".format(retry_limit, str(e)))

                sleep(retry_timeout)
