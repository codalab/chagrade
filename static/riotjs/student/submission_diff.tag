<submission-diff>
    <tr>
    <td>{ submission.id } { previous_submission.id }</td>
    </tr>
    <script>
        var self = this
        self.errors = []
        self.submission = {}
//            'method_name': '',
//            'method_description': '',
//            'project_url': '',
//            'publication_url': '',
//            'github_url': '',
//            'github_repo_name': '',
//            'github_branch_name': '',
//            'github_commit_hash': '',
//        }
        self.previous_submission = {}


        self.one('mount', function () {
            self.find_diff()
            console.log('mounted')
        })

        self.github_request = (url, done_function) => {
            console.log(url)
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
                console.log(error)
                toastr.error("Github API Error: " + error.statusText)
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
                        self.github_ref = null
                    }
 //                   console.info('submission data: ', self.submission)
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
                        self.github_ref = null
                    }
//                    console.info('submission data: ', self.previous_submission)
                    self.update()
                })
                .fail(function (error) {
                    toastr.error("Error fetching submission: " + error.statusText)
                })


            Promise.all([current_submission, previous_submission])
                .then( function(data) {
                    //console.info('both promises fulfilled... ', data)
                    let curr = self.submission
                    let prev = self.previous_submission

                    if ((curr.github_repo_name != prev.github_repo_name) || !curr.github_repo_name) {
                        self.no_diff = true
                    } else {
                        let repo = curr.github_repo_name
                        let curr_ref  = self.submission.github_ref
                        let prev_ref  = self.previous_submission.github_ref

                        if ((curr_ref != prev_ref) || !curr_ref) {
                            self.no_diff = true
                        } else {
                            console.info('current ref:', curr_ref)
                            console.info('previous ref:', prev_ref)

                            CHAGRADE.api.get_cha_user(self.opts.user_pk)
                                .done(function (data) {
                                    self.github_information = data.github_info
                                    self.user_information = data

//                            self.github_request(self.submission.github_url, function (commit_data) {
//                                self.github_repositories = commit_data
//                                console.info('commit_data', commit_data)
//                                self.update()
//                            })
                                })
                                .fail(function (error) {
                                    toastr.error("Error fetching user: " + error.statusText)
                                })
                        }
                    }
                })
        }
    </script>
</submission-diff>
