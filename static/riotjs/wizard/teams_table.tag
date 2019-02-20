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
                <th>Challenge URL</th>
                <th></th>
                <th>Entries</th>
            </tr>
            </thead>
            <tbody>
            <div each="{team, index in teams}" style="width: 100%;" class="ui styled accordion">
                <virtual>
                    <div class="title">
                        <tr>
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
                            <td>
                                {team.challenge_url
                            </td>
                            <td class="center aligned">
                                <div onclick="{delete_team.bind(this, team.id)}" class="ui mini red button">x</div>
                            </td>
                            <td>
                                {team.submissions.length}
                            </td>
                        </tr>
                    </div>
                    <div class="content">
                        <!--<label>Challenge URL:</label>
                        <input type="text" name="team_challenge_url" ref="team_{team.id}_challenge_url"
                               value="{team.challenge_url}">-->
                        <table class="ui table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Email</th>
                                    <th>Username</th>
                                    <th>Firstname</th>
                                    <th>Lastname</th>
                                    <th>Student ID</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr each="{student in team.members}">
                                    <td>{student.id}</td>
                                    <td>{student.user.email}</td>
                                    <td>{student.user.username}</td>
                                    <td>{student.user.first_name}</td>
                                    <td>{student.user.last_name}</td>
                                    <td>{student.student_id}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </virtual>
            </div>
            </tbody>
        </table>
    </div>

    <script>


        var self = this
        self.one('mount', function () {
            self.update_teams()
            $('.ui.accordion')
                .accordion()
            ;
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