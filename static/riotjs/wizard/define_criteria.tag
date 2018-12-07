<define-criteria>

    <div class="ui divider"></div>

    <div>

        <h4 class="ui header">Criteria</h4>

        <div style="margin-top: 2.5vh; margin-bottom: 0.5vh;" each="{criteria, index in criterias}">
            <h4 style="margin-bottom: 2.5vh" class="ui dividing header">Crtieria {index + 1}</h4>
            <div class="three inline fields">
                <div class="six wide inline field">
                    <label for="{'id_criteria_' + index + '_description'}">Criteria:</label>
                    <input type="text" name="{'criteria_' + index + '_description'}" maxlength="200"
                           id="{'id_criteria_' + index + '_description'}">
                </div>

                <div class="five wide inline field">
                    <label for="{'id_criteria_' + index + '_low_range'}">Lowest Grade:</label>
                    <input type="text" name="{'criteria_' + index + '_low_range'}" maxlength="6"
                           id="{'id_criteria_' + index + '_low_range'}">
                </div>

                <div class="five wide inline field">
                    <label for="{'id_criteria_' + index + '_high_range'}">Highest Grade:</label>
                    <input class="" type="text" name="{'criteria_' + index + '_high_range'}" maxlength="6"
                           id="{'id_criteria_' + index + '_high_range'}">
                </div>
            </div>
        </div>

        <a class="ui blue button" onclick="{add_criteria}">Add Criteria</a>

    </div>

    <div class="ui divider"></div>


    <script>
        var self = this
        self.criterias = []

        self.remove_criteria = function (index) {
            self.criterias.splice(index, 1)
            self.update()
        }

        self.add_criteria = function () {
            self.criterias[self.criterias.length] = {}
            self.update()
        }

    </script>
</define-criteria>