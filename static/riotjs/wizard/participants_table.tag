<field class="field">
    <div class="field {error: opts.error}">
        <label>{opts.name}</label>
        <input type="text" name="{ opts.input_name }" ref="input">
    </div>
    <div class="ui error message" show="{ opts.error }">
        <p>{ opts.error }</p>
    </div>
    <script>
        var self = this

        self.get_value = function() {
            return self.refs.input.value
        }
    </script>
</field>
<participants-table>
    <div>
        <span>
            <a onclick="{goto_create_team}" class="ui blue button">Create Student Team</a>
        </span>
        <h1>Teams</h1>
        <table class="ui sortable table">
            <thead>
            <tr>
                <th>#</th>
                <th>ID</th>
                <th>Name</th>
                <th>Leader Student ID</th>
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
                        { _.get(team, 'leader.student_id', '') }
                    </td>
                    <td>
                        { _.get(team, 'members.length', '') }
                    </td>
                    <td class="center aligned">
                        <div onclick="{delete_team.bind(this, team.id)}" class="ui mini red button">x</div>
                        <div onclick="{edit_team.bind(this, team.id)}" class="ui mini yellow icon button"><i class="wrench icon"></i></div>
                    </td>
                    <td>
                        { _.get(team, 'submissions.length', '') }
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    <div class="ui divider" style=""></div>

    <div style="">
        <span>
            <a onclick="{download_csv}" class="ui yellow button">Download CSV</a>
            <a class="ui blue button" data-tooltip="Format: First Name,Last Name,Display Name,Student ID,Email,Team,TeamLeader(Optional bool)"
               onclick="document.getElementById('hidden_file_input').click()">Upload CSV</a>
            <a href="/api/v1/enroll_students_sample_csv/?format=csv" class="ui blue button" download="sample_student_enroll.csv">Sample Students CSV Download</a>
            <input id="hidden_file_input" hidden type="file" onchange="{do_csv_upload}"/>
            <a class="ui green icon button" onclick="{ show_student_modal }">
                <i class="add square icon"></i> Add new student
            </a>
        </span>
        <h1>Students</h1>
        <table class="ui sortable table">
            <thead>
            <tr>
                <th>#</th>
                <th>First Name</th>
                <th>Last Name</th>
                <th>Display Name</th>
                <th>Student ID</th>
                <th>Email</th>
                <th>Team</th>
                <th></th>
                <th>Entries</th>
            </tr>
            </thead>
            <tbody>
                <tr each="{student, index in klass.enrolled_students}">
                    <td>
                        {index + 1}
                    </td>
                    <td>
                        { student.user.first_name }
                    </td>
                    <td>
                        { student.user.last_name }
                    </td>
                    <td>
                        { student.user.username }
                    </td>
                    <td>
                        { student.student_id }
                    </td>
                    <td>
                        { student.user.email }
                    </td>
                    <td>
                        { _.get(student, 'team.name', '') }
                    </td>
                    <td>
                        <div onclick="{delete_student.bind(this, student.id)}" class="ui mini red button">x</div>
                    </td>
                    <td>
                        { student.submitted_homeworks.length }
                    </td>
                </tr>
            </tbody>
        </table>
        <div id="student_form_modal" class="ui modal">
            <div class="header">Add Student</div>
            <div class="content">
                <i>Enter a username/email combo if the student is not registered yet. Their account will be created and waiting for them.</i>
                <form id="student_form" class="ui form error">
                    <field name="First Name (Optional)" ref="first_name"></field>
                    <field name="Last Name (Optional)" ref="last_name"></field>
                    <field name="User Name (Optional)" ref="username"></field>
                    <field name="Student ID (Optional)" ref="student_id"></field>
                    <field name="Email" ref="email"></field>
                    <field name="Team Name (Optional)" ref="team_name"></field>
                </form>
            </div>
                <a class="ui blue button" onclick="{add_student}">Add Student</a>
                <div class="ui cancel button">Cancel</div>
        </div>

        <!--<div id="message_form_modal" class="ui modal">
            <div class="header">Send Message to all Students</div>
            <div class="content">
                <form method="post" id="message_form" class="ui form error" onsubmit="{ add_student }">
                    <!--<field name="Subject" ref="subject" input_name="subject" error="{errors.subject}"></field>
                    <field name="Message" ref="message" input_name="message" error="{errors.message}"></field>
                        <div class="sixteen wide field">
                            <label>Subject</label>
                            <input type="text" name="subject" ref="subject">
                        </div>
                        <div class="field">
                            <label>Message</label>
                            <!--<input type="text" name="{ opts.input_name }" ref="input">
                            <textarea name="message" ref="message"></textarea>
                        </div>
                </form>
            </div>
            <div class="actions">
                <div onclick="{submit_message}" class="ui blue button">Submit</div>
                <div class="ui cancel button">Cancel</div>
            </div>
        </div>-->
    </div>

    <script>
        // TODO: RE-WRITE THIS SO THAT WE GET/QUERY FOR A STUDENT OR SOMETHING? WE NEED A CUSTOM API VIEW HERE

        var self = this
        self.errors = []
        self.klass = {
            'students': [],
            'password_reset_requests': []
        }


        //var csrftoken = Cookies.get('csrftoken');
        self.one('mount', function () {
            self.update_klass()
            self.update_teams()
        })

        self.goto_create_team = function () {
            window.location = '/groups/create/' + KLASS + '/'
        }

        self.edit_team = function(pk) {
            window.location='/groups/edit/' + KLASS + '/' + pk + '/'
        }

        self.delete_team = function(pk) {
            var result = confirm("Are you sure you wish to delete this team?")
            if (!result) {
                return
            } else {
                CHAGRADE.api.delete_team(pk)
                .done(function (data) {
                    toastr.success("Successfully deleted team")
                    self.update_teams()
                    self.update_klass()
                })
                .fail(function (response) {
                    console.log(response)
                    Object.keys(response.responseJSON).forEach(function (key) {
                        toastr.error("Error with " + key + "! " + response.responseJSON[key])
                    });
                })
            }

        }

        self.delete_student = function(pk) {
            var result = confirm("Are you sure you wish to remove this student?")
            if (!result) {
                return
            } else {
                CHAGRADE.api.delete_student(pk)
                .done(function (data) {
                    toastr.success("Successfully removed student")
                    self.update_teams()
                    self.update_klass()
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

        self.do_csv_upload = function () {
            var files = $('#hidden_file_input').prop("files")
            var form_data = new FormData();
            form_data.append('file', files[0], 'students.csv');
            form_data.append('klass', KLASS);

            // Make AJAX request
            $.ajax({
                type: 'post',
                url: "/api/v1/create_students_from_csv/",
                data: form_data,
                processData: false,
                contentType: false,
            })
                .done(function (data) {
                    toastr.success("Successfully submitted")
                    self.update_klass()
                    self.update_teams()
                })
                .fail(function (response) {
                    console.log(response)
                    Object.keys(response.responseJSON).forEach(function (key) {
                        toastr.error("Error with " + key + "! " + response.responseJSON[key])
                    });
                })
        }


        self.show_student_modal = function () {
            $("#student_form_modal").modal('show')
        }

        self.show_message_modal = function () {
            $("#message_form_modal").modal('show')
        }

        self.update_klass = function () {
            CHAGRADE.api.get_klass(KLASS)
                .done(function (data) {
                    self.update({klass: data})
                })
                .fail(function (error) {
                    toastr.error("Error fetching students: " + error.statusText)
                })
        }

        self.download_csv = function () {
            window.location='/klasses/download_student_csv/' + KLASS
        }

        self.submit_message = function () {
            var data = {
                'subject': self.refs.subject.value,
                'message': self.refs.message.value
            }

            CHAGRADE.api.message_klass_students(KLASS, data)
                .done(function (data) {
                    toastr.success("Successfully sent email!")

                    //self.update_klass()

                    $("#message_form")[0].reset();
                    $("#message_form_modal").modal('hide')
                })
                .fail(function (response) {
                    console.log(response)
                    Object.keys(response.responseJSON).forEach(function (key) {
                        toastr.error("Error with " + key + "! " + response.responseJSON[key])
                    });
                })
        }

        self.add_student = function () {
            var data = {
                "user": {
                    "username": self.refs.username.get_value() || "",
                    "first_name": self.refs.first_name.get_value() || "",
                    "last_name": self.refs.last_name.get_value() || "",
                    "email": self.refs.email.get_value() || ""
                },
                "klass": KLASS,
                "student_id": self.refs.student_id.get_value() || "",
            }

            if (self.refs.team_name.get_value() === null) {
                alert("Team cannot be null")
                return
            } else {
                data['team'] = {
                    "name": self.refs.team_name.get_value() || "",
                    "klass": KLASS
                }
            }

            CHAGRADE.api.create_single_student(data)
                .done(function (data) {
                    toastr.success("Successfully saved student")

                    self.update_klass()
                    self.update_teams()

                    $("#student_form")[0].reset();
                    $("#student_form_modal").modal('hide')
                })
                .fail(function (response) {
                    console.log(response)
                    Object.keys(response.responseJSON).forEach(function (key) {
                        toastr.error("Error with " + key + "! " + response.responseJSON[key])
                    });
                })
        }
    </script>
</participants-table>