<create-team>
    <form method="post" class="ui form" enctype="multipart/form-data">
        <div class="ui error message">{errors.message}</div>
        <div class="fields">
            <div class="six wide field">
                <label>Name:</label>
                <input name="name" ref="name" type="text" value="{team.name}">
            </div>
            <div class="six wide field">
                <label>Description:</label>
                <input name="description" ref="description" type="text" value="{team.description}">
            </div>
        </div>
        <div class="fields">
            <div class="eight wide field">
                <label>Members:</label>

                <div class="ui multiple selection dropdown" ref="members">
                    <input name="leader" type="hidden">
                    <div class="default text">Members</div>
                    <div class="menu"></div>
                </div>

<!--                <select id="members" multiple name="members" ref="members"> -->
<!--                    <option value="">-- None --</option> -->
<!--                    <option each="{student, index in klass.enrolled_students}" selected="{student.selected}" value="{student.id}" id="{'id_' + student.id}" data-user-id="{student.user.id}" data-username="{student.user.username}" data-student-id="{student.student_id}">{student.user.username}{student.team ? ' - ' + student.team.name : ''}</option> -->
<!--                </select> -->

            </div>
            <div class="eight wide field">
                <label>Leader:</label>
                <div class="ui selection dropdown" ref="leader">
                    <input name="leader" type="hidden">
                    <div class="default text">Leader</div>
                    <div class="menu"></div>
                </div>

<!--                <select id="leader" name="leader" ref="leader"> -->
<!--                    <option value="">-- None --</option> -->
<!--                    <option each="{student, index in klass.enrolled_students}" selected="{window.TEAM && _.get(window, 'TEAM.leader.id') == student.id}" value="{student.id}" id="{'id_leader_' + student.id}" data-user-id="{student.user.id}" data-username="{student.user.username}" data-student-id="{student.student_id}">{student.user.username}{student.team ? ' - ' + student.team.name : ''}</option> -->
<!--                </select> -->
            </div>
        </div>
        <span><a onclick="{submit_form}" class="ui green button">Submit</a><a onclick="{cancel_button}" class="ui red button">Cancel</a></span>
    </form>

    <script>
        var self = this
        self.klass = {}
        self.errors = {
            'message': 'Test'
        }
        self.team = {}

        self.one('mount', function () {
            $(self.refs.members).dropdown()
            $(self.refs.leader).dropdown()
            if (window.TEAM != undefined) {
               self.update_team()
            }
            self.update_klass()
        })

        self.cancel_button = function() {
            window.location='/klasses/wizard/' + KLASS + '/enroll'
        }

        self.submit_form = function () {
            const members = self.klass.enrolled_students.filter( (student) => {
                return student.on_team
            }).map( (student) => {
                return {
                    id: student.id,
                    klass: KLASS,
                    student_id: student.student_id,
                }
            })

            const student_leader = self.klass.enrolled_students.find( (student) => {
                return student.leader
            })

            var obj_data = {
                'klass': KLASS,
                'name': self.refs.name.value,
                'description': self.refs.description.value,
                'members': members,
            }
            if (student_leader) {
                obj_data.leader = {
                    id: student_leader.id,
                    klass: KLASS,
                    student_id: student_leader.student_id,
                }
            }

            if (window.TEAM != undefined) {
                var endpoint = CHAGRADE.api.update_team(TEAM, obj_data)
            }
            else {
                var endpoint = CHAGRADE.api.create_team(obj_data)
            }

            endpoint
                .done(function (data) {
                    window.location='/klasses/wizard/' + KLASS + '/enroll'
                })
                .fail(function (response) {
                    Object.keys(response.responseJSON).forEach(function (key) {
                        toastr.error("Error with " + key + "! " + response.responseJSON[key])
                    });
                })
        }

        self.get_eligible_leaders = () => {
            return self.klass.enrolled_students.filter( (student) => {
                return student.on_team
            })
                .map( (student) => {
                    return {
                        name: _.get(student, 'user.first_name') + ' ' + _.get(student, 'user.last_name'),
                        value: student.id,
                        selected: student.leader
                    }
                })
        }

        self.leader_dropdown_on_change = (value, text, $selectedItem) => {
            let leader_index = self.klass.enrolled_students.findIndex( (student) => {
                return student.id == value
            })

            for (let i = 0; i < self.klass.enrolled_students.length; i++) {
                self.klass.enrolled_students[i].leader = leader_index === i
            }
        }

        self.update_team = function () {
            CHAGRADE.api.get_team(TEAM)
                .done(function (data) {
                    self.update({team: data})
                })
                .fail(function (error) {
                    toastr.error("Error fetching team: " + error.statusText)
                })
        }

        self.update_klass = function () {
            CHAGRADE.api.get_klass(KLASS)
                .done(function (data) {
                    if (window.TEAM != undefined) {
                        data.enrolled_students.forEach(function (student) {
                            if (_.get(student, 'team.id') === _.get(self, 'team.id')) {
                                student.on_team = true
                            } else {
                                student.on_team = false
                            }
                            if (_.get(self, 'team.leader')) {
                                if (student.id === _.get(self, 'team.leader.id')) {
                                    student.leader = true
                                }
                            }
                        })
                    }
                    self.klass = data

                    self.update()
                    let members_dropdown_formatted = self.klass.enrolled_students.map( (student) => {
                        return {
                            name: _.get(student, 'user.first_name') + ' ' + _.get(student, 'user.last_name'),
                            value: student.id,
                            selected: student.on_team
                        }
                    })

                    $(self.refs.members).dropdown({
                        values: members_dropdown_formatted,
                        onChange: function(value, text, $selectedItem) {
                            const student_ids = value.split(',')
                            for (let i = 0; i < self.klass.enrolled_students.length; i++) {
                                self.klass.enrolled_students[i].on_team = student_ids.includes(String(self.klass.enrolled_students[i].id))
                            }

                            $(self.refs.leader).dropdown({
                                values: self.get_eligible_leaders(),
                                onChange: self.leader_dropdown_on_change
                            })
                        }
                    })
                    $(self.refs.leader).dropdown({
                        values: self.get_eligible_leaders(),
                        onChange: self.leader_dropdown_on_change
                    })
                })
                .fail(function (error) {
                    toastr.error("Error fetching students: " + error.statusText)
                })
        }
    </script>
</create-team>