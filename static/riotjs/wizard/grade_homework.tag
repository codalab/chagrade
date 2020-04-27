<grade-homework>
    <h4>Other Homework Questions</h4>
    <div class="ui relaxed celled list">
        <ol>
            <li each="{ question in definition.custom_questions }">{ question.question }
                <ul>
                    <li if="{ question.question_type == 'UL' }" each="{ answer in question.student_answers }">
                        <a href="{ answer }" target="_blank">{ answer }</a>
                    </li>
                    <li if="{ question.question_type != 'UL' }" each="{ answer in question.student_answers }">{ answer }</li>
                </ul>
            </li>
        </ol>
    </div>

    <h4 class="ui header">Grades:</h4>
    <label>Jupyter Notebook ({definition.jupyter_notebook_lowest} - {definition.jupyter_notebook_highest}):</label>
    <input placeholder="{definition.jupyter_notebook_lowest} - {definition.jupyter_notebook_highest}" name="jupyter_notebook_grade" ref="jupyter_notebook_grade" type="text" value="{grade.jupyter_notebook_grade}">
    <div class="ui relaxed celled list">
        <ol>
            <li each="{criteria, index in definition.criterias}" class="inline field">
                <label>{criteria.description} ({criteria.lower_range} - {criteria.upper_range}):</label>
                <input name="{'criteria_answer_def_' + index}" ref="{'criteria_answer_def_' + index}" type="hidden" value="{criteria.id}">
                <input name="{'criteria_answer_id_' + index}" ref="{'criteria_answer_id_' + index}" type="hidden" value="{criteria.answer_id}">
                <input placeholder="{criteria.lower_range} - {criteria.upper_range}" name="{'criteria_answer_' + index}" ref="{'criteria_answer_' + index}" type="text" value="{ criteria.prev_answer }">
            </li>
        </ol>
    </div>
    <div class="ui form">
        <div class="fields">
            <div class="eight wide field">
                <label>Comments visible by students:</label>
                <br>
                <textarea name="teacher_comments" ref="teacher_comments" rows="5" cols="60">{grade.teacher_comments}</textarea>
            </div>
            <div class="eight wide field">
                <label>Private Notes:</label>
                <br>
                <textarea name="instructor_notes" ref="instructor_notes" rows="5" cols="60">{grade.instructor_notes}</textarea>
            </div>
        </div>
    </div>


    <span>
        <a onclick="{submit_form.bind(this, true)}" class="ui green button">Save and Publish</a>
        <a onclick="{submit_form.bind(this, false)}" class="ui yellow button">Save and Un-Publish</a>
        <a onclick="{cancel_button}" class="ui red button">Cancel</a>
    </span><br>
    <span>Note: Students can view published grades, students cannot view un-published grades</span>

    <script>
        var self = this
        self.errors = []
        self.criteria_answers = []
        self.definition = {
            'ask_publication_url': false,
            'ask_project_url': false,
            'ask_method_name': false,
            'ask_method_description': false,
            'criterias': []
        }
        self.grade = {
            'criteria_answers': []
        }

        self.update_criteria_answers = function() {
            var data =self.definition

            for (var index = 0; index < self.grade.criteria_answers.length; index++) {
                for (var grade_index = 0; grade_index < data.criterias.length; grade_index++) {
                    if (self.grade.criteria_answers[index].criteria === data.criterias[grade_index].id) {
                        data.criterias[grade_index].prev_answer = self.grade.criteria_answers[index].score
                        data.criterias[grade_index].answer_id = self.grade.criteria_answers[index].id
                    }
                }
            }
            self.update({definition: data})
        }

        self.one('mount', function () {
            self.update_submission()
        })


        self.submit_form = function(published) {

            var obj_data = {
                "submission": SUBMISSION,
                "evaluator": INSTRUCTOR,
                "teacher_comments": self.refs.teacher_comments.value,
                "instructor_notes": self.refs.instructor_notes.value,
                "needs_review": false,
                "criteria_answers": [
                    /*{
                        "criteria": 0,
                        "score": 0
                    }*/
                ]
            }

            for (var index = 0; index < self.definition.criterias.length; index++) {
                var temp_data = {
                    'criteria': parseInt(self.refs['criteria_answer_def_' + index].value),
                    'score': self.refs['criteria_answer_' + index].value || 0,
                }
                if (self.refs['criteria_answer_id_' + index].value !== ""){
                    temp_data['id'] = self.refs['criteria_answer_id_' + index].value
                }
                obj_data['criteria_answers'].push(temp_data)
            }

            obj_data.published = published

            if (self.definition.jupyter_notebook_enabled) {
                obj_data['jupyter_notebook_grade'] = self.refs.jupyter_notebook_grade.value
            }

            if (window.GRADE != undefined) {
                var endpoint = CHAGRADE.api.update_grade(GRADE, obj_data)
            }
            else {
                var endpoint = CHAGRADE.api.create_grade(obj_data)
            }

            endpoint
                .done(function (data) {
                    window.location = '/klasses/wizard/' + KLASS + '/grade_homework'
                })
                .fail(function (response) {
                    Object.keys(response.responseJSON).forEach(function (key) {
                        if (key === 'criteria_answers') {
                            toastr.error("An error occured with " + key + "! Please make sure you did not leave any fields blank.")
                        } else {
                            toastr.error("Error with " + key + "! " + response.responseJSON[key])
                        }
                    });
                })
        }

        self.cancel_button = function() {
            window.location = '/klasses/wizard/' + KLASS + '/grade_homework'
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
                    self.update({
                        definition: data
                    })
                    if (window.GRADE != undefined) {
                        self.update_grade()
                    }
                })
                .fail(function (error) {
                    toastr.error("Error fetching definition: " + error.statusText)
                })
        }

        self.update_submission = function () {
            CHAGRADE.api.get_submission(SUBMISSION)
                .done(function (data) {
                    self.update_definition(data.definition)
                    self.update({
                        submission: data
                    })
                })
                .fail(function (error) {
                    toastr.error("Error fetching submission: " + error.statusText)
                })
        }

        self.update_grade = function () {
            CHAGRADE.api.get_grade(GRADE)
                .done(function (data) {
                    self.update({
                        grade: data
                    })
                    self.update_criteria_answers()
                })
                .fail(function (error) {
                    toastr.error("Error fetching submission: " + error.statusText)
                })
        }
    </script>
</grade-homework>
