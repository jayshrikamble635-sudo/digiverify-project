# DigiVerify — Enterprise KYC Document Screening (Academic Project)

**Stack:** Python 3.10–3.12, Flask, SQLite, Tesseract OCR, Pillow, HTML/CSS. The application has eight modules: Dashboard, Verify, Results, History, Admin, Analytics, Rules and About.

## 1. Windows setup (recommended Python 3.12)

1. Install Python 3.12 from https://www.python.org/downloads/ and select **Add Python to PATH**.
2. Install Tesseract OCR for Windows. Keep English language data selected. Typical executable path: `C:\Program Files\Tesseract-OCR\tesseract.exe`.
3. Extract the ZIP. Open Command Prompt in the extracted `DigiVerify_Complete` folder and run:

```cmd
py -3.12 -m venv .venv312
.venv312\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

4. If Tesseract is not on PATH, set its path for this CMD window:

```cmd
set TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

5. Start the app:

```cmd
python app.py
```

6. Open `http://127.0.0.1:5000`.

To run tests (after dependencies are installed):

```cmd
python -m unittest tests.py -v
```

## 2. Render deployment

1. Push the extracted project folder contents to a GitHub repository (the `DigiVerify_Complete` folder should be the repository root).
2. In Render choose **New → Blueprint** and select the repository so Render reads `render.yaml`. If creating a Web Service manually, use Python 3, build command `apt-get update && apt-get install -y tesseract-ocr && pip install -r requirements.txt`, and start command `gunicorn app:app`.
3. Add environment variable `SECRET_KEY` with a long random value. `render.yaml` also provides a generated secret when deployed as a Blueprint.
4. The Blueprint build command installs Tesseract OCR on the Render build image. The app uses the English OCR language data.
5. For persistent records/uploads, attach a persistent disk and configure the app's database/upload paths to that disk before production use. Free ephemeral instances may lose local files on restart/redeploy.
6. Test the deployed URL using fictional, watermarked sample documents only.

## 3. Eight pages

1. **Dashboard** — total submissions, counts by status and recent activity.
2. **Verify** — select Aadhaar/PAN/Passport/Voter ID/Driving Licence and upload JPG/JPEG/PNG/WEBP (max 8 MB).
3. **Results** — individual result detail with OCR text, extracted fields, risk score and reasons.
4. **History** — searchable submission history and status filter.
5. **Admin** — review queue; an administrator can record Approved/Rejected/Review Required with a note. This academic build has no login/authentication; do not expose it publicly with personal documents.
6. **Analytics** — counts by document type/status and average risk score.
7. **Rules** — explains screening indicators and thresholds.
8. **About** — project purpose, technology and limitations.

## 4. Screening logic

- OCR: Tesseract image-to-data pass with confidence estimate and a fallback text pass; preprocessing corrects EXIF orientation, converts to grayscale, upscales small images, adjusts contrast and sharpens.
- Supported number-pattern checks: Aadhaar (12 digits), PAN, Passport, Voter ID and Driving Licence.
- Risk indicators: unreadable/short OCR, low confidence, low resolution, unusual aspect ratio, missing selected-type number pattern, explicit FAKE/SAMPLE/SPECIMEN/DEMO/NOT VALID/DUPLICATE markers, and exact duplicate file hash.
- **APPROVED:** lower risk and a matching number pattern.
- **REVIEW REQUIRED:** inconclusive OCR or risk evidence requiring human review.
- **REJECTED:** explicit suspicious marker, exact duplicate, or risk score ≥ 60.
- Risk score is a rule-based screening indicator, not a probability of fraud. The pattern checks are heuristic and can produce false positives/negatives.

## 5. Demo test cases

Use only invented text and fictional document images; never upload real Aadhaar/PAN/passport data.

| Case | Input | Expected behavior |
|---|---|---|
| TC-01 | Open `/` | Dashboard loads |
| TC-02 | Open each of the 8 navigation pages | Page responds |
| TC-03 | Fictional PAN image containing `ABCDE1234F` and a readable label | OCR attempts extraction; likely Approved if no other risk flags |
| TC-04 | Fictional PAN image with `SAMPLE` or `DEMO ONLY` | Rejected with suspicious-marker reason |
| TC-05 | Submit the exact same image twice | Second upload flagged as exact duplicate |
| TC-06 | Blurry/low-resolution image or unreadable text | Review Required or Rejected depending on accumulated risk |
| TC-07 | Wrong document type selected for the number pattern | Missing-pattern warning; usually Review Required |
| TC-08 | Upload PDF or unsupported extension | Upload rejected with validation message |
| TC-09 | Search a reference in History | Matching record shown |
| TC-10 | Admin records a decision with note | Status/note saved in local database |

Expected outcomes are test guidance, not claimed test results. Run the tests on the target machine and record actual results.

## 6. Important limitations / privacy

This is an academic OCR + heuristic screening prototype. It does **not** connect to UIDAI, Income Tax, Passport Seva, Election Commission or any government database. It cannot prove identity, document genuineness or detect every AI-generated/edited document. A green/Approved result only means the configured local screening rules passed. There is no production-grade user authentication, encryption-at-rest, malware scanning, audit-grade access control or guaranteed persistent storage. Do not use real identity documents or treat results as official KYC decisions.
