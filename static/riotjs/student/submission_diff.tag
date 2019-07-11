<submission-diff>
    <tr>
    <td if={!no_diff}>
        <a class="ui small green button" href="{diff_url}">Diff</a>
    </td>
    <td if={no_diff}>No diff
    <div if={no_length}>No length</div>
    </td>
    </tr>
    <script>
        var self = this
        self.no_diff = false
        self.no_length = false
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
//            console.log('mounted')
        })

        self.github_request = (url, done_function) => {
//            console.log(url)
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
 //                   //console.info('both promises fulfilled... ', data)
 //                   console.log('\n\n')
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
 //                           console.info('current ref:', curr_ref)
 //                           console.info('previous ref:', prev_ref)
  //                          console.log('\n\n')
  //
                            CHAGRADE.api.get_cha_user(self.opts.user_pk)
                                .done(function (data) {
                                    self.github_information = data.github_info
                                    self.user_information = data

                            self.github_request(self.github_information.repos_url, function (repo_data) {
                                self.github_repositories = repo_data
//                                console.info('repo data', repo_data)
//                                console.info('repo', repo_name)
                                let repo = _.find(repo_data, ['name', repo_name])
//                                console.info('repo', repo)
//
                                let compare_url = repo.compare_url.replace('{base}', curr_ref).replace('{head}', prev_ref)
//                                let commits_url = repo.branches_url.slice(0,23) + 'repos/' + repo.full_name + '/commits/'
//                                console.info('commits url', commits_url)
//
//                                console.info('compare url', compare_url)
                                self.github_request(compare_url, function (comparison) {
                                    if (comparison.files.length == 0) {
                                        self.no_diff = true
                                        self.no_length = true
                                    }

                                    console.info('comparison', comparison.html_url, !self.no_diff, comparison.files)
                                    self.diff_url = comparison.html_url
                                    self.update()
                                })
                            })
                                })
                                .fail(function (error) {
                                    toastr.error("Error fetching user: " + error.statusText)
                                })
                        }
                    }
//                    console.info('pk:', self.submission.id)
//                    console.info('diff:', !self.no_diff)
//                    console.log('\n\n')
                    self.update()
                })
        }
    </script>
</submission-diff>
