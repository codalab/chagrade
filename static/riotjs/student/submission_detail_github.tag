<submission-detail-github>
    <p>{  }</p>
    <p>{  }</p>
    <p>{  }</p>
    <script>
        var self = this
        self.errors = []
        self.submission = {
            'method_name': '',
            'method_description': '',
            'project_url': '',
            'publication_url': '',
            'github_url': '',
            'github_repo_name': '',
            'github_branch_name': '',
            'github_commit_hash': '',
        }

        self.github_requests = 0

        self.one('mount', function () {
            self.update_submission()
        })

        self.github_request = (url, done_function) => {
            $.ajax({
                type: 'GET',
                url: url,
                data: JSON.stringify(null),
                headers:{"Authorization": 'token ' + self.github_information.access_token},
                contentType: "application/json",
                dataType: 'json',
            })
            .done(done_function)
        }

        self.update_submission = function () {
            CHAGRADE.api.get_submission(SUBMISSION)
                .done(function (data) {
                    self.submission = data
                    if (!!self.submission.github_commit_hash) {
                        self.github_ref = self.submission.github_commit_hash
                    } else if (!!self.submission.github_branch_name) {
                        self.github_ref = self.submission.github_branch_name
                    } else {
                        self.github_ref = null
                    }
                    self.update()
                    self.update_question_answers()
                })
                .fail(function (error) {
                    toastr.error("Error fetching submission: " + error.statusText)
                })
        }

        self.cancel_button = function () {
            window.location = '/homework/overview/' + KLASS
        }

        self.update_submission = function () {
            CHAGRADE.api.get_cha_user(self.opts.pk)
                .done(function (data) {
                    self.github_information = data.github_info
                    self.user_information = data

                    self.github_request(self.user_information.github_url, function (repo_data) {
                        self.github_repositories = repo_data
                        self.update()
                    })
                })
                .fail(function (error) {
                    toastr.error("Error fetching user: " + error.statusText)
                })
        }
    </script>
</submission-detail-github>
