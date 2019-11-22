<klass-overview>
    <div class="ui centered grid">
        <div class="row">
            <div class="twelve wide column">
                <div class="ui centered grid message">
                    <div class="row">
                        <div class="ui center aligned container" style="margin-bottom: 5px;">
                            <h1 class="ui massive header" style="font-size: 56px;">Your Classes</h1>
                            <h2 class="sub header">
                                Here you can create <b>and grade classes attached to challenges</b>
                            </h2>
                        </div>
                    </div>
                    <div class="row">
                        <div class="center aligned six wide column">
                            <!--<a class="ui large green button" href="klasses/create_klass" role="button">Create a Class</a>-->
                        </div>
                        <div class="center aligned six wide column">
                            <a class="ui large grey disabled button" href="" role="button">Create a Class from
                                Template</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="ui row">
            <div class="sixteen wide center aligned column">
                <table class="ui center aligned sortable celled table">
                    <thead style="background-color: #2185d0; color: white;">
                    <tr class="black">
                        <th>Image:</th>
                        <th>Title:</th>
                        <th>Course #:</th>
                        <th>Organizer:</th>
                        <th>Created:</th>
                        <th>Modified:</th>
                        <th>Edit:</th>
                        <th>Active:</th>
                        <th>Grades:</th>
                        <th>Submissions</th>
                        <th>Delete:</th>
                    </tr>
                    </thead>
                    <tbody>
                    <tr each="{klass in klasses}">
                        <td>
                            <img class="ui tiny image" show="{klass.image}" src="{ klass.image }" width="50">
                        </td>
                        <td>{ klass.title }</td>
                        <td>{ klass.course_number }</td>
                        <td>{ klass.instructor }</td>
                        <td>{ klass.created }</td>
                        <td>{ klass.modified }</td>
                        <td>
                            <!--<a href="klasses/wizard/{klass.pk}" class="ui blue mini button">View</a>-->
                        </td>
                        <td>{ klass.active }</td>
                        <td>
                            <!--<a href="homework/download_grades_csv/{klass.pk}" class="ui mini green button">Download</a>-->
                        </td>
                        <td><a href="" class="ui grey mini disabled button">Download</a></td>
                        <td><a href="" class="ui grey mini disabled button">X</a></td>
                    </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <script>
        var self = this
        self.klasses = []
        self.one('mount', function () {
            self.update_klasses()
        })

        /*self.goto_create_team = function() {
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

         }*/

        self.update_klasses = function () {
            CHAGRADE.api.get_my_klasses(INSTRUCTOR)
                .done(function (data) {
                    self.update({klasses: data})
                })
                .fail(function (error) {
                    toastr.error("Error fetching klasses: " + error.statusText)
                })
        }
    </script>
</klass-overview>