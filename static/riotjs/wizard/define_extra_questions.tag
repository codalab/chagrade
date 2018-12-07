<define-extra-questions>

    <div class="ui divider"></div>

    <div>

        <h4 class="ui header">Custom Questions</h4>

        <div style="margin-top: 2.5vh; margin-bottom: 0.5vh;" each="{question, index in questions}">
            <h4 style="margin-bottom: 2.5vh" class="ui dividing header">Question {index + 1}</h4>
            <div class="three inline fields">
                <div class="six wide inline field">
                    <label for="{'id_question_' + index + '_text'}">Question:</label>
                    <input type="text" name="{'question_' + index + '_text'}" maxlength="200"
                           id="{'id_question_' + index + '_text'}">
                </div>

                <div class="six wide inline field">
                    <label for="{'id_question_' + index + '_answer'}">Answer:</label>
                    <input type="text" name="{'question_' + index + '_answer'}" maxlength="200"
                           id="{'id_question_' + index + '_answer'}">
                </div>

                <div class="four wide inline field">
                    <label for="{'id_question_' + index + '_has_answer'}">Has Answer:</label>
                    <input class="ui checkbox" type="checkbox" name="{'question_' + index + '_has_answer'}" maxlength="200"
                           id="{'id_question_' + index + '_has_answer'}">
                </div>
            </div>
        </div>

        <a class="ui green button" onclick="{add_question}">Add Question</a>

    </div>


    <script>
        var self = this
        self.questions = []

        self.remove_question = function (index) {
            self.questions.splice(index, 1)
            self.update()
        }

        self.add_question = function () {
            self.questions[self.questions.length] = {}
            self.update()
        }

    </script>
</define-extra-questions>