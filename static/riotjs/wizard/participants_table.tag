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
            <a class="ui button">Send Message</a>
            <a class="ui button">Download CSV</a>
            <button class="ui green button" onclick="{ add }">
                <i class="add square icon"></i> Add new student
            </button>
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
                <th>Status</th>
                <th></th>
                <th>Entries</th>
            </tr>
            </thead>
            <tbody>
                <tr each="{student, index in students}">
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
                        { student.team }
                    </td>
                    <td>
                    </td>
                    <td>
                    </td>
                    <td>
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
                    <!--<td></td>
                    <td></td>
                    <td></td>
                    <td><field name="Display Name" ref="user_name" input_name="user_name" error="{errors.user_name}"></field></td>
                    <td><field name="Email" ref="email" input_name="email" error="{errors.email}"></field></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td>
                        <!-- <button class="ui blue icon button">+</button> -- >
                        <input type="submit" class="ui blue button" form="student_form" value="Save"/>
                    </td>-->
                </form>
            </div>
            <div class="actions">
                <input type="submit" class="ui blue button" form="student_form" value="Save"/>
                <div class="ui cancel button">Cancel</div>
            </div>
        </div>
    </div>

    <script>


        var self = this
        self.errors = []
        //var csrftoken = Cookies.get('csrftoken');
        self.one('mount', function () {
            self.update_students()
        })

        self.add = function () {
            $("#student_form_modal").modal('show')

            // We want to unselect the existing producer, so when we save we don't try to update it
            //self.selected_producer = {}
        }

        self.update_students = function () {
            CHAGRADE.api.get_students(KLASS)
                .done(function (data) {
                    self.update({students: data})
                })
                .fail(function (error) {
                    toastr.error("Error fetching students: " + error.statusText)
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

            CHAGRADE.api.create_student(data, csrftoken)
                .done(function (data) {
                    toastr.success("Successfully saved student")

                    self.update_students()

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