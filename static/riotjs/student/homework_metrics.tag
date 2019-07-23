<homework-metrics>
    <div class="ui grid">
        <div class="row">
            <div class="seven wide left floated column graph-container">
                <div class="row">
                    <div class="ui centered header">Class Median Score</div>
                </div>
                <div class="row">
                    <div class="canvas-container">
                        <canvas ref="codalab_scores" id="codalab_scores"></canvas>
                    </div>
                </div>
            </div>
            <div class="seven wide right floated column graph-container">
                <div class="row">
                    <div class="ui centered header">Busy Submission Hours</div>
                </div>
                <div class="row">
                    <div class="canvas-container">
                        <canvas ref="temporal_histogram" id="temporal_histogram"></canvas>
                    </div>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="seven wide left floated column graph-container">
 <!--           <div class="row">
                    <div class="ui centered header">Contribution Comparison</div>
                </div>-->
                <div class="row">
                    <div class="canvas-container">
                        <canvas ref="github_activity" id="github_activity"></canvas>
                    </div>
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
            self.update_score_data()
            self.update_github_data()

            self.codalab_score_chart = new Chart(self.refs.codalab_scores, create_chart_config('Submission Score'));
//            self.github_activity_chart = new Chart(self.refs.github_activity, create_stacked_bar_chart_config('Commit Frequency'));
            self.temporal_histogram = new Chart(self.refs.temporal_histogram, create_bar_chart_config('Commit Frequency'));
            console.log('mounted')
        })

        let score_data = {
            label: 'Median Class Score',
            data: [0.04, 0.1, 0.3, 0.6, 0.9],
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor:'rgba(54, 112, 185, 1)',
            borderWidth: 2.2,
            lineTension: 0,
        }

        let target_data = {
            label: 'Target Score',
            data: [
                {
                    x: new Date(2019, 1, 1),
                    y: 0.96,
                },{
                    x: new Date(2019, 1, 17),
                    y: 0.96,
                },
            ],
            backgroundColor: 'rgba(0, 0, 0, 0.0)',
            borderColor:'rgba(0, 190, 0, 1)',
            borderWidth: 2.2,
            lineTension: 0,
        }

        let baseline_data = {
            label: 'Baseline Score',
            data: [
                {
                    x: new Date(2019, 1, 1),
                    y: 0.2,
                },{
                    x: new Date(2019, 1, 17),
                    y: 0.2,
                },
            ],
            backgroundColor: 'rgba(0, 0, 0, 0.0)',
            borderColor:'rgba(190, 0, 0, 1)',
            borderWidth: 2.2,
            lineTension: 0,
        }


        let bar_data = [
            {
                label: 'Lines Removed',
                data: [25, 15, 40],
                borderColor: 'rgba(190, 0, 0, 1)',
                backgroundColor: 'rgba(190, 0, 0, 0.5)',
            },{
                label: 'Lines Added',
                data: [55, 80, 120],
                borderColor: 'rgba(0, 150, 0, 1)',
                backgroundColor: 'rgba(0, 150, 0, 0.5)',
            }
        ]

        function create_stacked_bar_chart_config(label) {
            return {
                type: 'bar',
                data: {
                    labels: ['Tom', 'Alice', 'Bjorne'],
                    datasets: bar_data,
                },
                options: {
                    legend: {
                        display: true,
                        position: 'bottom',
                    },
                    aspectRatio: 1.4,
//                    title: {
//                        display: true,
//                        text: 'Contribution Comparison',
//                    },
                    scales: {
                        xAxes: [{
                            stacked: true,
                        }],
                        yAxes: [{
                            stacked: true,
                        }]
                    }
                }
            }
        }

        function create_chart_config(label) {
            return {
                type: 'line',
                data: {
                    datasets: [
                        score_data,
//                        target_data,
//                        baseline_data,
                    ],
                    labels: ['HW 1', 'HW 2', 'HW 3', 'HW 4', 'HW 5'],
                },
                options: {
                    legend: {
                        display: true,
                        position: 'bottom',
                    },
                    aspectRatio: 1.4,
                    scales: {
                        xAxes: [{
//                            type: 'time',
//                            time: {
//                                unit: 'day',
//                            },
                        }],
                        yAxes: [{
                            ticks: {
                                beginAtZero: true,
                                stepSize: 0.25,
                            }
                        }]
                    }
                }
            }
        }

        let submission_counts = [1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 2, 4, 2, 0, 0, 3, 5, 6, 2, 3, 4, 4, 2, 1,]
        let submission_times = ['12 am', '1 am', '2 am', '3 am', '4 am', '5 am', '6 am', '7 am', '8 am', '9 am', '10 am', '11 am', '12 pm', '1 pm', '2 pm', '3 pm', '4 pm', '5 pm', '6 pm', '7 pm', '8 pm', '9 pm', '10 pm', '11 pm',]


        function create_bar_chart_config(label) {
            return {
                type: 'bar',
                data: {
                    labels: submission_times,
                    datasets: [{
                        label: 'Submissions Per Hour',
                        data: submission_counts,
                        backgroundColor:'rgba(54, 112, 185, 0.6)',
                        borderColor:'rgba(54, 112, 185, 1)',
                    }],
                },
                options: {
                    legend: {
                        display: true,
                        position: 'bottom',
                    },
                    aspectRatio: 1.4,
//                    title: {
//                        display: true,
//                        text: 'Busy Submission Hours',
//                    },
                    scales: {
                        xAxes: [{
                            display: true,
                        }],
                        yAxes: [{
                            display: true,
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
        homework-metrics {
            margin-top: 40px;
        }

        .ten.wide.column {
            height: 100%;
        }

        .canvas-container {
            margin-left: auto;
            margin-right: auto;
            position: relative;
            width: 350px;
        }

        .graph-container {
            padding-top: 20px;
            background: white;
            border: solid 1.5px #dddddd;
            border-radius: 4px;
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
