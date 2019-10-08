<submission-detail-github>
    <div class="{definition.questions_only ? 'sixteen' : 'six'} wide column">

        <a if="{ submission.github_url }" class="ui tiny black button" href="{ submission.github_url }">Submission File</a>
        <p>Submitted: { format_date(submission.created) }</p>
        <p if="{ !!submission.commit_hash && submission.commit_hash !== 'Commit' }">Commit hash: { submission.commit_hash.slice(0,6) }</p>
        <p if="{ submission.github_repo_name }">Repository Name: { submission.github_repo_name }</p>
        <p if="{ !!submission.github_branch_name && submission.github_branch_name !== 'Branch' }">Branch Name: { submission.github_branch_name }</p>

        <h4>Custom Questions</h4>
        <div class="ui relaxed celled list">
            <ol>
                <li each="{ question in definition.custom_questions }">{ question.question }
                    <ul>
                        <li each="{ answer in question.student_answers }">{ answer }</li>
                    </ul>
                </li>
            </ol>
        </div>
    </div>

    <div if="{ !definition.questions_only }" class="ten wide column">
        <div class="ui header">
            Repository Activity
        </div>

        <div class="commit-container">
            <div each={commit in commits} class="ui grid commit">
                <div class="row commit-header">
                    <a class="ui blue label" href="{ commit.html_url }">
                        <i class="hashtag icon"></i>
                        {commit.sha.slice(0,6)}
                    </a>
                    <a class="ui right floated author" href="{ commit.author.html_url }">
                        { commit.commit.author.name }
                    </a>
                    <br>
                    <div class="date">
                        {format_date(commit.commit.committer.date)}
                    </div>
                </div>
                <div class="ui row commit-message">
                    {commit.commit.message}
                </div>
            </div>
        </div>
    </div>


    <script>
        var self = this
        self.submission = {}
        self.definition = {}
        self.github_requests = 0

        var datetime = luxon.DateTime

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
            let d = datetime.fromISO(iso_string)
            return d.toRelative()
        }

        self.cancel_button = function () {
            window.location = '/homework/overview/' + KLASS
        }

        self.update_github_information = function () {
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
        }

        self.update_definition = function (pk) {
            CHAGRADE.api.get_definition(pk)
                .done(function (data) {
                    let question_answers = self.submission.question_answers
                    for (let i = 0; i < question_answers.length; i++) {
                        let question = _.find(data.custom_questions, function (question) {
                            return question.id === question_answers[i].question
                        })
                        question.student_answers = question_answers[i].answer
                    }
                    self.definition = data
                    self.update()
                    if (!data.questions_only) {
                        self.update_github_information()
                    }
                })
                .fail(function (error) {
                    toastr.error("Error fetching definition: " + error.statusText)
                })
        }

        self.update_submission = function () {
            CHAGRADE.api.get_submission(self.opts.submission_pk)
                .done(function (data) {
                    self.submission = data
                    console.info('submission', data)
                    self.update()

                    self.update_definition(data.definition)

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

        .commit-container {
            height: 40vh;
            overflow-y: scroll;
        }

        .commit-header {
            padding-bottom: 10px !important;
        }

        .commit-message {
            padding-top: 0 !important;
            font-size: 0.8em;
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
</submission-detail-github>
