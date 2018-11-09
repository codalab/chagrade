<grade-homework>

    <h4 class="ui header">Grades:</h4>
    <div class="ui relaxed celled list">
        <ol>
            <li each="{criteria, index in definition.criterias}" class="inline field">
                <label>{criteria.description}:</label>
                <input name="{'criteria_answer_def_' + index}" ref="{'criteria_answer_def_' + index}" type="hidden" value="{criteria.id}">
                <input name="{'criteria_answer_id_' + index}" ref="{'criteria_answer_id_' + index}" type="hidden" value="{criteria.answer_id}">
                <input placeholder="{criteria.lower_range} - {criteria.upper_range}" name="{'criteria_answer_' + index}" ref="{'criteria_answer_' + index}" type="text" value="{ criteria.prev_answer }">
            </li>
        </ol>
    </div>
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

    <span><a onclick="{submit_form}" class="ui green button">Submit</a><a onclick="{cancel_button}" class="ui red button">Cancel</a></span>

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

        /*self.get_answer_value = function(criteria_pk, key) {
            console.log(criteria_pk, key)
            for (var index = 0; index < grade.criteria_answers.length; index++) {
                if (grade.criteria_answers[index].criteria === criteria_pk) {
                    return grade.criteria_answers[index][key]
                }
            }
            return ''
        }*/

        self.update_criteria_answers = function() {
            console.log("#######@#@@@@@@@@@@@@@@@@@@@@")
            console.log(self.grade.criteria_answers.length)
            console.log(self.definition.criterias.length)
            //console.log(self.definition.criterias)


            var data =self.definition

            for (var index = 0; index < self.grade.criteria_answers.length; index++) {
                for (var grade_index = 0; grade_index < data.criterias.length; grade_index++) {
                    console.log("Testing: " + self.grade.criteria_answers[index].criteria + " and " + data.criterias[grade_index].id + "!")
                    if (self.grade.criteria_answers[index].criteria === data.criterias[grade_index].id) {
                        console.log("It's a match!!!!!!!!!!!!!!")
                        data.criterias[grade_index].prev_answer = self.grade.criteria_answers[index].score
                        data.criterias[grade_index].answer_id = self.grade.criteria_answers[index].id
                    }
                }
            }
            console.log(data)
            self.update({definition: data})
            console.log(self.definition)
        }

        /*self.remove_question_answer = function (index) {
            self.question_answers.splice(index, 1)
            self.update()
        }

        self.add_question_answer = function () {
            self.question_answers[self.question_answers.length] = {}
            self.update()
        }*/

        self.one('mount', function () {
            self.update_submission()
            /*if (window.GRADE != undefined) {
                console.log(window.GRADE)
                console.log("Updating grade")
                self.update_grade()
                self.update_criteria_answers()
            }*/
            //self.update_definition(self.submission.definition)
        })


        self.submit_form = function() {

            var obj_data = {
                "submission": SUBMISSION,
                "evaluator": INSTRUCTOR,
                "teacher_comments": self.refs.teacher_comments.value || '',
                "instructor_notes": self.refs.instructor_notes.value || '',
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
                    'score': self.refs['criteria_answer_' + index].value,
                }
                if (self.refs['criteria_answer_id_' + index].value !== ""){
                    temp_data['id'] = self.refs['criteria_answer_id_' + index].value
                }
                obj_data['criteria_answers'].push(temp_data)
                //Do something

            }

            // Nested writable doesn't like empty lists
            /*if (obj_data['criteria_answers'].length == 0){
                delete obj_data['criteria_answers']
            }*/

            console.log("@@@@@@@@@")
            console.log(obj_data)

            if (window.GRADE != undefined) {
                var endpoint = CHAGRADE.api.update_grade(GRADE, obj_data)
            }
            else {
                var endpoint = CHAGRADE.api.create_grade(obj_data)
            }

            endpoint
                .done(function (data) {
                    console.log(data)
                    window.location = '/klasses/wizard/' + KLASS + '/grade_homework'
                })
                .fail(function (error) {
                    toastr.error("Error creating submission: " + error.statusText)
                })
        }

        self.cancel_button = function() {
            window.location = '/klasses/wizard/' + KLASS + '/grade_homework'
        }


        self.update_definition = function (pk) {
            CHAGRADE.api.get_definition(pk)
                .done(function (data) {
                    //console.log("@@@@@@@@@@@@@@@@@@@")
                    //console.log(data)
                    self.update({
                        //questions: data.custom_questions,
                        definition: data
                    })
                    if (window.GRADE != undefined) {
                        //console.log(window.GRADE)
                        console.log("Updating grade")
                        self.update_grade()
                        //self.update_criteria_answers()
                    }
                })
                .fail(function (error) {
                    toastr.error("Error fetching definition: " + error.statusText)
                })
        }

        self.update_submission = function () {
            CHAGRADE.api.get_submission(SUBMISSION)
                .done(function (data) {
                    //console.log("!!!!!!!!!!!!!!!!!!")
                    //console.log(data)
                    self.update_definition(data.definition)
                    self.update({
                        //questions: data.custom_questions,
                        submission: data
                    })
                })
                .fail(function (error) {
                    toastr.error("Error fetching submission: " + error.statusText)
                })
        }

        self.update_grade = function () {
            console.log("I GOT CALLED")
            CHAGRADE.api.get_grade(GRADE)
                .done(function (data) {
                    console.log("#########")
                    console.log(data)
                    //self.update_definition(data.definition)
                    self.update({
                        //questions: data.custom_questions,
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