<teams-table>

    <div>
        <span>
            <!--<a href="" class="ui blue button">Create Student Team</a>-->
            <a onclick="{goto_create_team}" class="ui blue button">Create Student Team</a>
            <a class="ui button">Upload Team CSV</a>
        </span>
        <h1>Teams</h1>
        <table class="ui sortable table">
            <thead>
            <tr>
                <th>#</th>
                <th>ID</th>
                <th>Name</th>
                <th># Members</th>
                <th></th>
                <th>Entries</th>
            </tr>
            </thead>
            <tbody>
                <tr each="{team, index in teams}">
                    <td>
                        {index + 1}
                    </td>
                    <td>
                        {team.id}
                    </td>
                    <td>
                        {team.name}
                    </td>
                    <td>
                        {team.members.length}
                    </td>
                    <td class="center aligned">
                        <div onclick="{delete_team.bind(this, team.id)}" class="ui mini red button">x</div>
                    </td>
                    <td>
                        {team.submissions.length}
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    <script>


        var self = this
        self.one('mount', function () {
            self.update_teams()
        })

        self.goto_create_team = function() {
                window.location='/groups/create/' + KLASS + '/'
        }

        self.delete_team = function(pk) {
            var result = confirm("Are you sure you wish to delete this team?")
            if (!result) {
                return
            } else {
                CHAGRADE.api.delete_team(pk)
                .done(function (data) {
                    toastr.success("Successfully team")
                    self.update_teams()
                })
                .fail(function (response) {
                    console.log(response)
                    Object.keys(response.responseJSON).forEach(function (key) {
                        toastr.error("Error with " + key + "! " + response.responseJSON[key])
                    });
                })
            }

        }

        self.update_teams = function() {
            CHAGRADE.api.get_teams(KLASS)
                .done(function (data) {
                    self.update({teams: data})
                })
                .fail(function (error) {
                    toastr.error("Error fetching teams: " + error.statusText)
                })
        }
    </script>
</teams-table>