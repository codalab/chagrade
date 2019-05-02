<show-stats>
    <div class="content">
        <h4 class="ui sub blue header">Chagrade brings together</h4>
        <div class="ui two column grid">
            <div class="column" no-reorder>
                <div class="ui two tiny statistics">
                    <div class="statistic">
                        <div class="value">
                            { stats.students }
                        </div>
                        <div class="label">
                            Students
                        </div>
                    </div>
                    <div class="statistic">
                        <div class="value">
                            { stats.users }
                        </div>
                        <div class="label">
                            Users
                        </div>
                    </div>
                </div>
            </div>
            <div class="column" no-reorder>
                <div class="ui two tiny statistics">
                    <div class="statistic">
                        <div class="value">
                            { stats.submissions }
                        </div>
                        <div class="label">
                            Submissions
                        </div>
                    </div>
                    <div class="statistic">
                        <div class="value">
                            { stats.klasses }
                        </div>
                        <div class="label">
                            Classes
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>


    <script>
        var self = this
        self.stats = {
            students: 0,
            users: 0,
            submissions: 0,
            klasses: 0,
        }

        self.on("mount", function () {
            self.get_chagrade_stats()
        });

        self.get_chagrade_stats = function () {
            CHAGRADE.api.get_general_stats()
                .done(function (data) {
                    self.stats = data
                    self.update()
                }).fail(function () {
                console.log('Students not found.')
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

        .ui.two.statistics .statistic {
            margin: 0 0 3em !important;
        }
    </style>
</show-stats>
