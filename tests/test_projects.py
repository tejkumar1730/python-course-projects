import importlib.util
from pathlib import Path
import tempfile
import unittest
from datetime import date
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[1]
def load(folder):
    spec=importlib.util.spec_from_file_location(folder,ROOT/folder/'app.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
D=load('01_dictionary');R=load('02_railway_reservation');B=load('03_bank_management');S=load('04_supermarket_billing');T=load('06_todo_list');E=load('07_eda');W=load('08_web_scraping')
class ProjectsTest(unittest.TestCase):
    def test_dictionary_case_and_typo(self):
        self.assertEqual(D.lookup(' PYTHON ',{'python':'language'})[0],'language')
        self.assertIn('python',D.lookup('pythn',{'python':'language'})[1])
    def test_dictionary_blank(self):
        with self.assertRaises(ValueError): D.lookup(' ',{})
    def test_railway_book_cancel_capacity(self):
        with R.connect(':memory:') as db:
            day=date.today().isoformat();pnr,total=R.book(db,101,day,'Demo',60)
            self.assertEqual(total,27000);self.assertEqual(R.availability(db,101,day)[1],0)
            with self.assertRaises(ValueError): R.book(db,101,day,'Other',1)
            R.cancel(db,pnr);self.assertEqual(R.availability(db,101,day)[1],60)
            with self.assertRaises(ValueError): R.cancel(db,pnr)
    def test_railway_invalid(self):
        with R.connect(':memory:') as db:
            for train,day,name,seats in [(101,'2000-01-01','Demo',1),(999,date.today().isoformat(),'Demo',1),(101,date.today().isoformat(),' ',1),(101,date.today().isoformat(),'Demo',0)]:
                with self.assertRaises(ValueError): R.book(db,train,day,name,seats)
    def test_railway_persists(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'rail.sqlite3';db=R.connect(path)
            pnr,_=R.book(db,101,date.today().isoformat(),'Demo',2);db.close();db=R.connect(path)
            self.assertEqual(db.execute('SELECT seats FROM bookings WHERE pnr=?',(pnr,)).fetchone()[0],2);db.close()
    def test_bank_transfers_are_atomic(self):
        with B.connect(':memory:') as db:
            a=B.open_account(db,'A');b=B.open_account(db,'B');B.transact(db,a,'100.01','deposit');B.transact(db,a,'25.50','transfer',b)
            self.assertEqual(db.execute('SELECT balance FROM accounts WHERE id=?',(a,)).fetchone()[0],7451)
            with self.assertRaises(ValueError): B.transact(db,a,'5','transfer',999)
            self.assertEqual(db.execute('SELECT balance FROM accounts WHERE id=?',(a,)).fetchone()[0],7451)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM ledger').fetchone()[0],3)
            with self.assertRaises(ValueError): B.transact(db,a,'100','withdraw')
    def test_bank_invalid_amounts(self):
        for amount in ('0','-1','NaN','Infinity','1.001','abc'):
            with self.assertRaises(ValueError): B.paise(amount)
    def test_billing_arithmetic(self):
        receipt,total=S.invoice([{'name':'Item','quantity':3,'price':'10.10'}],'10','5')
        self.assertEqual(total,Decimal('28.63'));self.assertIn('TOTAL: INR 28.63',receipt)
    def test_billing_invalid(self):
        for items in ([],[{'name':'X','quantity':0,'price':'2'}],[{'name':'X','quantity':1,'price':'NaN'}]):
            with self.assertRaises(ValueError):S.invoice(items)
    def test_todo_lifecycle(self):
        with T.connect(':memory:') as db:
            task=T.add(db,'Learn Python','2030-01-01',1);T.change(db,task,'done')
            self.assertEqual(db.execute('SELECT done FROM tasks').fetchone()[0],1)
            T.change(db,task,'reopen');self.assertEqual(db.execute('SELECT done FROM tasks').fetchone()[0],0)
            T.change(db,task,'delete');self.assertEqual(db.execute('SELECT COUNT(*) FROM tasks').fetchone()[0],0)
    def test_todo_validation(self):
        with T.connect(':memory:') as db:
            with self.assertRaises(ValueError):T.add(db,' ')
            with self.assertRaises(ValueError):T.add(db,'Task','invalid')
            with self.assertRaises(ValueError):T.change(db,999,'done')
    def test_eda_known_sample(self):
        data=E.analyze(ROOT/'07_eda/sample_sales.csv')
        self.assertEqual(data['rows'],12);self.assertEqual(data['duplicate_rows'],1)
        self.assertEqual(data['columns']['quantity']['missing'],1)
        self.assertEqual(data['columns']['quantity']['median'],4)
        self.assertEqual(data['columns']['region']['missing'],1)
    def test_eda_rejects_bad_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'bad.csv';path.write_text('a,b\n1\n')
            with self.assertRaises(ValueError):E.analyze(path)
    def test_eda_escapes_html(self):
        data={'source':'<script>','rows':1,'duplicate_rows':0,'columns':{}}
        self.assertNotIn('<script>',E.report(data))
    def test_scraper_nested_and_deduplicated(self):
        data=W.parse((ROOT/'08_web_scraping/sample.html').read_text())
        self.assertEqual(data['title'],'Python Learning Library');self.assertEqual(len(data['links']),2)
        self.assertEqual(data['links'][0],{'text':'Python basics','url':'https://example.com/courses/python'})
        self.assertEqual(len(data['headings']),2)
    def test_scraper_rejects_non_http(self):
        with self.assertRaises(ValueError):W.download('file:///tmp/test')
if __name__=='__main__':unittest.main()
