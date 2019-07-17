import os
from tempfile import TemporaryFile
from urllib.parse import urlparse
import requests
from requests.auth import HTTPBasicAuth
from apps.homework.models import Submission, SubmissionTracker

# TODO: Clean this up and possibly have a flag between running this as a task vs actually calling it? (Heroku vs Docker)


# @task
def post_submission(submission_pk):
    # Get our URL's formatted and such
    submission = Submission.objects.get(pk=submission_pk)
    parsed_uri = urlparse(submission.get_challenge_url)
    print(submission.get_challenge_url)
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
        # repo_url = "{}/archive/master.zip".format(submission.submission_github_url)

        # https://github.com/codalab/chalab/raw/develop/chalab/static/chalab/resource/iris.zip
        # FROM
        # https://github.com/codalab/chalab/blob/develop/chalab/static/chalab/resource/iris.zip

        parsed_repo_uri = urlparse(submission.github_url)
        repo_scheme = parsed_repo_uri.scheme
        repo_loc = parsed_repo_uri.netloc
        repo_path = parsed_repo_uri.path
        # path_components = repo_path.split('/')
        path_components = [component if component != 'blob' else 'raw' for component in repo_path.split('/')]
        new_path = ""
        for index, component in enumerate(path_components):
            if index != len(path_components) - 1:
                new_path += component + '/'
            else:
                new_path += component
        repo_url = '{scheme}://{domain}{path}'.format(scheme=repo_scheme, domain=repo_loc, path=new_path)
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
        custom_filename = "{username}_{date}.zip".format(username=submission.creator.user.username, date=submission.created)
        print("Finalizing submission for phase: {}".format(phase_id))
        phase_final_resp = requests.post(finalize_url, data={
            'id': submission_data,
            # 'name': 'master.zip',
            'name': custom_filename,
            'type': 'application/zip',
            # 'size': ?
        }, auth=HTTPBasicAuth(
            os.environ.get('CODALAB_SUBMISSION_USERNAME'),
            os.environ.get('CODALAB_SUBMISSION_PASSWORD')
        ))
        print('url:', finalize_url)
        print('username:', os.environ.get('CODALAB_SUBMISSION_USERNAME'))
        print('password:', os.environ.get('CODALAB_SUBMISSION_PASSWORD'))

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
            print(phase_final_resp.content)
            print(dir(phase_final_resp))
    submission.submitted_to_challenge = True
