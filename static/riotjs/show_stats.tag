<show-stats>
    <div class="content">
        <h4 class="ui sub blue header">Chagrade brings together</h4>
        <div class="ui two column grid">
            <div class="column" each="{ stat in producer_stats }" no-reorder>
                <div class="ui six tiny statistics">
                    <div class="statistic">
                        <div class="value">
                            { stat.count }
                        </div>
                        <div class="label">
                            { stat.label }
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>


    <script>
        var self = this
        self.producer_stats = []

        self.on("mount", function () {
            self.get_chagrade_stats()
            self.update(self.producer_stats)
        });

        self.get_chagrade_stats = function () {
            CHAGRADE.api.students_list()
                .done(function (data) {
                    self.producer_stats.push({
                        label: "Students", count: data.length
                    });
                    self.update()
                }).fail(function () {
                console.log('Students not found.')
            });
            CHAGRADE.api.teams_list()
                .done(function (data) {
                    self.producer_stats.push({
                        label: "Teams", count: data.length
                    });
                    self.update()
                }).fail(function () {
                console.log('Teams not found.')
            });
            CHAGRADE.api.submissions_list()
                .done(function (data) {
                    self.producer_stats.push({
                        label: "Submissions", count: data.length
                    });
                    self.update()
                }).fail(function () {
                console.log('Submissons not found')
            });
            CHAGRADE.api.klasses_list()
                .done(function (data) {
                    self.producer_stats.push({
                        label: "Classes", count: data.length
                    });
                    self.update()
                }).fail(function () {
                console.log('Classes not found')
            });
            CHAGRADE.api.questions_list()
                .done(function (data) {
                    self.producer_stats.push({
                        label: "Questions", count: data.length
                    });
                    self.update()
                }).fail(function () {
                console.log('Questions not found')
            });

        }

    </script>

    <style>
        :scope {
            display: block;
            font-size: 0.95em;
        }

        .ui.two.column.grid {
            margin: 10px;
        }

        .sub.blue.header {
            margin-bottom: -1em;
        }

        .ui.statistics > .statistic {
            flex: 1 1 auto;
            font-size: 0.6em;
        }

        .ui.tiny.statistic > .value,
        .ui.tiny.statistics .statistic > .value {
            color: #565656 !important;
            font-weight: 700;
        }

        .ui.statistic > .label,
        .ui.statistics .statistic > .label {
            color: #565656 !important;
            font-size: 13px !important;
            line-height: 1.1em !important;
            font-weight: 100 !important;
        }
    </style>
</show-stats>