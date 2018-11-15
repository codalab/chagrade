<field class="field">
    <div class="field {error: opts.error}">
        <label>{opts.name}</label>
        <input type="text" name="{ opts.input_name }" ref="input">
    </div>
    <div class="ui error message" show="{ opts.error }">
        <p>{ opts.error }</p>
    </div>
    <style>
        /* Make this component "div like" */
        /*:scope {
            display: block;
        }*/
    </style>
</field>
<teams-table>

    <div>
        <span>
            <a onclick="{goto_create_team}" class="ui blue button">Create Student Team</a>
            <a class="ui button">Upload Team CSV</a>
        </span>
        <h1>Teams</h1>
        <table class="ui sortable table">
            <thead>
            <tr>
                <th>#</th>
                <th>Name</th>
                <th>Creator</th>
                <th># Members</th>
                <th>Pending Req/Inv</th>
                <th>Status</th>
                <th></th>
                <th>Entries</th>
            </tr>
            </thead>
            <tbody>
                <tr each="{team, index in klass.teams}">
                    <td>
                        {{ forloop.counter }}
                    </td>
                    <td>
                        {{ team.name }}
                    </td>
                    <td>
                        {{ team.members.count }}
                    </td>
                    <td>
                        Not Implemented
                    </td>
                    <td>
                        Not Implemented
                    </td>
                    <td>
                        Not Implemented
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    <script>


        var self = this
        self.errors = []
        self.klass = {
            'students': []
        }
        //var csrftoken = Cookies.get('csrftoken');
        self.one('mount', function () {
            self.update_klass()
        })

        /*self.update_students = function () {
            CHAGRADE.api.get_students(KLASS)
                .done(function (data) {
                    self.update({students: data})
                })
                .fail(function (error) {
                    toastr.error("Error fetching students: " + error.statusText)
                })
        }*/

        self.update_klass = function () {
            CHAGRADE.api.get_klass(KLASS)
                .done(function (data) {
                    console.log(data)
                    self.update({klass: data})
                })
                .fail(function (error) {
                    toastr.error("Error fetching students: " + error.statusText)
                })
        }
    </script>
</teams-table>