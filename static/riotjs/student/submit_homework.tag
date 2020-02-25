<submit-homework>
    <div class="ui form" style="margin-bottom: 2.5vh;">
        <div if="{loading}" class="ui active dimmer">
            <div class="ui text loader">Submitting</div>
        </div>
        <h1 class="ui dividing header" id="submission_header">
            Submission Form for { definition.name }
            <a if={ definition.challenge_url && !definition.starting_kit_github_url }
               href="{ definition.challenge_url }"
               target="_blank"
               rel="noopener noreferrer"
               id="challenge_button"
               class="ui blue button">
               Codalab Challenge
            </a>
            <a if={ definition.starting_kit_github_url }
               href="{ definition.starting_kit_github_url }"
               target="_blank"
               rel="noopener noreferrer"
               id="challenge_button"
               class="ui blue button">
                Jupyter Notebook Starting Kit
            </a>
        </h1>

        <div if="{ !definition.questions_only && !github_active }">
            <div class="fields">
                <div class="sixteen wide field">
                    <span>
                        <label>
                            <i class="pop-up question blue circle icon"
                               data-title="A URL from your github repo to a specific zip file"
                               data-content="Ex: https://github.com/Tthomas63/chagrade_test_submission/blob/master/chagrade_test_submission-master.zip"> </i>
                            Submission Github URL (Must be {definition.jupyter_notebook_enabled ? ".ipynb" : ".zip"} file):
                        </label>
                    </span>
                    <input name="github_url" ref="github_url" type="text"
                           value="{submission.github_url || ''}">
                </div>
                <div class="eight wide field">
                    <span>
                        <label>
                            <i class="pop-up question blue circle icon"
                               data-title="A reference of to a point in the repo's history"
                               data-content="Ex: a9dhe3 or master"> </i>
                            Commit or Branch Name (Optional):
                        </label>
                    </span>
                    <input name="github_ref" ref="github_ref" type="text">
                </div>
            </div>
            <div if="{ !_.get(definition, 'force_github', false) }" class="ui divider"></div>
            <div if="{ !_.get(definition, 'force_github', false) }" class="fields">
                <div class="sixteen wide field">
                    <h1>OR</h1>
                    <label>Direct File Upload {definition.jupyter_notebook_enabled ? "(.ipynb file)" : "(.zip file)"}:</label>
                    <input type="file" accept="{definition.jupyter_notebook_enabled ? ".ipynb" : "application/zip, .zip"}" ref="direct_file">
                </div>
            </div>
        </div>

        <div if="{ !definition.questions_only && github_active }" class="fields">
            <div class="sixteen wide field">
                <div class="row">
                <span>
                    <label>
                        <i class="pop-up question blue circle icon"
                           data-title="A URL from your github repo to a specific file"
                           data-content="Ex: https://github.com/Tthomas63/chagrade_test_submission/blob/master/chagrade_test_submission-master.zip"> </i>
                        Github Submission (Must be zip file):
                    </label>
                </span>
                </div>
                <div class="ui horizontal divider"></div>
                <div class="row">
                    <div class="ui search selection dropdown repository" ref="github_repo">
                        <div if="{ submission.github_repo_name }" class="default text">{ submission.github_repo_name }</div>
                        <div if="{ !submission.github_repo_name }" class="default text">Repository</div>
                        <i class="dropdown icon"></i>
                        <div class="menu">
                            <div each="{repository, r in github_repositories}" class="item" data-value="{r}" data-text="{ repository.name }">{ repository.name }</div>
                        </div>
                    </div>
                    <div class="ui search selection dropdown branch" ref="github_branch">
                        <div if="{ submission.github_branch_name }" class="default text">{ submission.github_branch_name }</div>
                        <div if="{ !submission.github_branch_name }" class="default text">Branch (Optional)</div>
                        <i class="dropdown icon"></i>
                        <div class="menu">
                            <div each="{branch in github_branches}" class="item" data-text="{ branch.name }">{ branch.name }</div>
                        </div>
                    </div>
                </div>
                <div class="ui horizontal divider"></div>
                <div class="sixteen wide row">
                    <div class="ui search selection dropdown commit" ref="github_commit_hash">
                        <i class="dropdown icon"></i>
                        <div if="{ submission.github_commit_hash }" class="default text">{ submission.github_commit_hash }</div>
                        <div if="{ !submission.github_commit_hash }" class="default text">Commit (Optional)</div>
                        <div class="menu">
                            <div each="{commit in github_commits}" class="item" data-text="{ commit.sha }">
                                <div class="ui container">
                                    <div class="ui row">
                                        <div class="commit-header">
                                            <div class='sha'>
                                                { commit.sha.slice(0,8) }
                                            </div>
                                            <div class='commit-message'>
                                                { commit.commit.message }
                                            </div>
                                        </div>
                                    </div>
                                    <div class="ui horizontal divider"></div>
                                    <div class="ui row">
                                        <div class='commit-date'>
                                            { commit.commit.committer.date.slice(0,10) }
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="ui horizontal divider"></div>
                <div class="twelve wide row">
                    <div id="file-tree-header" class="ui header hidden">
                        <div class="content">
                            <i class="blue alternate file icon"></i>
                            Select Zip File Below:
                        </div>
                    </div>
                    <div class="ui form">
                        <div class="ui styled accordion">
                            <accordion-file-tree each="{ file in github_file_tree }" file="{file}" class="{ file.type === 'dir' ? "styled accordion" : "" }"></accordion-file-tree>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="fields">
            <div show="{definition.ask_method_name}" class="four wide field">
                <label>
                    Method Name:
                </label>
                <input required name="method_name" ref="method_name" type="text" value="{submission.method_name || ''}">
            </div>
            <div show="{definition.ask_method_description}" class="four wide field">
                <label>
                    Method Description:
                </label>
                <input required name="method_description" ref="method_description" type="text"
                       value="{submission.method_description || ''}">
            </div>
            <div show="{definition.ask_project_url}" class="four wide field">
                <label>
                    Project URL:
                </label>
                <input required name="project_url" ref="project_url" type="text" value="{submission.project_url || ''}">
            </div>
            <div show="{definition.ask_publication_url}" class="four wide field">
                <label>
                    Publication URL:
                </label>
                <input name="publication_url" ref="publication_url" type="text"
                       value="{submission.publication_url || ''}">
            </div>
        </div>
        <h2 if="{_.get(definition.custom_questions, 'length', 0) > 0 }" class="ui dividing header">Custom Questions:</h2>
        <div each="{ question, index in definition.custom_questions }" class="fields">
            <div if="{ question.question_type === 'TX' }" class="sixteen wide field">
                <input name="{'question_id_' + index}" ref="{'question_id_' + index}" type="hidden"
                       value="{question.id}">
                <label><pre>{question.question}</pre></label>

                <textarea data-question-id="" name="{'question_answer_' + index}" ref="{'question_answer_' + question.id}"
                          type="text" value="{question.prev_answer || ''}" rows="2"> </textarea>
            </div>

            <div if="{ question.question_type === 'SS' }" class="grouped fields">
                <label><pre>{question.question}</pre></label>
                <div each="{ candidate_answer, candidate_index in question.candidate_answers }" class="field">
                    <div class="ui radio checkbox" ref="{'question_answer_' + question.id + '_' + candidate_index }">
                        <input type="radio" name="{question.id}" tabindex="0" class="hidden">
                        <label>{ candidate_answer }</label>
                    </div>
                </div>
            </div>

            <div if="{ question.question_type === 'MS' }" class="grouped fields">
                <label><pre>{question.question}</pre></label>
                <div each="{ candidate_answer, candidate_index in question.candidate_answers }" class="inline field">
                    <div class="ui checkbox" ref="{'question_answer_' + question.id + '_' + candidate_index }">
                        <input type="checkbox" tabindex="0" class="hidden">
                        <label>{ candidate_answer }</label>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <span><a onclick="{submit_form}" class="ui green button">Submit</a><a onclick="{cancel_button}"
                                                                          class="ui red button">Cancel</a></span>

    <script>

        var self = this
        self.loading = false
        self.errors = []
        self.question_answers = []
        self.definition = {
            'ask_publication_url': false,
            'ask_project_url': false,
            'ask_method_name': false,
            'ask_method_description': false,
        }
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
        self.repo_value = null
        self.branch_value = null
        self.commit_value = null
        self.github_active = false

        self.one('mount', function () {
            self.github_active = self.opts.github === 'True'
            self.update()

            self.update_definition()

            $('.pop-up').popup({
                inline: true,
                position: 'top left',
            })
        })

        self.update_dropdowns_and_checkboxes = () => {
            $('.ui.checkbox').checkbox()

            $('.ui.dropdown.repository', self.root).dropdown({
                onChange: function(value, text, $selectedItem) {
                    if (self.repo_value === value) {
                        return
                    }
                    self.repo_value = value
                    self.github_repo = self.github_repositories[parseInt(value)]
                    self.github_request(self.github_repo.branches_url.split('{')[0], function (branch_data) {
                        self.github_branches = branch_data
                        self.update()
                    })
                    self.github_request(self.github_repo.commits_url.split('{')[0], function (commit_data) {
                        self.github_commits = commit_data
                        self.update()
                    })
                    $('.ui.dropdown.branch', self.root).dropdown('restore defaults')
                    $('.ui.dropdown.commit', self.root).dropdown('restore defaults')

                    load_github_file_tree()
                }
            })

            $('.ui.dropdown.branch', self.root).dropdown({
                onChange: function(value, text, $selecteditem) {
                    if (self.branch_value === value) {
                        return
                    }
                    self.branch_value = value
                    self.github_ref = text
                    load_github_file_tree()
                },
            })

            $('.ui.dropdown.commit', self.root).dropdown({
                onChange: function(value, text, $selecteditem) {
                    if (self.commit_value === value) {
                        return
                    }
                    self.commit_value = value
                    self.github_ref = text
                    load_github_file_tree()
                },
            })

            $(document).on('click', '.file.title', function clickkky(e) {
                let file_element = $(e.target)
                let url = file_element.parent().parent().attr('data-url')
                if (!!url) {
                    let parent = file_element.parent()
                    parent.checkbox('check')
                    let checkbox = file_element.siblings().first()
                    self.github_url = url
                    $('.file-label').removeClass('selected-file')
                    file_element.addClass('selected-file')
                }
            })
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
                .fail( function (data) {
                    toastr.error('Please connect your account to GitHub.')
                })
        }

        function load_github_file_tree () {
            function create_tree(files) {
                for (let i = 0; i < files.length; i++) {
                    if (files[i].type == 'dir') {
                        self.github_requests++
                        self.github_request(files[i].url, function (data) {
                            files[i].files = data
                            create_tree(files[i].files)
                            self.github_requests--
                            if (self.github_requests == 0) {
                                $('.ui.accordion').accordion('close others')
                                self.update()
                                $('.ui.checkbox').checkbox()
                            }
                        })
                    }
                }
            }

            let root_url = self.github_repo.branches_url.slice(0,23) + 'repos/' + self.github_repo.full_name + '/contents/'
            if (!!self.github_ref) {
                root_url += '?ref=' + self.github_ref
            }

            setTimeout(function () {
                $('.ui.accordion').accordion('close others')
                self.update()
            }, 100)

            self.github_request(root_url, function (repo_files) {
                    self.github_file_tree = repo_files
                    create_tree(self.github_file_tree)
                })
            $('#file-tree-header').removeClass('hidden')
        }

        self.check_filename_extension = function (filename) {
            let split_url = filename.split('.')
            let extension = split_url[split_url.length - 1]
            let desired_extension = self.definition.jupyter_notebook_enabled ? 'ipynb' : 'zip'
            if (extension !== desired_extension) {
                toastr.error(`Please upload a file with .${desired_extension} extension. You uploaded a file with a .${extension} extension.`)
                return false
            } else {
                return true
            }
        }

        self.submit_form = function () {
            self.update({loading: true})
            let question_answers = []

            for (let i = 0; i < self.definition.custom_questions.length; i++) {
                let question = self.definition.custom_questions[i]
                let question_answer = []
                if (question.question_type === 'MS' || question.question_type === 'SS') {
                    for (let j = 0; j < question.candidate_answers.length; j++) {
                        let reference_string = 'question_answer_' + question.id + '_' + j
                        let checked = $(self.refs[reference_string]).checkbox('is checked')
                        if (checked) {
                            question_answer.push(question.candidate_answers[j])
                        }
                    }
                } else {
                    let reference_string = 'question_answer_' + question.id
                    question_answer.push(self.refs[reference_string].value)
                }

                let answer = {
                    question: question.id,
                    answer: question_answer,
                }
                question_answers.push(answer)
            }


            if (window.SUBMISSION !== undefined) {
                var result = confirm("There is already an existing submission. Submitting again will overwrite the previous submission and any previously attached grades will be lost. Continue?")
                if (!result) {
                    self.update({loading: false})
                    return
                }
            }

            var data = {
                "klass": KLASS,
                "definition": DEFINITION,
                "creator": STUDENT,
                "method_name": self.refs.method_name.value || '',
                "method_description": self.refs.method_description.value || '',
                "project_url": self.refs.project_url.value || '',
                "publication_url": self.refs.publication_url.value || '',
                "question_answers": [
                    /*{
                     "question": 0,
                     "text": "string"
                     }*/
                ]
            }
            data['question_answers'] = question_answers

            if (!self.definition.questions_only) {
                if (!self.github_active) {
                    let github_ref = self.refs.github_ref.value
                    self.github_url = self.refs.github_url.value
                    if (_.get(self.github_url, 'length', 0) > 0) {
                        if (!self.check_filename_extension(self.github_url)) {
                            return
                        }
                    }

                    if (!!github_ref) {
                        let split_url = self.github_url.split('/')
                        split_url[6] = github_ref
                        self.github_url = split_url.join('/')
                    }

                    if (!_.get(self.definition, 'force_github', false)) {
                        if (!!self.refs.direct_file.files && !_.isEmpty(self.refs.direct_file.files)) {
                            var formData = new FormData();

                            for (var key in data) {
                                formData.append(key, data[key]);
                            }
                            if (!self.check_filename_extension(self.refs.direct_file.files[0].name)) {
                                return
                            }

                            // add assoc key values, this will be posts values
                            formData.append("file", self.refs.direct_file.files[0], self.refs.direct_file.files[0].name);
                            formData.append("upload_file", true);

                            CHAGRADE.api.form_request('POST', URLS.API + "submissions/", formData)
                                .done(function (data) {
                                    window.location = '/homework/overview/' + KLASS
                                })
                                .fail(function (response) {
                                    toastr.error(response.responseText)
                                    self.update({loading: false})
                                })
                            return
                        }
                    }
                } else {
                    data["github_repo_name"] = $(self.refs.github_repo).dropdown('get text')
                    let branch_name = $(self.refs.github_branch).dropdown('get text')
                    if (branch_name !== 'Branch (Optional)') {
                        data["github_branch_name"] = branch_name
                    } else {
                        data["github_branch_name"] = ''
                    }

                    let commit_hash = $(self.refs.github_commit_hash).dropdown('get text')
                    if (commit_hash !== 'Commit (Optional)') {
                        data["github_commit_hash"] = commit_hash
                    } else {
                        data["github_commit_hash"] = ''
                    }
                }

                data["github_url"] = self.github_url
            }

            if (!self.github_url && !self.definition.questions_only && !data.files) {
                self.update({loading: false})
                toastr.error("Please select a file before submitting.")
                return
            }

            if (window.USER_TEAM !== undefined) {
                data['team'] = window.USER_TEAM
            }

            CHAGRADE.api.create_submission(data)
                .done(function (data) {
                    window.location = '/homework/overview/' + KLASS
                })
                .fail(function (response) {
                    Object.keys(response.responseJSON).forEach(function (key) {
                        if (key === 'question_answers') {
                            toastr.error("An error occured with " + key + "! Please make sure you did not leave any fields blank.")
                        } else {
                            self.update({loading: false})
                            toastr.error("Error with " + key + "! " + response.responseJSON[key])
                        }
                    });
                })
        }

        self.update_question_answers = function () {
            var data = self.definition

            for (var index = 0; index < self.submission.question_answers.length; index++) {
                for (var question_index = 0; question_index < data.custom_questions.length; question_index++) {
                    if (self.submission.question_answers[index].question === data.custom_questions[question_index].id) {
                        data.custom_questions[question_index].prev_answer = self.submission.question_answers[index].text
                        data.custom_questions[question_index].answer_id = self.submission.question_answers[index].id
                    }
                }
            }
            self.update({definition: data})
        }

        self.update_submission = function () {
            CHAGRADE.api.get_submission(SUBMISSION)
                .done(function (data) {
                    self.submission = data
                    self.github_ref = _.get(self.submission, 'github_commit_hash', _.get(self.submission, 'github_branch_name', null))
                    self.update()
                    self.update_question_answers()
                })
                .fail(function (error) {
                    self.update({loading: false})
                    toastr.error("Error fetching submission: " + error.statusText)
                })
        }

        self.cancel_button = function () {
            window.location = '/homework/overview/' + KLASS
        }

        self.update_definition = function () {
            CHAGRADE.api.get_definition(DEFINITION)
                .done(function (data) {
                    self.definition = data
                    self.update()

                    if (self.github_active) {
                        $('.ui.checkbox').checkbox()
                    }
                    self.update_dropdowns_and_checkboxes()
                })
                .fail(function (error) {
                    toastr.error("Error fetching definition: " + error.statusText)
                })

            if (self.github_active) {
                CHAGRADE.api.get_cha_user(self.opts.pk)
                    .done(function (data) {
                        self.github_information = data.github_info

                        self.github_request(self.github_information.repos_url.slice(0, 27) + '/repos', function (repo_data) {
                            self.github_repositories = repo_data
                            self.update()
                        })
                        self.update_dropdowns_and_checkboxes()
                    })
                    .fail(function (error) {
                        toastr.error("Error fetching user: " + error.statusText)
                    })
            }

            if (window.SUBMISSION !== undefined) {
                self.update_submission()
            }
        }
    </script>

    <style>
        .commit {
            width: 70%;
        }

        .commit-header {
            width: 100%;
            display: flex;
            flex-direction: row;
        }

        .sha {
            color: #70c4ff;
            font-weight: bold;
            width: 15%;
        }

        .commit-message {
            color: #636363;
            width: 80%;
        }

        .commit-date {
            color: #999999;
        }

        .hidden {
            display: none;
        }

        #challenge_button {
            margin-bottom: 10px;
            margin-left: 3em;
        }

        #submission_header {
            padding-top: 10px;
        }
    </style>
</submit-homework>

