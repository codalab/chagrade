<submission-diff>
    <a if={!behind && !no_diff} class="ui small green button" href="{diff_url}" target="_blank" rel="noopener noreferrer">{diff_magnitude} commits ahead</a>
    <a if={behind && !no_diff} class="ui small red button" href="{diff_url}" target="_blank" rel="noopener noreferrer">Behind</a>
    <div if={no_diff}>No Diff</div>
    <script>
        var self = this
        self.no_diff = true
        self.behind = false
        self.errors = []
        self.submission = {}
        self.previous_submission = {}


        self.one('mount', function () {
            console.log('self.repos_url', self.opts.repos_url)
            self.find_diff()
        })

        self.github_request = (url, done_function) => {
            $.ajax({
                type: 'GET',
                url: url,
                data: JSON.stringify(null),
                headers:{"Authorization": 'token ' + self.opts.github_access_token},
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
                console.log(comparison)
                if (comparison.behind_by > 0 && comparison.ahead_by == 0) {
                    self.behind = true
                    self.diff_request(head_ref, base_ref)
                }
                self.no_diff = false
                self.diff_url = comparison.html_url
                self.diff_magnitude = comparison.ahead_by
                self.update()
            })
        }

        self.find_diff = function () {
            // c stands for current submission
            // p stands for previous submission

            let c_github_ref = 'master'
            let p_github_ref = 'master'

            if (!!self.opts.c_github_commit_hash && self.opts.c_github_commit_hash !== 'Commit') {
                c_github_ref = self.opts.c_github_commit_hash
            } else if (!!self.opts.c_github_branch_name && self.opts.c_github_branch_name !== 'Branch') {
                c_github_ref = self.opts.c_github_branch_name
            }

            if (!!self.opts.p_github_commit_hash && self.opts.p_github_commit_hash !== 'Commit') {
                p_github_ref = self.opts.p_github_commit_hash
            } else if (!!self.opts.p_github_branch_name && self.opts.p_github_branch_name !== 'Branch') {
                p_github_ref = self.opts.p_github_branch_name
            }

            if ((c_github_ref === p_github_ref) || !c_github_ref) {
                self.no_diff = true
            } else {
                self.github_request(self.opts.repos_url, function (repo_data) {
                    self.repo = _.find(repo_data, ['name', self.opts.repo_name])
                    self.diff_request(p_github_ref, c_github_ref)
                })
            }
        }
    </script>
    <style>
        .button {
            margin: 0px !important;
        }

        .diff-behind {
            background: red;
            font: white;
        }
    </style>
</submission-diff>
