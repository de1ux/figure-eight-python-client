# figure-eight-python-client

Python client drawn from [Figure Eight's API docs](https://success.figure-eight.com/hc/en-us/articles/202703425-Figure-Eight-API-Requests-Guide)

## Install

```bash
$ pip install figure-eight-python-client
```

## Usage

Replace `<figure-eight-api-token>` with a token from https://make.figure-eight.com/account/api

```python
>>> from figure_eight_python_client import FigureEightClient
>>> client = FigureEightClient("<figure-eight-api-token>")
```

## Methods
|  |
|--------|
|copy_job(job_id, all_units=True)|
|copy_job_without_rows(job_id)|
|add_tag_to_job(job_id, tag)|
|upload_csv_to_job(job_id, data)|
|launch_job(job_id, units_count, channel='on_demand')|
|find_jobs_by_support_email(support_email, team_id=None)|
|get_judgements_by_job_id(job_id)|
|get_json_results_by_job_id(job_id)|

## Contributing

Consider making a pull request if you have an idea or discover a bug. 

## Thanks

Big thanks to [Density](https://www.density.io/) for sponsoring the development of figure-eight-python-client.
