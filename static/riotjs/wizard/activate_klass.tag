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
                <a class="ui yellow disabled button wide-button">Test</a>
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
        <div class="row">
            <div class="eight wide column">
                <h2 class="ui header">Download Your bundle</h2>
                <div class="ui sub header">

                </div>
            </div>
            <div class="ui center aligned eight wide column">
                <a class="ui blue disabled button wide-button">Download</a>
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
                    console.log(data)
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
                        console.log(data)
                        if (data.new_state) {
                            toastr.success("Successfully activated klass")
                        } else {
                            toastr.warning("Succesfully de-activated klass")
                        }

                        self.update_klass()
                    })
                    .fail(function (response) {
                        if (response) {
                            console.log(response)
                            //var errors = JSON.parse(response.responseText);
                            var data = JSON.parse(response.responseText);
                            var errors = data['errors']

                            self.update({errors: errors})
                        }
                    })
            }
        }
    </script>
</activate-klass>