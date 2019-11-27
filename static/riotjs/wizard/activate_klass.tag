<activate-klass>
    <div class="ui grid" style="margin-top: 2.5vh;">
        <div class="row">
            <div class="eight wide column">
                <h2 class="ui header">Test Your class</h2>
                <div class="ui sub header">
                    <!--Impersonate a student, try to make a submission-->
                </div>
            </div>
            <div class="ui center aligned eight wide column">
                <a href="{ opts.student_view_url }" class="ui yellow button wide-button">Test</a>
            </div>
        </div>
        <div class="row">
            <div class="eight wide column">
                <h2 class="ui header">Activate Your class</h2>
                <div class="ui sub header">

                </div>
            </div>
            <div class="ui center aligned eight wide column">
                <a class="ui {red: klass.active}{green: !klass.active} button wide-button"
                   onclick="{send_activate_klass}">{De-Activate: klass.active}{Activate: !klass.active}</a>
            </div>
        </div>
    </div>

    <script>
        var self = this
        self.errors = []
        var csrftoken = Cookies.get('csrftoken');
        self.one('mount', function () {
            //self.update_students()
            self.update_klass()
        })

        self.update_klass = function () {
            CHAGRADE.api.get_klass(KLASS)
                .done(function (data) {
                    self.update({klass: data})
                })
                .fail(function (error) {
                    toastr.error("Error fetching klass: " + error.statusText)
                })
        }

        self.send_activate_klass = function () {
            var confirmed = confirm("Are you sure you would like to activate/de-activate this class?")
            if (confirmed) {
                CHAGRADE.api.activate_klass(KLASS)
                    .done(function (data) {
                        if (data.new_state) {
                            toastr.success("Successfully activated class")
                        } else {
                            toastr.warning("Succesfully de-activated class")
                        }

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
    </script>
</activate-klass>