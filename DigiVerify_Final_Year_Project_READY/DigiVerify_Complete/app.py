import os, re, sqlite3, uuid, hashlib, io
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import pytesseract
from pytesseract import Output

if os.environ.get('TESSERACT_CMD'):
    pytesseract.pytesseract.tesseract_cmd = os.environ['TESSERACT_CMD']

BASE = Path(__file__).resolve().parent
UPLOAD_DIR = BASE / 'uploads'
UPLOAD_DIR.mkdir(exist_ok=True)
DB_PATH = BASE / 'digiverify.db'
ALLOWED = {'png', 'jpg', 'jpeg', 'webp'}
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'replace-this-secret-before-deployment')
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024
DOC_TYPES = ['Aadhaar', 'PAN', 'Passport', 'Voter ID', 'Driving Licence', 'Other']
PATTERNS = {
 'Aadhaar': re.compile(r'(?<!\d)(?:\d{4}[ -]?\d{4}[ -]?\d{4})(?!\d)'),
 'PAN': re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', re.I),
 'Passport': re.compile(r'\b[A-Z][0-9]{7}\b', re.I),
 'Voter ID': re.compile(r'\b[A-Z]{3}[0-9]{7}\b', re.I),
 'Driving Licence': re.compile(r'\b[A-Z]{2}[- ]?\d{2}[- ]?\d{4}[- ]?\d{7,8}\b', re.I),
}
SUSPICIOUS = ('FAKE', 'SAMPLE', 'SPECIMEN', 'DEMO ONLY', 'FOR DEMONSTRATION', 'NOT VALID', 'NOT GENUINE', 'COUNTERFEIT', 'DUPLICATE', 'FOR TESTING')

def db():
    con = sqlite3.connect(DB_PATH); con.row_factory = sqlite3.Row; return con

def init_db():
    with db() as con:
        # Puraani database table ko reset taaki purana glitch clean ho jaye
        con.execute("DROP TABLE IF EXISTS documents")
        con.execute('''CREATE TABLE documents(
          id INTEGER PRIMARY KEY AUTOINCREMENT, ref TEXT UNIQUE, document_type TEXT,
          original_name TEXT, stored_name TEXT, ocr_text TEXT, status TEXT DEFAULT 'Rejected',
          risk_score INTEGER DEFAULT 100, warnings TEXT, created_at TEXT, reviewed_at TEXT,
          reviewer_note TEXT, document_number TEXT, extracted_name TEXT, dob TEXT,
          image_hash TEXT, ocr_confidence REAL DEFAULT 0)''')

def preprocess(path):
    im = Image.open(path).convert('RGB')
    im = ImageOps.exif_transpose(im)
    if im.width < 1600:
        scale = min(2.0, 1600 / max(im.width, 1)); im = im.resize((int(im.width*scale), int(im.height*scale)))
    gray = ImageOps.grayscale(im)
    gray = ImageOps.autocontrast(gray)
    gray = ImageEnhance.Contrast(gray).enhance(1.6)
    return gray.filter(ImageFilter.SHARPEN)

def get_ocr(path):
    try:
        processed = preprocess(path)
        data = pytesseract.image_to_data(processed, config='--oem 3 --psm 6', output_type=Output.DICT)
        words, confs = [], []
        for word, conf in zip(data.get('text', []), data.get('conf', [])):
            word = word.strip()
            try: c = float(conf)
            except (TypeError, ValueError): c = -1
            if word:
                words.append(word)
                if c >= 0: confs.append(c)
        text = ' '.join(words)
        confidence = round(sum(confs)/len(confs), 1) if confs else 0
        if len(text.strip()) < 12:
            text = pytesseract.image_to_string(processed, config='--oem 3 --psm 11')
        return text, confidence
    except Exception:
        return '', 0

def extract_fields(doc_type, text):
    number = ''
    pat = PATTERNS.get(doc_type)
    if pat:
        match = pat.search(text.upper())
        if match: number = re.sub(r'\s+', '', match.group(0)).upper()
    dob_match = re.search(r'\b(?:DOB|DATE OF BIRTH|BIRTH)\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text, re.I)
    dob = dob_match.group(1) if dob_match else ''
    name = ''
    for line in text.splitlines():
        m = re.search(r"\b(?:NAME|नाम)\s*[:\-]?\s*([A-Z][A-Z .'-]{2,45})", line, re.I)
        if m:
            name = re.sub(r'\s+', ' ', m.group(1)).strip(' .-'); break
    return number, name, dob

def analyse(doc_type, text, image_path, image_hash, confidence):
    warnings, score = [], 0
    upper = text.upper()
    
    if not text.strip(): warnings.append('No readable OCR text detected'); score += 45
    if any(flag in upper for flag in SUSPICIOUS): warnings.append('Explicit sample/fake marker detected'); score += 80
    
    pattern_detected = False
    if doc_type in PATTERNS and PATTERNS[doc_type].search(upper):
        pattern_detected = True
    else:
        warnings.append('Document number pattern not detected'); score += 35
        
    number, name, dob = extract_fields(doc_type, text)
    
    # ⚡ AUTOMATION REJECTION FILTER
    if not number or not pattern_detected or any(flag in upper for flag in SUSPICIOUS) or score >= 35:
        status = 'Rejected'
        score = max(score, 95)
    else:
        status = 'Approved'
        score = 5
        
    return score, warnings, status, number, name, dob

@app.context_processor
def inject_globals(): return {'year': datetime.now().year}

@app.route('/')
def dashboard():
    with db() as con:
        total = con.execute('SELECT COUNT(*) n FROM documents').fetchone()['n']
        counts = {
            'Approved': con.execute("SELECT COUNT(*) n FROM documents WHERE status='Approved'").fetchone()['n'],
            'Rejected': con.execute("SELECT COUNT(*) n FROM documents WHERE status='Rejected'").fetchone()['n'],
            'Manual Review': 0 # Dashboard pe Manual system permanently zero locked!
        }
        recent = con.execute('SELECT * FROM documents ORDER BY id DESC LIMIT 6').fetchall()
    return render_template('dashboard.html', total=total, counts=counts, recent=recent, page='dashboard')

@app.route('/verify', methods=['GET','POST'])
def verify():
    if request.method == 'POST':
        doc_type = request.form.get('document_type','Other')
        upload = request.files.get('document') or request.files.get('file')
        if doc_type not in DOC_TYPES or not upload or not upload.filename: abort(400)
        
        ext = upload.filename.rsplit('.',1)[-1].lower()
        stored = f'{uuid.uuid4().hex}.{ext}'; path = UPLOAD_DIR / stored; upload.save(path)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
            
        text, confidence = get_ocr(path)
        score, warnings, status, number, name, dob = analyse(doc_type,text,path,digest,confidence)
        
        # 🚨 100% AUTOMATIC OVERRIDE LOCK: Kisi bhi haal me 'Manual Review' bacha toh use hard-change karein!
        if not number or status != 'Approved' or "Document number pattern not detected" in warnings:
            status = 'Rejected'
            score = max(score, 95)
            
        ref = 'DV-' + uuid.uuid4().hex[:8].upper()
        with db() as con:
            cur = con.execute('''INSERT INTO documents(ref,document_type,original_name,stored_name,ocr_text,status,risk_score,warnings,created_at,document_number,extracted_name,dob,image_hash,ocr_confidence)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (ref,doc_type,secure_filename(upload.filename),stored,text,status,score,' | '.join(warnings),datetime.now().strftime('%Y-%m-%d %H:%M:%S'),number,name,dob,digest,confidence))
            doc_id = cur.lastrowid
        return redirect(url_for('result',doc_id=doc_id))
    return render_template('verify.html', doc_types=DOC_TYPES, page='verify')

@app.route('/result/<int:doc_id>')
def result(doc_id):
    with db() as con: doc = con.execute('SELECT * FROM documents WHERE id=?',(doc_id,)).fetchone()
    return render_template('result.html',doc=doc,page='results')

@app.route('/results')
def results():
    with db() as con: docs = con.execute('SELECT * FROM documents ORDER BY id DESC').fetchall()
    return render_template('history.html',docs=docs,q='',selected_status='',page='results',heading='Results')

@app.route('/history')
def history():
    with db() as con: docs=con.execute('SELECT * FROM documents ORDER BY id DESC').fetchall()
    return render_template('history.html',docs=docs,q='',selected_status='',page='history',heading='History')

@app.route('/admin')
def admin():
    with db() as con: docs=con.execute("SELECT * FROM documents ORDER BY id DESC").fetchall()
    return render_template('admin.html',docs=docs,page='admin')

@app.route('/admin/review/<int:doc_id>',methods=['POST'])
def review(doc_id):
    action=request.form.get('action')
    with db() as con: con.execute('UPDATE documents SET status=? WHERE id=?',(action,doc_id))
    return redirect(url_for('admin'))

@app.route('/analytics')
def analytics():
    with db() as con:
        total=con.execute('SELECT COUNT(*) n FROM documents').fetchone()['n']
        by_type=con.execute('SELECT document_type,COUNT(*) n FROM documents GROUP BY document_type ORDER BY n DESC').fetchall()
        by_status=con.execute('SELECT status,COUNT(*) n FROM documents GROUP BY status').fetchall()
        avg=con.execute('SELECT AVG(risk_score) a FROM documents').fetchone()['a'] or 0
    return render_template('analytics.html',total=total,by_type=by_type,by_status=by_status,avg=round(avg,1),page='analytics')

@app.route('/rules')
def rules(): return render_template('rules.html',page='rules')
@app.route('/about')
def about(): return render_template('about.html',page='about')

init_db()
if __name__=='__main__': app.run(host='0.0.0.0',port=int(os.environ.get('PORT',5000)),debug=False)
