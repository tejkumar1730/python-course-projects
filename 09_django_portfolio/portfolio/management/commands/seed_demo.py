from django.core.management.base import BaseCommand
from portfolio.models import Project
class Command(BaseCommand):
    help='Add example project cards without overwriting existing entries.'
    def handle(self,*args,**kwargs):
        rows=[('Dictionary','Offline lookup, spelling suggestions and custom words.','Python · JSON','01_dictionary'),('Railway reservation','Date-specific seats, reservations and cancellation.','Python · SQLite','02_railway_reservation'),('Bank management','A transactional demo ledger with deposits and transfers.','Python · SQLite','03_bank_management'),('Supermarket billing','Itemized receipts with precise decimal arithmetic.','Python · Decimal','04_supermarket_billing'),('Audio ebook reader','Listen to text with voice and speed controls.','Python · Web Speech','05_audio_ebook_reader'),('To-do list','Persistent tasks with priorities and due dates.','Python · SQLite','06_todo_list'),('Exploratory data analysis','CSV summaries, missingness and duplicate detection.','Python · Statistics','07_eda'),('Web scraping','Extract titles, headings and links from HTML.','Python · HTMLParser','08_web_scraping'),('Django portfolio','Project cards and a local contact inbox.','Django · SQLite','09_django_portfolio'),('Student management','Staff-only student records with search and validation.','Django · SQLite','10_django_student_management')]
        for title,description,technology,folder in rows:
            Project.objects.get_or_create(title=title,defaults={'description':description,'technology':technology,'url':'https://github.com/tejkumar1730/python-course-projects/tree/main/'+folder})
        self.stdout.write(self.style.SUCCESS('Demo projects ready.'))
