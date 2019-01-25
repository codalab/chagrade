<criteria-table>

    <div style="margin-bottom: 2.5vh;">
        <h1>Existing Criteria</h1>
        <table class="ui sortable table">
            <thead>
            <tr>
                <th>#</th>
                <th>Description</th>
                <th>Low Range</th>
                <th>High Range</th>
                <th>Delete</th>
            </tr>
            </thead>
            <tbody>
            <tr each="{criteria, index in criterias}">
                <td>
                    {index + 1}
                </td>
                <td>
                    { criteria.description }
                </td>
                <td>
                    { criteria.lower_range }
                </td>
                <td>
                    { criteria.upper_range }
                </td>
                <td>
                    <a class="ui tiny red button" onclick="{delete_criteria.bind(this, criteria.id)}">x</a>
                </td>
            </tr>
            </tbody>
        </table>
    </div>

    <script>


        var self = this
        self.errors = []

        self.one('mount', function () {
            self.update_criterias()
        })


        self.update_criterias = function () {
            CHAGRADE.api.get_definition(DEFINITION)
                .done(function (data) {
                    self.update({criterias: data.criterias})
                })
                .fail(function (error) {
                    toastr.error("Error fetching students: " + error.statusText)
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
    </script>
</criteria-table>