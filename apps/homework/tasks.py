import logging
import re
import os
from tempfile import TemporaryFile
from urllib.parse import urlparse

import requests
from celery.task import task
from requests.auth import HTTPBasicAuth

from apps.homework.models import Submission, SubmissionTracker

# TODO: Clean this up and possibly have a flag between running this as a task vs actually calling it? (Heroku vs Docker)


logger = logging.getLogger(__name__)


class SubmissionPostException(BaseException):

    def __init__(self, *args, **kwargs):
        self.sub_type = kwargs.get('sub_type')
        super(SubmissionPostException, self).__init__(*args, **kwargs)


def retrieve_score_from_jupyter_notebook(fd, submission):
    content = fd.readlines()

    # Jupyter Notebook files are formatted as json. The json is formatted in a human-readable
    # way with newlines and indentation. We can exploit this formatting by parsing the file into
    # lines and then filtering the lines that don't match "Your final score is".
    #
    # The line that we are looking for is formatted in the following way:
    #   "Your final score is x / x, congratulations!"
    #
    # To receive the substring containing the score from the lines that match "Your final score is", we use regex.
    #
    # If there are multiple matches, a warning is placed on the submission, and the last match in the file is used
    # per the specs of this feature.

    filtered_content = list(filter(lambda line: 'Your final score is' in str(line) and 'print' not in str(line), content))
    if len(filtered_content) is not 1:
        # Add warning to the submission model
        logger.warning(f'Multiple Jupyter Notebook score string matches in submission {submission.pk} for homework "{submission.definition.name}" (pk={submission.definition.pk}). Exactly one line should contain the phrase "final score" and not include the phrase "print".')

    score_string = str(filtered_content[-1])
    start_index = score_string.find('is')

    found = re.search(r'(?=.)([+-]?([0-9]*)(\.([0-9]+))?) \/ (?=.)([+-]?([0-9]*)(\.([0-9]+))?)', score_string)

    # Check for no matches
    separated = found.group().split(' ')
    numerator = float(separated[0])
    denominator = float(separated[2])
    return numerator, denominator


@task
def post_submission(submission_pk, data_file=None):
    # Get our URL's formatted and such
    submission = Submission.objects.get(pk=submission_pk)
    submission_data = None
    s3_file_url = None

    if not submission.definition.jupyter_notebook_enabled:
        parsed_uri = urlparse(submission.get_challenge_url)
        scheme = parsed_uri.scheme
        domain = parsed_uri.netloc
        path = parsed_uri.path
        challenge_pk = path.split('/')[-1]
        site_url = "{0}://{1}".format(scheme, domain)
        submission_url = '{0}/api/competition/{1}/submission/sas'.format(site_url, challenge_pk)

        logger.info(f"Making submission to {submission_url}")

        # Post our request to the submission SAS API endpoint
        resp = requests.post(
            url=submission_url, auth=HTTPBasicAuth(
                os.environ.get('CODALAB_SUBMISSION_USERNAME'),
                os.environ.get('CODALAB_SUBMISSION_PASSWORD')
            )
        )

        # Example of url format we're expecting: competition/15595/submission/44798/4aba772a-a6c1-4e6f-a82b-fb9d23193cb6.zip
        if not resp.ok:
            logger.warning("Could not communicate with Codalab instance!")
            raise SubmissionPostException(f"Could not communicate with codalab instace from submission url: {submission_url}", sub_type='connection')
        submission_data = resp.json()['id']
        s3_file_url = resp.json()['url']

    with TemporaryFile() as f:
        data_to_upload = None
        if not data_file:
            logger.info(f"Beginning read of github repository for submission {submission.pk}.")
            parsed_repo_uri = urlparse(submission.github_url)
            repo_scheme = parsed_repo_uri.scheme
            repo_loc = parsed_repo_uri.netloc
            repo_path = parsed_repo_uri.path
            path_components = [component if component != 'blob' else 'raw' for component in repo_path.split('/')]
            new_path = ""
            for index, component in enumerate(path_components):
                if index != len(path_components) - 1:
                    new_path += component + '/'
                else:
                    new_path += component
            repo_url = '{scheme}://{domain}{path}'.format(scheme=repo_scheme, domain=repo_loc, path=new_path)
            logger.info(f"Streaming github file for submission: {submission.pk}.")
            repo_resp = requests.get(repo_url, stream=True)
            for chunk in repo_resp.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
            temp_size = str(f.tell())
            f.seek(0)
            data_to_upload = f
            logger.info(f"Succesfully read file from Github for submission: {submission.pk}")
        else:
            data_to_upload = data_file
            temp_size = str(data_to_upload.size)
        if data_to_upload:
            if submission.definition.jupyter_notebook_enabled:
                # Temporary files can only be opened once, so both reads need to happen within this context manager
                with data_to_upload.open() as fd:
                    numerator, denominator = retrieve_score_from_jupyter_notebook(data_to_upload, submission)
                    fd.seek(0)
                    submission.jupyter_notebook.save(data_to_upload.name, data_to_upload)
                    if denominator != submission.definition.jupyter_notebook_highest:
                        # Add warning to submission model
                        pass
                    if numerator > submission.definition.jupyter_notebook_highest:
                        # Add warning to submission model
                        numerator = submission.definition.jupyter_notebook_highest
                    if numerator < submission.definition.jupyter_notebook_lowest:
                        # Add warning to submission model
                        numerator = submission.definition.jupyter_notebook_lowest
                    submission.jupyter_score = numerator
                    submission.save()
            else:
                storage_resp = requests.put(
                    url=s3_file_url,
                    data=data_to_upload,
                    headers={
                        "x-ms-blob-type": 'BlockBlob',
                        "Content-Length": temp_size,
                    }
                )
            logger.info(f"Pushing data to S3 url for submission: {submission.pk}")
        else:
            logger.warning("Failed to read file, or retrieve direct upload")
            raise SubmissionPostException("Failed to read file, or retrieve direct upload file.", sub_type='data')

    if not submission.definition.jupyter_notebook_enabled:
        # Example of url format we're expecting: https://competitions.codalab.org/api/competition/20616/phases/
        phases_request_url = "{0}/api/competition/{1}/phases/".format(site_url, challenge_pk)
        phases_request = requests.get(url=phases_request_url, auth=HTTPBasicAuth(
            os.environ.get('CODALAB_SUBMISSION_USERNAME'),
            os.environ.get('CODALAB_SUBMISSION_PASSWORD')
        ))
        phases_dict = phases_request.json()[0]['phases']
        phase_id = None
        for phase in phases_dict:
            if phase.get('is_active'):
                phase_id = phase['id']
                break

        if not phase_id:
            logger.info(f'No is_active field on phase. Update Codalab to latest version. Not POSTing a submission to Codalab.')
            return

        sub_descr = "Chagrade_Submission_{0}".format(submission.id)
        finalize_url = "{0}/api/competition/{1}/submission?description={2}&phase_id={3}".format(site_url, challenge_pk,
                                                                                                sub_descr, phase_id)
        custom_filename = "{username}_{date}.zip".format(username=submission.creator.user.username, date=submission.created)
        phase_final_resp = requests.post(finalize_url, data={
            'id': submission_data,
            'name': custom_filename,
            'type': 'application/zip',
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
                remote_id=result['id'],
                stored_status='Submitted'
            )
            logger.info(f'Succeeded posting submission with id {submission.id} to phase.')
        else:
            logger.info(f'Did not succeed in posting submission with id {submission.id} to phase.')
        submission.submitted_to_challenge = True
