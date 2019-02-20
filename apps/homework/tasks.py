import os
from tempfile import TemporaryFile, NamedTemporaryFile
from urllib.parse import urlparse
import requests
from celery.task import task
from django.core.exceptions import ObjectDoesNotExist
# from django.core.files.temp import TemporaryFile
from requests.auth import HTTPBasicAuth
from apps.homework.models import Grade, Submission, SubmissionTracker


# @task
def post_submission(submission_pk):
    # Get our URL's formatted and such
    submission = Submission.objects.get(pk=submission_pk)
    definition = submission.definition
    # if definition.team_based:
    #     if not submission.team:
    #         print("No team for a team based submission")
    #         return
    #     else:
    #         custom_urls = submission.team.challenge_urls.filter(definition=definition, team=submission.team)
    #     # if not submission.team.challenge_url:
    #     if not custom_urls:
    #         if not definition.challenge_url:
    #             print("No challenge URL for either the team or the definition. Abandoning")
    #             return
    # if not submission.submission_github_url:
    #     print("No github url was provided")
    #     return
    # if not definition.challenge_url:
    #     print("No challenge url was provided")
    #     return
    # https://competitions.codalab.org/competitions/15595
    # if definition.team_based:
    #     parsed_uri = urlparse(custom_urls.first().challenge_url) if custom_urls else urlparse(definition.challenge_url)
    # else:
    #     parsed_uri = urlparse(definition.challenge_url)
    parsed_uri = urlparse(submission.get_challenge_url)
    scheme = parsed_uri.scheme
    domain = parsed_uri.netloc
    path = parsed_uri.path
    challenge_pk = path.split('/')[-1]
    site_url = "{0}://{1}".format(scheme, domain)
    submission_url = '{0}/api/competition/{1}/submission/sas'.format(site_url, challenge_pk)
    # Post our request to the submission SAS API endpoint
    print("Getting submission SAS info")
    resp = requests.post(
        url=submission_url, auth=HTTPBasicAuth(
            os.environ.get('CODALAB_SUBMISSION_USERNAME'),
            os.environ.get('CODALAB_SUBMISSION_PASSWORD')
        )
    )
    print(resp.status_code)
    # competition/15595/submission/44798/4aba772a-a6c1-4e6f-a82b-fb9d23193cb6.zip
    submission_data = resp.json()['id']
    submission_data_split = submission_data.split('/')
    submission_file_name = submission_data_split[-1]
    s3_file_url = resp.json()['url']
    print("Posting github submission to storage")

    with TemporaryFile() as f:
        # f = TemporaryFile()
        # https://github.com/Tthomas63/partspolls/archive/master.zip
        repo_url = "{}/archive/master.zip".format(submission.submission_github_url)
        print(repo_url)
        repo_resp = requests.get(repo_url, stream=True)
        for chunk in repo_resp.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
        temp_size = str(f.tell())
        f.seek(0)
        storage_resp = requests.put(
            url=s3_file_url,
            data=f,
            # data=get_github_submission_and_chunk(submission.submission_github_url),
            headers={
                # "Content-Type": "application/zip",
                "x-ms-blob-type": 'BlockBlob',
                # "content-name": submission_file_name,
                "Content-Length": temp_size,
                # "Content-Encoding": "gzip",
            }
        )
    print(storage_resp.status_code)
    # https://competitions.codalab.org/api/competition/20616/phases/
    phases_request_url = "{0}/api/competition/{1}/phases/".format(site_url, challenge_pk)
    print("Getting phase info for competition")
    phases_request = requests.get(url=phases_request_url, auth=HTTPBasicAuth(
        os.environ.get('CODALAB_SUBMISSION_USERNAME'),
        os.environ.get('CODALAB_SUBMISSION_PASSWORD')
    ))
    phases_dict = phases_request.json()[0]['phases']
    for i in range(len(phases_dict)):
        phase_id = phases_dict[i]['id']
        sub_descr = "Chagrade_Submission_{0}".format(submission.id)
        finalize_url = "{0}/api/competition/{1}/submission?description={2}&phase_id={3}".format(site_url, challenge_pk,
                                                                                                sub_descr, phase_id)
        print("Finalizing submission for phase: {}".format(phase_id))
        phase_final_resp = requests.post(finalize_url, data={
            'id': submission_data,
            'name': 'master.zip',
            'type': 'application/zip',
            # 'size': ?
        }, auth=HTTPBasicAuth(
            os.environ.get('CODALAB_SUBMISSION_USERNAME'),
            os.environ.get('CODALAB_SUBMISSION_PASSWORD')
        ))
        # If we succeed in posting to the phase, create a new tracker and store the submission info
        if phase_final_resp.status_code == 201:
            result = phase_final_resp.json()
            new_tracker = SubmissionTracker.objects.create(
                submission=submission,
                remote_phase=phase_id,
                remote_id=result['id']
            )
        else:
            print("Something went wrong making a submission to the challenge_url")
    submission.submitted_to_challenge = True
