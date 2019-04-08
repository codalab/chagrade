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
        self.producer_stats = {}

        self.on("mount", function () {
            self.update({
                producer_stats: [
                    {label: "Teachers", count: 59},
                    {label: "Students", count: 1031},
                    {label: "Homework Assigned", count: 201},
                    {label: "Homework Submitted", count: 16401},
                ],
            })
        })

        /* var self = this
        self.producer_stats = {}

        self.on("mount", function () {
            self.get_general_stats()
        })

        self.get_general_stats = function () {
            self.update({
                producer_stats: [
                    {label: "Competitions", count: num_formatter(data.competition_count, 1)},
                    {label: "Datasets", count: num_formatter(data.dataset_count, 1)},
                    {label: "Participants", count: num_formatter(data.participant_count, 1)},
                    {label: "Submissions", count: num_formatter(data.submission_count, 1)},
                    {label: "Users", count: num_formatter(data.user_count, 1)},
                    {label: "Organizers", count: num_formatter(data.organizer_count, 1)},
                ],
            })
        }
*/
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
            color: #565656  !important;
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