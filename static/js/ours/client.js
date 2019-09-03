var csrftoken = Cookies.get('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

var CHAGRADE = {
    URLS: []  // Set in base.html
}

CHAGRADE.api = {
    request: function (method, url, data) {
        return $.ajax({
            type: method,
            url: url,
            data: JSON.stringify(data),
            //headers:{"X-CSRFToken": csrf_token},
            contentType: "application/json",
            dataType: 'json'
        })
    },
    get_klass: function(pk) {
        return CHAGRADE.api.request('GET', URLS.API + 'klasses/' + pk)
    },
    get_klasses: function(data) {
        return CHAGRADE.api.request('GET', URLS.API + 'klasses/', data)
    },
    get_my_klasses: function(instructor) {
        return CHAGRADE.api.request('GET', URLS.API + 'klasses/?instructor=' + instructor)
    },
    activate_klass: function(pk) {
        return CHAGRADE.api.request('POST', '/klasses/wizard/' + pk + '/activate')
    },
    message_klass_students: function(pk, data) {
        return CHAGRADE.api.request('POST', '/klasses/email_students/' + pk + '/', data)
    },
    //Students
    create_student: function(data) {
        return CHAGRADE.api.request('POST', URLS.API + "students/", data)
    },
    create_single_student: function(data) {
        //return CHAGRADE.api.request('POST', URLS.API + "create_student/", data)
        return CHAGRADE.api.request('POST', URLS.API + "test_students/", data)
    },
    get_cha_user: function(pk) {
        return CHAGRADE.api.request('GET', URLS.API + "users/" + pk)
    },
    get_student: function(pk) {
        return CHAGRADE.api.request('GET', URLS.API + "students/" + pk)
    },
    update_student: function(pk, data) {
        return CHAGRADE.api.request('PUT', URLS.API + 'students/' + pk + "/", data)
    },
    delete_student: function(pk) {
        return CHAGRADE.api.request('DELETE', URLS.API + 'students/' + pk + "/")
    },
    // Definitions
    get_definition: function(pk) {
        return CHAGRADE.api.request('GET', URLS.API + "definitions/" + pk)
    },
    create_definition: function(data) {
        return CHAGRADE.api.request('POST', URLS.API + 'definitions/', data)
    },
    update_definition: function(pk, data) {
        return CHAGRADE.api.request('PUT', URLS.API + 'definitions/' + pk + "/", data)
    },
    // Questions
    delete_question: function(pk) {
        return CHAGRADE.api.request('DELETE', URLS.API + "questions/" + pk + "/")
    },
    // Criteria
    delete_criteria: function(pk) {
        return CHAGRADE.api.request('DELETE', URLS.API + "criterias/" + pk + "/")
    },
    // Submissions
    create_submission: function(data) {
        return CHAGRADE.api.request('POST', URLS.API + "submissions/", data)
    },
    get_submission: function(pk) {
        return CHAGRADE.api.request('GET', URLS.API + "submissions/" + pk)
    },
    // Grades
    create_grade: function(data) {
        return CHAGRADE.api.request('POST', URLS.API + "grades/", data)
    },
    get_grade: function(pk) {
        return CHAGRADE.api.request('GET', URLS.API + "grades/" + pk)
    },
    update_grade: function(pk, data) {
        return CHAGRADE.api.request('PUT', URLS.API + 'grades/' + pk + "/", data)
    },
    // Teams
    get_teams: function(klass) {
        return CHAGRADE.api.request('GET', URLS.API + 'teams/?klass=' + klass)
    },
    get_team: function(pk) {
        return CHAGRADE.api.request('GET', URLS.API + 'teams/' + pk)
    },
    create_team: function(data) {
        return CHAGRADE.api.request('POST', URLS.API + 'teams/', data)
    },
    update_team: function(pk, data) {
        return CHAGRADE.api.request('PUT', URLS.API + 'teams/' + pk + "/", data)
    },
    delete_team: function(pk) {
        return CHAGRADE.api.request('DELETE', URLS.API + "teams/" + pk + "/")
    },
    // Metrics
    get_overall_metrics: function() {
        return CHAGRADE.api.request('GET', URLS.API + "chagrade_overall_metrics/")
    },
    get_student_metrics: function() {
        return CHAGRADE.api.request('GET', URLS.API + "chagrade_student_metrics/")
    },
    get_instructor_metrics: function() {
        return CHAGRADE.api.request('GET', URLS.API + "chagrade_instructor_metrics/")
    },
    get_klass_metrics: function() {
        return CHAGRADE.api.request('GET', URLS.API + "chagrade_klass_metrics/")
    },
    get_submission_metrics: function() {
        return CHAGRADE.api.request('GET', URLS.API + "chagrade_submission_metrics/")
    },
    get_student_scores_metrics: function(student_pk) {
        return CHAGRADE.api.request('GET', URLS.API + "student_scores/" + student_pk)
    },
    get_student_submission_times_metrics: function(student_pk) {
        return CHAGRADE.api.request('GET', URLS.API + "student_submission_times/" + student_pk)
    },
    get_team_scores_metrics: function(team_pk) {
        return CHAGRADE.api.request('GET', URLS.API + "team_scores/" + team_pk)
    },
    get_team_submission_times_metrics: function(team_pk) {
        return CHAGRADE.api.request('GET', URLS.API + "team_submission_times/" + team_pk)
    },
    get_klass_scores_metrics: function(klass_pk) {
        return CHAGRADE.api.request('GET', URLS.API + "klass_scores/" + klass_pk)
    },
    get_klass_submission_times_metrics: function(klass_pk) {
        return CHAGRADE.api.request('GET', URLS.API + "klass_submission_times/" + klass_pk)
    },
    get_team_contributions_metrics: function(team_pk) {
        return CHAGRADE.api.request('GET', URLS.API + "team_contributions/" + team_pk)
    },
}
