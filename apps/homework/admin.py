from django.contrib import admin

# Register your models here.
from apps.homework.models import Grade, Criteria, Definition, Submission, Question, CriteriaAnswer, QuestionAnswer, \
    SubmissionTracker

admin.site.register(Grade)
admin.site.register(Criteria)
admin.site.register(Definition)
admin.site.register(Submission)
admin.site.register(SubmissionTracker)
admin.site.register(Question)
admin.site.register(CriteriaAnswer)
admin.site.register(QuestionAnswer)
