<submission-diff>
    <tr>
    <td if={!no_diff}>
        <a if={!behind} class="ui small green button" href="{diff_url}">Diff</a>
        <a if={behind} class="ui small red button" href="{diff_url}">Behind</a>
    </td>
    <td if={no_diff}>No diff
    </td>
    </tr>
    <script>
        var self = this
        self.no_diff = true
        self.behind = false
        self.errors = []
        self.submission = {}
        self.previous_submission = {}


        self.one('mount', function () {
            self.find_diff()
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
            .fail(function (error) {
                toastr.error("Github API Error: " + error.statusText)
            })
        }

        self.diff_request = function (base_ref, head_ref) {
            let compare_url = self.repo.compare_url.replace('{base}', base_ref).replace('{head}', head_ref)
            self.github_request(compare_url, function (comparison) {
                if (comparison.behind_by > 0 && comparison.ahead_by == 0) {
                    self.behind = true
                    self.diff_request(head_ref, base_ref)
                }
                self.no_diff = false
                self.diff_url = comparison.html_url
                self.update()
            })
        }

        self.find_diff = function () {
            let current_submission = CHAGRADE.api.get_submission(self.opts.submission_pk)
                .done(function (data) {
                    self.submission = data
                    if (!!self.submission.github_commit_hash) {
                        self.submission.github_ref = self.submission.github_commit_hash
                    } else if (!!self.submission.github_branch_name) {
                        self.submission.github_ref = self.submission.github_branch_name
                    } else {
                        self.submission.github_ref = 'master'
                    }
                    self.update()
                })
                .fail(function (error) {
                    toastr.error("Error fetching submission: " + error.statusText)
                })
            let previous_submission = CHAGRADE.api.get_submission(self.opts.previous_submission_pk)
                .done(function (data) {
                    self.previous_submission = data
                    if (!!self.previous_submission.github_commit_hash) {
                        self.previous_submission.github_ref = self.previous_submission.github_commit_hash
                    } else if (!!self.previous_submission.github_branch_name) {
                        self.previous_submission.github_ref = self.previous_submission.github_branch_name
                    } else {
                        self.previous_submission.github_ref = 'master'
                    }
                    self.update()
                })
                .fail(function (error) {
                    toastr.error("Error fetching submission: " + error.statusText)
                })


            Promise.all([current_submission, previous_submission])
                .then( function(data) {
                    let curr = self.submission
                    let prev = self.previous_submission

                    if ((curr.github_repo_name !== prev.github_repo_name) || !curr.github_repo_name) {
                        self.no_diff = true
                    } else {
                        let repo_name = curr.github_repo_name
                        let curr_ref  = self.submission.github_ref
                        let prev_ref  = self.previous_submission.github_ref

                        if ((curr_ref === prev_ref) || !curr_ref) {
                            self.no_diff = true
                        } else {
                            CHAGRADE.api.get_cha_user(self.opts.user_pk)
                                .done(function (data) {
                                    self.github_information = data.github_info
                                    self.user_information = data

                                    self.github_request(self.github_information.repos_url, function (repo_data) {
                                        self.github_repositories = repo_data
                                        self.repo = _.find(repo_data, ['name', repo_name])
                                        self.diff_request(prev_ref, curr_ref)
                                    })
                                })
                                .fail(function (error) {
                                    toastr.error("Error fetching user: " + error.statusText)
                                })
                        }
                    }
                    self.update()
                })
        }
    </script>
    <style>
        .button {
            margin: 0px !important;
        }
    </style>
</submission-diff>
