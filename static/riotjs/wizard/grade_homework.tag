<grade-homework>

    <h4 class="ui header">Grades:</h4>
    <div class="ui relaxed celled list">
        <ol>
            <li each="{criteria, index in definition.criterias}" class="inline field">
                <label>{criteria.description}:</label>
                <input name="{'criteria_answer_def_' + index}" ref="{'criteria_answer_def_' + index}" type="hidden" value="{criteria.id}">
                <input placeholder="{criteria.lower_range} - {criteria.upper_range}" name="{'criteria_answer_' + index}" ref="{'criteria_answer_' + index}" type="text">
            </li>
        </ol>
    </div>
    <div class="fields">
        <div class="field">
            <label>Comments visible by students:</label>
            <br>
            <textarea name="teacher_comments" ref="teacher_comments" rows="5" cols="60"></textarea>
        </div>
        <div class="field">
            <label>Private Notes:</label>
            <br>
            <textarea name="instructor_notes" ref="instructor_notes" rows="5" cols="60"></textarea>
        </div>
    </div>

    <span><a onclick="{submit_form}" class="ui green button">Submit</a><a class="ui red button">Cancel</a></span>

    <script>


        var self = this
        self.errors = []
        self.definition = {
            'ask_publication_url': false,
            'ask_project_url': false,
            'ask_method_name': false,
            'ask_method_description': false,
            'criterias': []
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
                obj_data['criteria_answers'].push({
                    'criteria': parseInt(self.refs['criteria_answer_def_' + index].value),
                    'score': self.refs['criteria_answer_' + index].value,
                })
                //Do something

            }

            // Nested writable doesn't like empty lists
            /*if (obj_data['criteria_answers'].length == 0){
                delete obj_data['criteria_answers']
            }*/

            console.log("@@@@@@@@@")
            console.log(obj_data)

            CHAGRADE.api.create_grade(obj_data)
                .done(function (data) {
                    console.log(data)
                    window.location='/klasses/wizard/' + KLASS + '/grade_homework'
                })
                .fail(function (error) {
                    toastr.error("Error creating submission: " + error.statusText)
                })
        }


        self.update_definition = function (pk) {
            CHAGRADE.api.get_definition(pk)
                .done(function (data) {
                    console.log("@@@@@@@@@@@@@@@@@@@")
                    console.log(data)
                    self.update({
                        //questions: data.custom_questions,
                        definition: data
                    })
                })
                .fail(function (error) {
                    toastr.error("Error fetching definition: " + error.statusText)
                })
        }

        self.update_submission = function () {
            CHAGRADE.api.get_submission(SUBMISSION)
                .done(function (data) {
                    console.log("!!!!!!!!!!!!!!!!!!")
                    console.log(data)
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
    </script>
</grade-homework>