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
<participants-table>

    <div style="">
        <span>
            <a onclick="{ show_message_modal }" class="ui blue button">Send Message</a>
            <a onclick="{download_csv}" class="ui yellow button">Download CSV</a>
            <a class="ui green icon button" onclick="{ show_student_modal }">
                <i class="add square icon"></i> Add new student
            </a>
        </span>
        <h1>Participants</h1>
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
                <!--<th>Status</th>-->
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
                        { student.team.name || '' }
                    </td>
                    <!--<td>
                    </td>-->
                    <td>
                    </td>
                    <td>
                        { student.submitted_homeworks.length }
                    </td>
                </tr>
                <!--<tr style="background-color: #21ba45;">-->
                <!--<tr style="background-color: rgba(33, 186, 69, 0.25);">-->
                <!--</tr>-->
            </tbody>
        </table>
        <div id="student_form_modal" class="ui modal">
            <div class="header">Add Student</div>
            <div class="content">
                <i>Enter a username/email combo if the student is not registered yet. Their account will be created and waiting for them.</i>
                <form id="student_form" class="ui form error" onsubmit="{ add_student }">
                    <field name="Display Name" ref="user_name" input_name="user_name"
                           error="{errors.user_name}"></field>
                    <field name="Email" ref="user_email" input_name="user_email" error="{errors.user_email}"></field>
                    <field name="Student ID" ref="student_id" input_name="student_id"
                           error="{errors.student_id}"></field>
                </form>
            </div>
            <div class="actions">
                <input type="submit" class="ui blue button" form="student_form" value="Save"/>
                <div class="ui cancel button">Cancel</div>
            </div>
        </div>

        <div id="message_form_modal" class="ui modal">
            <div class="header">Send Message to all Students</div>
            <div class="content">
                <form method="post" id="message_form" class="ui form error" onsubmit="{ add_student }">
                    <!--<field name="Subject" ref="subject" input_name="subject" error="{errors.subject}"></field>
                    <field name="Message" ref="message" input_name="message" error="{errors.message}"></field>-->
                        <div class="sixteen wide field">
                            <label>Subject</label>
                            <input type="text" name="subject" ref="subject">
                        </div>
                        <div class="field">
                            <label>Message</label>
                            <!--<input type="text" name="{ opts.input_name }" ref="input">-->
                            <textarea name="message" ref="message"></textarea>
                        </div>
                </form>
            </div>
            <div class="actions">
                <div onclick="{submit_message}" class="ui blue button">Submit</div>
                <div class="ui cancel button">Cancel</div>
            </div>
        </div>
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

        self.show_student_modal = function () {
            $("#student_form_modal").modal('show')

            // We want to unselect the existing producer, so when we save we don't try to update it
            //self.selected_producer = {}
        }

        self.show_message_modal = function () {
            $("#message_form_modal").modal('show')

            // We want to unselect the existing producer, so when we save we don't try to update it
            //self.selected_producer = {}
        }

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

        self.download_csv = function () {
            window.location='/klasses/download_student_csv/' + KLASS
        }

        self.submit_message = function () {
            console.log("This was called")

            //var data = $("#student_form").serializeObject()
            var data = {
                'subject': self.refs.subject.value,
                'message': self.refs.message.value
            }

            console.log(data)

            CHAGRADE.api.message_klass_students(KLASS, data)
                .done(function (data) {
                    toastr.success("Successfully sent email!")

                    //self.update_klass()

                    $("#message_form")[0].reset();
                    $("#message_form_modal").modal('hide')
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

        self.add_student = function (save_event) {
            save_event.preventDefault()
            console.log("This was called")

            var data = $("#student_form").serializeObject()
            data['klass'] = KLASS
            //data['csrftoken'] = csrftoken

            /*console.log("@@@@@@@")
            console.log(data)
            console.log("@@@@@@@")*/

            CHAGRADE.api.create_student(data)
                .done(function (data) {
                    toastr.success("Successfully saved student")

                    self.update_klass()

                    $("#student_form")[0].reset();
                    $("#student_form_modal").modal('hide')
                })
                .fail(function (response) {
                    if (response) {
                        //var errors = JSON.parse(response.responseText);
                        var data = JSON.parse(response.responseText);
                        var errors = data['errors']
                        //console.log("@@@@@@@")
                        //console.log(errors)
                        //console.log(errors['user_name'])
                        //console.log("@@@@@@@")

                        // Clean up errors to not be arrays but plain text
                        /*Object.keys(errors).map(function (key, index) {
                            if (errors[key] !== null){
                                errors[key] = errors[key].join('; ')
                            }
                        })*/

                        self.update({errors: errors})
                    }
                })
        }
    </script>
</participants-table>