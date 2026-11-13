# DigiVerify — Live Demo & Examiner Guide

## Live demo flow

1. Start the app and show Dashboard.
2. Open Verify; select PAN and upload a fictional test image that contains a made-up PAN-shaped string such as `ABCDE1234F` (do not use an actual person's number).
3. Explain that Tesseract extracts visible text and the rules check the selected document-number pattern, OCR confidence and image indicators.
4. Show the result page: reference ID, status, risk score, reasons, OCR text and extracted fields.
5. Upload the same image again to demonstrate duplicate-image detection.
6. Upload a clearly watermarked `SAMPLE / DEMO ONLY` fictional card to demonstrate a suspicious-marker rejection.
7. Show History search, Admin review notes, Analytics, Rules and About.
8. State the limitations honestly: no government API, no guarantee of authenticity, no real-document usage.

## English presentation script

Good morning respected examiner. My name is Riddhi Kamble, from TYCS-A, Roll Number 21. Today I am presenting my final-year project, **DigiVerify — Enterprise KYC Document Screening System**.

The main objective of DigiVerify is to provide a web-based platform for preliminary screening of identity-document images. It supports Aadhaar, PAN, Passport, Voter ID and Driving Licence document categories.

The application is developed using Python Flask for the backend, HTML and CSS for the user interface, SQLite for local data storage, Tesseract OCR for text extraction and Pillow for image preprocessing.

When a user uploads an image, the system validates the file, preprocesses the image and runs OCR. It then checks the extracted text for the selected document-number pattern. It also checks image quality, OCR confidence, suspicious words such as SAMPLE or DEMO, and whether the exact same image was submitted earlier.

Based on these indicators, the system displays one of three outcomes: APPROVED, REJECTED or REVIEW REQUIRED. It also displays a risk score and the reasons behind the result. The Admin page allows a reviewer to record a decision and a note for cases that need human attention.

The project contains eight modules: Dashboard, Verify, Results, History, Admin, Analytics, Rules and About. These modules provide submission, screening, record tracking, review and summary functions.

One important limitation is that DigiVerify is an academic screening prototype. It does not connect to government databases such as UIDAI or the Income Tax Department. Therefore, APPROVED means that the local screening rules passed; it is not official proof that an identity document is genuine.

In the future, the project can be improved with secure authentication, encrypted storage, stronger document tampering analysis, multilingual OCR, secure cloud storage and authorized verification APIs if access is legally available.

Thank you. I am ready to demonstrate the application and answer your questions.

## Hindi explanation (simple Hinglish)

Good morning sir/madam. Mera naam Riddhi Kamble hai. Main TYCS-A, Roll Number 21 se hoon. Mere final-year project ka naam DigiVerify hai.

DigiVerify ek web application hai jo identity document ki image ko upload karke uska initial screening karta hai. Isme Aadhaar, PAN, Passport, Voter ID aur Driving Licence categories hain.

User image upload karta hai. Flask backend image ko receive karta hai. Pillow image ko readable banane ke liye preprocessing karta hai. Tesseract OCR image ke andar likha hua text read karta hai. Phir system selected document type ka number pattern, image quality, OCR confidence, SAMPLE/DEMO jaise suspicious words aur duplicate image check karta hai.

In checks ke basis par result APPROVED, REJECTED ya REVIEW REQUIRED aata hai. Saath mein risk score aur reason bhi dikhte hain. Admin page par reviewer apna decision aur note save kar sakta hai.

Is project mein total 8 pages hain: Dashboard, Verify, Results, History, Admin, Analytics, Rules aur About.

Important limitation ye hai ki project kisi government database se connected nahi hai. Isliye APPROVED ka matlab sirf itna hai ki hamare local rules pass hue hain. Ye official Aadhaar ya PAN verification nahi hai.

Future mein authentication, encrypted database, better OCR, document tampering detection aur legally authorized APIs add ki ja sakti hain.

Thank you.

## Viva questions and answers

**Q1. What is DigiVerify?**  
It is a web-based academic prototype for preliminary OCR-based identity-document screening.

**Q2. What is OCR?**  
OCR means Optical Character Recognition. It converts text visible in an image into machine-readable text.

**Q3. Which OCR engine is used?**  
Tesseract OCR, through the Python `pytesseract` library.

**Q4. Why is Pillow used?**  
Pillow is used for image opening, orientation correction, grayscale conversion, resizing, contrast enhancement and sharpening.

**Q5. Which document categories are supported?**  
Aadhaar, PAN, Passport, Voter ID and Driving Licence.

**Q6. What is a risk score?**  
It is a rule-based numeric indicator that increases when suspicious or incomplete signals are detected. It is not a statistical fraud probability.

**Q7. What does REVIEW REQUIRED mean?**  
The automated checks do not have enough confidence for a clear decision, so a human reviewer should inspect it.

**Q8. How is a duplicate detected?**  
The system calculates a SHA-256 hash of the uploaded file and compares it with earlier submissions.

**Q9. Does APPROVED guarantee a genuine document?**  
No. It only means that the configured local screening rules passed. There is no government database connection.

**Q10. Which database is used?**  
SQLite, which stores document metadata, OCR text, status, risk score and review information.

**Q11. Why Flask?**  
Flask is a lightweight Python web framework suitable for routing, handling uploads and connecting application logic to HTML templates.

**Q12. What are the eight modules?**  
Dashboard, Verify, Results, History, Admin, Analytics, Rules and About.

**Q13. What are the limitations?**  
OCR errors, heuristic false positives/negatives, no government verification API, and no production-grade authentication or security controls.

**Q14. What is the future scope?**  
Secure login, encryption, stronger tampering analysis, multilingual OCR, cloud storage and authorized verification APIs.

**Q15. Why do we need human review?**  
OCR may misread text and rule checks cannot reliably prove authenticity. Human review handles uncertain cases.
