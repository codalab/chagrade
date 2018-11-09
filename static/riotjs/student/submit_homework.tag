<submit-homework>

    <div class="ui form" style="margin-bottom: 2.5vh;">
        <h1 class="ui dividing header">Submission Form</h1>
        <div class="fields">
            <div class="sixteen wide field">
                <label>Submission Github URL:</label>
                <input name="submission_github_url" ref="submission_github_url" type="text">
            </div>
        </div>
        <div class="fields">
            <div show="{definition.ask_method_name}" class="four wide field">
                <label>Method Name:</label>
                <input required name="method_name" ref="method_name" type="text">
            </div>
            <div show="{definition.ask_method_description}" class="four wide field">
                <label>Method Description:</label>
                <input required name="method_description" ref="method_description" type="text">
            </div>
            <div show="{definition.ask_project_url}" class="four wide field">
                <label>Project URL:</label>
                <input required name="project_url" ref="project_url" type="text">
            </div>
            <div show="{definition.ask_publication_url}" class="four wide field">
                <label>Publication URL:</label>
                <input name="publication_url" ref="publication_url" type="text">
            </div>
        </div>
        <h2 class="ui dividing header">Extra Questions:</h2>
        <div each="{question, index in definition.custom_questions}" class="fields">
            <div class="sixteen wide field">
                <label>{question.question}:</label>
                <input name="{'question_answer_' + index}" ref="{'question_answer_' + index}" type="text">
            </div>
        </div>
    </div>

    <span><a onclick="{submit_form}" class="ui green button">Submit</a><a class="ui red button">Cancel</a></span>

    <script>


        var self = this
        self.errors = []
        self.question_answers = []
        self.definition = {
            'ask_publication_url': false,
            'ask_project_url': false,
            'ask_method_name': false,
            'ask_method_description': false,
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
            self.update_definition()
        })


        self.submit_form = function() {

            var data = {
                "klass": KLASS,
                "definition": DEFINITION,
                "creator": STUDENT,
                "submission_github_url": self.refs.submission_github_url.value,
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
            // TODO: Make this ID based or something
            for (var index = 0; index < self.definition.custom_questions.length; index++) {
                data['question_answers'].push({'question': self.definition.custom_questions[index].id, 'text': self.refs['question_answer_' + index].value})
                //Do something

            }

            console.log(data)

            CHAGRADE.api.create_submission(data)
                .done(function (data) {
                    console.log(data)
                    window.location='/homework/overview/' + KLASS
                })
                .fail(function (error) {
                    toastr.error("Error creating submission: " + error.statusText)
                })
        }


        self.update_definition = function () {
            CHAGRADE.api.get_definition(DEFINITION)
                .done(function (data) {
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
    </script>
</submit-homework>