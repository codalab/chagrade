<define-homework>

    <form class="ui form">
        <!-- Important information -->
        <div class="fields">
            <div class="three wide field">
                <div class="ui calendar field required">
                    <label>Start</label>
                    <div class="ui input left icon datepicker">
                        <i class="calendar icon"></i>
                        <input name="due_date" ref="due_date" type="text" value="{definition.due_date}">
                    </div>
                </div>
            </div>

            <div class="three wide field">
                <label>Name:</label>
                <input type="text" name="name" maxlength="100" required ref="name" value="{definition.name}">
            </div>

            <div class="ten wide field">
                <label>Description:</label>
                <input type="text" name="description" maxlength="300" ref="description" value="{definition.description}">
            </div>
        </div>
        <!-- URL Fields -->
        <div class="fields">
            <div class="eight wide field">
                <label>Challenge url:</label>
                <input type="url" name="challenge_url" maxlength="200" ref="challenge_url" value="{definition.challenge_url}">
            </div>

            <div class="eight wide field">
                <label>Starting kit github url:</label>
                <input type="url" name="starting_kit_github_url" maxlength="200"
                       ref="starting_kit_github_url" value="{definition.starting_kit_github_url}">
            </div>
        </div>
        <!-- Default Submission Questions -->
        <div class="fields">
            <div class="four wide field">
                <label>Ask method name:</label>
                <input class="ui checkbox" type="checkbox" name="ask_method_name" ref="ask_method_name" checked="{definition.ask_method_name}">
            </div>

            <div class="four wide field">
                <label>Ask method description:</label>
                <input class="ui checkbox" type="checkbox" name="ask_method_description" ref="ask_method_description" checked="{definition.ask_method_description}">
            </div>

            <div class="four wide field">
                <label>Ask project url:</label>
                <input class="ui checkbox" type="checkbox" name="ask_project_url" ref="ask_project_url" checked="{definiton.ask_project_url}">
            </div>

            <div class="four wide field">
                <label>Ask publication url:</label>
                <input class="ui checkbox" type="checkbox" name="ask_publication_url" ref="ask_publication_url" checked="{definition.ask_publication_url}">
            </div>

            <div class="four wide field">
                <label>Team based:</label>
                <input class="ui checkbox" type="checkbox" name="team_based" ref="team_based" checked="{definition.team_based}">
            </div>
        </div>

        <!-- Custom Questions + Criteria -->

        <div class="ui divider"></div>

        <div>
            <h4 class="ui header">Custom Questions</h4>

            <div style="margin-top: 2.5vh; margin-bottom: 0.5vh;" each="{question, index in questions}">
                <h4 style="margin-bottom: 2.5vh" class="ui dividing header">Question {index + 1}</h4>
                <div class="three inline fields">
                    <div class="four wide inline field">
                        <input type="hidden" name="{'question' + '_id_' + index}" ref="{'question' + '_id_' + index}"
                               value="{question.id}">
                        <label>Question:</label>
                        <input type="text" name="{'question' + '_question_' + index}" maxlength="200"
                               ref="{'question' + '_question_' + index}" value="{question.question}">
                    </div>

                    <div class="four wide inline field">
                        <label>Answer:</label>
                        <input type="text" name="{'question' + '_answer_' + index}" maxlength="200"
                               ref="{'question' + '_answer_' + index}" value="{question.answer}">
                    </div>

                    <div class="four wide inline field">
                        <label>Has Answer:</label>
                        <input class="ui checkbox" type="checkbox" name="{'question' + '_has_specific_answer_' + index}"
                               ref="{'question' + '_has_specific_answer_' + index}" checked="{question.has_specific_answer}">
                    </div>
                    <div class="four wide inline field">
                        <a onclick="{remove_question.bind(this, index)}" class="ui red button">X</a>
                    </div>
                </div>
            </div>

            <a class="ui green button" onclick="{add_question}">Add Question</a>
        </div>

        <div class="ui divider"></div>

        <div>

            <h4 class="ui header">Criteria</h4>

            <div style="margin-top: 2.5vh; margin-bottom: 0.5vh;" each="{criteria, index in criterias}">
                <h4 style="margin-bottom: 2.5vh" class="ui dividing header">Crtieria {index + 1}</h4>
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
                        <a onclick="{remove_criteria.bind(this, index)}" class="ui red button">X</a>
                    </div>
                </div>
            </div>

            <a class="ui blue button" onclick="{add_criteria}">Add Criteria</a>

        </div>

        <div class="ui divider"></div>

        <span><a onclick="{submit_form}" class="ui green button">Submit</a><a onclick="{cancel_button}" class="ui red button">Cancel</a></span>

    </form>

    <script>

        var self = this
        self.criterias = []
        self.questions = []
        self.definition = {}

        self.one('mount', function () {
            //self.update_submission()
            //self.update_definition(self.submission.definition)
            if (window.DEFINITION != undefined) {
                console.log(window.DEFINITION)
                console.log("Updating definition")
               self.update_definition()
            }

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

        })

        self.remove_question = function (index) {
            if (self.refs['question' + '_id_' + index].value !== ""){
                self.delete_question(self.refs['question' + '_id_' + index].value)
            }
            self.questions.splice(index, 1)
            self.update()
        }

        self.add_question = function () {
            self.questions[self.questions.length] = {}
            self.update()
        }

        self.remove_criteria = function (index) {
            if (self.refs['criteria' + '_id_' + index].value !== ""){
                self.delete_criteria(self.refs['criteria' + '_id_' + index].value)
            }
            self.criterias.splice(index, 1)
            self.update()
        }

        self.add_criteria = function () {
            self.criterias[self.criterias.length] = {}
            self.update()
        }

        /*self.update_questions = function () {
            CHAGRADE.api.get_definition(DEFINITION)
                .done(function (data) {
                    self.update({questions: data.custom_questions})
                })
                .fail(function (error) {
                    toastr.error("Error fetching definition: " + error.statusText)
                })
        }*/

        self.update_definition = function() {
            CHAGRADE.api.get_definition(DEFINITION)
                .done(function (data) {
                    self.update({
                        definition: data,
                        questions: data.custom_questions,
                        criterias: data.criterias
                    })
                })
                .fail(function (error) {
                    toastr.error("Error fetching definition: " + error.statusText)
                })
        }

        self.delete_question = function (pk) {
            var result = confirm('Are you sure you wish to delete this Question?')
            if (result) {
                CHAGRADE.api.delete_question(pk)
                .done(function (data) {
                    toastr.success("Successfully deleted question")
                    //self.update_questions()
                })
                .fail(function (response) {
                    if (response) {
                        //var errors = JSON.parse(response.responseText);
                        var data = JSON.parse(response.responseText);
                        var errors = data['errors']

                        self.update({errors: errors})
                    }
                })
            }
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
                    if (response) {
                        //var errors = JSON.parse(response.responseText);
                        var data = JSON.parse(response.responseText);
                        var errors = data['errors']

                        self.update({errors: errors})
                    }
                })
            }
        }

        self.cancel_button = function() {
            window.location='/klasses/wizard/' + KLASS + '/define_homework'
        }

        self.submit_form = function() {

            var obj_data = {
                "klass": KLASS,
                "creator": INSTRUCTOR,
                "due_date": self.refs.due_date.value,
                "name": self.refs.name.value,
                "description": self.refs.description.value,
                "challenge_url": self.refs.challenge_url.value,
                "starting_kit_github_url": self.refs.starting_kit_github_url.value,
                "ask_method_name": self.refs.ask_method_name.value || true,
                "ask_method_description": self.refs.ask_method_description.value || true,
                "ask_project_url": self.refs.ask_project_url.value || true,
                "ask_publication_url": self.refs.ask_publication_url.value || true,
                "team_based": self.refs.team_based.value || false,
                "criterias": [
                    /*{
                        "description": "string",
                        "lower_range": 0,
                        "upper_range": 0
                    }*/
                ],
                "custom_questions": [
                    /*{
                        "has_specific_answer": true,
                        "question": "string",
                        "answer": "string"
                    }*/
                ]
            }

            for (var index = 0; index < self.criterias.length; index++) {
                var temp_data = {
                    //'criteria': parseInt(self.refs['criteria_answer_def_' + index].value),
                    //'score': self.refs['criteria_answer_' + index].value,
                    'description': self.refs['criteria' + '_description_' + index].value,
                    'lower_range': self.refs['criteria' + '_lower_range_' + index].value,
                    'upper_range': self.refs['criteria' + '_upper_range_' + index].value,
                }
                if (self.refs['criteria' + '_id_' + index].value !== ""){
                    temp_data['id'] = self.refs['criteria' + '_id_' + index].value
                }
                obj_data['criterias'].push(temp_data)
            }

            for (var index = 0; index < self.questions.length; index++) {
                var temp_data = {
                    //'criteria': parseInt(self.refs['criteria_answer_def_' + index].value),
                    //'score': self.refs['criteria_answer_' + index].value,
                    'question': self.refs['question' + '_question_' + index].value,
                    'answer': self.refs['question' + '_answer_' + index].value,
                    'has_specific_answer': self.refs['question' + '_has_specific_answer_' + index].value,
                }
                if (self.refs['question' + '_id_' + index].value !== ""){
                    temp_data['id'] = self.refs['question' + '_id_' + index].value
                }
                obj_data['custom_questions'].push(temp_data)
            }

            console.log("@@@@@@@@@")
            console.log(self.refs.due_date.value,)
            console.log(obj_data)

            if (window.DEFINITION != undefined) {
                var endpoint = CHAGRADE.api.update_definition(DEFINITION, obj_data)
            }
            else {
                var endpoint = CHAGRADE.api.create_definition(obj_data)
            }

            endpoint
                .done(function (data) {
                    console.log(data)
                    window.location='/klasses/wizard/' + KLASS + '/define_homework'
                })
                .fail(function (error) {
                    toastr.error("Error creating definition: " + error.statusText)
                })
        }

    </script>
</define-homework>