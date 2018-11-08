<question-table>

    <div style="margin-bottom: 2.5vh;">
        <h1>Existing Questions</h1>
        <table class="ui sortable table">
            <thead>
            <tr>
                <th>#</th>
                <th>Question</th>
                <th>Has Answer?</th>
                <th>Answer</th>
                <th>Delete</th>
            </tr>
            </thead>
            <tbody>
                <tr each="{question, index in questions}">
                    <td>
                        {index + 1}
                    </td>
                    <td>
                        { question.question }
                    </td>
                    <td>
                        { question.has_specific_answer }
                    </td>
                    <td>
                        { question.answer }
                    </td>
                    <td>
                        <a class="ui tiny red button" onclick="{delete_question.bind(this, question.id)}">x</a>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    <script>


        var self = this
        self.errors = []

        self.one('mount', function () {
            self.update_questions()
        })


        self.update_questions = function () {
            CHAGRADE.api.get_definition(DEFINITION)
                .done(function (data) {
                    self.update({questions: data.custom_questions})
                })
                .fail(function (error) {
                    toastr.error("Error fetching students: " + error.statusText)
                })
        }

        self.delete_question = function (pk) {
            var result = confirm('Are you sure you wish to delete this Question?')
            if (result) {
                CHAGRADE.api.delete_question(pk)
                .done(function (data) {
                    toastr.success("Successfully deleted question")
                    self.update_questions()
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
    </script>
</question-table>