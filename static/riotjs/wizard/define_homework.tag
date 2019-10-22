<define-homework>

    <form class="ui form" ref="form" onsubmit="{  }">
        <!-- Important information -->
        <div class="fields">
            <div class="three wide field">
                <div class="ui required calendar field">
                    <label>
                        Due-Date:
                    </label>
                    <div class="ui input left icon datepicker">
                        <i class="calendar icon"></i>
                        <input name="due_date" ref="due_date" type="text" value="{definition.due_date}">
                    </div>
                </div>
            </div>

            <div class="three wide required field">
                <label>Name:</label>
                <input type="text" name="name" maxlength="100" required ref="name" value="{definition.name}">
            </div>

            <div class="ten wide field">
                <label>Description:</label>
                <input type="text" name="description" maxlength="300" ref="description"
                       value="{definition.description}">
            </div>
        </div>

        <div class="fields">
            <div class="eight wide field">
                <label>Custom Questions Only (No competition):</label>
                <input class="ui checkbox" type="checkbox" name="questions_only" ref="questions_only"
                       checked="{definition.questions_only}" onclick="{ update_questions_only }">
            </div>
        </div>

        <!-- URL Fields -->
        <div if="{ !definition.questions_only }" class="fields">
            <div class="eight wide required field">
                <label>
                    <i class="pop-up question blue circle icon"
                       data-title="A URL to a challenge. Chagrade compatible features should be enabled."
                       data-content="Ex: http://competitions.codalab.org/competitions/1"></i>
                    Default Challenge url:
                </label>
                <input type="url" name="challenge_url" maxlength="200" ref="challenge_url"
                       value="{definition.challenge_url}">
            </div>

            <div class="eight wide field">
                <label>
                    <i class="pop-up question blue circle icon"
                       data-title="A direct link for a starting kit file"
                       data-content="Ex: https://github.com/Tthomas63/chagrade_test_submission/blob/master/chagrade_test_submission-master.zip"></i>
                    Starting kit github url:
                </label>
                <input type="url" name="starting_kit_github_url" maxlength="200"
                       ref="starting_kit_github_url" value="{definition.starting_kit_github_url}">
            </div>
        </div>
        <!-- Scoring Fields -->
        <div if="{ !definition.questions_only }" class="fields">
            <div class="eight wide required field">
                <label>
                    <i class="pop-up question blue circle icon"
                       data-content="This is the lowest score expected. Usually zero or the score that the homework starting kit achieves. This serves as the baseline score for the metrics scale. "></i>
                       Baseline Score
                </label>
                <input type="number" name="baseline_score" maxlength="10" ref="baseline_score"
                       value="{definition.baseline_score}">
            </div>

            <div class="eight wide required field">
                <label>
                    <i class="pop-up question blue circle icon"
                       data-title="Target Score"
                       data-content="This is the score that everyone will be shooting for. In metrics, a score this high or higher will be considered 100%."></i>
                       Target Score
                </label>
                <input type="number" name="target_score" maxlength="10"
                       ref="target_score" value="{definition.target_score}">
            </div>
        </div>
        <!-- Default Submission Questions -->
        <div class="fields">
            <div class="four wide field">
                <label>Ask method name:</label>
                <input class="ui checkbox" type="checkbox" name="ask_method_name" ref="ask_method_name"
                       checked="{definition.ask_method_name}">
            </div>

            <div class="four wide field">
                <label>Ask method description:</label>
                <input class="ui checkbox" type="checkbox" name="ask_method_description" ref="ask_method_description"
                       checked="{definition.ask_method_description}">
            </div>

            <div class="four wide field">
                <label>Ask project url:</label>
                <input class="ui checkbox" type="checkbox" name="ask_project_url" ref="ask_project_url"
                       checked="{definition.ask_project_url}">
            </div>

            <div class="four wide field">
                <label>Ask publication url:</label>
                <input class="ui checkbox" type="checkbox" name="ask_publication_url" ref="ask_publication_url"
                       checked="{definition.ask_publication_url}">
            </div>

            <div class="four wide field">
                <label>Team based:</label>
                <input class="ui checkbox" type="checkbox" name="team_based" ref="team_based"
                       checked="{definition.team_based}">
            </div>
        </div>

        <!-- Team Challenge URL -->

        <div if="{ !definition.questions_only }" style="width: 100%;" class="ui styled accordion">
            <virtual each="{team in definition.teams}">
                <div class="title">
                    <i class="dropdown icon"></i>
                    {team.name}
                </div>
                <div class="content">
                    <label>
                        <i class="pop-up question blue circle icon"
                           data-title="A URL to a challenge. Overrides the default for a team."
                           data-content="Ex: http://competitions.codalab.org/competitions/2"></i>
                        Challenge URL:
                    </label>
                    <input type="text" data-custom-challenge-id="{team.custom_challenge_id}" name="team_challenge_url"
                           ref="team_{team.id}_challenge_url" value="{team.custom_challenge_url}">
                </div>
            </virtual>
        </div>

        <!-- Custom Questions + Criteria -->

        <div class="ui divider"></div>

        <div>
            <h4 class="ui header">Custom Questions</h4>

            <div style="margin-top: 2.5vh; margin-bottom: 0.5vh;" each="{question, index in questions}">
                <h4 style="margin-bottom: 2.5vh" class="ui dividing header">Question {index + 1}</h4>
                <div class="ui four inline fields">
                    <div class="required six wide field">
                        <label>Question:</label>
                        <textarea type="text" name="{'question' + '_question_' + index}" rows="1"
                                  ref="{'question' + '_question_' + index}" value="{question.question}"> </textarea>
                        <input type="hidden" name="{'question' + '_id_' + index}" ref="{'question' + '_id_' + index}"
                               value="{question.id}">
                    </div>

                    <div class="ui four wide field"></div>

                    <div class="ui four wide required field">
                        <label>Type:</label>
                        <div class="ui selection dropdown" ref="{'selection_dropdown_' + index}">
                            <input type="hidden" name="{ 'question_type_' + index }">
                            <div class="default text">Type</div>
                            <i class="dropdown icon"> </i>
                            <div class="menu">
                                <div class="item" data-value="MS">
                                    <i class="ui check square outline icon"></i> Multiple Select
                                </div>
                                <div class="item" data-value="SS">
                                    <i class="ui dot circle outline icon"></i> Single Select
                                </div>
                                <div class="item" data-value="TX">
                                    <i class="ui align left icon"></i> Text
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="ui one wide field">
                        <a onclick="{remove_question.bind(this, index)}" class="delete-button">
                            <i class="ui large red icon trash alternate outline"> </i>
                        </a>
                    </div>
                </div>

                <div if="{ question.type === 'MS' || question.type === 'SS' }" each="{answer_candidate, candidate_index in question.answer_candidates}" class="two inline fields">
                    <div class="six wide inline field">
                        <label>
                            <i if="{ question.type === 'MS' }" class="ui grey square icon"> </i>
                            <i if="{ question.type === 'SS' }" class="ui grey circle icon"> </i>
                        </label>
                        <input type="text" name="{'question' + '_answer_' + index}" maxlength="200" placeholder="Option {candidate_index + 1}"
                               ref="{'answer_candidate_' + index + '_' + candidate_index}" value="{answer_candidate}" onkeypress="{ () => focus_next_input(event, index, candidate_index)}" onkeyup="{ () => update_answer_candidate_text(event, index, candidate_index)}">
                    </div>
                    <div class="six wide inline field">
                        <a onclick="{remove_answer_candidate.bind(this, index, candidate_index)}" class="delete-button">
                            <i class="ui grey trash alternate outline icon"> </i>
                        </a>
                    </div>
                </div>

                <button if="{question.type === 'MS' || question.type === 'SS'}" class="ui basic green button add-answer-candidate" onclick="{ () => add_answer_candidate(event, index) }" ref="{'add_answer_candidate_button_' + index}">
                    <i class="green plus icon"> </i> Add answer candidate
                </button>

            </div>

            <a class="ui green button" onclick="{ () => add_question(questions.length) }">Add Question</a>
        </div>

        <div class="ui divider"></div>

        <div>

            <h4 class="ui header">Criteria</h4>

            <div style="margin-top: 2.5vh; margin-bottom: 0.5vh;" each="{criteria, index in criterias}">
                <h4 style="margin-bottom: 2.5vh" class="ui dividing header">Criterion {index + 1}</h4>
                <div class="three inline fields">
                    <div class="four wide inline field">
                        <input type="hidden" name="{'criteria' + '_id_' + index}" ref="{'criteria' + '_id_' + index}"
                               value="{criteria.id}">
                        <label>Criteria:</label>
                        <input type="text" name="{'criteria' + '_description_' + index}" maxlength="200"
                               ref="{'criteria' + '_description_' + index}" value="{criteria.description || ''}">
                    </div>

                    <div class="four wide inline field">
                        <label>Lowest Grade:</label>
                        <input type="text" name="{'criteria' + '_lower_range_' + index}" maxlength="6"
                               ref="{'criteria' + '_lower_range_' + index}" value="{criteria.lower_range || 0}">
                    </div>

                    <div class="four wide inline field">
                        <label>Highest Grade:</label>
                        <input class="" type="text" name="{'criteria' + '_upper_range_' + index}" maxlength="6"
                               ref="{'criteria' + '_upper_range_' + index}" value="{criteria.upper_range || 10}">
                    </div>
                    <div class="four wide inline field">
                        <a onclick="{remove_criteria.bind(this, index)}" class="delete-button">
                            <i class="ui large red trash alternate outline icon"></i>
                        </a>
                    </div>
                </div>
            </div>

            <a class="ui blue button" onclick="{add_criteria}">Add Criterion</a>

        </div>

        <div class="ui divider"></div>

        <span><a onclick="{submit_form}" class="ui green button">Submit</a><a onclick="{cancel_button}"
                                                                              class="ui red button">Cancel</a></span>
        <div class="ui error message"></div>

    </form>

    <script>

        var self = this
        self.criterias = []
        self.questions = []
        self.definition = {}

        self.one('mount', function () {
            if (window.DEFINITION != undefined) {
                self.update_definition()
            } else {
                self.update_teams()
            }

            $('.ui.accordion')
                .accordion()
            ;

            $('.datepicker').calendar({
                type: 'date',
                formatter: {
                    date: function (date, settings) {
                        return luxon.DateTime.fromJSDate(date).toISO()
                    }
                },
                popupOptions: {
                    position: 'bottom left',
                    lastResort: 'bottom left',
                    hideOnScroll: false
                }
            })

            $('.pop-up').popup({
                inline: true,
                position: 'top left',
            });


            $(document).on('submit', 'form', function(e){
                /* on form submit find the trigger */
                console.info('submit event', e)
                if( $(e.delegateTarget.activeElement).not('input, textarea').length == 0 ){
                    /* if the trigger is not between selectors list, return super false */
                    e.preventDefault();
                    return false;
                }
            });
        })


        self.focus_next_input = function (event, question_index, candidate_index) {
            if (event.which === 13) {
                event.preventDefault()
                let question = self.questions[question_index]
                if (question.hasOwnProperty('answer_candidates')){
                    if (question.answer_candidates.length - 1 <= candidate_index) {
                        self.refs['add_answer_candidate_button_' + question_index].click()
                    } else {
                        $(self.refs['answer_candidate_' + question_index + '_' + (candidate_index + 1)]).focus()
                    }
                } else {
                    self.refs['add_answer_candidate_button_' + question_index].click()
                }
            }
        }

        self.update_teams = function () {
            CHAGRADE.api.get_teams(KLASS)
                .done(function (data) {
                    //self.update({definition['teams']: data})
                    console.log(data)
                    self.definition.teams = data
                    self.update()
                })
                .fail(function (error) {
                    toastr.error("Error fetching teams: " + error.statusText)
                })
        }

        self.remove_question = function (index) {
            var result = confirm('Are you sure you wish to delete this Question?')
            if (result) {
                if (self.refs['question' + '_id_' + index].value !== "") {
                    self.delete_question(self.refs['question' + '_id_' + index].value)
                }
                self.questions.splice(index, 1)
                self.update()

                self.update_dropdowns()
            }
        }

        self.update_dropdowns = function () {
            let fields = {}

            for(let question_index = 0; question_index < self.questions.length; question_index++) {
                $(self.refs['selection_dropdown_' + question_index])
                    .dropdown({
                        action: 'activate',
                        onChange: function (value, readable_name, element) {
                            let question = self.questions[question_index]
                            question.type = value
                            self.update()

                            if (value === 'MS' || value === 'SS') {
                                if (question.hasOwnProperty('answer_candidates')) {
                                    if (question.answer_candidates.length === 0) {
                                        self.refs['add_answer_candidate_button_' + question_index].click()
                                    }
                                } else {

                                    self.refs['add_answer_candidate_button_' + question_index].click()
                                }
                            }
                        }
                    })

                let question_field = {}
                question_field.rules = [
                    {
                        type: 'minLength[1]',
                        prompt: 'Question ' + (question_index + 1) + ' must not be empty.',
                    }
                ]
                fields['question_question_' + question_index] = question_field

                let type_field = {}
                type_field.rules = [
                    {
                        type: 'minLength[2]',
                        prompt: 'Question ' + (question_index + 1) + ' type selection must not be empty.',
                    }
                ]
                fields['question_type_' + question_index] = type_field
            }

            let form = $(self.refs.form)
            form.form({
                fields: fields,
            })
        }


        self.add_question = function (question_index) {
            self.questions[question_index] = {
                type: null,
            }
            self.update()
            $(self.refs['selection_dropdown_' + question_index])
                .dropdown({
                    action: 'activate',
                    onChange: function (value, readable_name, element) {
                        let question = self.questions[question_index]
                        question.type = value
                        self.update()

                        if (value === 'MS' || value === 'SS') {
                            if (question.hasOwnProperty('answer_candidates')) {
                                if (question.answer_candidates.length === 0) {
                                    self.refs['add_answer_candidate_button_' + question_index].click()
                                }
                            } else {

                                self.refs['add_answer_candidate_button_' + question_index].click()
                            }
                        }
                    }
                })
            self.update()
            self.update_dropdowns()
        }

        self.update_answer_candidate_text = function (event, index, candidate_index) {
            if (candidate_index === null) {
                self.questions[index].text = event.target.value
            } else {
                self.questions[index].answer_candidates[candidate_index] = event.target.value
            }
            self.update()
        }

        self.remove_answer_candidate = function (index, candidate_index) {
            let question = self.questions[index]
            if (question.hasOwnProperty('answer_candidates')) {
                question.answer_candidates.splice(candidate_index, 1)
            }
            self.update()
        }

        self.add_answer_candidate = function (event, index) {
            event.preventDefault()
            let question = self.questions[index]
            if (!question.hasOwnProperty('answer_candidates')) {
                question.answer_candidates = []
            }
            question.answer_candidates.push('')
            self.update()
            $(self.refs['answer_candidate_' + index + '_' + (question.answer_candidates.length - 1)]).focus()
        }

        self.remove_criteria = function (index) {
            if (self.refs['criteria' + '_id_' + index].value !== "") {
                self.delete_criteria(self.refs['criteria' + '_id_' + index].value)
            }
            self.criterias.splice(index, 1)
            self.update()
        }

        self.add_criteria = function () {
            self.criterias[self.criterias.length] = {}
            self.update()
        }

        self.update_definition = function () {
            CHAGRADE.api.get_definition(DEFINITION)
                .done(function (data) {
                    data.teams.forEach(function (team) {
                        data.custom_challenge_urls.forEach(function (custom_url) {
                            if (team.id === custom_url.team) {
                                team.custom_challenge_url = custom_url.challenge_url,
                                    team.custom_challenge_id = custom_url.id
                            }
                        })
                    })


                    self.update({
                        definition: data,
                        questions: data.custom_questions,
                        criterias: data.criterias
                    })

                    $('.pop-up').popup({
                        inline: true,
                        position: 'top left',
                    })


                    self.update_dropdowns()

                    for (let i = 0; i < self.questions.length; i++) {
                        let question = self.questions[i]
                        if (question.type === 'SS' || question.type === 'MS') {
                            self.questions[i].answer_candidates = question.candidate_answers
                        }
                        $(self.refs['selection_dropdown_' + i]).dropdown('set selected', question.type)

                    }


                    $(document).on('input', 'textarea', function () {
                        $(this).outerHeight(38).outerHeight(this.scrollHeight); // 38 or '1em' -min-height
                    });

                    let textareas = $('textarea')
                    _.forEach(textareas, textarea => {
                        let event = new Event('input', {
                            'bubbles': true,
                            'cancelable': true
                        });
                        textarea.dispatchEvent(event)

                    })

                })
                .fail(function (error) {
                    toastr.error("Error fetching definition: " + error.statusText)
                })
        }

        self.update_questions_only = function () {
            self.definition.questions_only = self.refs.questions_only.checked
            self.update()
        }

        self.delete_question = function (pk) {
            CHAGRADE.api.delete_question(pk)
                .done(function (data) {
                    toastr.success("Successfully deleted question")
                })
                .fail(function (response) {
                    console.log(response)
                    Object.keys(response.responseJSON).forEach(function (key) {
                        toastr.error("Error with " + key + "! " + response.responseJSON[key])
                    });
                })
        }

        self.delete_criteria = function (pk) {
            var result = confirm('Are you sure you wish to delete this Criteria?')
            if (result) {
                CHAGRADE.api.delete_criteria(pk)
                    .done(function (data) {
                        toastr.success("Successfully deleted criteria")
                        self.update_criterias()
                    })
                    .fail(function (response) {
                        console.log(response)
                        Object.keys(response.responseJSON).forEach(function (key) {
                            toastr.error("Error with " + key + "! " + response.responseJSON[key])
                        });
                    })
            }
        }

        self.cancel_button = function () {
            window.location = '/klasses/wizard/' + KLASS + '/define_homework'
        }

        self.submit_form = function () {
            let form = $(self.refs.form)
            form.form('validate form')

            //self.submit_team_changes()
            if (!form.form('is valid')) {
                console.log('not valid')
                return
            }

            var obj_data = {
                "klass": KLASS,
                "creator": INSTRUCTOR,
                "due_date": self.refs.due_date.value,
                "name": self.refs.name.value,
                "description": self.refs.description.value,
                "questions_only": self.definition.questions_only,
                "ask_method_name": self.refs.ask_method_name.checked,
                "ask_method_description": self.refs.ask_method_description.checked,
                "ask_project_url": self.refs.ask_project_url.checked,
                "ask_publication_url": self.refs.ask_publication_url.checked,
                "team_based": self.refs.team_based.checked,
                "criterias": [
                    /*{
                     "description": "string",
                     "lower_range": 0,
                     "upper_range": 0
                     }*/
                ],
                "custom_challenge_urls": [],
                "custom_questions": [
                    /*{
                     "has_specific_answer": true,
                     "question": "string",
                     "answer": "string"
                     }*/
                ]
            }
            console.table(obj_data)
//            return

            for (var index = 0; index < self.criterias.length; index++) {
                var temp_data = {
                    'description': self.refs['criteria' + '_description_' + index].value,
                    'lower_range': self.refs['criteria' + '_lower_range_' + index].value,
                    'upper_range': self.refs['criteria' + '_upper_range_' + index].value,
                }
                if (self.refs['criteria' + '_id_' + index].value !== "") {
                    temp_data['id'] = self.refs['criteria' + '_id_' + index].value
                }
                obj_data['criterias'].push(temp_data)
            }

            // Strip empty questions off of questions array
            self.questions = self.questions.filter( function (question) {
                if (question.type === null) {
                    return false
                } else {
                    return true
                }
            })

            for (var index = 0; index < self.questions.length; index++) {
                let question = self.questions[index]
                if (question.type !== null) {
                    let answer_candidates = null
                    if (question.type === 'TX') {
                        answer_candidates = question.text
                    } else if (question.type === 'MS' || question.type === 'SS') {
                        answer_candidates = question.answer_candidates.filter(function (answer) {
                            return answer !== ''
                        })
                    }

                    var temp_data = {
                        'question': self.refs['question' + '_question_' + index].value,
                        'type': question.type,
                        'candidate_answers': answer_candidates,
                        //'answer': self.refs['question' + '_answer_' + index].value,
                        //'has_specific_answer': self.refs['question' + '_has_specific_answer_' + index].value,
                    }
                    if (self.refs['question' + '_id_' + index].value !== "") {
                        temp_data['id'] = self.refs['question' + '_id_' + index].value
                    }
                    obj_data['custom_questions'].push(temp_data)
                }
            }

            if (!self.definition.questions_only) {
                obj_data["challenge_url"] = self.refs.challenge_url.value
                obj_data["starting_kit_github_url"] = self.refs.starting_kit_github_url.value
                obj_data["baseline_score"] = self.refs.baseline_score.value
                obj_data["target_score"] = self.refs.target_score.value

                self.definition.teams.forEach(function (team) {
                    if (self.refs["team_" + team.id + "_challenge_url"].value !== '') {
                        temp_data = {
                            //'definition': self.definition.id,
                            'team': team.id,
                            'challenge_url': self.refs["team_" + team.id + "_challenge_url"].value
                        }
                        if (self.refs["team_" + team.id + "_challenge_url"].dataset.customChallengeId !== undefined) {
                            temp_data['id'] = self.refs["team_" + team.id + "_challenge_url"].dataset.customChallengeId
                        }
                        obj_data['custom_challenge_urls'].push(temp_data)
                    }
                })
            }

            if (window.DEFINITION != undefined) {
                var endpoint = CHAGRADE.api.update_definition(DEFINITION, obj_data)
            }
            else {
                var endpoint = CHAGRADE.api.create_definition(obj_data)
            }

            console.log(obj_data)

            endpoint
                .done(function (data) {
                    window.location = '/klasses/wizard/' + KLASS + '/define_homework'
                })
                .fail(function (response) {
                    console.log(response)
                    Object.keys(response.responseJSON).forEach(function (key) {
                        if (key === 'criterias' || key === 'custom_questions') {
                            toastr.error("An error occured with " + key + "! Please make sure you did not leave any fields blank.")
                        } else {
                            toastr.error("Error with " + key + "! " + response.responseJSON[key])
                        }
                    });
                })
        }

    </script>

    <style>
        textarea {
            resize: none !important;
            overflow: hidden;
            height: 3em;
            font-size: 1.0em !important;
        }

        .delete-button {
            cursor: pointer;
        }
    </style>

</define-homework>