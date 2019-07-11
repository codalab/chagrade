<submission-detail-github>

    <div class="ui grid">
        <div class="six wide column">
            <p>Date: { format_date(submission.created) }</p>
            <p if={ submission.commit_hash }>Commit hash: { submission.commit_hash.slice(0,6) }</p>
            <a class="ui tiny black button" href="{ submission.github_url }">Submission File</a>
            <p if={ submission.github_repo_name }>Repository Name: { submission.github_repo_name }</p>
            <p if={ submission.github_branch_name }>Branch Name: { submission.github_branch_name }</p>
        </div>
        <div class="ten wide column">
            <div class="ui header">
                Repository Activity
            </div>

            <div each={commit in commits} class="ui grid commit">
                <div class="row">
                    <a class="ui blue label" href="{ commit.html_url }">
                        <i class="hashtag icon"></i>
                        {commit.sha.slice(0,6)}
                    </a>
                    <div class="ui right floated date">
                        {format_date(commit.commit.committer.date)}
                    </div>
                </div>
                {commit.commit.message}
            </div>
        </div>
    </div>
    </div>
    <script>
        var self = this
        self.errors = []
        self.submission = {}

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
            .fail(function (error) {
                toastr.error("Github API Error: " + error.statusText)
            })
        }

        self.format_date = function (iso_string) {
            let options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: 'numeric', second: '2-digit' };
            let d = new Date(iso_string)
            return d.toLocaleDateString('en-US', options)
        }

        self.cancel_button = function () {
            window.location = '/homework/overview/' + KLASS
        }

        self.update_submission = function () {
            CHAGRADE.api.get_submission(self.opts.submission_pk)
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
                    CHAGRADE.api.get_cha_user(self.opts.user_pk)
                        .done(function (data) {
                            self.github_information = data.github_info
                            self.user_information = data
                            self.github_request(self.github_information.repos_url, function (repo_data) {
                                self.github_repositories = repo_data
                                let repo = _.find(repo_data, ['name', self.submission.github_repo_name])
                                self.github_request(repo.commits_url.split('{')[0], function (data) {
                                    self.commits = data
                                    self.update()
                                })
                                self.update()
                            })
                        })
                        .fail(function (error) {
                            toastr.error("Error fetching user: " + error.statusText)
                        })
                })
                .fail(function (error) {
                    toastr.error("Error fetching submission: " + error.statusText)
                })

        }
    </script>
    <style>
        .ten.wide.column {
            height: 100%;
        }

        .commit {
            margin: 28px 0 28px 0 !important;
            font-size: 1.3em;
            line-height: 1.5em;
        }

        .date {
            color: #888888;
            margin-left: 15px;
        }
    </style>
</submission-detail-github>
