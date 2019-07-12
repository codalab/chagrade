<homework-metrics>
    <div class="ui grid">
        <div class="row">
            <div class="ui header">Start</div>
        </div>
        <div class="row">
            <canvas ref="codalab_scores"></canvas>
        </div>
        <div class="row">
            <canvas ref="github_activity"></canvas>
        </div>
        <div class="row">
            <div class="ui header">End</div>
        </div>
    </div>

    <script>
        var self = this
        self.errors = []
        self.submission = {}

        self.github_requests = 0

        self.one('mount', function () {
            self.update_score_data()
            self.update_github_data()
            self.codalab_score_chart = new Chart($(self.refs.codalab_scores), create_chart_config('Submission Score'));
            self.github_activity_chart = new Chart($(self.refs.github_activity), create_chart_config('Commit Frequency'));
            console.log('mounted')
        })



        function create_chart_config(label) {
            return {
                type: 'line',
                data: {
                    datasets: [{
                        label: label,
                        data: [
                            {
                                x: new Date(2019, 1, 1),
                                y: 2,
                            },{
                                x: new Date(2019, 1, 2),
                                y: 3,
                            },{
                            },
                        ],
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor:'rgba(54, 162, 235, 1)',
                        borderWidth: 1,
                        lineTension: 0,
                    }],
                },
                options: {
                    scales: {
                        xAxes: [{
                            type: 'time',
                            time: {
                                unit: 'month'
                            }
                        }],
                        yAxes: [{
                            ticks: {
                                beginAtZero: true,
                                stepSize: 1,
                            }
                        }]
                    }
                }
            }
        }


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

        self.update_score_data = function () {

        }

        self.update_github_data = function () {
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
                                    console.log(data)
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

        .author {
            color: #444444;
            margin-left: 15px;
            margin-right: auto;
        }

        .date {
            color: #888888;
            margin-right: 15px;
            font-size: 0.8em;
        }
    </style>
</homework-metrics>
